"""
Pandas Window Functions Snippets
Production-ready examples for window operations
"""

import pandas as pd
import numpy as np
from typing import Optional


def rolling_mean(df: pd.DataFrame, column: str, window: int = 3) -> pd.DataFrame:
    """Calculate rolling mean"""
    df = df.copy()
    df[f'{column}_rolling_mean'] = df[column].rolling(window=window).mean()
    return df


def rolling_sum(df: pd.DataFrame, column: str, window: int = 3) -> pd.DataFrame:
    """Calculate rolling sum"""
    df = df.copy()
    df[f'{column}_rolling_sum'] = df[column].rolling(window=window).sum()
    return df


def rolling_std(df: pd.DataFrame, column: str, window: int = 3) -> pd.DataFrame:
    """Calculate rolling standard deviation"""
    df = df.copy()
    df[f'{column}_rolling_std'] = df[column].rolling(window=window).std()
    return df


def rolling_min_max(df: pd.DataFrame, column: str, window: int = 3) -> pd.DataFrame:
    """Calculate rolling min and max"""
    df = df.copy()
    df[f'{column}_rolling_min'] = df[column].rolling(window=window).min()
    df[f'{column}_rolling_max'] = df[column].rolling(window=window).max()
    return df


def rolling_median(df: pd.DataFrame, column: str, window: int = 3) -> pd.DataFrame:
    """Calculate rolling median"""
    df = df.copy()
    df[f'{column}_rolling_median'] = df[column].rolling(window=window).median()
    return df


def rolling_quantile(df: pd.DataFrame, column: str, window: int = 3, quantile: float = 0.75) -> pd.DataFrame:
    """Calculate rolling quantile"""
    df = df.copy()
    df[f'{column}_rolling_q{int(quantile*100)}'] = df[column].rolling(window=window).quantile(quantile)
    return df


def rolling_variance(df: pd.DataFrame, column: str, window: int = 3) -> pd.DataFrame:
    """Calculate rolling variance"""
    df = df.copy()
    df[f'{column}_rolling_var'] = df[column].rolling(window=window).var()
    return df


def rolling_skew_kurt(df: pd.DataFrame, column: str, window: int = 3) -> pd.DataFrame:
    """Calculate rolling skewness and kurtosis"""
    df = df.copy()
    df[f'{column}_rolling_skew'] = df[column].rolling(window=window).skew()
    df[f'{column}_rolling_kurt'] = df[column].rolling(window=window).kurt()
    return df


def expanding_mean(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Calculate expanding mean (cumulative mean)"""
    df = df.copy()
    df[f'{column}_expanding_mean'] = df[column].expanding().mean()
    return df


def expanding_sum(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Calculate expanding sum (cumulative sum)"""
    df = df.copy()
    df[f'{column}_expanding_sum'] = df[column].expanding().sum()
    return df


def expanding_std(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Calculate expanding standard deviation"""
    df = df.copy()
    df[f'{column}_expanding_std'] = df[column].expanding().std()
    return df


def exponential_weighted_mean(df: pd.DataFrame, column: str, span: int = 3) -> pd.DataFrame:
    """Calculate exponential weighted moving average (EWMA)"""
    df = df.copy()
    df[f'{column}_ewm'] = df[column].ewm(span=span, adjust=False).mean()
    return df


def exponential_weighted_std(df: pd.DataFrame, column: str, span: int = 3) -> pd.DataFrame:
    """Calculate exponential weighted standard deviation"""
    df = df.copy()
    df[f'{column}_ewm_std'] = df[column].ewm(span=span, adjust=False).std()
    return df


def rolling_correlation(df: pd.DataFrame, col1: str, col2: str, window: int = 3) -> pd.DataFrame:
    """Calculate rolling correlation between two columns"""
    df = df.copy()
    df[f'{col1}_{col2}_rolling_corr'] = df[col1].rolling(window=window).corr(df[col2])
    return df


def rolling_covariance(df: pd.DataFrame, col1: str, col2: str, window: int = 3) -> pd.DataFrame:
    """Calculate rolling covariance between two columns"""
    df = df.copy()
    df[f'{col1}_{col2}_rolling_cov'] = df[col1].rolling(window=window).cov(df[col2])
    return df


def rolling_window_custom_function(df: pd.DataFrame, column: str, window: int, func) -> pd.DataFrame:
    """Apply custom function to rolling window"""
    df = df.copy()
    df[f'{column}_rolling_custom'] = df[column].rolling(window=window).apply(func, raw=True)
    return df


def rolling_window_with_min_periods(df: pd.DataFrame, column: str, window: int = 3, min_periods: int = 1) -> pd.DataFrame:
    """Rolling window with minimum periods requirement"""
    df = df.copy()
    df[f'{column}_rolling_mean'] = df[column].rolling(window=window, min_periods=min_periods).mean()
    return df


def rolling_center_window(df: pd.DataFrame, column: str, window: int = 3) -> pd.DataFrame:
    """Rolling window centered on current observation"""
    df = df.copy()
    df[f'{column}_rolling_center'] = df[column].rolling(window=window, center=True).mean()
    return df


def rolling_window_by_time(df: pd.DataFrame, date_col: str, value_col: str, window: str = '7D') -> pd.DataFrame:
    """Rolling window based on time period"""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    df[f'{value_col}_rolling_time'] = df[value_col].rolling(window=window).mean()
    return df.reset_index()


def shift_values(df: pd.DataFrame, column: str, periods: int = 1) -> pd.DataFrame:
    """Shift values by specified periods (lag/lead)"""
    df = df.copy()
    if periods > 0:
        df[f'{column}_lag{periods}'] = df[column].shift(periods)
    else:
        df[f'{column}_lead{abs(periods)}'] = df[column].shift(periods)
    return df
