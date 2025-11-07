"""
Matplotlib Plotting Snippets
Production-ready examples for creating plots with Matplotlib
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, List


def basic_line_plot(x: np.ndarray, y: np.ndarray, title: str = "Line Plot"):
    """Create basic line plot"""
    plt.figure(figsize=(10, 6))
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True)
    plt.show()


def multiple_lines_plot(x: np.ndarray, y_list: List[np.ndarray], labels: List[str]):
    """Plot multiple lines"""
    plt.figure(figsize=(10, 6))
    for y, label in zip(y_list, labels):
        plt.plot(x, y, label=label, linewidth=2)
    plt.legend()
    plt.title('Multiple Lines')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True)
    plt.show()


def scatter_plot(x: np.ndarray, y: np.ndarray, colors: Optional[np.ndarray] = None):
    """Create scatter plot"""
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, c=colors, alpha=0.6, s=50)
    plt.title('Scatter Plot')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.colorbar(label='Value')
    plt.grid(True)
    plt.show()


def bar_chart(categories: List[str], values: np.ndarray):
    """Create bar chart"""
    plt.figure(figsize=(10, 6))
    plt.bar(categories, values, color='skyblue', edgecolor='navy')
    plt.title('Bar Chart')
    plt.xlabel('Categories')
    plt.ylabel('Values')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def horizontal_bar_chart(categories: List[str], values: np.ndarray):
    """Create horizontal bar chart"""
    plt.figure(figsize=(10, 6))
    plt.barh(categories, values, color='lightgreen', edgecolor='darkgreen')
    plt.title('Horizontal Bar Chart')
    plt.xlabel('Values')
    plt.ylabel('Categories')
    plt.tight_layout()
    plt.show()


def histogram(data: np.ndarray, bins: int = 30):
    """Create histogram"""
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=bins, color='purple', alpha=0.7, edgecolor='black')
    plt.title('Histogram')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    plt.show()


def pie_chart(sizes: List[float], labels: List[str], explode: Optional[List[float]] = None):
    """Create pie chart"""
    plt.figure(figsize=(10, 8))
    plt.pie(sizes, labels=labels, explode=explode, autopct='%1.1f%%',
            startangle=90, shadow=True)
    plt.title('Pie Chart')
    plt.axis('equal')
    plt.show()


def box_plot(data: List[np.ndarray], labels: List[str]):
    """Create box plot"""
    plt.figure(figsize=(10, 6))
    plt.boxplot(data, labels=labels, patch_artist=True)
    plt.title('Box Plot')
    plt.ylabel('Values')
    plt.grid(True, alpha=0.3)
    plt.show()


def violin_plot(data: List[np.ndarray], positions: List[int]):
    """Create violin plot"""
    plt.figure(figsize=(10, 6))
    parts = plt.violinplot(data, positions=positions, showmeans=True, showmedians=True)
    plt.title('Violin Plot')
    plt.xlabel('Groups')
    plt.ylabel('Values')
    plt.grid(True, alpha=0.3)
    plt.show()


def area_plot(x: np.ndarray, y: np.ndarray):
    """Create area plot"""
    plt.figure(figsize=(10, 6))
    plt.fill_between(x, y, alpha=0.5, color='coral')
    plt.plot(x, y, color='red', linewidth=2)
    plt.title('Area Plot')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True)
    plt.show()


def stacked_area_plot(x: np.ndarray, y_arrays: List[np.ndarray], labels: List[str]):
    """Create stacked area plot"""
    plt.figure(figsize=(10, 6))
    plt.stackplot(x, *y_arrays, labels=labels, alpha=0.7)
    plt.legend(loc='upper left')
    plt.title('Stacked Area Plot')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.show()


def error_bar_plot(x: np.ndarray, y: np.ndarray, yerr: np.ndarray):
    """Create error bar plot"""
    plt.figure(figsize=(10, 6))
    plt.errorbar(x, y, yerr=yerr, fmt='o-', capsize=5, capthick=2)
    plt.title('Error Bar Plot')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True)
    plt.show()


def stem_plot(x: np.ndarray, y: np.ndarray):
    """Create stem plot"""
    plt.figure(figsize=(10, 6))
    plt.stem(x, y, basefmt=" ")
    plt.title('Stem Plot')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True)
    plt.show()


def step_plot(x: np.ndarray, y: np.ndarray):
    """Create step plot"""
    plt.figure(figsize=(10, 6))
    plt.step(x, y, where='mid', linewidth=2)
    plt.title('Step Plot')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True)
    plt.show()


def subplots_example(x: np.ndarray, y: np.ndarray):
    """Create multiple subplots"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    axes[0, 0].plot(x, y)
    axes[0, 0].set_title('Line Plot')

    axes[0, 1].scatter(x, y)
    axes[0, 1].set_title('Scatter Plot')

    axes[1, 0].bar(range(len(y)), y)
    axes[1, 0].set_title('Bar Chart')

    axes[1, 1].hist(y, bins=20)
    axes[1, 1].set_title('Histogram')

    plt.tight_layout()
    plt.show()


def customized_plot(x: np.ndarray, y: np.ndarray):
    """Create highly customized plot"""
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, color='#FF6B6B', linewidth=3, linestyle='--',
             marker='o', markersize=8, markerfacecolor='yellow',
             markeredgecolor='black', markeredgewidth=2, label='Data')

    plt.title('Customized Plot', fontsize=16, fontweight='bold')
    plt.xlabel('X-axis', fontsize=12)
    plt.ylabel('Y-axis', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.show()


def save_plot_to_file(x: np.ndarray, y: np.ndarray, filename: str = 'plot.png'):
    """Save plot to file"""
    plt.figure(figsize=(10, 6))
    plt.plot(x, y)
    plt.title('Saved Plot')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True)
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def log_scale_plot(x: np.ndarray, y: np.ndarray):
    """Create plot with logarithmic scale"""
    plt.figure(figsize=(10, 6))
    plt.semilogy(x, y)
    plt.title('Semi-log Plot')
    plt.xlabel('X-axis (linear)')
    plt.ylabel('Y-axis (log)')
    plt.grid(True)
    plt.show()


def polar_plot(theta: np.ndarray, r: np.ndarray):
    """Create polar plot"""
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, projection='polar')
    ax.plot(theta, r, linewidth=2)
    ax.set_title('Polar Plot')
    plt.show()
