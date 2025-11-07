"""
Altair Chart Snippets
Production-ready examples for declarative visualizations with Altair
"""

import altair as alt
import pandas as pd
import numpy as np


def line_chart_altair(df: pd.DataFrame, x: str, y: str):
    """Create line chart with Altair"""
    chart = alt.Chart(df).mark_line().encode(
        x=x,
        y=y
    ).properties(
        title='Line Chart',
        width=600,
        height=400
    )
    return chart


def scatter_chart_altair(df: pd.DataFrame, x: str, y: str, color: str = None):
    """Create scatter chart with Altair"""
    chart = alt.Chart(df).mark_circle(size=60).encode(
        x=x,
        y=y,
        color=color,
        tooltip=[x, y] if not color else [x, y, color]
    ).properties(
        title='Scatter Chart',
        width=600,
        height=400
    ).interactive()
    return chart


def bar_chart_altair(df: pd.DataFrame, x: str, y: str):
    """Create bar chart with Altair"""
    chart = alt.Chart(df).mark_bar().encode(
        x=x,
        y=y,
        color=alt.value('steelblue')
    ).properties(
        title='Bar Chart',
        width=600,
        height=400
    )
    return chart


def area_chart_altair(df: pd.DataFrame, x: str, y: str):
    """Create area chart with Altair"""
    chart = alt.Chart(df).mark_area(opacity=0.7).encode(
        x=x,
        y=y
    ).properties(
        title='Area Chart',
        width=600,
        height=400
    )
    return chart


def histogram_altair(df: pd.DataFrame, column: str, bins: int = 30):
    """Create histogram with Altair"""
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f'{column}:Q', bin=alt.Bin(maxbins=bins)),
        y='count()'
    ).properties(
        title='Histogram',
        width=600,
        height=400
    )
    return chart


def heatmap_altair(df: pd.DataFrame, x: str, y: str, color: str):
    """Create heatmap with Altair"""
    chart = alt.Chart(df).mark_rect().encode(
        x=x,
        y=y,
        color=alt.Color(color, scale=alt.Scale(scheme='viridis'))
    ).properties(
        title='Heatmap',
        width=600,
        height=400
    )
    return chart


def layered_chart(df: pd.DataFrame, x: str, y: str):
    """Create layered chart (line + points)"""
    base = alt.Chart(df).encode(x=x, y=y)
    line = base.mark_line()
    points = base.mark_circle(size=100, opacity=0.5)

    chart = (line + points).properties(
        title='Layered Chart',
        width=600,
        height=400
    )
    return chart


def faceted_chart(df: pd.DataFrame, x: str, y: str, facet: str):
    """Create faceted chart"""
    chart = alt.Chart(df).mark_point().encode(
        x=x,
        y=y,
        facet=alt.Facet(f'{facet}:N', columns=3)
    ).properties(
        width=200,
        height=200,
        title='Faceted Chart'
    )
    return chart


def multi_series_line(df: pd.DataFrame, x: str, y: str, color: str):
    """Create multi-series line chart"""
    chart = alt.Chart(df).mark_line().encode(
        x=x,
        y=y,
        color=color
    ).properties(
        title='Multi-series Line Chart',
        width=600,
        height=400
    )
    return chart


def box_plot_altair(df: pd.DataFrame, x: str, y: str):
    """Create box plot with Altair"""
    chart = alt.Chart(df).mark_boxplot().encode(
        x=x,
        y=y
    ).properties(
        title='Box Plot',
        width=600,
        height=400
    )
    return chart
