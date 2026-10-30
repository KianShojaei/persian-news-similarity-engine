"""Persian text normalization module."""

import re
import unicodedata
from typing import Dict


class PersianNormalizer:
    """Normalizes Persian and Arabic character discrepancies, diacritics, and whitespace."""

    CHAR_MAPPING: Dict[str, str] = {
        "\u064a": "\u06cc",  # ي -> ی
        "\u0649": "\u06cc",  # ى -> ی
        "\u06d2": "\u06cc",  # ے -> ی
        "\u0643": "\u06a9",  # ك -> ک
        "\u06aa": "\u06a9",  # ڪ -> ک
        "\u0629": "\u0647",  # ة -> ه
        "\u06c0": "\u0647",  # ۀ -> ه
        "\u0660": "\u06f0",
        "\u0661": "\u06f1",
        "\u0662": "\u06f2",
        "\u0663": "\u06f3",
        "\u0664": "\u06f4",
        "\u0665": "\u06f5",
        "\u0666": "\u06f6",
        "\u0667": "\u06f7",
        "\u0668": "\u06f8",
        "\u0669": "\u06f9",
    }

    MULTIPLE_ZWNJ_REGEX = re.compile(r"\u200c+")
    ZWNJ_WHITESPACE_REGEX = re.compile(r"(\s+\u200c|\u200c\s+)")
    MULTIPLE_SPACES_REGEX = re.compile(r"[\s\u00a0\u2000-\u200b\u202f]+")

    def __init__(self) -> None:
        self.trans_table = str.maketrans(self.CHAR_MAPPING)

    def strip_diacritics(self, text: str) -> str:
        """Strip Arabic/Persian diacritics."""
        return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")

    def normalize(self, text: str) -> str:
        """Normalize Persian/Arabic characters, strip diacritics, and standardize whitespace."""
        if not text:
            return ""

        normalized = text.translate(self.trans_table)
        normalized = self.strip_diacritics(normalized)
        normalized = self.MULTIPLE_ZWNJ_REGEX.sub("\u200c", normalized)
        normalized = self.ZWNJ_WHITESPACE_REGEX.sub(" ", normalized)
        normalized = normalized.strip("\u200c")
        normalized = self.MULTIPLE_SPACES_REGEX.sub(" ", normalized)

        return normalized.strip()
