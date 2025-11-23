"""Hybrid retrieval system combining dense and sparse retrieval"""
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from app.core.config import settings
from .embeddings import EmbeddingService
from .vector_store import VectorStoreManager
import re


class HybridRetriever:
    """Hybrid retriever combining dense (semantic) and sparse (keyword) retrieval"""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreManager()
        self.bm25_index = None
        self.documents = []
        self.alpha = settings.hybrid_alpha  # Weight for dense vs sparse (0-1)

    async def initialize(self):
        """Initialize the retriever"""
        await self.vector_store.initialize_collection()

    def preprocess_text(self, text: str) -> List[str]:
        """Preprocess text for BM25"""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Split into tokens
        tokens = text.split()
        return tokens

    async def index_documents(
        self,
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ):
        """Index documents for both dense and sparse retrieval"""
        # Generate embeddings for dense retrieval
        embeddings = await self.embedding_service.embed_texts(documents)

        # Add to vector store
        await self.vector_store.add_documents(documents, embeddings, metadata)

        # Create BM25 index for sparse retrieval
        self.documents = documents
        tokenized_docs = [self.preprocess_text(doc) for doc in documents]
        self.bm25_index = BM25Okapi(tokenized_docs)

    async def retrieve(
        self,
        query: str,
        top_k: int = None,
        filters: Optional[Dict[str, Any]] = None,
        rerank: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents using hybrid approach

        Args:
            query: Search query
            top_k: Number of results to return
            filters: Metadata filters
            rerank: Whether to use reranking

        Returns:
            List of retrieved documents with scores
        """
        top_k = top_k or settings.top_k_retrieval

        # Dense retrieval (semantic search)
        query_embedding = await self.embedding_service.embed_text(query)
        dense_results = await self.vector_store.search(
            query_vector=query_embedding,
            top_k=top_k * 2,  # Retrieve more for fusion
            filters=filters
        )

        # Sparse retrieval (BM25 keyword search)
        sparse_results = []
        if self.bm25_index is not None:
            query_tokens = self.preprocess_text(query)
            bm25_scores = self.bm25_index.get_scores(query_tokens)

            # Get top documents with scores
            top_indices = sorted(
                range(len(bm25_scores)),
                key=lambda i: bm25_scores[i],
                reverse=True
            )[:top_k * 2]

            sparse_results = [
                {
                    "text": self.documents[i],
                    "score": float(bm25_scores[i]),
                    "source": "bm25"
                }
                for i in top_indices if bm25_scores[i] > 0
            ]

        # Hybrid fusion using Reciprocal Rank Fusion (RRF)
        fused_results = self._reciprocal_rank_fusion(
            dense_results,
            sparse_results,
            k=60  # RRF parameter
        )

        # Take top-k after fusion
        fused_results = fused_results[:top_k]

        # Optional reranking
        if rerank and settings.cohere_api_key:
            fused_results = await self._rerank(query, fused_results)

        return fused_results[:settings.rerank_top_k if rerank else top_k]

    def _reciprocal_rank_fusion(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]],
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Combine results from dense and sparse retrieval using RRF

        RRF formula: score = sum(1 / (k + rank_i)) for each retrieval method
        """
        # Create a dictionary to accumulate scores
        doc_scores = {}

        # Add dense results
        for rank, result in enumerate(dense_results, 1):
            doc_id = result.get("id", result.get("text", ""))
            score = 1.0 / (k + rank)
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {
                    "text": result.get("text", ""),
                    "metadata": result.get("metadata", {}),
                    "dense_score": result.get("score", 0),
                    "sparse_score": 0,
                    "rrf_score": 0
                }
            doc_scores[doc_id]["rrf_score"] += self.alpha * score

        # Add sparse results
        for rank, result in enumerate(sparse_results, 1):
            doc_id = result.get("id", result.get("text", ""))
            score = 1.0 / (k + rank)
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {
                    "text": result.get("text", ""),
                    "metadata": result.get("metadata", {}),
                    "dense_score": 0,
                    "sparse_score": result.get("score", 0),
                    "rrf_score": 0
                }
            else:
                doc_scores[doc_id]["sparse_score"] = result.get("score", 0)
            doc_scores[doc_id]["rrf_score"] += (1 - self.alpha) * score

        # Sort by RRF score
        sorted_results = sorted(
            [{"id": k, **v} for k, v in doc_scores.items()],
            key=lambda x: x["rrf_score"],
            reverse=True
        )

        return sorted_results

    async def _rerank(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rerank results using Cohere Rerank API"""
        try:
            import cohere
            co = cohere.Client(settings.cohere_api_key)

            documents = [r["text"] for r in results]
            rerank_response = co.rerank(
                query=query,
                documents=documents,
                top_n=settings.rerank_top_k,
                model="rerank-english-v3.0"
            )

            # Reorder results based on reranking
            reranked = []
            for result in rerank_response.results:
                original = results[result.index]
                original["rerank_score"] = result.relevance_score
                reranked.append(original)

            return reranked
        except Exception as e:
            # Fallback to original results if reranking fails
            print(f"Reranking failed: {e}")
            return results

    async def expand_query(self, query: str) -> List[str]:
        """
        Expand query with medical synonyms and related terms
        This could use a medical ontology or LLM for expansion
        """
        # Placeholder for query expansion
        # In production, integrate with UMLS, SNOMED CT, or use LLM
        return [query]
