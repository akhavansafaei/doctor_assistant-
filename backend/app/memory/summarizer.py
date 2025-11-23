"""
Conversation Summarizer using LLM

Generates concise summaries of conversations for long-term memory management.
"""

from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings


class ConversationSummarizer:
    """Uses LLM to create intelligent conversation summaries"""

    def __init__(self):
        """Initialize summarizer with configured LLM"""
        self.llm = self._get_llm()

    def _get_llm(self):
        """Get configured LLM for summarization (uses cheaper/faster model)"""
        # Use cheaper model for summarization
        if settings.primary_llm == "openai":
            return ChatOpenAI(
                api_key=settings.openai_api_key,
                model="gpt-3.5-turbo",  # Cheaper for summarization
                temperature=0.3,
                max_tokens=1000
            )
        elif settings.primary_llm == "anthropic":
            return ChatAnthropic(
                api_key=settings.anthropic_api_key,
                model="claude-3-haiku-20240307",  # Cheapest Claude model
                temperature=0.3,
                max_tokens=1000
            )
        else:
            # Default to OpenAI
            return ChatOpenAI(
                api_key=settings.openai_api_key,
                model="gpt-3.5-turbo",
                temperature=0.3,
                max_tokens=1000
            )

    async def summarize_conversation(
        self,
        messages: List[Dict[str, Any]],
        target_length: int = 500
    ) -> str:
        """
        Summarize a single conversation

        Args:
            messages: List of message dicts with 'role' and 'content'
            target_length: Target token length for summary

        Returns:
            Concise summary of the conversation
        """
        # Format conversation for summarization
        conversation_text = self._format_messages(messages)

        system_prompt = """You are a medical conversation summarizer. Create a concise medical summary of the following patient conversation.

IMPORTANT GUIDELINES:
1. Focus on MEDICAL INFORMATION ONLY (symptoms, diagnoses, treatments, advice given)
2. Use clinical terminology where appropriate
3. Preserve specific details: medications, dosages, allergies, conditions
4. Note any follow-up recommendations or warnings
5. Keep it factual and structured
6. Omit pleasantries, greetings, and non-medical chatter

FORMAT:
Chief Complaint: [Main issue discussed]
Key Symptoms: [List of symptoms mentioned]
Medical Advice Given: [Summary of recommendations]
Medications/Treatments: [Any mentioned]
Follow-up: [Any follow-up instructions]
Red Flags: [Any warnings or concerns raised]
"""

        user_prompt = f"""Summarize this medical conversation (target ~{target_length} tokens):

{conversation_text}

Provide a structured summary following the format above."""

        messages_for_llm = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        try:
            response = await self.llm.ainvoke(messages_for_llm)
            summary = response.content.strip()
            return summary
        except Exception as e:
            # Fallback to simple concatenation if LLM fails
            print(f"Summarization failed: {e}")
            return self._fallback_summary(messages)

    async def summarize_multiple_conversations(
        self,
        messages: List[Dict[str, Any]],
        target_length: int = 2000
    ) -> str:
        """
        Create a comprehensive summary of multiple conversations

        Args:
            messages: All messages from multiple conversations
            target_length: Target token length for comprehensive summary

        Returns:
            Comprehensive summary of patient history
        """
        conversation_text = self._format_messages(messages)

        system_prompt = """You are a medical historian creating a comprehensive patient history summary from multiple past conversations.

IMPORTANT GUIDELINES:
1. Create a LONGITUDINAL medical summary showing progression over time
2. Group information by medical categories (conditions, medications, symptoms, etc.)
3. Note any changes or progression in health status
4. Highlight recurring issues or chronic conditions
5. Preserve all medication names, dosages, and allergies
6. Note patterns and trends
7. Keep it concise but comprehensive

FORMAT:
Medical History Overview: [Brief overview of patient's journey]

Chronic Conditions: [Ongoing conditions mentioned]

Recurring Symptoms: [Symptoms mentioned across multiple visits]

Medications History: [All medications mentioned over time]

Allergies/Contraindications: [Any allergies or warnings]

Key Medical Advice: [Important recommendations given]

Trends & Observations: [Any patterns noticed]
"""

        user_prompt = f"""Create a comprehensive medical history summary from these past conversations (target ~{target_length} tokens):

{conversation_text}

Provide a structured longitudinal summary."""

        messages_for_llm = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        try:
            response = await self.llm.ainvoke(messages_for_llm)
            summary = response.content.strip()
            return summary
        except Exception as e:
            print(f"Multi-conversation summarization failed: {e}")
            return self._fallback_summary(messages)

    def _format_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Format messages into readable conversation text"""
        lines = []
        for msg in messages:
            role = msg.get('role', 'unknown').upper()
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')

            if timestamp:
                lines.append(f"[{timestamp}] {role}: {content}")
            else:
                lines.append(f"{role}: {content}")

        return "\n".join(lines)

    def _fallback_summary(self, messages: List[Dict[str, Any]]) -> str:
        """Simple fallback summary if LLM fails"""
        user_messages = [m for m in messages if m.get('role') == 'user']

        if not user_messages:
            return "No significant medical information to summarize."

        # Extract first few user queries as topics
        topics = [m.get('content', '')[:100] for m in user_messages[:5]]

        summary_parts = [
            "Medical consultation covered the following topics:",
            *[f"- {topic}" for topic in topics]
        ]

        if len(user_messages) > 5:
            summary_parts.append(f"- ... and {len(user_messages) - 5} more topics")

        return "\n".join(summary_parts)

    async def extract_key_medical_entities(
        self,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Extract key medical entities from conversation
        (conditions, medications, symptoms, etc.)

        Returns:
            Dictionary with categorized entities
        """
        conversation_text = self._format_messages(messages)

        system_prompt = """Extract key medical entities from this conversation.

Return ONLY a JSON object with these categories:
{
  "symptoms": ["list of symptoms mentioned"],
  "conditions": ["list of conditions/diagnoses mentioned"],
  "medications": ["list of medications mentioned"],
  "allergies": ["list of allergies mentioned"],
  "procedures": ["list of procedures/tests mentioned"],
  "warnings": ["list of warnings or red flags"]
}

Only include items explicitly mentioned. Return empty arrays for missing categories."""

        user_prompt = f"""Extract medical entities from:\n\n{conversation_text}"""

        messages_for_llm = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        try:
            response = await self.llm.ainvoke(messages_for_llm)
            import json
            entities = json.loads(response.content.strip())
            return entities
        except Exception as e:
            print(f"Entity extraction failed: {e}")
            return {
                "symptoms": [],
                "conditions": [],
                "medications": [],
                "allergies": [],
                "procedures": [],
                "warnings": []
            }

    async def generate_continuity_context(
        self,
        past_summaries: List[str],
        current_query: str
    ) -> str:
        """
        Generate continuity context by connecting past history to current query

        Args:
            past_summaries: List of past conversation summaries
            current_query: Current user query

        Returns:
            Continuity context to inject into prompt
        """
        if not past_summaries:
            return ""

        combined_history = "\n\n".join(past_summaries)

        system_prompt = """Based on the patient's history and current query, provide brief context about relevant past information.

Focus on:
1. Related past symptoms or conditions
2. Previously prescribed medications that might be relevant
3. Past advice that might inform current situation
4. Any patterns or trends

Keep it very brief (2-3 sentences max). If no relevant history, say "No directly relevant past history."
"""

        user_prompt = f"""Patient History:
{combined_history}

Current Query: {current_query}

Provide brief relevant context:"""

        messages_for_llm = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        try:
            response = await self.llm.ainvoke(messages_for_llm)
            return response.content.strip()
        except Exception as e:
            print(f"Continuity context generation failed: {e}")
            return ""
