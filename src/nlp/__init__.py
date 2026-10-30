"""Persian NLP preprocessing subpackage."""

from typing import List, Tuple
from src.nlp.normalizer import PersianNormalizer
from src.nlp.cleaner import TextCleaner
from src.nlp.stopwords import StopwordFilter


class PersianNLPPipeline:
    """Orchestrates the Persian NLP pipeline through all three transformation stages."""

    def __init__(self) -> None:
        self.normalizer = PersianNormalizer()
        self.cleaner = TextCleaner()
        self.stopword_filter = StopwordFilter()

    def transform(self, raw_text: str) -> str:
        """Run complete preprocessing: Normalize -> Clean -> Filter Stopwords."""
        step1 = self.normalizer.normalize(raw_text)
        step2 = self.cleaner.clean(step1)
        step3 = self.stopword_filter.filter_tokens(step2)
        return step3

    def transform_detailed(self, raw_text: str) -> Tuple[str, str, str, str]:
        """Return text at each intermediate stage: (raw, normalized, cleaned, filtered)."""
        normalized = self.normalizer.normalize(raw_text)
        cleaned = self.cleaner.clean(normalized)
        filtered = self.stopword_filter.filter_tokens(cleaned)
        return raw_text, normalized, cleaned, filtered

    @staticmethod
    def extract_shared_tokens(cleaned_a: str, cleaned_b: str) -> List[str]:
        """Extract shared informative keywords between two preprocessed Persian texts."""
        if not cleaned_a or not cleaned_b:
            return []
        set_a = set(cleaned_a.split())
        set_b = set(cleaned_b.split())
        return sorted(set_a.intersection(set_b), key=lambda w: len(w), reverse=True)


__all__ = [
    "PersianNormalizer",
    "TextCleaner",
    "StopwordFilter",
    "PersianNLPPipeline",
]
