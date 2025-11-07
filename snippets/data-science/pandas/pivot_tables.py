"""
Pandas Pivot Tables Snippets
Production-ready examples for pivot tables and reshaping
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Union


def create_basic_pivot(df: pd.DataFrame, index: str, columns: str, values: str, aggfunc: str = 'mean') -> pd.DataFrame:
    """Create basic pivot table"""
    return df.pivot_table(index=index, columns=columns, values=values, aggfunc=aggfunc)


def pivot_with_multiple_aggregations(df: pd.DataFrame, index: str, columns: str, values: str) -> pd.DataFrame:
    """Pivot table with multiple aggregation functions"""
    return df.pivot_table(index=index, columns=columns, values=values, aggfunc=['mean', 'sum', 'count'])


def pivot_with_margins(df: pd.DataFrame, index: str, columns: str, values: str) -> pd.DataFrame:
    """Pivot table with totals (margins)"""
    return df.pivot_table(index=index, columns=columns, values=values, aggfunc='sum', margins=True, margins_name='Total')


def pivot_multiple_values(df: pd.DataFrame, index: str, columns: str, values: List[str]) -> pd.DataFrame:
    """Pivot table with multiple value columns"""
    return df.pivot_table(index=index, columns=columns, values=values, aggfunc='mean')


def pivot_with_fill_value(df: pd.DataFrame, index: str, columns: str, values: str, fill_value: float = 0) -> pd.DataFrame:
    """Pivot table with fill value for missing data"""
    return df.pivot_table(index=index, columns=columns, values=values, aggfunc='sum', fill_value=fill_value)


def crosstab_basic(df: pd.DataFrame, index_col: str, column_col: str) -> pd.DataFrame:
    """Create crosstab (frequency table)"""
    return pd.crosstab(df[index_col], df[column_col])


def crosstab_with_values(df: pd.DataFrame, index_col: str, column_col: str, values_col: str, aggfunc: str = 'mean') -> pd.DataFrame:
    """Crosstab with values and aggregation"""
    return pd.crosstab(df[index_col], df[column_col], values=df[values_col], aggfunc=aggfunc)


def crosstab_with_margins(df: pd.DataFrame, index_col: str, column_col: str) -> pd.DataFrame:
    """Crosstab with row and column totals"""
    return pd.crosstab(df[index_col], df[column_col], margins=True, margins_name='Total')


def crosstab_normalize(df: pd.DataFrame, index_col: str, column_col: str, normalize: str = 'all') -> pd.DataFrame:
    """Crosstab with normalization (percentages)"""
    return pd.crosstab(df[index_col], df[column_col], normalize=normalize)


def melt_dataframe(df: pd.DataFrame, id_vars: List[str], value_vars: Optional[List[str]] = None) -> pd.DataFrame:
    """Melt DataFrame from wide to long format"""
    return df.melt(id_vars=id_vars, value_vars=value_vars)


def melt_with_custom_names(df: pd.DataFrame, id_vars: List[str], var_name: str = 'variable', value_name: str = 'value') -> pd.DataFrame:
    """Melt with custom variable and value names"""
    return df.melt(id_vars=id_vars, var_name=var_name, value_name=value_name)


def pivot_simple(df: pd.DataFrame, index: str, columns: str, values: str) -> pd.DataFrame:
    """Simple pivot (no aggregation, requires unique index-column pairs)"""
    return df.pivot(index=index, columns=columns, values=values)


def stack_dataframe(df: pd.DataFrame) -> pd.Series:
    """Stack DataFrame (pivot column level to row level)"""
    return df.stack()


def unstack_dataframe(df: pd.DataFrame, level: int = -1) -> pd.DataFrame:
    """Unstack DataFrame (pivot row level to column level)"""
    return df.unstack(level=level)


def transpose_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Transpose DataFrame (swap rows and columns)"""
    return df.T


def wide_to_long(df: pd.DataFrame, stubnames: Union[str, List[str]], i: str, j: str) -> pd.DataFrame:
    """Convert wide format to long format for panel data"""
    return pd.wide_to_long(df, stubnames=stubnames, i=i, j=j)


def pivot_multi_index(df: pd.DataFrame, index: List[str], columns: str, values: str) -> pd.DataFrame:
    """Pivot with multiple index columns"""
    return df.pivot_table(index=index, columns=columns, values=values, aggfunc='mean')


def flatten_multiindex_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten multi-level column index"""
    df = df.copy()
    df.columns = ['_'.join(map(str, col)).strip('_') for col in df.columns.values]
    return df


def explode_list_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Explode list-like column into multiple rows"""
    return df.explode(column).reset_index(drop=True)


def get_dummies_from_pivot(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Create dummy variables (one-hot encoding)"""
    return pd.get_dummies(df, columns=[column], prefix=column)
