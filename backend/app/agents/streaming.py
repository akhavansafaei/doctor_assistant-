"""Streaming support for agents"""
from typing import Dict, Any, Optional, AsyncIterator, Callable
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import LLMResult
import asyncio


class StreamingCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM tokens"""

    def __init__(self, on_token: Callable[[str], None]):
        """
        Initialize callback handler

        Args:
            on_token: Async function to call for each token
        """
        self.on_token = on_token
        self.tokens = []

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when LLM generates a new token"""
        self.tokens.append(token)
        await self.on_token(token)

    async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Called when LLM finishes"""
        pass

    async def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Called when LLM encounters an error"""
        pass


class StreamingAgent:
    """Mixin for adding streaming capabilities to agents"""

    async def stream_process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        on_token: Optional[Callable[[str], None]] = None,
        on_status: Optional[Callable[[str, Dict], None]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Process input with streaming support

        Args:
            input_data: Input data for processing
            context: Additional context
            on_token: Callback for each token
            on_status: Callback for status updates

        Yields:
            Dict containing streaming updates
        """
        # Send initial status
        if on_status:
            await on_status("processing", {"agent": self.name})

        # Retrieve context if RAG is enabled
        if self.use_rag and self.retriever:
            if on_status:
                await on_status("retrieving_context", {"agent": self.name})

            message = input_data.get("message", "")
            retrieved_docs = await self.retrieve_context(message)
            medical_context = self.format_context(retrieved_docs)

            yield {
                "type": "context_retrieved",
                "sources": [
                    {
                        "text": doc["text"][:200],
                        "score": doc.get("rerank_score", doc.get("rrf_score", 0))
                    }
                    for doc in retrieved_docs[:3]
                ]
            }
        else:
            medical_context = ""

        # Prepare messages
        conversation_history = context.get("conversation_history", []) if context else []
        messages = self.create_messages(
            user_message=input_data.get("message", ""),
            context=medical_context,
            conversation_history=conversation_history
        )

        if on_status:
            await on_status("generating_response", {"agent": self.name})

        # Stream LLM response
        accumulated_response = []

        async def token_callback(token: str):
            accumulated_response.append(token)
            if on_token:
                await on_token(token)

        # Create streaming callback
        callback = StreamingCallbackHandler(on_token=token_callback)

        # Invoke LLM with streaming
        llm_with_streaming = self.llm.bind(
            streaming=True,
            callbacks=[callback]
        )

        response = await llm_with_streaming.ainvoke(messages)
        full_response = "".join(accumulated_response)

        # Yield final result
        yield {
            "type": "response_complete",
            "content": full_response,
            "agent": self.name
        }


def make_streaming_agent(agent_class):
    """
    Decorator to add streaming capabilities to an agent class

    Usage:
        @make_streaming_agent
        class MyAgent(BaseAgent):
            ...
    """
    class StreamingAgentClass(agent_class, StreamingAgent):
        pass

    StreamingAgentClass.__name__ = f"Streaming{agent_class.__name__}"
    return StreamingAgentClass
