"""
Feature Engineering Snippets
Production-ready examples for creating and transforming features
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import (StandardScaler, MinMaxScaler, RobustScaler,
                                   PolynomialFeatures, PowerTransformer)
from sklearn.base import BaseEstimator, TransformerMixin


def create_polynomial_features(X: np.ndarray, degree: int = 2):
    """Create polynomial features"""
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    return poly.fit_transform(X)


def create_interaction_features(df: pd.DataFrame, col1: str, col2: str):
    """Create interaction features between columns"""
    df[f'{col1}_{col2}_interaction'] = df[col1] * df[col2]
    return df


def create_ratio_features(df: pd.DataFrame, numerator: str, denominator: str):
    """Create ratio features"""
    df[f'{numerator}_{denominator}_ratio'] = df[numerator] / (df[denominator] + 1e-10)
    return df


def create_binned_features(df: pd.DataFrame, column: str, bins: int = 5):
    """Create binned (discretized) features"""
    df[f'{column}_binned'] = pd.cut(df[column], bins=bins, labels=False)
    return df


def create_log_features(df: pd.DataFrame, columns: list):
    """Create log-transformed features"""
    for col in columns:
        df[f'{col}_log'] = np.log1p(df[col])
    return df


def create_sqrt_features(df: pd.DataFrame, columns: list):
    """Create square root features"""
    for col in columns:
        df[f'{col}_sqrt'] = np.sqrt(df[col])
    return df


def create_power_features(df: pd.DataFrame, column: str, powers: list = [2, 3]):
    """Create power features"""
    for power in powers:
        df[f'{column}_pow{power}'] = df[column] ** power
    return df


def create_aggregated_features(df: pd.DataFrame, group_col: str, agg_col: str):
    """Create aggregated features by group"""
    agg_features = df.groupby(group_col)[agg_col].agg(['mean', 'sum', 'std', 'min', 'max'])
    agg_features.columns = [f'{agg_col}_{stat}_by_{group_col}' for stat in agg_features.columns]
    df = df.join(agg_features, on=group_col)
    return df


def create_lag_features(df: pd.DataFrame, column: str, lags: list = [1, 7, 30]):
    """Create lag features for time series"""
    for lag in lags:
        df[f'{column}_lag{lag}'] = df[column].shift(lag)
    return df


def create_rolling_features(df: pd.DataFrame, column: str, windows: list = [3, 7, 30]):
    """Create rolling window features"""
    for window in windows:
        df[f'{column}_rolling_mean_{window}'] = df[column].rolling(window=window).mean()
        df[f'{column}_rolling_std_{window}'] = df[column].rolling(window=window).std()
    return df


def create_date_features(df: pd.DataFrame, date_col: str):
    """Extract date-based features"""
    df[date_col] = pd.to_datetime(df[date_col])
    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month
    df['day'] = df[date_col].dt.day
    df['dayofweek'] = df[date_col].dt.dayofweek
    df['quarter'] = df[date_col].dt.quarter
    df['is_weekend'] = (df[date_col].dt.dayofweek >= 5).astype(int)
    df['is_month_start'] = df[date_col].dt.is_month_start.astype(int)
    df['is_month_end'] = df[date_col].dt.is_month_end.astype(int)
    return df


def create_cyclic_features(df: pd.DataFrame, date_col: str):
    """Create cyclic encoding for date features"""
    df[date_col] = pd.to_datetime(df[date_col])
    df['month_sin'] = np.sin(2 * np.pi * df[date_col].dt.month / 12)
    df['month_cos'] = np.cos(2 * np.pi * df[date_col].dt.month / 12)
    df['day_sin'] = np.sin(2 * np.pi * df[date_col].dt.day / 31)
    df['day_cos'] = np.cos(2 * np.pi * df[date_col].dt.day / 31)
    return df


def create_text_features(df: pd.DataFrame, text_col: str):
    """Create text-based features"""
    df[f'{text_col}_length'] = df[text_col].str.len()
    df[f'{text_col}_word_count'] = df[text_col].str.split().str.len()
    df[f'{text_col}_unique_words'] = df[text_col].apply(lambda x: len(set(str(x).split())))
    return df


def create_frequency_encoding(df: pd.DataFrame, column: str):
    """Create frequency encoding for categorical variables"""
    freq_map = df[column].value_counts(normalize=True).to_dict()
    df[f'{column}_frequency'] = df[column].map(freq_map)
    return df


def create_target_encoding(df: pd.DataFrame, column: str, target: str):
    """Create target encoding (mean encoding)"""
    target_map = df.groupby(column)[target].mean().to_dict()
    df[f'{column}_target_encoded'] = df[column].map(target_map)
    return df


def create_difference_features(df: pd.DataFrame, col1: str, col2: str):
    """Create difference features"""
    df[f'{col1}_{col2}_diff'] = df[col1] - df[col2]
    df[f'{col1}_{col2}_abs_diff'] = np.abs(df[col1] - df[col2])
    return df


def create_flag_features(df: pd.DataFrame, column: str, threshold: float):
    """Create binary flag features"""
    df[f'{column}_above_{threshold}'] = (df[column] > threshold).astype(int)
    df[f'{column}_below_{threshold}'] = (df[column] < threshold).astype(int)
    return df


def yeo_johnson_transform(X: np.ndarray):
    """Apply Yeo-Johnson transformation"""
    pt = PowerTransformer(method='yeo-johnson')
    return pt.fit_transform(X)


def box_cox_transform(X: np.ndarray):
    """Apply Box-Cox transformation (requires positive data)"""
    pt = PowerTransformer(method='box-cox')
    return pt.fit_transform(X)


class OutlierCapTransformer(BaseEstimator, TransformerMixin):
    """Custom transformer to cap outliers at percentiles"""

    def __init__(self, lower_percentile=0.01, upper_percentile=0.99):
        self.lower_percentile = lower_percentile
        self.upper_percentile = upper_percentile
        self.lower_bounds = None
        self.upper_bounds = None

    def fit(self, X, y=None):
        self.lower_bounds = np.percentile(X, self.lower_percentile * 100, axis=0)
        self.upper_bounds = np.percentile(X, self.upper_percentile * 100, axis=0)
        return self

    def transform(self, X):
        X_transformed = np.clip(X, self.lower_bounds, self.upper_bounds)
        return X_transformed
