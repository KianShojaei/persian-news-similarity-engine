"""Global configuration for Eitaa & Soroush Plus Similarity Engine."""

from pathlib import Path
from typing import Dict, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Application settings schema validated with Pydantic."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Lightweight multilingual model (only loaded on-demand if user checks the box)
    EMBEDDING_MODEL_NAME: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    SIMILARITY_HIGH_THRESHOLD: float = Field(default=0.70, ge=0.0, le=1.0)
    SIMILARITY_MODERATE_THRESHOLD: float = Field(default=0.40, ge=0.0, le=1.0)

    USER_AGENT: str = Field(
        default=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    )
    REQUEST_TIMEOUT: float = Field(default=12.0, gt=0.0)
    MIN_POST_LENGTH: int = Field(default=35, ge=1)

    EITAA_BASE_URL: str = Field(default="https://eitaa.com")
    SOROUSH_BASE_URL: str = Field(default="https://splus.ir")

    DEFAULT_EITAA_CHANNEL: str = Field(default="farsna")
    DEFAULT_SOROUSH_CHANNEL: str = Field(default="tasnimnews")

    POPULAR_CHANNELS: Dict[str, List[str]] = Field(
        default={
            "Eitaa": ["farsna", "tasnimnews", "iribnews", "akharinkhabar", "mehrnews", "isna", "irnanews"],
            "Soroush": ["tasnimnews", "farsna", "iribnews", "akharinkhabar", "mehrnews", "isna", "irnanews"],
        }
    )


settings = Settings()

NEWS_AGENCIES: Dict[str, str] = {
    "farsna": "خبرگزاری فارس",
    "tasnimnews": "خبرگزاری تسنیم",
    "iribnews": "خبرگزاری صدا و سیما",
    "akharinkhabar": "آخرین خبر",
    "mehrnews": "خبرگزاری مهر",
    "isna": "خبرگزاری ایسنا",
    "irnanews": "خبرگزاری ایرنا",
}


def get_channel_display_name(channel_id: str) -> str:
    """Return friendly Persian news agency name or formatted handle."""
    clean = channel_id.strip().lstrip("@").lower()
    return NEWS_AGENCIES.get(clean, f"کانال @{clean}")


EMBEDDING_MODEL_NAME: str = settings.EMBEDDING_MODEL_NAME
SIMILARITY_HIGH_THRESHOLD: float = settings.SIMILARITY_HIGH_THRESHOLD
SIMILARITY_MODERATE_THRESHOLD: float = settings.SIMILARITY_MODERATE_THRESHOLD
USER_AGENT: str = settings.USER_AGENT
REQUEST_TIMEOUT: float = settings.REQUEST_TIMEOUT
MIN_POST_LENGTH: int = settings.MIN_POST_LENGTH
EITAA_BASE_URL: str = settings.EITAA_BASE_URL
SOROUSH_BASE_URL: str = settings.SOROUSH_BASE_URL
DEFAULT_EITAA_CHANNEL: str = settings.DEFAULT_EITAA_CHANNEL
DEFAULT_SOROUSH_CHANNEL: str = settings.DEFAULT_SOROUSH_CHANNEL
POPULAR_CHANNELS: Dict[str, List[str]] = settings.POPULAR_CHANNELS
