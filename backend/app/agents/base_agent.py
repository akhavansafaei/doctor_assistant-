"""Base agent class for all specialized agents"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from app.core.config import settings
from app.rag import HybridRetriever


class BaseAgent(ABC):
    """Base class for all specialized medical agents"""

    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        use_rag: bool = True
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.use_rag = use_rag

        # Initialize LLM
        self.llm = self._initialize_llm()

        # Initialize RAG if needed
        self.retriever = HybridRetriever() if use_rag else None

    def _initialize_llm(self):
        """Initialize the LLM based on configuration"""
        if settings.primary_llm == "openai":
            return ChatOpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                api_key=settings.openai_api_key
            )
        elif settings.primary_llm == "anthropic":
            return ChatAnthropic(
                model="claude-3-opus-20240229",
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                api_key=settings.anthropic_api_key
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.primary_llm}")

    async def retrieve_context(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context from knowledge base"""
        if not self.use_rag or not self.retriever:
            return []

        results = await self.retriever.retrieve(
            query=query,
            filters=filters,
            rerank=True
        )
        return results

    def format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents into context string"""
        if not retrieved_docs:
            return ""

        context_parts = ["Retrieved Medical Knowledge:\n"]
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"\n[Source {i}]")
            context_parts.append(f"Text: {doc['text']}")
            if 'metadata' in doc:
                metadata = doc['metadata']
                if 'source' in metadata:
                    context_parts.append(f"Source: {metadata['source']}")
                if 'title' in metadata:
                    context_parts.append(f"Title: {metadata['title']}")
            context_parts.append(f"Relevance Score: {doc.get('rerank_score', doc.get('rrf_score', 0)):.3f}")
            context_parts.append("")

        return "\n".join(context_parts)

    @abstractmethod
    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process input and return agent output

        Args:
            input_data: Input data for the agent
            context: Additional context (conversation history, patient profile, etc.)

        Returns:
            Dict containing agent output
        """
        pass

    async def invoke_llm(
        self,
        messages: List[Any],
        temperature: Optional[float] = None
    ) -> str:
        """Invoke the LLM with messages"""
        if temperature is not None:
            # Create a new LLM instance with different temperature
            llm = self.llm.bind(temperature=temperature)
        else:
            llm = self.llm

        response = await llm.ainvoke(messages)
        return response.content

    def create_messages(
        self,
        user_message: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Any]:
        """Create message list for LLM invocation"""
        messages = [SystemMessage(content=self.system_prompt)]

        # Add context if available
        if context:
            messages.append(SystemMessage(content=context))

        # Add conversation history
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

        # Add current user message
        messages.append(HumanMessage(content=user_message))

        return messages

    def extract_structured_output(
        self,
        response: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract structured output from LLM response
        In production, use function calling or structured output features
        """
        # Placeholder - in production, use JSON mode or function calling
        import json
        import re

        # Try to find JSON in response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {"raw_response": response}
