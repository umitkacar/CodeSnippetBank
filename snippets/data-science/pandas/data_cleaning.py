"""
Pandas Data Cleaning Snippets
Production-ready examples for cleaning and preparing data
"""

try:
    import pandas as pd
    import numpy as np
    from typing import List, Optional, Union
except ImportError as e:
    raise ImportError(f"Required package not installed: {e}. Install with: pip install pandas numpy")


def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
    """Remove duplicate rows"""
    return df.drop_duplicates(subset=subset, keep='first')


def handle_missing_values_drop(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """Drop columns with missing values above threshold"""
    missing_pct = df.isnull().sum() / len(df)
    cols_to_keep = missing_pct[missing_pct <= threshold].index
    return df[cols_to_keep]


def fill_missing_with_median(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Fill missing values with median"""
    df = df.copy()
    for col in columns:
        df[col].fillna(df[col].median(), inplace=True)
    return df


def fill_missing_with_mean(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Fill missing values with mean"""
    df = df.copy()
    for col in columns:
        df[col].fillna(df[col].mean(), inplace=True)
    return df


def fill_missing_with_mode(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Fill missing values with mode (most frequent value)"""
    df = df.copy()
    for col in columns:
        df[col].fillna(df[col].mode()[0], inplace=True)
    return df


def forward_fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Forward fill missing values (carry last valid observation forward)"""
    return df.ffill()


def backward_fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Backward fill missing values"""
    return df.bfill()


def interpolate_missing(df: pd.DataFrame, method: str = 'linear') -> pd.DataFrame:
    """Interpolate missing values"""
    return df.interpolate(method=method)


def remove_outliers_iqr(df: pd.DataFrame, column: str, multiplier: float = 1.5) -> pd.DataFrame:
    """Remove outliers using IQR method"""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]


def remove_outliers_zscore(df: pd.DataFrame, column: str, threshold: float = 3.0) -> pd.DataFrame:
    """Remove outliers using Z-score method"""
    z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
    return df[z_scores < threshold]


def cap_outliers(df: pd.DataFrame, column: str, lower_pct: float = 0.01, upper_pct: float = 0.99) -> pd.DataFrame:
    """Cap outliers at percentile values"""
    df = df.copy()
    lower_bound = df[column].quantile(lower_pct)
    upper_bound = df[column].quantile(upper_pct)
    df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
    return df


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names (lowercase, replace spaces with underscores)"""
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('[^a-z0-9_]', '', regex=True)
    return df


def remove_whitespace(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Remove leading and trailing whitespace from string columns"""
    df = df.copy()
    for col in columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip()
    return df


def convert_to_numeric(df: pd.DataFrame, columns: List[str], errors: str = 'coerce') -> pd.DataFrame:
    """Convert columns to numeric, coercing errors to NaN"""
    df = df.copy()
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors=errors)
    return df


def convert_to_datetime(df: pd.DataFrame, columns: List[str], format: Optional[str] = None) -> pd.DataFrame:
    """Convert columns to datetime"""
    df = df.copy()
    for col in columns:
        df[col] = pd.to_datetime(df[col], format=format, errors='coerce')
    return df


def replace_values(df: pd.DataFrame, column: str, replacements: dict) -> pd.DataFrame:
    """Replace values in a column using a mapping dictionary"""
    df = df.copy()
    df[column] = df[column].replace(replacements)
    return df


def remove_constant_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove columns with constant values"""
    return df.loc[:, df.nunique() > 1]


def remove_highly_correlated(df: pd.DataFrame, threshold: float = 0.95) -> pd.DataFrame:
    """Remove highly correlated numeric columns"""
    numeric_df = df.select_dtypes(include=[np.number])
    corr_matrix = numeric_df.corr().abs()
    upper_triangle = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = [column for column in upper_triangle.columns if any(upper_triangle[column] > threshold)]
    return df.drop(columns=to_drop)


def reset_index_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Reset index and drop old index"""
    return df.reset_index(drop=True)


def clean_currency_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Clean currency column (remove $, commas, etc.)"""
    df = df.copy()
    df[column] = df[column].str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)
    return df


# Example usage with synthetic data
if __name__ == "__main__":
    # Create sample data with missing values and outliers
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'id': range(1, 101),
        'age': np.random.randint(18, 80, 100),
        'salary': np.random.randint(30000, 150000, 100),
        'category': np.random.choice(['A', 'B', 'C', None], 100),
        'score': np.random.randn(100) * 10 + 50
    })

    # Add some missing values
    sample_data.loc[np.random.choice(100, 10, replace=False), 'age'] = np.nan
    sample_data.loc[np.random.choice(100, 15, replace=False), 'salary'] = np.nan

    # Add outliers
    sample_data.loc[5, 'salary'] = 1000000
    sample_data.loc[10, 'score'] = 200

    print("Testing data cleaning functions:")
    print("\nOriginal data:")
    print(sample_data.head(20))
    print(f"\nMissing values:\n{sample_data.isnull().sum()}")

    # Test removing duplicates
    print("\n--- Testing remove_duplicates ---")
    cleaned = remove_duplicates(sample_data)
    print(f"Shape after removing duplicates: {cleaned.shape}")

    # Test filling missing values
    print("\n--- Testing fill_missing_with_median ---")
    filled = fill_missing_with_median(sample_data, ['age', 'salary'])
    print(f"Missing values after median fill:\n{filled[['age', 'salary']].isnull().sum()}")

    # Test outlier removal
    print("\n--- Testing remove_outliers_iqr ---")
    no_outliers = remove_outliers_iqr(sample_data.copy(), 'salary')
    print(f"Shape after removing outliers: {no_outliers.shape}")
