"""
Seaborn Visualization Snippets
Production-ready examples for statistical visualizations with Seaborn
"""

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def set_style(style: str = 'whitegrid'):
    """Set Seaborn style"""
    sns.set_style(style)


def distribution_plot(data: np.ndarray):
    """Create distribution plot (histogram + KDE)"""
    plt.figure(figsize=(10, 6))
    sns.histplot(data, kde=True, color='skyblue')
    plt.title('Distribution Plot')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.show()


def kde_plot(data: np.ndarray):
    """Create KDE (Kernel Density Estimation) plot"""
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data, fill=True, color='purple')
    plt.title('KDE Plot')
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.show()


def box_plot_seaborn(df: pd.DataFrame, x: str, y: str):
    """Create box plot with Seaborn"""
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x=x, y=y, palette='Set2')
    plt.title('Box Plot')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def violin_plot_seaborn(df: pd.DataFrame, x: str, y: str):
    """Create violin plot with Seaborn"""
    plt.figure(figsize=(10, 6))
    sns.violinplot(data=df, x=x, y=y, palette='muted')
    plt.title('Violin Plot')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def swarm_plot(df: pd.DataFrame, x: str, y: str):
    """Create swarm plot (categorical scatter)"""
    plt.figure(figsize=(10, 6))
    sns.swarmplot(data=df, x=x, y=y, palette='husl')
    plt.title('Swarm Plot')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def strip_plot(df: pd.DataFrame, x: str, y: str):
    """Create strip plot"""
    plt.figure(figsize=(10, 6))
    sns.stripplot(data=df, x=x, y=y, palette='Set1', jitter=True)
    plt.title('Strip Plot')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def scatter_plot_seaborn(df: pd.DataFrame, x: str, y: str, hue: str = None):
    """Create scatter plot with Seaborn"""
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x=x, y=y, hue=hue, s=100, alpha=0.6)
    plt.title('Scatter Plot')
    plt.show()


def line_plot_seaborn(df: pd.DataFrame, x: str, y: str, hue: str = None):
    """Create line plot with Seaborn"""
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x=x, y=y, hue=hue, linewidth=2.5)
    plt.title('Line Plot')
    plt.show()


def bar_plot_seaborn(df: pd.DataFrame, x: str, y: str):
    """Create bar plot with Seaborn"""
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x=x, y=y, palette='coolwarm')
    plt.title('Bar Plot')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def count_plot(df: pd.DataFrame, x: str):
    """Create count plot (bar chart for counts)"""
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x=x, palette='pastel')
    plt.title('Count Plot')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def heatmap_correlation(df: pd.DataFrame):
    """Create correlation heatmap"""
    plt.figure(figsize=(12, 10))
    correlation = df.corr()
    sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.show()


def heatmap_custom(data: np.ndarray, xticklabels: list, yticklabels: list):
    """Create custom heatmap"""
    plt.figure(figsize=(10, 8))
    sns.heatmap(data, annot=True, fmt='.2f', cmap='YlOrRd',
                xticklabels=xticklabels, yticklabels=yticklabels)
    plt.title('Custom Heatmap')
    plt.tight_layout()
    plt.show()


def pair_plot(df: pd.DataFrame, hue: str = None):
    """Create pair plot (scatter plot matrix)"""
    sns.pairplot(df, hue=hue, diag_kind='kde', palette='husl')
    plt.suptitle('Pair Plot', y=1.02)
    plt.show()


def joint_plot(df: pd.DataFrame, x: str, y: str, kind: str = 'scatter'):
    """Create joint plot (scatter with marginal distributions)"""
    sns.jointplot(data=df, x=x, y=y, kind=kind, height=8)
    plt.show()


def regression_plot(df: pd.DataFrame, x: str, y: str):
    """Create regression plot with confidence interval"""
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df, x=x, y=y, scatter_kws={'alpha': 0.5})
    plt.title('Regression Plot')
    plt.show()


def residual_plot(df: pd.DataFrame, x: str, y: str):
    """Create residual plot for regression diagnostics"""
    plt.figure(figsize=(10, 6))
    sns.residplot(data=df, x=x, y=y, lowess=True, color='coral')
    plt.title('Residual Plot')
    plt.show()


def facet_grid_plot(df: pd.DataFrame, row: str, col: str, x: str, y: str):
    """Create facet grid (multiple subplots)"""
    g = sns.FacetGrid(df, row=row, col=col, height=4, aspect=1.5)
    g.map(sns.scatterplot, x, y, alpha=0.6)
    g.add_legend()
    plt.show()


def categorical_plot(df: pd.DataFrame, x: str, y: str, kind: str = 'box'):
    """Create categorical plot (flexible categorical visualization)"""
    plt.figure(figsize=(10, 6))
    sns.catplot(data=df, x=x, y=y, kind=kind, height=6, aspect=1.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def clustermap(df: pd.DataFrame):
    """Create clustered heatmap with dendrograms"""
    sns.clustermap(df, cmap='viridis', standard_scale=1,
                   figsize=(12, 10), annot=True, fmt='.2f')
    plt.show()


def point_plot(df: pd.DataFrame, x: str, y: str, hue: str = None):
    """Create point plot (mean and confidence interval)"""
    plt.figure(figsize=(10, 6))
    sns.pointplot(data=df, x=x, y=y, hue=hue, markers='o', linestyles='-')
    plt.title('Point Plot')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def ecdf_plot(data: np.ndarray):
    """Create ECDF (Empirical Cumulative Distribution Function) plot"""
    plt.figure(figsize=(10, 6))
    sns.ecdfplot(data=data, color='teal')
    plt.title('ECDF Plot')
    plt.xlabel('Value')
    plt.ylabel('Proportion')
    plt.grid(True)
    plt.show()


def rug_plot(data: np.ndarray):
    """Create rug plot (1D scatter on axis)"""
    plt.figure(figsize=(10, 2))
    sns.rugplot(data=data, height=0.5, color='red')
    plt.title('Rug Plot')
    plt.show()


def multiple_distributions(df: pd.DataFrame, column: str, hue: str):
    """Plot multiple distributions"""
    plt.figure(figsize=(10, 6))
    for category in df[hue].unique():
        subset = df[df[hue] == category][column]
        sns.kdeplot(subset, label=category, fill=True, alpha=0.5)
    plt.title('Multiple Distributions')
    plt.xlabel(column)
    plt.ylabel('Density')
    plt.legend()
    plt.show()


def styled_plot(df: pd.DataFrame, x: str, y: str):
    """Create plot with custom style"""
    sns.set_context("talk")
    sns.set_palette("husl")

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x=x, y=y, s=100, alpha=0.7)
    plt.title('Styled Plot')
    plt.show()

    sns.reset_defaults()
