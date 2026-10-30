"""Unit tests for Cosine Similarity and Jaccard Similarity engines."""

import numpy as np
import pytest
from src.similarity.lexical_engine import LexicalSimilarityEngine
from src.similarity.faiss_engine import FaissSimilarityEngine


class TestLexicalAndJaccardSimilarityEngine:
    @pytest.fixture
    def engine(self) -> LexicalSimilarityEngine:
        return LexicalSimilarityEngine()

    def test_identical_texts_cosine_one(self, engine: LexicalSimilarityEngine) -> None:
        text = "بانک مرکزی نرخ جدید سود سپرده بانکی را اعلام کرد"
        sim = engine.compute_similarity(text, text)
        assert pytest.approx(sim, 0.01) == 1.0

    def test_completely_disjoint_texts_cosine_zero(self, engine: LexicalSimilarityEngine) -> None:
        text_a = "سیب پرتقال گلابی هلو"
        text_b = "اتومبیل هواپیما قطار کشتی"
        sim = engine.compute_similarity(text_a, text_b)
        assert sim == 0.0

    def test_jaccard_similarity_calculation(self, engine: LexicalSimilarityEngine) -> None:
        text_a = "بانک مرکزی سود سپرده"
        text_b = "بانک مرکزی نرخ تورم"
        # Intersection: {"بانک", "مرکزی"} (2), Union: {"بانک", "مرکزی", "سود", "سپرده", "نرخ", "تورم"} (6) -> 2/6 = 0.3333
        jac = engine.compute_jaccard_similarity(text_a, text_b)
        assert pytest.approx(jac, 0.01) == (2.0 / 6.0)

    def test_empty_and_whitespace_edge_cases(self, engine: LexicalSimilarityEngine) -> None:
        assert engine.compute_similarity("", "متن نمونه") == 0.0
        assert engine.compute_jaccard_similarity("", "متن نمونه") == 0.0

    def test_search_top_k_ranking(self, engine: LexicalSimilarityEngine) -> None:
        query = "بارش باران و برف در جاده‌های کوهستانی"
        docs = [
            "نرخ جدید سود بانکی اعلام شد",
            "پیش‌بینی هواشناسی از بارش شدید برف و باران در مناطق کوهستانی",
            "صادرات نفت ایران افزایش یافت",
        ]
        results = engine.search_top_k(query, docs, top_k=2)
        assert len(results) == 2
        assert results[0][0] == 1
        assert results[0][1] > 0.3


class TestFaissFastAndCosineMath:
    def test_exact_cosine_similarity_formula(self) -> None:
        vec_a = np.array([3.0, 4.0], dtype=np.float32)
        vec_b = np.array([6.0, 8.0], dtype=np.float32)
        vec_orthogonal = np.array([-4.0, 3.0], dtype=np.float32)

        assert pytest.approx(
            FaissSimilarityEngine.compute_vector_cosine_similarity(vec_a, vec_b), 0.001
        ) == 1.0
        assert pytest.approx(
            FaissSimilarityEngine.compute_vector_cosine_similarity(vec_a, vec_orthogonal), 0.001
        ) == 0.0

    def test_fast_faiss_engine_similarity_and_search(self) -> None:
        faiss_eng = FaissSimilarityEngine(use_neural=False)
        sim = faiss_eng.compute_similarity("سازمان هواشناسی بارش باران", "هشدار سازمان هواشناسی بارش شدید باران")
        assert sim > 0.5

        docs = ["افزایش شاخص بورس تهران", "هشدار سازمان هواشناسی درباره بارش باران"]
        index, _ = faiss_eng.build_index(docs)
        top_k = faiss_eng.search_top_k(index, "بارش باران هواشناسی", top_k=1)
        assert top_k[0][0] == 1
