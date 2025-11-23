"""Vector store manager using Qdrant"""
from typing import List, Dict, Any, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue, SearchParams
)
from app.core.config import settings
import uuid


class VectorStoreManager:
    """Manages vector database operations with Qdrant"""

    def __init__(self):
        self.client = AsyncQdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection_name
        self.vector_size = 3072 if "3-large" in settings.embedding_model else 1536

    async def initialize_collection(self):
        """Initialize the vector collection if it doesn't exist"""
        try:
            await self.client.get_collection(self.collection_name)
        except Exception:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )

    async def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]]
    ) -> List[str]:
        """Add documents to vector store"""
        points = []
        ids = []

        for doc, embedding, meta in zip(documents, embeddings, metadata):
            point_id = str(uuid.uuid4())
            ids.append(point_id)

            payload = {
                "text": doc,
                **meta
            }

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            )

        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return ids

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        search_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            search_filter = Filter(must=conditions)

        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=search_filter,
            search_params=SearchParams(hnsw_ef=128, exact=False)
        )

        return [
            {
                "id": result.id,
                "score": result.score,
                "text": result.payload.get("text", ""),
                "metadata": {k: v for k, v in result.payload.items() if k != "text"}
            }
            for result in results
        ]

    async def delete_documents(self, document_ids: List[str]):
        """Delete documents from vector store"""
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=document_ids
        )

    async def update_document(
        self,
        document_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        """Update a document in the vector store"""
        await self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=document_id,
                    vector=embedding,
                    payload=metadata
                )
            ]
        )
