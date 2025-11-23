"""Embedding generation service"""
from typing import List, Optional
from openai import AsyncOpenAI
from app.core.config import settings
import numpy as np


class EmbeddingService:
    """Service for generating embeddings"""

    def __init__(self, model: Optional[str] = None):
        self.model = model or settings.embedding_model
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.dimension = 3072 if "3-large" in self.model else 1536

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        return float(np.dot(vec1_np, vec2_np) / (np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np)))
