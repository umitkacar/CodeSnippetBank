"""
NumPy Vectorization Snippets
Production-ready examples for vectorized operations
"""

import numpy as np
from typing import Callable


def vectorize_function(func: Callable) -> np.ndarray:
    """Vectorize a scalar function"""
    vectorized_func = np.vectorize(func)
    return vectorized_func


def apply_vectorized_function(arr: np.ndarray, func: Callable) -> np.ndarray:
    """Apply function to array elements (vectorized)"""
    vfunc = np.vectorize(func)
    return vfunc(arr)


def element_wise_operations(arr1: np.ndarray, arr2: np.ndarray) -> dict:
    """Perform element-wise operations"""
    return {
        'add': arr1 + arr2,
        'subtract': arr1 - arr2,
        'multiply': arr1 * arr2,
        'divide': arr1 / arr2,
        'power': arr1 ** arr2
    }


def vectorized_conditional(arr: np.ndarray, threshold: float) -> np.ndarray:
    """Apply conditional logic (vectorized)"""
    return np.where(arr > threshold, arr * 2, arr / 2)


def vectorized_clip(arr: np.ndarray, min_val: float, max_val: float) -> np.ndarray:
    """Clip values (vectorized)"""
    return np.clip(arr, min_val, max_val)


def vectorized_absolute(arr: np.ndarray) -> np.ndarray:
    """Calculate absolute values (vectorized)"""
    return np.abs(arr)


def vectorized_square_root(arr: np.ndarray) -> np.ndarray:
    """Calculate square root (vectorized)"""
    return np.sqrt(arr)


def vectorized_exponential(arr: np.ndarray) -> np.ndarray:
    """Calculate exponential (vectorized)"""
    return np.exp(arr)


def vectorized_logarithm(arr: np.ndarray) -> np.ndarray:
    """Calculate natural logarithm (vectorized)"""
    return np.log(arr + 1e-10)  # Add small value to avoid log(0)


def vectorized_trigonometric(arr: np.ndarray) -> dict:
    """Calculate trigonometric functions (vectorized)"""
    return {
        'sin': np.sin(arr),
        'cos': np.cos(arr),
        'tan': np.tan(arr)
    }


def vectorized_rounding(arr: np.ndarray) -> dict:
    """Rounding operations (vectorized)"""
    return {
        'round': np.round(arr),
        'floor': np.floor(arr),
        'ceil': np.ceil(arr)
    }


def vectorized_sign(arr: np.ndarray) -> np.ndarray:
    """Get sign of elements (vectorized)"""
    return np.sign(arr)


def vectorized_maximum_minimum(arr1: np.ndarray, arr2: np.ndarray) -> dict:
    """Element-wise maximum and minimum"""
    return {
        'maximum': np.maximum(arr1, arr2),
        'minimum': np.minimum(arr1, arr2)
    }


def vectorized_boolean_operations(arr1: np.ndarray, arr2: np.ndarray) -> dict:
    """Boolean operations (vectorized)"""
    return {
        'and': np.logical_and(arr1, arr2),
        'or': np.logical_or(arr1, arr2),
        'not': np.logical_not(arr1),
        'xor': np.logical_xor(arr1, arr2)
    }


def vectorized_comparison(arr1: np.ndarray, arr2: np.ndarray) -> dict:
    """Comparison operations (vectorized)"""
    return {
        'equal': arr1 == arr2,
        'not_equal': arr1 != arr2,
        'greater': arr1 > arr2,
        'greater_equal': arr1 >= arr2,
        'less': arr1 < arr2,
        'less_equal': arr1 <= arr2
    }


def vectorized_string_operations(arr: np.ndarray) -> dict:
    """String operations (vectorized)"""
    return {
        'upper': np.char.upper(arr),
        'lower': np.char.lower(arr),
        'strip': np.char.strip(arr),
        'replace': np.char.replace(arr, 'old', 'new')
    }


def vectorized_polynomial(arr: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    """Evaluate polynomial (vectorized)"""
    return np.polyval(coefficients, arr)


def vectorized_cumulative_operations(arr: np.ndarray) -> dict:
    """Cumulative operations (vectorized)"""
    return {
        'cumsum': np.cumsum(arr),
        'cumprod': np.cumprod(arr)
    }


def vectorized_diff(arr: np.ndarray) -> np.ndarray:
    """Calculate differences between consecutive elements"""
    return np.diff(arr)


def vectorized_gradient(arr: np.ndarray) -> np.ndarray:
    """Calculate gradient (numerical derivative)"""
    return np.gradient(arr)


def vectorized_unique_with_counts(arr: np.ndarray) -> tuple:
    """Get unique values with counts (vectorized)"""
    unique_vals, counts = np.unique(arr, return_counts=True)
    return unique_vals, counts


def vectorized_searchsorted(arr: np.ndarray, values: np.ndarray) -> np.ndarray:
    """Find indices where values should be inserted"""
    return np.searchsorted(arr, values)


def vectorized_digitize(arr: np.ndarray, bins: np.ndarray) -> np.ndarray:
    """Digitize (bin) values"""
    return np.digitize(arr, bins)


def vectorized_interp(x: np.ndarray, xp: np.ndarray, fp: np.ndarray) -> np.ndarray:
    """Linear interpolation (vectorized)"""
    return np.interp(x, xp, fp)


def fast_euclidean_norm(arr: np.ndarray, axis: int = -1) -> np.ndarray:
    """Fast Euclidean norm calculation"""
    return np.sqrt(np.sum(arr**2, axis=axis))


def vectorized_replace_values(arr: np.ndarray, old_values: list, new_values: list) -> np.ndarray:
    """Replace multiple values efficiently"""
    result = arr.copy()
    for old, new in zip(old_values, new_values):
        result = np.where(result == old, new, result)
    return result


def vectorized_bincount(arr: np.ndarray, weights: np.ndarray = None) -> np.ndarray:
    """Count occurrences of each value"""
    return np.bincount(arr.astype(int), weights=weights)


def einsum_operations(arr1: np.ndarray, arr2: np.ndarray) -> dict:
    """Einstein summation examples (advanced vectorization)"""
    return {
        'dot_product': np.einsum('i,i->', arr1, arr2),
        'outer_product': np.einsum('i,j->ij', arr1, arr2),
        'matrix_multiply': np.einsum('ij,jk->ik', arr1, arr2),
        'trace': np.einsum('ii->', arr1)
    }
