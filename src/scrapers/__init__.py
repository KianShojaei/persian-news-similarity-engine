"""Scrapers subpackage for Eitaa and Soroush Plus platforms."""

from src.scrapers.base import BaseScraper, ScraperError, ChannelNotFoundError, RateLimitError
from src.scrapers.eitaa import EitaaScraper
from src.scrapers.soroush import SoroushScraper

__all__ = [
    "BaseScraper",
    "ScraperError",
    "ChannelNotFoundError",
    "RateLimitError",
    "EitaaScraper",
    "SoroushScraper",
]
