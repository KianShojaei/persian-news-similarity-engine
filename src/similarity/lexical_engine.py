"""Lexical TF-IDF Cosine Similarity and Jaccard Similarity engine."""

from typing import List, Set, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class LexicalSimilarityEngine:
    """Computes lexical Cosine Similarity (TF-IDF) and Set-based Jaccard Similarity."""

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        """Compute lexical TF-IDF Cosine Similarity between two cleaned texts.

        Formula: cos(theta) = (A . B) / (||A|| * ||B||)
        """
        if not text_a or not text_b or not text_a.strip() or not text_b.strip():
            return 0.0

        try:
            vectorizer = TfidfVectorizer(
                token_pattern=r"(?u)\b\w[\w\u200c]+\b|\b\w+\b"
            )
            tfidf_matrix = vectorizer.fit_transform([text_a, text_b])

            if tfidf_matrix.shape[1] == 0:
                return 0.0

            sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            score = float(sim_matrix[0, 0])

            if np.isnan(score):
                return 0.0

            return float(np.clip(score, 0.0, 1.0))

        except (ValueError, ZeroDivisionError):
            return 0.0

    @staticmethod
    def compute_jaccard_similarity(text_a: str, text_b: str) -> float:
        """Compute Jaccard Similarity between two texts: |A intersect B| / |A union B|."""
        if not text_a or not text_b or not text_a.strip() or not text_b.strip():
            return 0.0

        set_a: Set[str] = set(text_a.split())
        set_b: Set[str] = set(text_b.split())

        if not set_a or not set_b:
            return 0.0

        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        if union == 0:
            return 0.0

        return float(np.clip(intersection / union, 0.0, 1.0))

    def search_top_k(
        self,
        query: str,
        documents: List[str],
        top_k: int = 1,
    ) -> List[Tuple[int, float]]:
        """Compute lexical Cosine Similarity between a query and a list of documents."""
        if not query or not query.strip() or not documents or top_k <= 0:
            return []

        corpus = [query] + list(documents)
        try:
            vectorizer = TfidfVectorizer(
                token_pattern=r"(?u)\b\w[\w\u200c]+\b|\b\w+\b"
            )
            tfidf_matrix = vectorizer.fit_transform(corpus)
            if tfidf_matrix.shape[1] == 0:
                return [(i, 0.0) for i in range(min(top_k, len(documents)))]

            query_vec = tfidf_matrix[0:1]
            doc_vecs = tfidf_matrix[1:]
            scores = cosine_similarity(query_vec, doc_vecs)[0]

            ranked_indices = np.argsort(scores)[::-1][:top_k]
            return [
                (int(idx), float(np.clip(scores[idx], 0.0, 1.0)))
                for idx in ranked_indices
            ]
        except (ValueError, ZeroDivisionError):
            return [(i, 0.0) for i in range(min(top_k, len(documents)))]
