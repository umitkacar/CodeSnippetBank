"""
Pandas Transformations Snippets
Production-ready examples for transforming data
"""

import pandas as pd
import numpy as np
from typing import List, Callable, Optional


def apply_custom_function(df: pd.DataFrame, column: str, func: Callable) -> pd.DataFrame:
    """Apply custom function to a column"""
    df = df.copy()
    df[column] = df[column].apply(func)
    return df


def create_categorical_column(df: pd.DataFrame, column: str, bins: List[float], labels: List[str]) -> pd.DataFrame:
    """Create categorical column from continuous values"""
    df = df.copy()
    df[f'{column}_category'] = pd.cut(df[column], bins=bins, labels=labels)
    return df


def one_hot_encode(df: pd.DataFrame, columns: List[str], drop_first: bool = False) -> pd.DataFrame:
    """One-hot encode categorical columns"""
    return pd.get_dummies(df, columns=columns, drop_first=drop_first)


def label_encode(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Label encode a categorical column"""
    df = df.copy()
    df[f'{column}_encoded'] = df[column].astype('category').cat.codes
    return df


def normalize_minmax(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Min-Max normalization (scale to 0-1)"""
    df = df.copy()
    for col in columns:
        df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
    return df


def standardize_zscore(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Z-score standardization (mean=0, std=1)"""
    df = df.copy()
    for col in columns:
        df[col] = (df[col] - df[col].mean()) / df[col].std()
    return df


def log_transform(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Apply log transformation to reduce skewness"""
    df = df.copy()
    for col in columns:
        df[f'{col}_log'] = np.log1p(df[col])  # log1p handles zeros
    return df


def sqrt_transform(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Apply square root transformation"""
    df = df.copy()
    for col in columns:
        df[f'{col}_sqrt'] = np.sqrt(df[col])
    return df


def box_cox_transform(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Apply Box-Cox transformation"""
    from scipy.stats import boxcox
    df = df.copy()
    df[f'{column}_boxcox'], _ = boxcox(df[column] + 1)  # Add 1 to handle zeros
    return df


def create_interaction_features(df: pd.DataFrame, col1: str, col2: str) -> pd.DataFrame:
    """Create interaction feature between two columns"""
    df = df.copy()
    df[f'{col1}_{col2}_interaction'] = df[col1] * df[col2]
    return df


def create_polynomial_features(df: pd.DataFrame, column: str, degree: int = 2) -> pd.DataFrame:
    """Create polynomial features"""
    df = df.copy()
    for d in range(2, degree + 1):
        df[f'{column}_pow{d}'] = df[column] ** d
    return df


def bin_numeric_column(df: pd.DataFrame, column: str, bins: int = 5) -> pd.DataFrame:
    """Bin numeric column into equal-width bins"""
    df = df.copy()
    df[f'{column}_binned'] = pd.cut(df[column], bins=bins)
    return df


def qcut_numeric_column(df: pd.DataFrame, column: str, quantiles: int = 4) -> pd.DataFrame:
    """Bin numeric column into equal-frequency bins (quantiles)"""
    df = df.copy()
    df[f'{column}_qcut'] = pd.qcut(df[column], q=quantiles, duplicates='drop')
    return df


def rank_column(df: pd.DataFrame, column: str, method: str = 'average') -> pd.DataFrame:
    """Rank values in a column"""
    df = df.copy()
    df[f'{column}_rank'] = df[column].rank(method=method)
    return df


def create_flag_column(df: pd.DataFrame, column: str, condition: Callable) -> pd.DataFrame:
    """Create binary flag column based on condition"""
    df = df.copy()
    df[f'{column}_flag'] = df[column].apply(condition).astype(int)
    return df


def encode_frequency(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Frequency encoding for categorical variables"""
    df = df.copy()
    freq_map = df[column].value_counts(normalize=True).to_dict()
    df[f'{column}_frequency'] = df[column].map(freq_map)
    return df


def target_encode(df: pd.DataFrame, column: str, target: str) -> pd.DataFrame:
    """Target encoding (mean encoding) for categorical variables"""
    df = df.copy()
    target_map = df.groupby(column)[target].mean().to_dict()
    df[f'{column}_target_encoded'] = df[column].map(target_map)
    return df


def create_ratio_feature(df: pd.DataFrame, numerator: str, denominator: str) -> pd.DataFrame:
    """Create ratio feature"""
    df = df.copy()
    df[f'{numerator}_{denominator}_ratio'] = df[numerator] / (df[denominator] + 1e-10)
    return df


def create_difference_feature(df: pd.DataFrame, col1: str, col2: str) -> pd.DataFrame:
    """Create difference feature"""
    df = df.copy()
    df[f'{col1}_{col2}_diff'] = df[col1] - df[col2]
    return df


def extract_datetime_features(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Extract datetime features (year, month, day, etc.)"""
    df = df.copy()
    df[f'{column}_year'] = df[column].dt.year
    df[f'{column}_month'] = df[column].dt.month
    df[f'{column}_day'] = df[column].dt.day
    df[f'{column}_dayofweek'] = df[column].dt.dayofweek
    df[f'{column}_quarter'] = df[column].dt.quarter
    df[f'{column}_is_weekend'] = df[column].dt.dayofweek.isin([5, 6]).astype(int)
    return df
