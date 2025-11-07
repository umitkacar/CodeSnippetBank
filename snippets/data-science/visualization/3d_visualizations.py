"""
3D Visualization Snippets
Production-ready examples for 3D visualizations
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


def scatter_3d(x: np.ndarray, y: np.ndarray, z: np.ndarray, colors: np.ndarray = None):
    """Create 3D scatter plot"""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(x, y, z, c=colors, cmap='viridis', s=50, alpha=0.6)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Scatter Plot')
    if colors is not None:
        plt.colorbar(scatter)
    plt.show()


def line_3d(x: np.ndarray, y: np.ndarray, z: np.ndarray):
    """Create 3D line plot"""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x, y, z, linewidth=2, color='blue')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Line Plot')
    plt.show()


def surface_3d(X: np.ndarray, Y: np.ndarray, Z: np.ndarray):
    """Create 3D surface plot"""
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8,
                           linewidth=0, antialiased=True)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Surface Plot')
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()


def wireframe_3d(X: np.ndarray, Y: np.ndarray, Z: np.ndarray):
    """Create 3D wireframe plot"""
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_wireframe(X, Y, Z, color='cyan', linewidth=0.5)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Wireframe Plot')
    plt.show()


def contour_3d(X: np.ndarray, Y: np.ndarray, Z: np.ndarray):
    """Create 3D contour plot"""
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    ax.contour(X, Y, Z, levels=20, cmap='viridis')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Contour Plot')
    plt.show()


def bar_3d(x: np.ndarray, y: np.ndarray, z: np.ndarray):
    """Create 3D bar plot"""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    dx = dy = 0.8
    dz = z

    ax.bar3d(x, y, np.zeros_like(z), dx, dy, dz, shade=True, color='steelblue')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Bar Plot')
    plt.show()


def quiver_3d(x: np.ndarray, y: np.ndarray, z: np.ndarray,
              u: np.ndarray, v: np.ndarray, w: np.ndarray):
    """Create 3D quiver plot (vector field)"""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.quiver(x, y, z, u, v, w, length=0.1, normalize=True, color='red')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Quiver Plot')
    plt.show()


def parametric_curve_3d(t: np.ndarray):
    """Create parametric 3D curve"""
    x = np.sin(t)
    y = np.cos(t)
    z = t

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x, y, z, linewidth=2, color='purple')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Parametric Curve')
    plt.show()


def multiple_surfaces_3d(X: np.ndarray, Y: np.ndarray, Z1: np.ndarray, Z2: np.ndarray):
    """Plot multiple 3D surfaces"""
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')

    ax.plot_surface(X, Y, Z1, alpha=0.5, cmap='viridis')
    ax.plot_surface(X, Y, Z2, alpha=0.5, cmap='plasma')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Multiple 3D Surfaces')
    plt.show()


def trisurf_3d(x: np.ndarray, y: np.ndarray, z: np.ndarray):
    """Create triangulated 3D surface"""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(x, y, z, cmap='viridis', linewidth=0.2)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Triangulated 3D Surface')
    plt.show()
