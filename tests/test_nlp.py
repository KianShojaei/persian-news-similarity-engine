"""Unit tests for Persian NLP preprocessing modules."""

import pytest
from src.nlp.normalizer import PersianNormalizer
from src.nlp.cleaner import TextCleaner
from src.nlp.stopwords import StopwordFilter
from src.nlp import PersianNLPPipeline


class TestPersianNormalizer:
    @pytest.fixture
    def normalizer(self) -> PersianNormalizer:
        return PersianNormalizer()

    def test_arabic_yeh_and_kaf_normalization(self, normalizer: PersianNormalizer) -> None:
        arabic_text = "شركت‌هاي دولتي كشور"
        expected = "شرکت‌های دولتی کشور"
        assert normalizer.normalize(arabic_text) == expected

    def test_teh_marbuta_conversion(self, normalizer: PersianNormalizer) -> None:
        arabic_text = "جامعة المصطفی"
        assert "جامعه" in normalizer.normalize(arabic_text)

    def test_diacritics_and_erab_stripping(self, normalizer: PersianNormalizer) -> None:
        text_with_erab = "مُحَمَّدٌ رَسُولُ اللَّهِ"
        assert normalizer.normalize(text_with_erab) == "محمد رسول الله"

    def test_zwnj_standardization(self, normalizer: PersianNormalizer) -> None:
        text_with_multiple_zwnj = "می\u200c\u200c\u200cرود"
        assert normalizer.normalize(text_with_multiple_zwnj) == "می\u200cرود"


class TestTextCleaner:
    @pytest.fixture
    def cleaner(self) -> TextCleaner:
        return TextCleaner()

    def test_url_removal(self, cleaner: TextCleaner) -> None:
        text = "جزئیات خبر در https://eitaa.com/farsna/1234 و https://splus.ir/tasnimnews منتشر شد."
        cleaned = cleaner.clean(text)
        assert "https://" not in cleaned
        assert "eitaa.com" not in cleaned
        assert "splus.ir" not in cleaned
        assert "جزئیات خبر در" in cleaned

    def test_mentions_and_digits_removal(self, cleaner: TextCleaner) -> None:
        text = "رشد ۱۲ درصدی در کانال @tasnim_news در سال 1403"
        cleaned = cleaner.clean(text)
        assert "@tasnim_news" not in cleaned
        assert "۱۲" not in cleaned
        assert "1403" not in cleaned


class TestNLPPipeline:
    def test_end_to_end_and_shared_tokens(self) -> None:
        pipeline = PersianNLPPipeline()
        raw_a = "بانك مركزي در https://splus.ir/tasnimnews اعلام كرد: نرخ تورّم ۱۲٪ كاهش يافت! 🚀"
        raw_b = "طبق گزارش بانک مرکزی، نرخ تورم سالانه کاهش چشمگیری یافت."
        clean_a = pipeline.transform(raw_a)
        clean_b = pipeline.transform(raw_b)
        shared = pipeline.extract_shared_tokens(clean_a, clean_b)
        assert "بانک" in shared
        assert "مرکزی" in shared
        assert "تورم" in shared
