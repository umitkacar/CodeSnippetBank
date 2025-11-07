"""
Pandas CSV and Excel Handling Snippets
Production-ready examples for CSV and Excel operations
"""

import pandas as pd
from typing import List, Optional, Dict


def read_csv_basic(filepath: str) -> pd.DataFrame:
    """Read CSV file with basic settings"""
    return pd.read_csv(filepath)


def read_csv_with_encoding(filepath: str, encoding: str = 'utf-8') -> pd.DataFrame:
    """Read CSV with specific encoding"""
    return pd.read_csv(filepath, encoding=encoding)


def read_csv_with_delimiter(filepath: str, delimiter: str = ',') -> pd.DataFrame:
    """Read CSV with custom delimiter"""
    return pd.read_csv(filepath, sep=delimiter)


def read_csv_skip_rows(filepath: str, skip_rows: int) -> pd.DataFrame:
    """Read CSV skipping first N rows"""
    return pd.read_csv(filepath, skiprows=skip_rows)


def read_csv_select_columns(filepath: str, columns: List[str]) -> pd.DataFrame:
    """Read only specific columns from CSV"""
    return pd.read_csv(filepath, usecols=columns)


def read_csv_with_dtypes(filepath: str, dtypes: Dict[str, type]) -> pd.DataFrame:
    """Read CSV with specified data types"""
    return pd.read_csv(filepath, dtype=dtypes)


def read_csv_parse_dates(filepath: str, date_columns: List[str]) -> pd.DataFrame:
    """Read CSV and parse date columns"""
    return pd.read_csv(filepath, parse_dates=date_columns)


def read_csv_no_header(filepath: str, column_names: List[str]) -> pd.DataFrame:
    """Read CSV without header and assign column names"""
    return pd.read_csv(filepath, header=None, names=column_names)


def read_csv_with_index(filepath: str, index_col: str) -> pd.DataFrame:
    """Read CSV and set index column"""
    return pd.read_csv(filepath, index_col=index_col)


def read_csv_handle_missing(filepath: str, na_values: List[str]) -> pd.DataFrame:
    """Read CSV with custom missing value indicators"""
    return pd.read_csv(filepath, na_values=na_values)


def read_csv_nrows(filepath: str, nrows: int) -> pd.DataFrame:
    """Read only first N rows from CSV"""
    return pd.read_csv(filepath, nrows=nrows)


def read_csv_compression(filepath: str) -> pd.DataFrame:
    """Read compressed CSV file"""
    return pd.read_csv(filepath, compression='gzip')


def write_csv_basic(df: pd.DataFrame, filepath: str):
    """Write DataFrame to CSV"""
    df.to_csv(filepath, index=False)


def write_csv_with_encoding(df: pd.DataFrame, filepath: str, encoding: str = 'utf-8'):
    """Write CSV with specific encoding"""
    df.to_csv(filepath, index=False, encoding=encoding)


def write_csv_with_delimiter(df: pd.DataFrame, filepath: str, delimiter: str = ','):
    """Write CSV with custom delimiter"""
    df.to_csv(filepath, index=False, sep=delimiter)


def write_csv_selected_columns(df: pd.DataFrame, filepath: str, columns: List[str]):
    """Write only selected columns to CSV"""
    df[columns].to_csv(filepath, index=False)


def write_csv_compression(df: pd.DataFrame, filepath: str):
    """Write compressed CSV file"""
    df.to_csv(filepath, index=False, compression='gzip')


def write_csv_append(df: pd.DataFrame, filepath: str):
    """Append DataFrame to existing CSV"""
    df.to_csv(filepath, mode='a', header=False, index=False)


def write_csv_with_header(df: pd.DataFrame, filepath: str, header: bool = True):
    """Write CSV with or without header"""
    df.to_csv(filepath, index=False, header=header)


def read_excel_basic(filepath: str, sheet_name: str = 'Sheet1') -> pd.DataFrame:
    """Read Excel file"""
    return pd.read_excel(filepath, sheet_name=sheet_name)


def read_excel_multiple_sheets(filepath: str) -> Dict[str, pd.DataFrame]:
    """Read all sheets from Excel file"""
    return pd.read_excel(filepath, sheet_name=None)


def read_excel_specific_sheets(filepath: str, sheet_names: List[str]) -> Dict[str, pd.DataFrame]:
    """Read specific sheets from Excel"""
    dfs = {}
    for sheet in sheet_names:
        dfs[sheet] = pd.read_excel(filepath, sheet_name=sheet)
    return dfs


def read_excel_range(filepath: str, sheet_name: str, skiprows: int = 0, nrows: int = 100) -> pd.DataFrame:
    """Read specific range from Excel"""
    return pd.read_excel(filepath, sheet_name=sheet_name, skiprows=skiprows, nrows=nrows)


def read_excel_with_index(filepath: str, sheet_name: str, index_col: int = 0) -> pd.DataFrame:
    """Read Excel with index column"""
    return pd.read_excel(filepath, sheet_name=sheet_name, index_col=index_col)


def write_excel_basic(df: pd.DataFrame, filepath: str, sheet_name: str = 'Sheet1'):
    """Write DataFrame to Excel"""
    df.to_excel(filepath, sheet_name=sheet_name, index=False)


def write_excel_multiple_sheets(dfs: Dict[str, pd.DataFrame], filepath: str):
    """Write multiple DataFrames to different sheets"""
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def write_excel_with_formatting(df: pd.DataFrame, filepath: str):
    """Write Excel with cell formatting"""
    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1
        })

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)


def write_excel_append(df: pd.DataFrame, filepath: str, sheet_name: str = 'NewSheet'):
    """Append DataFrame to existing Excel file"""
    with pd.ExcelWriter(filepath, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


def export_to_csv_chunked(df: pd.DataFrame, filepath: str, chunksize: int = 10000):
    """Export large DataFrame to CSV in chunks"""
    for i in range(0, len(df), chunksize):
        chunk = df.iloc[i:i + chunksize]
        mode = 'w' if i == 0 else 'a'
        header = i == 0
        chunk.to_csv(filepath, mode=mode, header=header, index=False)


def read_csv_with_converters(filepath: str, converters: Dict[str, callable]) -> pd.DataFrame:
    """Read CSV with custom converters for columns"""
    return pd.read_csv(filepath, converters=converters)


def read_csv_thousands_separator(filepath: str, thousands: str = ',') -> pd.DataFrame:
    """Read CSV with thousands separator in numbers"""
    return pd.read_csv(filepath, thousands=thousands)


def read_csv_decimal_separator(filepath: str, decimal: str = '.') -> pd.DataFrame:
    """Read CSV with custom decimal separator"""
    return pd.read_csv(filepath, decimal=decimal)


def write_csv_float_format(df: pd.DataFrame, filepath: str, float_format: str = '%.2f'):
    """Write CSV with custom float formatting"""
    df.to_csv(filepath, index=False, float_format=float_format)


def read_excel_with_engine(filepath: str, engine: str = 'openpyxl') -> pd.DataFrame:
    """Read Excel with specific engine"""
    return pd.read_excel(filepath, engine=engine)


def validate_csv_before_reading(filepath: str) -> bool:
    """Validate CSV file before reading"""
    try:
        pd.read_csv(filepath, nrows=5)
        return True
    except Exception as e:
        print(f"CSV validation failed: {e}")
        return False
