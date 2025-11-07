"""
Pandas Time Series Snippets
Production-ready examples for time series analysis
"""

import pandas as pd
import numpy as np
from typing import Optional


def create_date_range(start: str, end: str, freq: str = 'D') -> pd.DatetimeIndex:
    """Create date range with specified frequency"""
    return pd.date_range(start=start, end=end, freq=freq)


def resample_time_series(df: pd.DataFrame, date_col: str, value_col: str, freq: str = 'M') -> pd.DataFrame:
    """Resample time series to different frequency"""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    return df.set_index(date_col)[value_col].resample(freq).mean().reset_index()


def calculate_rolling_mean(df: pd.DataFrame, column: str, window: int = 7) -> pd.DataFrame:
    """Calculate rolling mean (moving average)"""
    df = df.copy()
    df[f'{column}_rolling_mean'] = df[column].rolling(window=window).mean()
    return df


def calculate_rolling_std(df: pd.DataFrame, column: str, window: int = 7) -> pd.DataFrame:
    """Calculate rolling standard deviation"""
    df = df.copy()
    df[f'{column}_rolling_std'] = df[column].rolling(window=window).std()
    return df


def calculate_exponential_moving_average(df: pd.DataFrame, column: str, span: int = 7) -> pd.DataFrame:
    """Calculate exponential moving average (EMA)"""
    df = df.copy()
    df[f'{column}_ema'] = df[column].ewm(span=span, adjust=False).mean()
    return df


def calculate_lag_features(df: pd.DataFrame, column: str, lags: list = [1, 7, 30]) -> pd.DataFrame:
    """Create lag features"""
    df = df.copy()
    for lag in lags:
        df[f'{column}_lag{lag}'] = df[column].shift(lag)
    return df


def calculate_lead_features(df: pd.DataFrame, column: str, leads: list = [1, 7, 30]) -> pd.DataFrame:
    """Create lead features"""
    df = df.copy()
    for lead in leads:
        df[f'{column}_lead{lead}'] = df[column].shift(-lead)
    return df


def calculate_difference(df: pd.DataFrame, column: str, periods: int = 1) -> pd.DataFrame:
    """Calculate difference between current and previous values"""
    df = df.copy()
    df[f'{column}_diff'] = df[column].diff(periods=periods)
    return df


def calculate_percentage_change(df: pd.DataFrame, column: str, periods: int = 1) -> pd.DataFrame:
    """Calculate percentage change"""
    df = df.copy()
    df[f'{column}_pct_change'] = df[column].pct_change(periods=periods) * 100
    return df


def calculate_cumulative_sum(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Calculate cumulative sum"""
    df = df.copy()
    df[f'{column}_cumsum'] = df[column].cumsum()
    return df


def extract_time_features(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Extract comprehensive time features"""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month
    df['day'] = df[date_col].dt.day
    df['dayofweek'] = df[date_col].dt.dayofweek
    df['dayofyear'] = df[date_col].dt.dayofyear
    df['quarter'] = df[date_col].dt.quarter
    df['week'] = df[date_col].dt.isocalendar().week
    df['is_weekend'] = df[date_col].dt.dayofweek.isin([5, 6]).astype(int)
    df['is_month_start'] = df[date_col].dt.is_month_start.astype(int)
    df['is_month_end'] = df[date_col].dt.is_month_end.astype(int)

    return df


def calculate_rolling_sum(df: pd.DataFrame, column: str, window: int = 7) -> pd.DataFrame:
    """Calculate rolling sum"""
    df = df.copy()
    df[f'{column}_rolling_sum'] = df[column].rolling(window=window).sum()
    return df


def calculate_rolling_min_max(df: pd.DataFrame, column: str, window: int = 7) -> pd.DataFrame:
    """Calculate rolling min and max"""
    df = df.copy()
    df[f'{column}_rolling_min'] = df[column].rolling(window=window).min()
    df[f'{column}_rolling_max'] = df[column].rolling(window=window).max()
    return df


def detect_missing_dates(df: pd.DataFrame, date_col: str, freq: str = 'D') -> pd.DatetimeIndex:
    """Detect missing dates in time series"""
    df[date_col] = pd.to_datetime(df[date_col])
    expected_dates = pd.date_range(start=df[date_col].min(), end=df[date_col].max(), freq=freq)
    missing_dates = expected_dates.difference(df[date_col])
    return missing_dates


def fill_missing_dates(df: pd.DataFrame, date_col: str, freq: str = 'D') -> pd.DataFrame:
    """Fill missing dates in time series"""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    df = df.asfreq(freq)
    return df.reset_index()


def calculate_year_over_year_growth(df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
    """Calculate year-over-year growth"""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    df[f'{value_col}_yoy'] = df[value_col].pct_change(periods=365) * 100
    return df.reset_index()


def calculate_month_over_month_growth(df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
    """Calculate month-over-month growth"""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    df[f'{value_col}_mom'] = df[value_col].pct_change(periods=30) * 100
    return df.reset_index()


def create_seasonal_features(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Create seasonal features (cyclical encoding)"""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    # Cyclical encoding for month
    df['month_sin'] = np.sin(2 * np.pi * df[date_col].dt.month / 12)
    df['month_cos'] = np.cos(2 * np.pi * df[date_col].dt.month / 12)

    # Cyclical encoding for day of week
    df['dayofweek_sin'] = np.sin(2 * np.pi * df[date_col].dt.dayofweek / 7)
    df['dayofweek_cos'] = np.cos(2 * np.pi * df[date_col].dt.dayofweek / 7)

    return df


def calculate_bollinger_bands(df: pd.DataFrame, column: str, window: int = 20, num_std: int = 2) -> pd.DataFrame:
    """Calculate Bollinger Bands"""
    df = df.copy()
    rolling_mean = df[column].rolling(window=window).mean()
    rolling_std = df[column].rolling(window=window).std()

    df[f'{column}_bb_upper'] = rolling_mean + (rolling_std * num_std)
    df[f'{column}_bb_lower'] = rolling_mean - (rolling_std * num_std)
    df[f'{column}_bb_middle'] = rolling_mean

    return df
