"""
NumPy Matrix Operations Snippets
Production-ready examples for matrix operations
"""

import numpy as np
from typing import Tuple


def create_matrix(rows: int, cols: int, fill_value: float = 0) -> np.ndarray:
    """Create matrix with specified dimensions"""
    return np.full((rows, cols), fill_value)


def create_random_matrix(rows: int, cols: int) -> np.ndarray:
    """Create random matrix"""
    return np.random.rand(rows, cols)


def create_identity_matrix(n: int) -> np.ndarray:
    """Create identity matrix"""
    return np.eye(n)


def create_diagonal_matrix(diagonal_values: np.ndarray) -> np.ndarray:
    """Create diagonal matrix from values"""
    return np.diag(diagonal_values)


def create_upper_triangular(arr: np.ndarray) -> np.ndarray:
    """Extract upper triangular part"""
    return np.triu(arr)


def create_lower_triangular(arr: np.ndarray) -> np.ndarray:
    """Extract lower triangular part"""
    return np.tril(arr)


def matrix_addition(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Add two matrices"""
    return A + B


def matrix_subtraction(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Subtract two matrices"""
    return A - B


def matrix_scalar_multiplication(A: np.ndarray, scalar: float) -> np.ndarray:
    """Multiply matrix by scalar"""
    return scalar * A


def matrix_element_wise_multiplication(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Element-wise multiplication (Hadamard product)"""
    return A * B


def matrix_element_wise_division(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Element-wise division"""
    return A / B


def matrix_power_element_wise(A: np.ndarray, power: float) -> np.ndarray:
    """Raise each element to power"""
    return A ** power


def block_matrix_create(A: np.ndarray, B: np.ndarray, C: np.ndarray, D: np.ndarray) -> np.ndarray:
    """Create block matrix from sub-matrices"""
    top = np.hstack([A, B])
    bottom = np.hstack([C, D])
    return np.vstack([top, bottom])


def get_matrix_diagonal(A: np.ndarray, offset: int = 0) -> np.ndarray:
    """Get diagonal elements (with offset)"""
    return np.diag(A, k=offset)


def set_matrix_diagonal(A: np.ndarray, values: np.ndarray) -> np.ndarray:
    """Set diagonal elements"""
    result = A.copy()
    np.fill_diagonal(result, values)
    return result


def matrix_sum_rows(A: np.ndarray) -> np.ndarray:
    """Sum matrix rows"""
    return A.sum(axis=1)


def matrix_sum_columns(A: np.ndarray) -> np.ndarray:
    """Sum matrix columns"""
    return A.sum(axis=0)


def matrix_mean_rows(A: np.ndarray) -> np.ndarray:
    """Calculate mean of each row"""
    return A.mean(axis=1)


def matrix_mean_columns(A: np.ndarray) -> np.ndarray:
    """Calculate mean of each column"""
    return A.mean(axis=0)


def matrix_max_rows(A: np.ndarray) -> np.ndarray:
    """Find maximum in each row"""
    return A.max(axis=1)


def matrix_min_columns(A: np.ndarray) -> np.ndarray:
    """Find minimum in each column"""
    return A.min(axis=0)


def matrix_argmax_rows(A: np.ndarray) -> np.ndarray:
    """Find index of maximum in each row"""
    return A.argmax(axis=1)


def matrix_argmin_columns(A: np.ndarray) -> np.ndarray:
    """Find index of minimum in each column"""
    return A.argmin(axis=0)


def matrix_flatten_row_major(A: np.ndarray) -> np.ndarray:
    """Flatten matrix in row-major order (C-style)"""
    return A.flatten('C')


def matrix_flatten_column_major(A: np.ndarray) -> np.ndarray:
    """Flatten matrix in column-major order (Fortran-style)"""
    return A.flatten('F')


def matrix_swap_rows(A: np.ndarray, row1: int, row2: int) -> np.ndarray:
    """Swap two rows"""
    result = A.copy()
    result[[row1, row2]] = result[[row2, row1]]
    return result


def matrix_swap_columns(A: np.ndarray, col1: int, col2: int) -> np.ndarray:
    """Swap two columns"""
    result = A.copy()
    result[:, [col1, col2]] = result[:, [col2, col1]]
    return result


def matrix_delete_row(A: np.ndarray, row_idx: int) -> np.ndarray:
    """Delete a row"""
    return np.delete(A, row_idx, axis=0)


def matrix_delete_column(A: np.ndarray, col_idx: int) -> np.ndarray:
    """Delete a column"""
    return np.delete(A, col_idx, axis=1)


def matrix_insert_row(A: np.ndarray, row_idx: int, values: np.ndarray) -> np.ndarray:
    """Insert a row"""
    return np.insert(A, row_idx, values, axis=0)


def matrix_insert_column(A: np.ndarray, col_idx: int, values: np.ndarray) -> np.ndarray:
    """Insert a column"""
    return np.insert(A, col_idx, values, axis=1)


def matrix_rotate_90(A: np.ndarray) -> np.ndarray:
    """Rotate matrix 90 degrees clockwise"""
    return np.rot90(A, k=-1)


def matrix_flip_horizontal(A: np.ndarray) -> np.ndarray:
    """Flip matrix horizontally"""
    return np.fliplr(A)


def matrix_flip_vertical(A: np.ndarray) -> np.ndarray:
    """Flip matrix vertically"""
    return np.flipud(A)


def matrix_to_symmetric(A: np.ndarray) -> np.ndarray:
    """Make matrix symmetric"""
    return (A + A.T) / 2


def is_matrix_symmetric(A: np.ndarray, tol: float = 1e-10) -> bool:
    """Check if matrix is symmetric"""
    return np.allclose(A, A.T, atol=tol)


def is_matrix_diagonal(A: np.ndarray, tol: float = 1e-10) -> bool:
    """Check if matrix is diagonal"""
    return np.allclose(A, np.diag(np.diag(A)), atol=tol)


def matrix_frobenius_norm(A: np.ndarray) -> float:
    """Calculate Frobenius norm"""
    return np.linalg.norm(A, 'fro')
