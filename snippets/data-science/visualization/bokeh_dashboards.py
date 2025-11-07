"""
Bokeh Dashboard Snippets
Production-ready examples for interactive dashboards with Bokeh
"""

from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.layouts import column, row, gridplot
from bokeh.io import curdoc
import numpy as np
import pandas as pd


def basic_line_plot_bokeh(x: np.ndarray, y: np.ndarray):
    """Create basic line plot with Bokeh"""
    p = figure(title="Line Plot", x_axis_label='X', y_axis_label='Y',
               width=800, height=400)
    p.line(x, y, line_width=2, color='navy', alpha=0.8)
    show(p)


def scatter_plot_bokeh(x: np.ndarray, y: np.ndarray, colors: list = None):
    """Create scatter plot with Bokeh"""
    p = figure(title="Scatter Plot", width=800, height=400)
    p.circle(x, y, size=10, color=colors or 'blue', alpha=0.5)
    show(p)


def bar_chart_bokeh(categories: list, values: list):
    """Create bar chart with Bokeh"""
    p = figure(x_range=categories, title="Bar Chart",
               width=800, height=400)
    p.vbar(x=categories, top=values, width=0.9, color='steelblue')
    p.xgrid.grid_line_color = None
    show(p)


def hover_tool_plot(df: pd.DataFrame, x: str, y: str):
    """Create plot with hover tool"""
    source = ColumnDataSource(df)

    hover = HoverTool(tooltips=[
        ("Index", "$index"),
        (x, f"@{x}"),
        (y, f"@{y}")
    ])

    p = figure(title="Hover Tool Plot", width=800, height=400,
               tools=[hover, 'pan', 'wheel_zoom', 'box_zoom', 'reset'])
    p.circle(x, y, size=10, source=source, color='green', alpha=0.6)
    show(p)


def multi_line_plot_bokeh(x: np.ndarray, y_list: list, labels: list):
    """Create multi-line plot"""
    p = figure(title="Multi-line Plot", width=800, height=400)

    colors = ['red', 'blue', 'green', 'orange', 'purple']
    for i, (y, label) in enumerate(zip(y_list, labels)):
        p.line(x, y, legend_label=label, line_width=2,
               color=colors[i % len(colors)])

    p.legend.location = "top_left"
    show(p)


def histogram_bokeh(data: np.ndarray, bins: int = 30):
    """Create histogram with Bokeh"""
    hist, edges = np.histogram(data, bins=bins)

    p = figure(title="Histogram", width=800, height=400)
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color="navy", line_color="white", alpha=0.7)
    show(p)


def heatmap_bokeh(data: np.ndarray, x_labels: list, y_labels: list):
    """Create heatmap with Bokeh"""
    from bokeh.models import LinearColorMapper
    from bokeh.palettes import Viridis256

    # Flatten data for ColumnDataSource
    x_coords, y_coords, values = [], [], []
    for i, y_label in enumerate(y_labels):
        for j, x_label in enumerate(x_labels):
            x_coords.append(x_label)
            y_coords.append(y_label)
            values.append(data[i, j])

    source = ColumnDataSource(data=dict(x=x_coords, y=y_coords, values=values))

    mapper = LinearColorMapper(palette=Viridis256,
                                low=min(values), high=max(values))

    p = figure(title="Heatmap", x_range=x_labels, y_range=y_labels,
               width=800, height=400)
    p.rect(x="x", y="y", width=1, height=1, source=source,
           fill_color={'field': 'values', 'transform': mapper})
    show(p)


def linked_plots(x: np.ndarray, y1: np.ndarray, y2: np.ndarray):
    """Create linked plots (shared tools)"""
    p1 = figure(title="Plot 1", width=400, height=400)
    p1.circle(x, y1, size=5, color='blue', alpha=0.5)

    p2 = figure(title="Plot 2", width=400, height=400,
                x_range=p1.x_range, y_range=p1.y_range)
    p2.circle(x, y2, size=5, color='red', alpha=0.5)

    show(row(p1, p2))


def grid_layout(x: np.ndarray, y: np.ndarray):
    """Create grid layout of plots"""
    p1 = figure(title="Line", width=350, height=250)
    p1.line(x, y, line_width=2)

    p2 = figure(title="Scatter", width=350, height=250)
    p2.circle(x, y, size=8, color='red')

    p3 = figure(title="Bar", width=350, height=250)
    p3.vbar(x=x, top=y, width=0.5, color='green')

    p4 = figure(title="Area", width=350, height=250)
    p4.varea(x=x, y1=0, y2=y, alpha=0.5, color='purple')

    grid = gridplot([[p1, p2], [p3, p4]])
    show(grid)


def area_plot_bokeh(x: np.ndarray, y: np.ndarray):
    """Create area plot with Bokeh"""
    p = figure(title="Area Plot", width=800, height=400)
    p.varea(x=x, y1=0, y2=y, alpha=0.5, color='coral')
    p.line(x, y, line_width=2, color='red')
    show(p)


def step_plot_bokeh(x: np.ndarray, y: np.ndarray):
    """Create step plot with Bokeh"""
    p = figure(title="Step Plot", width=800, height=400)
    p.step(x, y, line_width=2, mode="center", color='navy')
    show(p)


def patch_plot_bokeh(x: np.ndarray, y: np.ndarray):
    """Create patch (polygon) plot"""
    p = figure(title="Patch Plot", width=800, height=400)
    p.patch(x, y, alpha=0.5, line_width=2, color='lightblue')
    show(p)
