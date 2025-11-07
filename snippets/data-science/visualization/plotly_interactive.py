"""
Plotly Interactive Visualization Snippets
Production-ready examples for interactive plots with Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def interactive_line_plot(x: np.ndarray, y: np.ndarray, title: str = "Interactive Line Plot"):
    """Create interactive line plot"""
    fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines', name='Data'))
    fig.update_layout(
        title=title,
        xaxis_title='X-axis',
        yaxis_title='Y-axis',
        hovermode='x unified'
    )
    fig.show()


def interactive_scatter_plot(df: pd.DataFrame, x: str, y: str, color: str = None):
    """Create interactive scatter plot"""
    fig = px.scatter(df, x=x, y=y, color=color, hover_data=df.columns,
                     title='Interactive Scatter Plot')
    fig.update_traces(marker=dict(size=10, opacity=0.7))
    fig.show()


def interactive_bar_chart(categories: list, values: list):
    """Create interactive bar chart"""
    fig = go.Figure(data=[go.Bar(x=categories, y=values, marker_color='lightblue')])
    fig.update_layout(
        title='Interactive Bar Chart',
        xaxis_title='Categories',
        yaxis_title='Values'
    )
    fig.show()


def interactive_histogram(data: np.ndarray, bins: int = 30):
    """Create interactive histogram"""
    fig = go.Figure(data=[go.Histogram(x=data, nbinsx=bins, marker_color='purple')])
    fig.update_layout(
        title='Interactive Histogram',
        xaxis_title='Value',
        yaxis_title='Frequency'
    )
    fig.show()


def interactive_box_plot(df: pd.DataFrame, y: str, x: str = None):
    """Create interactive box plot"""
    fig = px.box(df, y=y, x=x, title='Interactive Box Plot')
    fig.show()


def interactive_violin_plot(df: pd.DataFrame, y: str, x: str = None):
    """Create interactive violin plot"""
    fig = px.violin(df, y=y, x=x, box=True, points='all',
                    title='Interactive Violin Plot')
    fig.show()


def interactive_heatmap(z: np.ndarray, x: list = None, y: list = None):
    """Create interactive heatmap"""
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x,
        y=y,
        colorscale='Viridis',
        hoverongaps=False
    ))
    fig.update_layout(title='Interactive Heatmap')
    fig.show()


def interactive_3d_scatter(df: pd.DataFrame, x: str, y: str, z: str, color: str = None):
    """Create interactive 3D scatter plot"""
    fig = px.scatter_3d(df, x=x, y=y, z=z, color=color,
                        title='Interactive 3D Scatter Plot')
    fig.show()


def interactive_3d_surface(z: np.ndarray):
    """Create interactive 3D surface plot"""
    fig = go.Figure(data=[go.Surface(z=z, colorscale='Viridis')])
    fig.update_layout(
        title='Interactive 3D Surface',
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z'
        )
    )
    fig.show()


def interactive_pie_chart(values: list, labels: list):
    """Create interactive pie chart"""
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
    fig.update_layout(title='Interactive Pie Chart')
    fig.show()


def interactive_sunburst(df: pd.DataFrame, path: list, values: str):
    """Create interactive sunburst chart"""
    fig = px.sunburst(df, path=path, values=values,
                      title='Interactive Sunburst Chart')
    fig.show()


def interactive_treemap(df: pd.DataFrame, path: list, values: str):
    """Create interactive treemap"""
    fig = px.treemap(df, path=path, values=values,
                     title='Interactive Treemap')
    fig.show()


def interactive_funnel_chart(df: pd.DataFrame, x: str, y: str):
    """Create interactive funnel chart"""
    fig = px.funnel(df, x=x, y=y, title='Interactive Funnel Chart')
    fig.show()


def interactive_area_plot(df: pd.DataFrame, x: str, y: str):
    """Create interactive area plot"""
    fig = px.area(df, x=x, y=y, title='Interactive Area Plot')
    fig.show()


def interactive_timeline(df: pd.DataFrame, x_start: str, x_end: str, y: str):
    """Create interactive timeline (Gantt chart)"""
    fig = px.timeline(df, x_start=x_start, x_end=x_end, y=y,
                      title='Interactive Timeline')
    fig.show()


def animated_scatter_plot(df: pd.DataFrame, x: str, y: str, animation_frame: str):
    """Create animated scatter plot"""
    fig = px.scatter(df, x=x, y=y, animation_frame=animation_frame,
                     title='Animated Scatter Plot')
    fig.show()


def animated_bar_chart(df: pd.DataFrame, x: str, y: str, animation_frame: str):
    """Create animated bar chart"""
    fig = px.bar(df, x=x, y=y, animation_frame=animation_frame,
                 title='Animated Bar Chart')
    fig.show()


def multiple_traces_plot(x: np.ndarray, y_list: list, names: list):
    """Create plot with multiple traces"""
    fig = go.Figure()
    for y, name in zip(y_list, names):
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=name))
    fig.update_layout(
        title='Multiple Traces',
        xaxis_title='X-axis',
        yaxis_title='Y-axis'
    )
    fig.show()


def subplots_plotly(x: np.ndarray, y: np.ndarray):
    """Create subplots with Plotly"""
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=('Line', 'Scatter', 'Bar', 'Histogram'))

    fig.add_trace(go.Scatter(x=x, y=y, mode='lines'), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers'), row=1, col=2)
    fig.add_trace(go.Bar(x=x, y=y), row=2, col=1)
    fig.add_trace(go.Histogram(x=y), row=2, col=2)

    fig.update_layout(height=600, showlegend=False, title_text='Subplots')
    fig.show()


def candlestick_chart(df: pd.DataFrame):
    """Create candlestick chart (for financial data)"""
    fig = go.Figure(data=[go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )])
    fig.update_layout(title='Candlestick Chart')
    fig.show()


def waterfall_chart(x: list, y: list):
    """Create waterfall chart"""
    fig = go.Figure(go.Waterfall(
        x=x,
        y=y,
        textposition="outside"
    ))
    fig.update_layout(title='Waterfall Chart')
    fig.show()


def sankey_diagram(labels: list, source: list, target: list, value: list):
    """Create Sankey diagram (flow diagram)"""
    fig = go.Figure(data=[go.Sankey(
        node=dict(label=labels),
        link=dict(source=source, target=target, value=value)
    )])
    fig.update_layout(title='Sankey Diagram')
    fig.show()


def parallel_coordinates(df: pd.DataFrame, color: str):
    """Create parallel coordinates plot"""
    fig = px.parallel_coordinates(df, color=color,
                                   title='Parallel Coordinates')
    fig.show()


def polar_plot(r: np.ndarray, theta: np.ndarray):
    """Create polar plot"""
    fig = go.Figure(data=go.Scatterpolar(r=r, theta=theta, mode='lines'))
    fig.update_layout(title='Polar Plot')
    fig.show()
