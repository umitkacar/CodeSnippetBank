"""
Heatmap Visualization Snippets
Production-ready examples for heatmap visualizations
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


def basic_heatmap(data: np.ndarray, cmap: str = 'viridis'):
    """Create basic heatmap"""
    plt.figure(figsize=(10, 8))
    plt.imshow(data, cmap=cmap, aspect='auto')
    plt.colorbar(label='Value')
    plt.title('Basic Heatmap')
    plt.tight_layout()
    plt.show()


def annotated_heatmap(data: np.ndarray, row_labels: list, col_labels: list):
    """Create annotated heatmap with Seaborn"""
    plt.figure(figsize=(12, 10))
    sns.heatmap(data, annot=True, fmt='.2f', cmap='coolwarm',
                xticklabels=col_labels, yticklabels=row_labels,
                linewidths=0.5, square=True)
    plt.title('Annotated Heatmap')
    plt.tight_layout()
    plt.show()


def correlation_heatmap(df: pd.DataFrame):
    """Create correlation heatmap"""
    plt.figure(figsize=(12, 10))
    corr = df.corr()
    sns.heatmap(corr, annot=True, cmap='RdBu_r', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.show()


def masked_heatmap(df: pd.DataFrame):
    """Create masked heatmap (show only lower triangle)"""
    plt.figure(figsize=(12, 10))
    corr = df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, cmap='coolwarm', center=0,
                square=True, linewidths=1)
    plt.title('Masked Correlation Heatmap')
    plt.tight_layout()
    plt.show()


def diverging_heatmap(data: np.ndarray):
    """Create diverging heatmap (centered at zero)"""
    plt.figure(figsize=(10, 8))
    sns.heatmap(data, cmap='RdBu_r', center=0, annot=True,
                fmt='.1f', linewidths=0.5)
    plt.title('Diverging Heatmap')
    plt.tight_layout()
    plt.show()


def clustered_heatmap(df: pd.DataFrame):
    """Create clustered heatmap with dendrograms"""
    sns.clustermap(df, cmap='viridis', standard_scale=1,
                   figsize=(12, 10), annot=True, fmt='.2f')
    plt.show()


def confusion_matrix_heatmap(cm: np.ndarray, labels: list):
    """Create confusion matrix heatmap"""
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels,
                square=True, cbar_kws={"shrink": 0.8})
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.show()


def time_series_heatmap(df: pd.DataFrame, time_col: str, category_col: str, value_col: str):
    """Create time series heatmap"""
    pivot = df.pivot(index=category_col, columns=time_col, values=value_col)

    plt.figure(figsize=(14, 8))
    sns.heatmap(pivot, cmap='YlOrRd', annot=False, cbar_kws={"shrink": 0.8})
    plt.title('Time Series Heatmap')
    plt.xlabel('Time')
    plt.ylabel('Category')
    plt.tight_layout()
    plt.show()


def custom_colormap_heatmap(data: np.ndarray):
    """Create heatmap with custom colormap"""
    from matplotlib.colors import LinearSegmentedColormap

    colors = ['blue', 'white', 'red']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)

    plt.figure(figsize=(10, 8))
    sns.heatmap(data, cmap=cmap, center=0, annot=True, fmt='.2f')
    plt.title('Custom Colormap Heatmap')
    plt.tight_layout()
    plt.show()


def percentage_heatmap(data: np.ndarray):
    """Create percentage heatmap"""
    plt.figure(figsize=(10, 8))
    percentage = (data / data.sum()) * 100
    sns.heatmap(percentage, annot=True, fmt='.1f', cmap='Greens',
                cbar_kws={"label": "Percentage (%)"})
    plt.title('Percentage Heatmap')
    plt.tight_layout()
    plt.show()
