"""
NumPy Statistical Functions Snippets
Production-ready examples for statistical operations
"""

import numpy as np
from typing import Optional, Tuple


def calculate_mean(arr: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
    """Calculate mean (average)"""
    return np.mean(arr, axis=axis)


def calculate_median(arr: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
    """Calculate median"""
    return np.median(arr, axis=axis)


def calculate_mode(arr: np.ndarray) -> float:
    """Calculate mode (most frequent value)"""
    from scipy import stats
    return stats.mode(arr, keepdims=False).mode


def calculate_std(arr: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
    """Calculate standard deviation"""
    return np.std(arr, axis=axis)


def calculate_variance(arr: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
    """Calculate variance"""
    return np.var(arr, axis=axis)


def calculate_min_max(arr: np.ndarray, axis: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate minimum and maximum"""
    return np.min(arr, axis=axis), np.max(arr, axis=axis)


def calculate_range(arr: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
    """Calculate range (max - min)"""
    return np.ptp(arr, axis=axis)


def calculate_percentile(arr: np.ndarray, percentile: float, axis: Optional[int] = None) -> np.ndarray:
    """Calculate percentile"""
    return np.percentile(arr, percentile, axis=axis)


def calculate_quantile(arr: np.ndarray, q: float, axis: Optional[int] = None) -> np.ndarray:
    """Calculate quantile"""
    return np.quantile(arr, q, axis=axis)


def calculate_quartiles(arr: np.ndarray) -> Tuple[float, float, float]:
    """Calculate Q1, Q2 (median), Q3"""
    q1 = np.percentile(arr, 25)
    q2 = np.percentile(arr, 50)
    q3 = np.percentile(arr, 75)
    return q1, q2, q3


def calculate_iqr(arr: np.ndarray) -> float:
    """Calculate Interquartile Range (IQR)"""
    q1 = np.percentile(arr, 25)
    q3 = np.percentile(arr, 75)
    return q3 - q1


def calculate_sum(arr: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
    """Calculate sum"""
    return np.sum(arr, axis=axis)


def calculate_cumsum(arr: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
    """Calculate cumulative sum"""
    return np.cumsum(arr, axis=axis)


def calculate_cumprod(arr: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
    """Calculate cumulative product"""
    return np.cumprod(arr, axis=axis)


def calculate_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """Calculate Pearson correlation coefficient"""
    return np.corrcoef(x, y)[0, 1]


def calculate_correlation_matrix(arr: np.ndarray) -> np.ndarray:
    """Calculate correlation matrix"""
    return np.corrcoef(arr.T)


def calculate_covariance(x: np.ndarray, y: np.ndarray) -> float:
    """Calculate covariance"""
    return np.cov(x, y)[0, 1]


def calculate_covariance_matrix(arr: np.ndarray) -> np.ndarray:
    """Calculate covariance matrix"""
    return np.cov(arr.T)


def calculate_skewness(arr: np.ndarray) -> float:
    """Calculate skewness"""
    from scipy import stats
    return stats.skew(arr)


def calculate_kurtosis(arr: np.ndarray) -> float:
    """Calculate kurtosis"""
    from scipy import stats
    return stats.kurtosis(arr)


def normalize_zscore(arr: np.ndarray) -> np.ndarray:
    """Z-score normalization (standardization)"""
    return (arr - np.mean(arr)) / np.std(arr)


def normalize_minmax(arr: np.ndarray) -> np.ndarray:
    """Min-max normalization (scale to 0-1)"""
    return (arr - np.min(arr)) / (np.max(arr) - np.min(arr))


def moving_average(arr: np.ndarray, window_size: int) -> np.ndarray:
    """Calculate moving average"""
    return np.convolve(arr, np.ones(window_size)/window_size, mode='valid')


def weighted_average(arr: np.ndarray, weights: np.ndarray) -> float:
    """Calculate weighted average"""
    return np.average(arr, weights=weights)


def count_nonzero(arr: np.ndarray, axis: Optional[int] = None) -> int:
    """Count non-zero elements"""
    return np.count_nonzero(arr, axis=axis)


def histogram(arr: np.ndarray, bins: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate histogram"""
    counts, bin_edges = np.histogram(arr, bins=bins)
    return counts, bin_edges


def binned_statistic(x: np.ndarray, values: np.ndarray, statistic: str = 'mean', bins: int = 10):
    """Calculate statistic for binned data"""
    from scipy import stats
    return stats.binned_statistic(x, values, statistic=statistic, bins=bins)


def standard_error(arr: np.ndarray) -> float:
    """Calculate standard error of the mean"""
    return np.std(arr, ddof=1) / np.sqrt(len(arr))


def coefficient_of_variation(arr: np.ndarray) -> float:
    """Calculate coefficient of variation"""
    return (np.std(arr) / np.mean(arr)) * 100


def mean_absolute_deviation(arr: np.ndarray) -> float:
    """Calculate mean absolute deviation"""
    return np.mean(np.abs(arr - np.mean(arr)))


def exponential_moving_average(arr: np.ndarray, alpha: float = 0.3) -> np.ndarray:
    """Calculate exponential moving average"""
    ema = np.zeros_like(arr)
    ema[0] = arr[0]
    for i in range(1, len(arr)):
        ema[i] = alpha * arr[i] + (1 - alpha) * ema[i-1]
    return ema
