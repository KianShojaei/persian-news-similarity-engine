"""User interface subpackage for Streamlit."""

from src.ui.styles import get_custom_css
from src.ui.components import (
    format_post_option_label,
    render_header,
    render_scraped_posts_columns,
    render_similarity_cards,
    render_side_by_side_comparison,
    render_shared_keywords,
    render_nlp_pipeline_stages,
    render_ranking_list,
    get_similarity_classification,
)

__all__ = [
    "get_custom_css",
    "format_post_option_label",
    "render_header",
    "render_scraped_posts_columns",
    "render_similarity_cards",
    "render_side_by_side_comparison",
    "render_shared_keywords",
    "render_nlp_pipeline_stages",
    "render_ranking_list",
    "get_similarity_classification",
]
