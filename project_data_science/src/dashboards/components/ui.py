"""
Reusable UI components for Streamlit dashboards.
"""

import streamlit as st


def metric_card(label: str, value: str | int | float, help_text: str = None):
    """
    Display a metric card with consistent styling.

    Args:
        label: Metric label
        value: Metric value
        help_text: Optional help text
    """
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{value:,}</div>' if isinstance(value, (int, float)) else f'<div class="metric-value">{value}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-label">{label}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if help_text:
        st.caption(help_text)


def insight_box(title: str, content: str, box_type: str = "info"):
    """
    Display an insight box with formatted content.

    Args:
        title: Box title
        content: Box content (supports markdown)
        box_type: Type of box ('info', 'warning', 'success', 'error')
    """
    colors = {
        "info": "#EFF6FF",
        "warning": "#FEF3C7",
        "success": "#D1FAE5",
        "error": "#FEE2E2",
    }

    border_colors = {
        "info": "#3B82F6",
        "warning": "#F59E0B",
        "success": "#10B981",
        "error": "#EF4444",
    }

    bg_color = colors.get(box_type, colors["info"])
    border_color = border_colors.get(box_type, border_colors["info"])

    st.markdown(
        f"""
        <div style="
            background-color: {bg_color};
            border-left: 5px solid {border_color};
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 4px;
        ">
            <strong>{title}</strong><br>
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(text: str, level: int = 2):
    """
    Display a section header with consistent styling.

    Args:
        text: Header text
        level: Header level (1, 2, or 3)
    """
    class_map = {
        1: "main-header",
        2: "sub-header",
        3: "section-header",
    }

    class_name = class_map.get(level, "section-header")
    st.markdown(f'<div class="{class_name}">{text}</div>', unsafe_allow_html=True)


def apply_custom_css():
    """Apply custom CSS styling for the dashboard."""
    st.markdown(
        """
        <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: 700;
                color: #1E3A8A;
                margin-bottom: 1rem;
            }
            .sub-header {
                font-size: 1.8rem;
                font-weight: 600;
                color: #2563EB;
                margin-top: 2rem;
                margin-bottom: 1rem;
            }
            .section-header {
                font-size: 1.4rem;
                font-weight: 600;
                color: #3B82F6;
                margin-top: 1.5rem;
                margin-bottom: 0.8rem;
            }
            .metric-card {
                background-color: #F3F4F6;
                border-radius: 8px;
                padding: 1.5rem;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .metric-value {
                font-size: 2rem;
                font-weight: 700;
                color: #1E3A8A;
                margin-bottom: 0.5rem;
            }
            .metric-label {
                font-size: 0.9rem;
                color: #4B5563;
                font-weight: 500;
            }
            .stButton>button {
                border-radius: 4px;
                font-weight: 500;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_config(
    page_title: str,
    page_icon: str = "📊",
    layout: str = "wide",
):
    """
    Configure Streamlit page settings.

    Args:
        page_title: Page title
        page_icon: Page icon (emoji or path)
        layout: Page layout ('wide' or 'centered')
    """
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state="expanded",
    )
