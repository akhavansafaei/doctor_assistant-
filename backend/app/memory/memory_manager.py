"""
Memory Management System for AI Doctor Chatbot

Implements short-term and long-term memory with automatic summarization:
- Short-term: Current chat session messages
- Long-term: Past conversations from database with summarization

Thresholds:
1. Single chat threshold: Summarize individual chats if too long
2. Total memory threshold: Summarize all long-term memory if exceeds limit
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.database import Conversation, Message as DBMessage
from app.memory.summarizer import ConversationSummarizer
from app.core.config import settings


class MemoryThresholds:
    """Configuration for memory thresholds"""

    # Token counts (approximate)
    SINGLE_CHAT_TOKEN_THRESHOLD = 2000  # If single chat > 2000 tokens, summarize to ~500
    SINGLE_CHAT_SUMMARY_TARGET = 500    # Target size for summarized chat

    TOTAL_MEMORY_TOKEN_THRESHOLD = 8000  # If total memory > 8000 tokens, summarize to ~2000
    TOTAL_MEMORY_SUMMARY_TARGET = 2000   # Target size for total memory summary

    # Message counts (alternative to token counts)
    SINGLE_CHAT_MESSAGE_THRESHOLD = 30   # If chat has > 30 messages, summarize
    TOTAL_MEMORY_MESSAGE_THRESHOLD = 100 # If total messages > 100, create summary

    # Time-based relevance
    RECENT_CONVERSATIONS_DAYS = 30       # Consider conversations from last 30 days
    MAX_CONVERSATIONS_TO_RETRIEVE = 10   # Maximum number of past conversations


class ConversationMemory:
    """Represents a conversation with optional summary"""

    def __init__(
        self,
        conversation_id: str,
        session_id: str,
        messages: List[Dict[str, Any]],
        created_at: datetime,
        is_summarized: bool = False,
        summary: Optional[str] = None,
        token_count: Optional[int] = None
    ):
        self.conversation_id = conversation_id
        self.session_id = session_id
        self.messages = messages
        self.created_at = created_at
        self.is_summarized = is_summarized
        self.summary = summary
        self.token_count = token_count or self._estimate_tokens()

    def _estimate_tokens(self) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 characters)"""
        total_chars = sum(len(msg.get('content', '')) for msg in self.messages)
        return total_chars // 4

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'conversation_id': self.conversation_id,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'is_summarized': self.is_summarized,
            'summary': self.summary,
            'messages': self.messages if not self.is_summarized else [],
            'token_count': self.token_count
        }


class MemoryManager:
    """Manages short-term and long-term memory with automatic summarization"""

    def __init__(self, db: Session, user_id: int, thresholds: Optional[MemoryThresholds] = None):
        self.db = db
        self.user_id = user_id
        self.thresholds = thresholds or MemoryThresholds()
        self.summarizer = ConversationSummarizer()

    async def get_short_term_memory(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get current session messages (short-term memory)

        Returns:
            List of message dictionaries
        """
        conversation = self.db.query(Conversation).filter(
            Conversation.session_id == session_id,
            Conversation.user_id == self.user_id
        ).first()

        if not conversation:
            return []

        messages = self.db.query(DBMessage).filter(
            DBMessage.conversation_id == conversation.id
        ).order_by(DBMessage.created_at).all()

        return [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.created_at.isoformat()
            }
            for msg in messages
        ]

    async def get_long_term_memory(
        self,
        current_session_id: str,
        include_summaries: bool = True
    ) -> List[ConversationMemory]:
        """
        Get past conversations (long-term memory) with automatic summarization

        Args:
            current_session_id: Current session to exclude
            include_summaries: Whether to include conversation summaries

        Returns:
            List of ConversationMemory objects
        """
        # Get recent conversations (excluding current session)
        cutoff_date = datetime.utcnow() - timedelta(days=self.thresholds.RECENT_CONVERSATIONS_DAYS)

        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == self.user_id,
            Conversation.session_id != current_session_id,
            Conversation.created_at >= cutoff_date
        ).order_by(
            desc(Conversation.updated_at)
        ).limit(self.thresholds.MAX_CONVERSATIONS_TO_RETRIEVE).all()

        memory_items: List[ConversationMemory] = []

        for conv in conversations:
            # Get messages for this conversation
            messages = self.db.query(DBMessage).filter(
                DBMessage.conversation_id == conv.id
            ).order_by(DBMessage.created_at).all()

            message_dicts = [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat()
                }
                for msg in messages
            ]

            # Check if conversation needs summarization
            memory = ConversationMemory(
                conversation_id=str(conv.id),
                session_id=conv.session_id,
                messages=message_dicts,
                created_at=conv.created_at
            )

            # Apply single-chat threshold
            if self._should_summarize_conversation(memory):
                summary = await self.summarizer.summarize_conversation(
                    message_dicts,
                    target_length=self.thresholds.SINGLE_CHAT_SUMMARY_TARGET
                )
                memory.is_summarized = True
                memory.summary = summary
                memory.token_count = len(summary) // 4  # Rough estimate

            memory_items.append(memory)

        # Apply total memory threshold
        total_tokens = sum(m.token_count for m in memory_items)
        if total_tokens > self.thresholds.TOTAL_MEMORY_TOKEN_THRESHOLD:
            memory_items = await self._compress_memory(memory_items)

        return memory_items

    def _should_summarize_conversation(self, memory: ConversationMemory) -> bool:
        """Check if a single conversation should be summarized"""
        # Check token threshold
        if memory.token_count > self.thresholds.SINGLE_CHAT_TOKEN_THRESHOLD:
            return True

        # Check message count threshold
        if len(memory.messages) > self.thresholds.SINGLE_CHAT_MESSAGE_THRESHOLD:
            return True

        return False

    async def _compress_memory(
        self,
        memory_items: List[ConversationMemory]
    ) -> List[ConversationMemory]:
        """
        Compress total memory by creating a meta-summary

        Strategy:
        1. Keep most recent 2 conversations as-is
        2. Summarize the rest into a single comprehensive summary
        """
        if len(memory_items) <= 2:
            return memory_items

        # Keep most recent 2 conversations
        recent = memory_items[:2]
        older = memory_items[2:]

        # Create comprehensive summary of older conversations
        all_messages = []
        for mem in older:
            if mem.is_summarized and mem.summary:
                all_messages.append({
                    'role': 'assistant',
                    'content': f"[Previous conversation summary]: {mem.summary}",
                    'timestamp': mem.created_at.isoformat()
                })
            else:
                all_messages.extend(mem.messages)

        if all_messages:
            comprehensive_summary = await self.summarizer.summarize_multiple_conversations(
                all_messages,
                target_length=self.thresholds.TOTAL_MEMORY_SUMMARY_TARGET
            )

            # Create a single compressed memory item
            compressed_memory = ConversationMemory(
                conversation_id="compressed_memory",
                session_id="multiple",
                messages=[],
                created_at=older[0].created_at if older else datetime.utcnow(),
                is_summarized=True,
                summary=comprehensive_summary,
                token_count=len(comprehensive_summary) // 4
            )

            return recent + [compressed_memory]

        return recent

    async def format_memory_for_prompt(
        self,
        current_session_id: str,
        include_short_term: bool = True
    ) -> str:
        """
        Format memory (short-term + long-term) for inclusion in LLM prompt

        Args:
            current_session_id: Current session ID
            include_short_term: Whether to include current session messages

        Returns:
            Formatted memory string for prompt injection
        """
        parts = []

        # Long-term memory (past conversations)
        long_term = await self.get_long_term_memory(current_session_id)

        if long_term:
            parts.append("=== PATIENT HISTORY (Past Conversations) ===\n")

            for memory in reversed(long_term):  # Oldest first
                date_str = memory.created_at.strftime("%Y-%m-%d")

                if memory.is_summarized and memory.summary:
                    parts.append(f"[{date_str}] Summary: {memory.summary}\n")
                else:
                    # Include key messages only
                    user_messages = [m for m in memory.messages if m['role'] == 'user']
                    if user_messages:
                        parts.append(f"[{date_str}] Topics discussed: ")
                        topics = [m['content'][:100] for m in user_messages[:3]]
                        parts.append(", ".join(topics) + "\n")

            parts.append("\n")

        # Short-term memory (current session)
        if include_short_term:
            short_term = await self.get_short_term_memory(current_session_id)

            if short_term:
                parts.append("=== CURRENT CONVERSATION ===\n")
                for msg in short_term:
                    role = msg['role'].upper()
                    content = msg['content']
                    parts.append(f"{role}: {content}\n")
                parts.append("\n")

        return "".join(parts)

    async def get_memory_summary(self, current_session_id: str) -> Dict[str, Any]:
        """
        Get a summary of memory status (for debugging/monitoring)

        Returns:
            Dictionary with memory statistics
        """
        long_term = await self.get_long_term_memory(current_session_id)
        short_term = await self.get_short_term_memory(current_session_id)

        total_long_term_tokens = sum(m.token_count for m in long_term)
        summarized_count = sum(1 for m in long_term if m.is_summarized)

        return {
            'short_term_messages': len(short_term),
            'long_term_conversations': len(long_term),
            'summarized_conversations': summarized_count,
            'total_long_term_tokens': total_long_term_tokens,
            'thresholds': {
                'single_chat_token_threshold': self.thresholds.SINGLE_CHAT_TOKEN_THRESHOLD,
                'total_memory_token_threshold': self.thresholds.TOTAL_MEMORY_TOKEN_THRESHOLD
            }
        }

    async def clear_old_memories(self, days: int = 90) -> int:
        """
        Clear conversations older than specified days

        Args:
            days: Number of days to keep

        Returns:
            Number of conversations deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        old_conversations = self.db.query(Conversation).filter(
            Conversation.user_id == self.user_id,
            Conversation.created_at < cutoff_date
        ).all()

        count = len(old_conversations)

        for conv in old_conversations:
            # Delete messages first
            self.db.query(DBMessage).filter(
                DBMessage.conversation_id == conv.id
            ).delete()

            # Delete conversation
            self.db.delete(conv)

        self.db.commit()

        return count
