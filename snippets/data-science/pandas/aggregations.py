"""
Pandas Aggregations Snippets
Production-ready examples for aggregating and summarizing data
"""

try:
    import pandas as pd
    import numpy as np
    from typing import List, Dict, Callable
except ImportError as e:
    raise ImportError(f"Required package not installed: {e}. Install with: pip install pandas numpy")


def group_by_single_agg(df: pd.DataFrame, group_col: str, agg_col: str, agg_func: str = 'mean') -> pd.DataFrame:
    """Group by single column and aggregate"""
    return df.groupby(group_col)[agg_col].agg(agg_func).reset_index()


def group_by_multiple_aggs(df: pd.DataFrame, group_col: str, agg_col: str, agg_funcs: List[str]) -> pd.DataFrame:
    """Group by and apply multiple aggregations"""
    return df.groupby(group_col)[agg_col].agg(agg_funcs).reset_index()


def group_by_multiple_columns(df: pd.DataFrame, group_cols: List[str], agg_dict: Dict) -> pd.DataFrame:
    """Group by multiple columns with different aggregations"""
    return df.groupby(group_cols).agg(agg_dict).reset_index()


def aggregate_with_custom_names(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Aggregate with custom column names"""
    return df.groupby(group_col).agg(
        avg_value=('value', 'mean'),
        total_value=('value', 'sum'),
        count=('value', 'count'),
        max_value=('value', 'max'),
        min_value=('value', 'min')
    ).reset_index()


def count_unique_values(df: pd.DataFrame, group_col: str, count_col: str) -> pd.DataFrame:
    """Count unique values per group"""
    return df.groupby(group_col)[count_col].nunique().reset_index(name='unique_count')


def get_first_last_in_group(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Get first and last record in each group"""
    first = df.groupby(group_col).first()
    last = df.groupby(group_col).last()
    return first, last


def calculate_percentiles(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """Calculate percentiles per group"""
    return df.groupby(group_col)[value_col].quantile([0.25, 0.5, 0.75]).reset_index()


def aggregate_with_filter(df: pd.DataFrame, group_col: str, filter_col: str, threshold: float) -> pd.DataFrame:
    """Aggregate after filtering"""
    filtered_df = df[df[filter_col] > threshold]
    return filtered_df.groupby(group_col).agg({'value': ['mean', 'sum', 'count']}).reset_index()


def cumulative_sum_by_group(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """Calculate cumulative sum within each group"""
    df = df.copy()
    df[f'{value_col}_cumsum'] = df.groupby(group_col)[value_col].cumsum()
    return df


def cumulative_product_by_group(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """Calculate cumulative product within each group"""
    df = df.copy()
    df[f'{value_col}_cumprod'] = df.groupby(group_col)[value_col].cumprod()
    return df


def rank_within_group(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """Rank values within each group"""
    df = df.copy()
    df[f'{value_col}_rank'] = df.groupby(group_col)[value_col].rank(ascending=False)
    return df


def calculate_group_statistics(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """Calculate comprehensive statistics per group"""
    return df.groupby(group_col)[value_col].describe()


def count_value_occurrences(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Count occurrences of each value"""
    return df[column].value_counts().reset_index(name='count')


def aggregate_by_time_period(df: pd.DataFrame, date_col: str, value_col: str, freq: str = 'M') -> pd.DataFrame:
    """Aggregate by time period (M=month, W=week, D=day, Y=year)"""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    return df.set_index(date_col).resample(freq)[value_col].agg(['mean', 'sum', 'count']).reset_index()


def calculate_moving_average(df: pd.DataFrame, column: str, window: int = 3) -> pd.DataFrame:
    """Calculate moving average"""
    df = df.copy()
    df[f'{column}_ma{window}'] = df[column].rolling(window=window).mean()
    return df


def calculate_percentage_of_total(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """Calculate percentage of total within each group"""
    df = df.copy()
    df[f'{value_col}_pct'] = df.groupby(group_col)[value_col].transform(lambda x: x / x.sum() * 100)
    return df


def aggregate_with_custom_function(df: pd.DataFrame, group_col: str, value_col: str, func: Callable) -> pd.DataFrame:
    """Aggregate with custom function"""
    return df.groupby(group_col)[value_col].apply(func).reset_index()


def calculate_variance_std(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """Calculate variance and standard deviation per group"""
    return df.groupby(group_col)[value_col].agg(['var', 'std']).reset_index()


def get_top_n_per_group(df: pd.DataFrame, group_col: str, value_col: str, n: int = 3) -> pd.DataFrame:
    """Get top N records per group"""
    return df.groupby(group_col).apply(lambda x: x.nlargest(n, value_col)).reset_index(drop=True)


def calculate_mode_per_group(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """Calculate mode (most frequent value) per group"""
    return df.groupby(group_col)[value_col].apply(lambda x: x.mode()[0] if len(x.mode()) > 0 else np.nan).reset_index()
