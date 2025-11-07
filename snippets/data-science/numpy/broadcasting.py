"""
NumPy Broadcasting Snippets
Production-ready examples for broadcasting operations
"""

import numpy as np


def add_scalar_to_array(arr: np.ndarray, scalar: float) -> np.ndarray:
    """Add scalar to all array elements (broadcasting)"""
    return arr + scalar


def multiply_array_by_scalar(arr: np.ndarray, scalar: float) -> np.ndarray:
    """Multiply array by scalar (broadcasting)"""
    return arr * scalar


def broadcast_1d_to_2d_row(arr_1d: np.ndarray, arr_2d: np.ndarray) -> np.ndarray:
    """Broadcast 1D array as row to 2D array"""
    return arr_2d + arr_1d


def broadcast_1d_to_2d_column(arr_1d: np.ndarray, arr_2d: np.ndarray) -> np.ndarray:
    """Broadcast 1D array as column to 2D array"""
    return arr_2d + arr_1d[:, np.newaxis]


def normalize_rows(arr: np.ndarray) -> np.ndarray:
    """Normalize each row to have mean 0 and std 1"""
    row_means = arr.mean(axis=1, keepdims=True)
    row_stds = arr.std(axis=1, keepdims=True)
    return (arr - row_means) / row_stds


def normalize_columns(arr: np.ndarray) -> np.ndarray:
    """Normalize each column to have mean 0 and std 1"""
    col_means = arr.mean(axis=0, keepdims=True)
    col_stds = arr.std(axis=0, keepdims=True)
    return (arr - col_means) / col_stds


def center_rows(arr: np.ndarray) -> np.ndarray:
    """Center each row (subtract row mean)"""
    row_means = arr.mean(axis=1, keepdims=True)
    return arr - row_means


def center_columns(arr: np.ndarray) -> np.ndarray:
    """Center each column (subtract column mean)"""
    col_means = arr.mean(axis=0, keepdims=True)
    return arr - col_means


def scale_rows_to_unit_norm(arr: np.ndarray) -> np.ndarray:
    """Scale each row to unit norm"""
    row_norms = np.linalg.norm(arr, axis=1, keepdims=True)
    return arr / row_norms


def scale_columns_to_unit_norm(arr: np.ndarray) -> np.ndarray:
    """Scale each column to unit norm"""
    col_norms = np.linalg.norm(arr, axis=0, keepdims=True)
    return arr / col_norms


def element_wise_with_different_shapes(arr_2d: np.ndarray, arr_1d: np.ndarray) -> np.ndarray:
    """Element-wise operations with broadcasting"""
    # arr_2d shape: (m, n), arr_1d shape: (n,)
    return arr_2d * arr_1d


def outer_operation(arr1: np.ndarray, arr2: np.ndarray) -> np.ndarray:
    """Perform outer operation using broadcasting"""
    return arr1[:, np.newaxis] * arr2[np.newaxis, :]


def distance_matrix(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Calculate pairwise distance matrix using broadcasting"""
    # X shape: (n, d), Y shape: (m, d)
    # Result shape: (n, m)
    return np.sqrt(((X[:, np.newaxis, :] - Y[np.newaxis, :, :]) ** 2).sum(axis=2))


def pairwise_squared_distances(X: np.ndarray) -> np.ndarray:
    """Calculate pairwise squared distances efficiently"""
    # X shape: (n, d)
    # Result shape: (n, n)
    sum_X = np.sum(X**2, axis=1)
    return sum_X[:, np.newaxis] + sum_X[np.newaxis, :] - 2 * np.dot(X, X.T)


def apply_function_to_each_row(arr: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Apply weighted sum to each row using broadcasting"""
    return (arr * weights).sum(axis=1)


def softmax_rows(arr: np.ndarray) -> np.ndarray:
    """Apply softmax to each row"""
    exp_arr = np.exp(arr - arr.max(axis=1, keepdims=True))
    return exp_arr / exp_arr.sum(axis=1, keepdims=True)


def softmax_columns(arr: np.ndarray) -> np.ndarray:
    """Apply softmax to each column"""
    exp_arr = np.exp(arr - arr.max(axis=0, keepdims=True))
    return exp_arr / exp_arr.sum(axis=0, keepdims=True)


def combine_arrays_with_broadcasting(arr1: np.ndarray, arr2: np.ndarray, arr3: np.ndarray) -> np.ndarray:
    """Combine multiple arrays with different shapes"""
    # arr1: (a, 1, c), arr2: (1, b, c), arr3: (a, b, 1)
    return arr1 + arr2 + arr3


def weighted_average_broadcasting(arr: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Calculate weighted average using broadcasting"""
    return (arr * weights).sum(axis=1) / weights.sum()


def mask_with_broadcasting(arr: np.ndarray, mask: np.ndarray, fill_value: float = 0) -> np.ndarray:
    """Apply mask using broadcasting"""
    return np.where(mask, arr, fill_value)
