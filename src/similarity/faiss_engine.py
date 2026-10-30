"""Dual-Mode FAISS Cosine Similarity Engine (Instant Offline Mode + Optional Lightweight Neural Mode)."""

from typing import Any, List, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    import faiss
    FaissIndexType = faiss.IndexFlatIP
except ImportError:
    faiss = None
    FaissIndexType = Any

import config


class FaissSimilarityEngine:
    """Computes Semantic Cosine Similarity using FAISS IndexFlatIP.

    Supports two modes:
    1. Fast Offline Mode (use_neural=False): Instant Character N-Gram + Word Sublinear Vectorization in FAISS.
    2. Lightweight Neural Mode (use_neural=True): Loads 'paraphrase-multilingual-MiniLM-L12-v2' on demand.
    """

    def __init__(
        self,
        model_name: str = config.EMBEDDING_MODEL_NAME,
        use_neural: bool = False,
    ) -> None:
        self.model_name = model_name
        self.use_neural = use_neural
        self.model: Optional[Any] = None
        self.dimension: int = 384

        if self.use_neural:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            if hasattr(self.model, "get_embedding_dimension"):
                self.dimension = self.model.get_embedding_dimension()
            else:
                self.dimension = self.model.get_sentence_embedding_dimension()

    @staticmethod
    def compute_vector_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Explicitly compute mathematical Cosine Similarity: (A . B) / (||A|| * ||B||)."""
        norm_a = float(np.linalg.norm(vec_a))
        norm_b = float(np.linalg.norm(vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        cos_sim = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
        return float(np.clip(cos_sim, 0.0, 1.0))

    @staticmethod
    def map_cosine_to_percentage(cosine_val: float) -> float:
        """Clamp cosine similarity value cleanly into [0.0, 1.0]."""
        return float(np.clip(cosine_val, 0.0, 1.0))

    def _encode_fast_subword(self, texts: List[str]) -> np.ndarray:
        """Encode texts instantaneously using Persian morphological char n-grams (L2 normalized)."""
        if not texts:
            return np.empty((0, 1), dtype=np.float32)

        vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 5),
            sublinear_tf=True,
        )
        try:
            tfidf_mat = vectorizer.fit_transform(texts)
            if tfidf_mat.shape[1] == 0:
                return np.zeros((len(texts), 1), dtype=np.float32)

            dense = tfidf_mat.toarray().astype(np.float32)
            norms = np.linalg.norm(dense, axis=1, keepdims=True)
            norms[norms == 0.0] = 1.0
            return (dense / norms).astype(np.float32)
        except ValueError:
            return np.zeros((len(texts), 1), dtype=np.float32)

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts using neural model (if enabled) or instant subword embeddings."""
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        if self.use_neural and self.model is not None:
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            return embeddings.astype(np.float32)

        return self._encode_fast_subword(texts)

    def build_index(self, documents: List[str]) -> Tuple[Any, Any]:
        """Build index for candidate documents."""
        if self.use_neural and self.model is not None and faiss is not None:
            index = faiss.IndexFlatIP(self.dimension)
            if not documents:
                return index, np.empty((0, self.dimension), dtype=np.float32)
            embeddings = self.encode(documents)
            index.add(embeddings)
            return index, embeddings

        return documents, documents

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        """Compute exact Cosine Similarity between two texts via FAISS IndexFlatIP."""
        if not text_a or not text_b or not text_a.strip() or not text_b.strip():
            return 0.0

        vecs = self.encode([text_a, text_b])
        if faiss is not None and vecs.shape[1] > 0:
            dim = vecs.shape[1]
            index = faiss.IndexFlatIP(dim)
            index.add(vecs[1:2])
            scores, _ = index.search(vecs[0:1], 1)
            return self.map_cosine_to_percentage(float(scores[0][0]))

        return self.compute_vector_cosine_similarity(vecs[0], vecs[1])

    def search_top_k(
        self,
        index: Any,
        query: str,
        top_k: int = 1,
    ) -> List[Tuple[int, float]]:
        """Query FAISS IndexFlatIP for the top-k most similar documents via Cosine Similarity."""
        if not query or not query.strip() or top_k <= 0:
            return []

        # Case 1: Neural FAISS IndexFlatIP
        if self.use_neural and self.model is not None and not isinstance(index, list):
            if index.ntotal == 0:
                return []
            query_vec = self.encode([query])
            k = min(top_k, index.ntotal)
            scores, indices = index.search(query_vec, k)
            return [
                (int(idx), self.map_cosine_to_percentage(float(score)))
                for idx, score in zip(indices[0], scores[0])
                if idx != -1
            ]

        # Case 2: Instant Offline FAISS IndexFlatIP
        documents: List[str] = index if isinstance(index, list) else []
        if not documents:
            return []

        corpus = [query] + list(documents)
        vecs = self._encode_fast_subword(corpus)
        query_vec = vecs[0:1]
        doc_vecs = vecs[1:]
        k = min(top_k, len(documents))

        if faiss is not None and vecs.shape[1] > 0:
            faiss_index = faiss.IndexFlatIP(vecs.shape[1])
            faiss_index.add(doc_vecs)
            scores, indices = faiss_index.search(query_vec, k)
            return [
                (int(idx), self.map_cosine_to_percentage(float(score)))
                for idx, score in zip(indices[0], scores[0])
                if idx != -1
            ]

        scores_list = [
            (i, self.compute_vector_cosine_similarity(query_vec[0], doc_vecs[i]))
            for i in range(len(documents))
        ]
        scores_list.sort(key=lambda x: x[1], reverse=True)
        return scores_list[:k]
