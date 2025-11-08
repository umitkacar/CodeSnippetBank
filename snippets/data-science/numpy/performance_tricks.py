"""
NumPy Performance Tricks Snippets
Production-ready examples for optimizing NumPy code
"""

try:
    import numpy as np
    from typing import Callable
except ImportError as e:
    raise ImportError(f"Required package not installed: {e}. Install with: pip install numpy")


def use_inplace_operations(arr: np.ndarray) -> np.ndarray:
    """Use in-place operations to save memory"""
    arr += 10  # In-place addition
    arr *= 2   # In-place multiplication
    return arr


def preallocate_arrays(size: int) -> np.ndarray:
    """Preallocate arrays instead of growing them"""
    result = np.empty(size)
    for i in range(size):
        result[i] = i ** 2
    return result


def use_views_not_copies(arr: np.ndarray) -> np.ndarray:
    """Use views instead of copies when possible"""
    view = arr[::2]  # View, not copy
    return view


def vectorize_instead_of_loops(arr: np.ndarray) -> np.ndarray:
    """Use vectorization instead of Python loops"""
    # Fast: vectorized
    return arr ** 2 + 2 * arr + 1


def use_ufuncs(arr: np.ndarray) -> np.ndarray:
    """Use universal functions (ufuncs) for element-wise operations"""
    return np.sqrt(np.exp(arr))


def avoid_unnecessary_copies(arr: np.ndarray) -> float:
    """Avoid unnecessary array copies"""
    # Bad: result = arr.copy().sum()
    # Good:
    return arr.sum()


def use_contiguous_arrays(arr: np.ndarray) -> np.ndarray:
    """Ensure arrays are contiguous in memory"""
    if not arr.flags['C_CONTIGUOUS']:
        arr = np.ascontiguousarray(arr)
    return arr


def use_numexpr_for_complex_expressions():
    """Use numexpr for complex numerical expressions"""
    try:
        import numexpr as ne
        a = np.random.rand(10000)
        b = np.random.rand(10000)
        c = np.random.rand(10000)
        # Fast evaluation
        result = ne.evaluate('a * b + c * a - b / c')
        return result
    except ImportError:
        print("Install numexpr: pip install numexpr")
        return None


def use_einsum_for_operations(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Use einsum for efficient multi-dimensional operations"""
    # Matrix multiplication using einsum
    return np.einsum('ij,jk->ik', A, B)


def use_out_parameter(a: np.ndarray, b: np.ndarray, out: np.ndarray = None) -> np.ndarray:
    """Use out parameter to avoid creating new arrays"""
    if out is None:
        out = np.empty_like(a)
    np.add(a, b, out=out)
    return out


def batch_processing(arr: np.ndarray, batch_size: int = 1000) -> list:
    """Process large arrays in batches"""
    n = len(arr)
    results = []
    for i in range(0, n, batch_size):
        batch = arr[i:i+batch_size]
        results.append(batch.mean())
    return results


def use_boolean_indexing(arr: np.ndarray, threshold: float) -> np.ndarray:
    """Use boolean indexing for filtering"""
    # Fast vectorized filtering
    return arr[arr > threshold]


def cache_frequently_used_values(arr: np.ndarray):
    """Cache frequently computed values"""
    # Cache mean and std for reuse
    mean = arr.mean()
    std = arr.std()
    normalized = (arr - mean) / std
    return normalized, mean, std


def use_fancy_indexing_carefully(arr: np.ndarray, indices: np.ndarray) -> np.ndarray:
    """Fancy indexing creates copies, use carefully"""
    # Returns a copy
    return arr[indices]


def memory_efficient_operations(arr: np.ndarray) -> np.ndarray:
    """Use memory-efficient operations"""
    # Use dtype that fits your needs
    if arr.max() < 256:
        arr = arr.astype(np.uint8)
    return arr


def parallel_computation_with_numba():
    """Use Numba for parallel computation"""
    try:
        from numba import jit, prange
    except ImportError:
        raise ImportError("numba not installed. Install with: pip install numba")

    @jit(nopython=True, parallel=True)
    def parallel_sum(arr):
        total = 0.0
        for i in prange(len(arr)):
            total += arr[i] ** 2
        return total

    arr = np.random.rand(1000000)
    return parallel_sum(arr)


def use_stride_tricks_for_windows(arr: np.ndarray, window_size: int) -> np.ndarray:
    """Use stride tricks for efficient window operations"""
    from numpy.lib.stride_tricks import as_strided
    shape = (len(arr) - window_size + 1, window_size)
    strides = (arr.strides[0], arr.strides[0])
    return as_strided(arr, shape=shape, strides=strides)


def reduce_memory_with_dtype(arr: np.ndarray) -> np.ndarray:
    """Reduce memory by using appropriate dtype"""
    # Example: Use float32 instead of float64 if precision allows
    return arr.astype(np.float32)


def use_memmap_for_large_arrays(filename: str, shape: tuple, dtype=np.float32):
    """Use memory-mapped arrays for very large datasets"""
    return np.memmap(filename, dtype=dtype, mode='w+', shape=shape)


def optimize_dot_products(a: np.ndarray, b: np.ndarray) -> float:
    """Optimize dot product computation"""
    # Use np.dot or @ operator (both call optimized BLAS)
    return np.dot(a, b)


def avoid_python_loops():
    """Demonstrate avoiding Python loops"""
    # Bad: Using Python loop
    def slow_sum(arr):
        total = 0
        for x in arr:
            total += x ** 2
        return total

    # Good: Using NumPy
    def fast_sum(arr):
        return np.sum(arr ** 2)

    return fast_sum


def use_appropriate_dtypes(n: int):
    """Choose appropriate dtypes for your data"""
    # For integers 0-255
    small_ints = np.arange(n, dtype=np.uint8)
    # For small floats
    small_floats = np.random.rand(n).astype(np.float16)
    return small_ints, small_floats


def leverage_blas_operations(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Leverage BLAS for optimized linear algebra"""
    # These operations use optimized BLAS routines
    return np.dot(A, B.T)


def chunk_large_arrays(arr: np.ndarray, chunk_size: int = 10000):
    """Process large arrays in chunks"""
    for i in range(0, len(arr), chunk_size):
        chunk = arr[i:i+chunk_size]
        # Process chunk
        yield chunk.mean()


def use_reduceat_for_grouped_operations(arr: np.ndarray, indices: np.ndarray) -> np.ndarray:
    """Use reduceat for efficient grouped operations"""
    return np.add.reduceat(arr, indices)


def optimize_memory_layout(arr: np.ndarray) -> np.ndarray:
    """Optimize memory layout for access patterns"""
    # For row-major access
    if not arr.flags['C_CONTIGUOUS']:
        arr = np.ascontiguousarray(arr)
    # For column-major access
    # arr = np.asfortranarray(arr)
    return arr


def profile_numpy_code():
    """Example of profiling NumPy code"""
    import time

    arr = np.random.rand(1000000)

    # Profile operation
    start = time.time()
    result = np.sqrt(arr ** 2 + 1)
    end = time.time()

    print(f"Operation took {end - start:.4f} seconds")
    return result
