"""
NumPy Linear Algebra Snippets
Production-ready examples for linear algebra operations
"""

import numpy as np
from typing import Tuple


def matrix_multiplication(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Matrix multiplication"""
    return np.dot(A, B)


def matrix_multiplication_operator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Matrix multiplication using @ operator"""
    return A @ B


def element_wise_multiplication(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Element-wise multiplication (Hadamard product)"""
    return A * B


def matrix_transpose(A: np.ndarray) -> np.ndarray:
    """Transpose matrix"""
    return A.T


def matrix_inverse(A: np.ndarray) -> np.ndarray:
    """Calculate matrix inverse"""
    return np.linalg.inv(A)


def matrix_determinant(A: np.ndarray) -> float:
    """Calculate matrix determinant"""
    return np.linalg.det(A)


def matrix_rank(A: np.ndarray) -> int:
    """Calculate matrix rank"""
    return np.linalg.matrix_rank(A)


def matrix_trace(A: np.ndarray) -> float:
    """Calculate matrix trace (sum of diagonal elements)"""
    return np.trace(A)


def eigenvalues_eigenvectors(A: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate eigenvalues and eigenvectors"""
    eigenvalues, eigenvectors = np.linalg.eig(A)
    return eigenvalues, eigenvectors


def singular_value_decomposition(A: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Perform Singular Value Decomposition (SVD)"""
    U, S, Vt = np.linalg.svd(A)
    return U, S, Vt


def qr_decomposition(A: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Perform QR decomposition"""
    Q, R = np.linalg.qr(A)
    return Q, R


def cholesky_decomposition(A: np.ndarray) -> np.ndarray:
    """Perform Cholesky decomposition (for positive definite matrices)"""
    return np.linalg.cholesky(A)


def solve_linear_system(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Solve linear system Ax = b"""
    return np.linalg.solve(A, b)


def least_squares_solution(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute least-squares solution"""
    x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
    return x


def matrix_norm(A: np.ndarray, ord: str = 'fro') -> float:
    """Calculate matrix norm"""
    return np.linalg.norm(A, ord=ord)


def vector_norm(v: np.ndarray, ord: int = 2) -> float:
    """Calculate vector norm (default: L2 norm)"""
    return np.linalg.norm(v, ord=ord)


def cross_product(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Calculate cross product of two vectors"""
    return np.cross(a, b)


def dot_product(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate dot product of two vectors"""
    return np.dot(a, b)


def outer_product(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Calculate outer product of two vectors"""
    return np.outer(a, b)


def matrix_power(A: np.ndarray, n: int) -> np.ndarray:
    """Raise matrix to power n"""
    return np.linalg.matrix_power(A, n)


def pseudo_inverse(A: np.ndarray) -> np.ndarray:
    """Calculate Moore-Penrose pseudo-inverse"""
    return np.linalg.pinv(A)


def condition_number(A: np.ndarray) -> float:
    """Calculate condition number of matrix"""
    return np.linalg.cond(A)


def diagonal_matrix(v: np.ndarray) -> np.ndarray:
    """Create diagonal matrix from vector"""
    return np.diag(v)


def extract_diagonal(A: np.ndarray) -> np.ndarray:
    """Extract diagonal from matrix"""
    return np.diag(A)


def kronecker_product(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Calculate Kronecker product"""
    return np.kron(A, B)


def matrix_exponential(A: np.ndarray) -> np.ndarray:
    """Calculate matrix exponential"""
    from scipy.linalg import expm
    return expm(A)


def vector_projection(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Project vector a onto vector b"""
    return (np.dot(a, b) / np.dot(b, b)) * b


def gram_schmidt(A: np.ndarray) -> np.ndarray:
    """Gram-Schmidt orthogonalization"""
    Q, R = np.linalg.qr(A)
    return Q


def angle_between_vectors(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate angle between two vectors (in radians)"""
    cos_angle = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return np.arccos(np.clip(cos_angle, -1.0, 1.0))


def is_positive_definite(A: np.ndarray) -> bool:
    """Check if matrix is positive definite"""
    try:
        np.linalg.cholesky(A)
        return True
    except np.linalg.LinAlgError:
        return False
