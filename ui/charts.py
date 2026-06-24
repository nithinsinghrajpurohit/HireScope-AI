"""
Data visualization and charting helpers using Plotly.
"Minimal Luxe" edition — provides radar charts, horizontal bars, and gauge
charts styled with a refined gold/cream/sage palette for the HireScope AI dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ── LUXE PALETTE ────────────────────────────────────────────────────────────
GOLD = "#D4A574"
CREAM = "#F5E6D3"
SAGE = "#A8C3A0"
WARM_TAUPE = "#C9A88A"
MUTED_ROSE = "#D4756A"
LAVENDER = "#B4AAC8"
SOFT_GREY = "#A09890"
CHARCOAL_BG = "rgba(0,0,0,0)"

# Trace colors for multi-candidate overlays
TRACE_COLORS = [GOLD, SAGE, LAVENDER, WARM_TAUPE]
TRACE_FILLS = [
    "rgba(212, 165, 116, 0.08)",
    "rgba(168, 195, 160, 0.08)",
    "rgba(180, 170, 200, 0.08)",
    "rgba(201, 168, 138, 0.08)",
]


def radar_comparison_chart(candidates: list, max_candidates: int = 4) -> go.Figure:
    """
    Generate a Plotly radar chart comparing the scores of the top candidates.

    Args:
        candidates: List of CandidateScore objects.
        max_candidates: Maximum number of candidates to plot.

    Returns:
        plotly.graph_objects.Figure object.
    """
    fig = go.Figure()

    # Plot up to max_candidates
    candidates_to_plot = candidates[:max_candidates]
    categories = ["Skill Match", "Semantic Alignment", "Experience Match", "Education Match", "Bonus Skills"]

    for i, c in enumerate(candidates_to_plot):
        score_dict = c.explanation.score_breakdown
        r_values = [
            score_dict.get("skill_match", 0.0),
            score_dict.get("semantic", 0.0),
            score_dict.get("experience", 0.0),
            score_dict.get("education", 0.0),
            score_dict.get("bonus", 0.0)
        ]
        # Append the first value to close the radar shape
        r_values.append(r_values[0])
        categories_closed = categories + [categories[0]]

        trace_color = TRACE_COLORS[i % len(TRACE_COLORS)]
        fill_color = TRACE_FILLS[i % len(TRACE_FILLS)]

        fig.add_trace(
            go.Scatterpolar(
                r=r_values,
                theta=categories_closed,
                fill="toself",
                fillcolor=fill_color,
                name=c.candidate_name,
                line=dict(color=trace_color, width=2),
                marker=dict(size=5, color=trace_color)
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color=SOFT_GREY, size=10, family="Inter"),
                gridcolor="rgba(212, 165, 116, 0.06)",
                linecolor="rgba(212, 165, 116, 0.06)"
            ),
            angularaxis=dict(
                tickfont=dict(color=CREAM, size=11, family="Inter"),
                gridcolor="rgba(212, 165, 116, 0.06)"
            ),
            bgcolor=CHARCOAL_BG
        ),
        showlegend=True,
        legend=dict(
            font=dict(color=CREAM, family="Inter"),
            bgcolor=CHARCOAL_BG,
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=20, b=40),
        height=320,
        paper_bgcolor=CHARCOAL_BG,
        plot_bgcolor=CHARCOAL_BG
    )

    return fig


def breakdown_bar_chart(candidate) -> go.Figure:
    """
    Generate a Plotly horizontal bar chart for a single candidate's score breakdown.
    """
    score_dict = candidate.explanation.score_breakdown

    df = pd.DataFrame({
        "Dimension": [
            "Skill Match",
            "Semantic Similarity",
            "Experience Fit",
            "Education Alignment",
            "Bonus Skills"
        ],
        "Score": [
            score_dict.get("skill_match", 0.0),
            score_dict.get("semantic", 0.0),
            score_dict.get("experience", 0.0),
            score_dict.get("education", 0.0),
            score_dict.get("bonus", 0.0)
        ],
        "Weight": [40, 25, 20, 10, 5]
    })

    # Sort so highest weighting/bars are laid out nicely
    df = df.iloc[::-1]

    fig = px.bar(
        df,
        x="Score",
        y="Dimension",
        orientation="h",
        text="Score",
        color="Score",
        color_continuous_scale=[
            [0.0, MUTED_ROSE],
            [0.5, GOLD],
            [1.0, SAGE]
        ],
        range_x=[0, 100]
    )

    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='inside',
        insidetextanchor='end',
        marker_line_color='rgba(0,0,0,0)',
        width=0.5
    )

    fig.update_layout(
        xaxis=dict(
            title="Score (%)",
            tickfont=dict(color=SOFT_GREY, family="Inter"),
            titlefont=dict(color=SOFT_GREY, family="Inter"),
            gridcolor="rgba(212, 165, 116, 0.05)"
        ),
        yaxis=dict(
            title="",
            tickfont=dict(color=CREAM, size=11, family="Inter")
        ),
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=10, b=10),
        height=220,
        paper_bgcolor=CHARCOAL_BG,
        plot_bgcolor=CHARCOAL_BG
    )

    return fig


def gauge_chart(score: float, candidate_name: str) -> go.Figure:
    """
    Generate an elegant circular gauge/ring indicator for the overall score.
    Uses a refined gold/sage/rose color scheme.
    """
    # Color based on score range — luxury palette
    if score >= 75:
        ring_color = SAGE          # Sage green for strong
    elif score >= 50:
        ring_color = GOLD          # Gold for moderate
    else:
        ring_color = MUTED_ROSE    # Muted rose for weak

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "%", "font": {"color": CREAM, "size": 36, "family": "Playfair Display"}},
            title={"text": f"{candidate_name}", "font": {"color": SOFT_GREY, "size": 14, "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": SOFT_GREY, "visible": False},
                "bar": {"color": ring_color, "thickness": 0.22},
                "bgcolor": "rgba(212, 165, 116, 0.06)",
                "borderwidth": 0
            }
        )
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=140,
        paper_bgcolor=CHARCOAL_BG,
        plot_bgcolor=CHARCOAL_BG
    )

    return fig
