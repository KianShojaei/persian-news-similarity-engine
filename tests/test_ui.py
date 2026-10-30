"""Unit tests for UI helper functions and similarity classification."""

from src.ui.components import get_similarity_classification
from src.ui.styles import get_custom_css


def test_similarity_classification_thresholds() -> None:
    label_high, badge_high = get_similarity_classification(0.85)
    assert badge_high == "score-badge-high"
    assert "بالا" in label_high

    label_mod, badge_mod = get_similarity_classification(0.55)
    assert badge_mod == "score-badge-moderate"
    assert "متوسط" in label_mod

    label_low, badge_low = get_similarity_classification(0.20)
    assert badge_low == "score-badge-low"
    assert "ضعیف" in label_low


def test_custom_css_loading() -> None:
    css = get_custom_css()
    assert "<style>" in css
    assert "Vazirmatn" in css
    assert "platform-soroush" in css
