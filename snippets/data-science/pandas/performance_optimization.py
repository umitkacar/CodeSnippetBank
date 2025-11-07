"""
Pandas Performance Optimization Snippets
Production-ready examples for improving pandas performance
"""

import pandas as pd
import numpy as np
from typing import List, Dict


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize data types to reduce memory usage"""
    df = df.copy()

    # Optimize integers
    for col in df.select_dtypes(include=['int']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')

    # Optimize floats
    for col in df.select_dtypes(include=['float']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')

    # Convert object to category if unique values < 50% of total
    for col in df.select_dtypes(include=['object']).columns:
        num_unique = df[col].nunique()
        num_total = len(df[col])
        if num_unique / num_total < 0.5:
            df[col] = df[col].astype('category')

    return df


def reduce_memory_usage(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Reduce memory usage by optimizing data types"""
    start_mem = df.memory_usage().sum() / 1024**2
    df = df.copy()

    for col in df.columns:
        col_type = df[col].dtype

        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()

            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)

    if verbose:
        end_mem = df.memory_usage().sum() / 1024**2
        print(f'Memory usage decreased from {start_mem:.2f} MB to {end_mem:.2f} MB '
              f'({100 * (start_mem - end_mem) / start_mem:.1f}% reduction)')

    return df


def use_categorical(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Convert columns to categorical type for memory efficiency"""
    df = df.copy()
    for col in columns:
        df[col] = df[col].astype('category')
    return df


def vectorized_string_operations(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Use vectorized string operations instead of apply"""
    df = df.copy()
    # Vectorized (fast)
    df[f'{column}_upper'] = df[column].str.upper()
    df[f'{column}_lower'] = df[column].str.lower()
    df[f'{column}_length'] = df[column].str.len()
    return df


def use_numpy_where(df: pd.DataFrame, column: str, condition_value: float, true_value: str, false_value: str) -> pd.DataFrame:
    """Use numpy.where instead of apply for conditional operations"""
    df = df.copy()
    df['result'] = np.where(df[column] > condition_value, true_value, false_value)
    return df


def use_query_method(df: pd.DataFrame, condition: str) -> pd.DataFrame:
    """Use query method for faster filtering"""
    return df.query(condition)


def use_eval_method(df: pd.DataFrame, expression: str) -> pd.DataFrame:
    """Use eval method for faster arithmetic operations"""
    df = df.copy()
    df.eval(expression, inplace=True)
    return df


def chunk_processing(filepath: str, chunksize: int = 10000):
    """Process large files in chunks"""
    results = []
    for chunk in pd.read_csv(filepath, chunksize=chunksize):
        # Process each chunk
        processed = chunk[chunk['value'] > 100]  # Example processing
        results.append(processed)
    return pd.concat(results, ignore_index=True)


def use_inplace_operations(df: pd.DataFrame) -> pd.DataFrame:
    """Use inplace operations to save memory (use with caution)"""
    df.drop_duplicates(inplace=True)
    df.fillna(0, inplace=True)
    df.sort_values('column_name', inplace=True)
    return df


def avoid_chained_indexing(df: pd.DataFrame, condition: bool, column: str, value) -> pd.DataFrame:
    """Avoid chained indexing, use loc instead"""
    df = df.copy()
    # Bad: df[df['col1'] > 0]['col2'] = value
    # Good:
    df.loc[df[column] > 0, column] = value
    return df


def use_isin_instead_of_apply(df: pd.DataFrame, column: str, values: List) -> pd.DataFrame:
    """Use isin() instead of apply() for membership testing"""
    df = df.copy()
    # Fast vectorized operation
    df['is_member'] = df[column].isin(values)
    return df


def parallel_processing_with_dask(filepath: str):
    """Use Dask for parallel processing of large datasets"""
    import dask.dataframe as dd
    ddf = dd.read_csv(filepath)
    result = ddf.groupby('column').agg({'value': 'mean'}).compute()
    return result


def use_arrow_engine(filepath: str) -> pd.DataFrame:
    """Use PyArrow engine for faster CSV reading"""
    return pd.read_csv(filepath, engine='pyarrow')


def optimize_groupby(df: pd.DataFrame, group_col: str, agg_dict: Dict) -> pd.DataFrame:
    """Optimize groupby operations"""
    # Use sort=False if order doesn't matter
    return df.groupby(group_col, sort=False).agg(agg_dict).reset_index()


def use_numba_for_custom_functions(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Use Numba to compile custom functions for speed"""
    from numba import jit

    @jit(nopython=True)
    def custom_calculation(x):
        return x ** 2 + 2 * x + 1

    df = df.copy()
    df[f'{column}_calculated'] = df[column].apply(custom_calculation)
    return df


def cache_intermediate_results(df: pd.DataFrame) -> pd.DataFrame:
    """Cache intermediate results to avoid recomputation"""
    # Create a persistent copy for reuse
    cached_df = df.copy()
    return cached_df


def use_swifter_for_apply(df: pd.DataFrame, column: str, func) -> pd.DataFrame:
    """Use swifter for intelligent apply optimization"""
    try:
        import swifter
        df = df.copy()
        df[f'{column}_result'] = df[column].swifter.apply(func)
        return df
    except ImportError:
        print("Install swifter: pip install swifter")
        return df


def batch_insert_to_sql(df: pd.DataFrame, connection_string: str, table_name: str, batch_size: int = 1000):
    """Batch insert for efficient SQL operations"""
    from sqlalchemy import create_engine
    engine = create_engine(connection_string)

    for start in range(0, len(df), batch_size):
        end = start + batch_size
        df.iloc[start:end].to_sql(table_name, engine, if_exists='append', index=False)


def use_parquet_format(df: pd.DataFrame, filepath: str):
    """Save as Parquet for efficient storage and fast I/O"""
    df.to_parquet(filepath, compression='snappy', index=False)


def profile_memory_usage(df: pd.DataFrame):
    """Profile memory usage of DataFrame"""
    print(df.info(memory_usage='deep'))
    print("\nMemory usage by column:")
    print(df.memory_usage(deep=True) / 1024**2, "MB")
