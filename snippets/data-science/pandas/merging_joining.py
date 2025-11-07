"""
Pandas Merging and Joining Snippets
Production-ready examples for combining datasets
"""

import pandas as pd
from typing import List, Optional


def inner_join(df1: pd.DataFrame, df2: pd.DataFrame, on: str) -> pd.DataFrame:
    """Inner join two DataFrames"""
    return pd.merge(df1, df2, on=on, how='inner')


def left_join(df1: pd.DataFrame, df2: pd.DataFrame, on: str) -> pd.DataFrame:
    """Left join two DataFrames"""
    return pd.merge(df1, df2, on=on, how='left')


def right_join(df1: pd.DataFrame, df2: pd.DataFrame, on: str) -> pd.DataFrame:
    """Right join two DataFrames"""
    return pd.merge(df1, df2, on=on, how='right')


def outer_join(df1: pd.DataFrame, df2: pd.DataFrame, on: str) -> pd.DataFrame:
    """Outer join (full join) two DataFrames"""
    return pd.merge(df1, df2, on=on, how='outer')


def merge_on_multiple_keys(df1: pd.DataFrame, df2: pd.DataFrame, on: List[str]) -> pd.DataFrame:
    """Merge on multiple key columns"""
    return pd.merge(df1, df2, on=on, how='inner')


def merge_with_different_column_names(df1: pd.DataFrame, df2: pd.DataFrame, left_on: str, right_on: str) -> pd.DataFrame:
    """Merge DataFrames with different column names"""
    return pd.merge(df1, df2, left_on=left_on, right_on=right_on, how='inner')


def merge_with_suffixes(df1: pd.DataFrame, df2: pd.DataFrame, on: str) -> pd.DataFrame:
    """Merge with custom suffixes for overlapping columns"""
    return pd.merge(df1, df2, on=on, how='inner', suffixes=('_left', '_right'))


def merge_on_index(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """Merge DataFrames on their indexes"""
    return pd.merge(df1, df2, left_index=True, right_index=True, how='inner')


def concat_vertically(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate DataFrames vertically (stacking rows)"""
    return pd.concat(dfs, axis=0, ignore_index=True)


def concat_horizontally(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate DataFrames horizontally (adding columns)"""
    return pd.concat(dfs, axis=1)


def concat_with_keys(dfs: List[pd.DataFrame], keys: List[str]) -> pd.DataFrame:
    """Concatenate with hierarchical index using keys"""
    return pd.concat(dfs, keys=keys)


def join_on_index(df1: pd.DataFrame, df2: pd.DataFrame, how: str = 'left') -> pd.DataFrame:
    """Join DataFrames using their indexes"""
    return df1.join(df2, how=how)


def cross_join(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """Cross join (Cartesian product) of two DataFrames"""
    df1['_key'] = 1
    df2['_key'] = 1
    result = pd.merge(df1, df2, on='_key', how='outer').drop('_key', axis=1)
    return result


def anti_join(df1: pd.DataFrame, df2: pd.DataFrame, on: str) -> pd.DataFrame:
    """Anti join (rows in df1 not in df2)"""
    merged = pd.merge(df1, df2, on=on, how='left', indicator=True)
    return merged[merged['_merge'] == 'left_only'].drop('_merge', axis=1)


def semi_join(df1: pd.DataFrame, df2: pd.DataFrame, on: str) -> pd.DataFrame:
    """Semi join (rows in df1 that have match in df2)"""
    return df1[df1[on].isin(df2[on])]


def merge_asof(df1: pd.DataFrame, df2: pd.DataFrame, on: str, direction: str = 'backward') -> pd.DataFrame:
    """Merge asof (fuzzy/nearest key join for time series)"""
    return pd.merge_asof(df1, df2, on=on, direction=direction)


def merge_with_validation(df1: pd.DataFrame, df2: pd.DataFrame, on: str, validate: str = 'one_to_one') -> pd.DataFrame:
    """Merge with relationship validation"""
    return pd.merge(df1, df2, on=on, how='inner', validate=validate)


def update_dataframe(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """Update values in df1 with values from df2 where they exist"""
    df1 = df1.copy()
    df1.update(df2)
    return df1


def combine_first(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """Combine two DataFrames, preferring df1 values"""
    return df1.combine_first(df2)


def append_rows(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """Append rows from df2 to df1"""
    return pd.concat([df1, df2], ignore_index=True)
