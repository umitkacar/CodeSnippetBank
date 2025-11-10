"""
Pandas Data Loading Snippets
Production-ready examples for loading data from various sources
"""

try:
    import pandas as pd
    import numpy as np
    from typing import Dict, List, Optional
    import io
except ImportError as e:
    raise ImportError(f"Required package not installed: {e}. Install with: pip install pandas numpy")


def load_csv_with_options(filepath: str) -> pd.DataFrame:
    """Load CSV with common production settings"""
    return pd.read_csv(
        filepath,
        encoding='utf-8',
        low_memory=False,
        parse_dates=True
    )


def load_csv_chunked(filepath: str, chunksize: int = 10000):
    """Load large CSV files in chunks to save memory"""
    chunks = []
    for chunk in pd.read_csv(filepath, chunksize=chunksize):
        # Process each chunk
        chunks.append(chunk)
    return pd.concat(chunks, ignore_index=True)


def load_csv_selective_columns(filepath: str, columns: List[str]) -> pd.DataFrame:
    """Load only specific columns to reduce memory usage"""
    return pd.read_csv(filepath, usecols=columns)


def load_csv_with_dtype(filepath: str, dtype_dict: Dict[str, str]) -> pd.DataFrame:
    """Load CSV with explicit data types for better performance"""
    return pd.read_csv(filepath, dtype=dtype_dict)


def load_multiple_csvs(filepaths: List[str]) -> pd.DataFrame:
    """Load and concatenate multiple CSV files"""
    dfs = [pd.read_csv(fp) for fp in filepaths]
    return pd.concat(dfs, ignore_index=True)


def load_csv_with_date_parser(filepath: str, date_columns: List[str]) -> pd.DataFrame:
    """Load CSV with custom date parsing"""
    return pd.read_csv(
        filepath,
        parse_dates=date_columns,
        date_format='%Y-%m-%d'
    )


def load_tsv_file(filepath: str) -> pd.DataFrame:
    """Load tab-separated values file"""
    return pd.read_csv(filepath, sep='\t')


def load_csv_skip_rows(filepath: str, skip_rows: int = 0) -> pd.DataFrame:
    """Load CSV skipping header rows"""
    return pd.read_csv(filepath, skiprows=skip_rows)


def load_json_normalized(filepath: str) -> pd.DataFrame:
    """Load JSON file and normalize nested structures"""
    return pd.read_json(filepath, orient='records')


def load_json_lines(filepath: str) -> pd.DataFrame:
    """Load JSON Lines format (newline-delimited JSON)"""
    return pd.read_json(filepath, lines=True)


def load_from_url(url: str) -> pd.DataFrame:
    """Load data directly from URL"""
    return pd.read_csv(url)


def load_excel_single_sheet(filepath: str, sheet_name: str = 'Sheet1') -> pd.DataFrame:
    """Load specific sheet from Excel file"""
    return pd.read_excel(filepath, sheet_name=sheet_name)


def load_excel_all_sheets(filepath: str) -> Dict[str, pd.DataFrame]:
    """Load all sheets from Excel file"""
    return pd.read_excel(filepath, sheet_name=None)


def load_from_clipboard() -> pd.DataFrame:
    """Load data from clipboard"""
    return pd.read_clipboard()


def load_sql_query(connection_string: str, query: str) -> pd.DataFrame:
    """Load data from SQL query"""
    try:
        from sqlalchemy import create_engine
    except ImportError:
        raise ImportError("sqlalchemy not installed. Install with: pip install sqlalchemy")

    engine = create_engine(connection_string)
    return pd.read_sql_query(query, engine)


def load_parquet_file(filepath: str) -> pd.DataFrame:
    """Load Parquet file (efficient columnar format)"""
    return pd.read_parquet(filepath)


def load_feather_file(filepath: str) -> pd.DataFrame:
    """Load Feather file (fast binary format)"""
    return pd.read_feather(filepath)


def load_hdf5_file(filepath: str, key: str = 'df') -> pd.DataFrame:
    """Load HDF5 file"""
    return pd.read_hdf(filepath, key=key)


def load_pickle_file(filepath: str) -> pd.DataFrame:
    """Load pickled DataFrame"""
    return pd.read_pickle(filepath)


# Example usage with synthetic data
if __name__ == "__main__":
    # Create sample CSV data
    sample_data = pd.DataFrame({
        'id': range(1, 101),
        'name': [f'User_{i}' for i in range(1, 101)],
        'age': np.random.randint(18, 80, 100),
        'salary': np.random.randint(30000, 150000, 100),
        'date': pd.date_range('2023-01-01', periods=100)
    })

    # Save to CSV for testing
    sample_data.to_csv('/tmp/sample_data.csv', index=False)

    # Test loading functions
    print("Testing load_csv_with_options:")
    df = load_csv_with_options('/tmp/sample_data.csv')
    print(df.head())
    print(f"\nShape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")


def load_fixed_width_file(filepath: str, colspecs: List[tuple]) -> pd.DataFrame:
    """Load fixed-width formatted file"""
    return pd.read_fwf(filepath, colspecs=colspecs)
