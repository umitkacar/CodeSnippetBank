"""
NumPy Array Operations Snippets
Production-ready examples for array operations
"""

import numpy as np
from typing import Tuple, List


def create_array_from_list(data: List) -> np.ndarray:
    """Create NumPy array from Python list"""
    return np.array(data)


def create_zeros_array(shape: Tuple) -> np.ndarray:
    """Create array filled with zeros"""
    return np.zeros(shape)


def create_ones_array(shape: Tuple) -> np.ndarray:
    """Create array filled with ones"""
    return np.ones(shape)


def create_empty_array(shape: Tuple) -> np.ndarray:
    """Create uninitialized array"""
    return np.empty(shape)


def create_full_array(shape: Tuple, fill_value: float) -> np.ndarray:
    """Create array filled with specific value"""
    return np.full(shape, fill_value)


def create_identity_matrix(n: int) -> np.ndarray:
    """Create identity matrix"""
    return np.eye(n)


def create_range_array(start: int, stop: int, step: int = 1) -> np.ndarray:
    """Create array with range of values"""
    return np.arange(start, stop, step)


def create_linspace_array(start: float, stop: float, num: int = 50) -> np.ndarray:
    """Create array with evenly spaced values"""
    return np.linspace(start, stop, num)


def create_logspace_array(start: float, stop: float, num: int = 50) -> np.ndarray:
    """Create array with logarithmically spaced values"""
    return np.logspace(start, stop, num)


def reshape_array(arr: np.ndarray, new_shape: Tuple) -> np.ndarray:
    """Reshape array to new dimensions"""
    return arr.reshape(new_shape)


def flatten_array(arr: np.ndarray) -> np.ndarray:
    """Flatten multi-dimensional array to 1D"""
    return arr.flatten()


def transpose_array(arr: np.ndarray) -> np.ndarray:
    """Transpose array (swap axes)"""
    return arr.T


def concatenate_arrays(arrays: List[np.ndarray], axis: int = 0) -> np.ndarray:
    """Concatenate multiple arrays"""
    return np.concatenate(arrays, axis=axis)


def stack_arrays_vertically(arrays: List[np.ndarray]) -> np.ndarray:
    """Stack arrays vertically (row-wise)"""
    return np.vstack(arrays)


def stack_arrays_horizontally(arrays: List[np.ndarray]) -> np.ndarray:
    """Stack arrays horizontally (column-wise)"""
    return np.hstack(arrays)


def split_array(arr: np.ndarray, n_sections: int) -> List[np.ndarray]:
    """Split array into multiple sub-arrays"""
    return np.array_split(arr, n_sections)


def repeat_array(arr: np.ndarray, repeats: int, axis: int = 0) -> np.ndarray:
    """Repeat array elements"""
    return np.repeat(arr, repeats, axis=axis)


def tile_array(arr: np.ndarray, reps: Tuple) -> np.ndarray:
    """Tile array by repeating it"""
    return np.tile(arr, reps)


def expand_dimensions(arr: np.ndarray, axis: int) -> np.ndarray:
    """Add new axis to array"""
    return np.expand_dims(arr, axis=axis)


def squeeze_array(arr: np.ndarray) -> np.ndarray:
    """Remove single-dimensional entries"""
    return np.squeeze(arr)


def reverse_array(arr: np.ndarray) -> np.ndarray:
    """Reverse array elements"""
    return arr[::-1]


def sort_array(arr: np.ndarray, axis: int = -1) -> np.ndarray:
    """Sort array elements"""
    return np.sort(arr, axis=axis)


def get_unique_values(arr: np.ndarray) -> np.ndarray:
    """Get unique values from array"""
    return np.unique(arr)


def clip_array_values(arr: np.ndarray, min_val: float, max_val: float) -> np.ndarray:
    """Clip array values to range"""
    return np.clip(arr, min_val, max_val)


def where_condition(condition: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Apply condition with where"""
    return np.where(condition, x, y)


def select_elements_by_condition(arr: np.ndarray, condition) -> np.ndarray:
    """Select elements that satisfy condition"""
    return arr[condition(arr)]


def meshgrid_2d(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Create 2D coordinate grids"""
    return np.meshgrid(x, y)


def pad_array(arr: np.ndarray, pad_width: int, mode: str = 'constant') -> np.ndarray:
    """Pad array with values"""
    return np.pad(arr, pad_width=pad_width, mode=mode)


def roll_array(arr: np.ndarray, shift: int, axis: int = 0) -> np.ndarray:
    """Roll array elements along axis"""
    return np.roll(arr, shift=shift, axis=axis)
