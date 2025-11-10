"""
Time Series Visualization Snippets
Production-ready examples for time series plots
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def time_series_line_plot(df: pd.DataFrame, date_col: str, value_col: str):
    """Create basic time series line plot"""
    plt.figure(figsize=(12, 6))
    plt.plot(df[date_col], df[value_col], linewidth=2)
    plt.title('Time Series Plot')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def multiple_time_series_plot(df: pd.DataFrame, date_col: str, value_cols: list):
    """Plot multiple time series"""
    plt.figure(figsize=(12, 6))
    for col in value_cols:
        plt.plot(df[date_col], df[col], label=col, linewidth=2)
    plt.title('Multiple Time Series')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def time_series_with_trend(df: pd.DataFrame, date_col: str, value_col: str, trend: np.ndarray):
    """Plot time series with trend line"""
    plt.figure(figsize=(12, 6))
    plt.plot(df[date_col], df[value_col], label='Data', linewidth=1.5, alpha=0.7)
    plt.plot(df[date_col], trend, label='Trend', linewidth=2, color='red', linestyle='--')
    plt.title('Time Series with Trend')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def seasonal_decomposition_plot(df: pd.DataFrame, date_col: str, value_col: str):
    """Plot seasonal decomposition"""
    try:
        from statsmodels.tsa.seasonal import seasonal_decompose
    except ImportError:
        raise ImportError("statsmodels not installed. Install with: pip install statsmodels")

    df_indexed = df.set_index(date_col)
    result = seasonal_decompose(df_indexed[value_col], model='additive', period=12)

    fig, axes = plt.subplots(4, 1, figsize=(12, 10))

    result.observed.plot(ax=axes[0], title='Original', legend=False)
    result.trend.plot(ax=axes[1], title='Trend', legend=False)
    result.seasonal.plot(ax=axes[2], title='Seasonal', legend=False)
    result.resid.plot(ax=axes[3], title='Residual', legend=False)

    plt.tight_layout()
    plt.show()


def moving_average_plot(df: pd.DataFrame, date_col: str, value_col: str, windows: list = [7, 30]):
    """Plot time series with moving averages"""
    plt.figure(figsize=(12, 6))
    plt.plot(df[date_col], df[value_col], label='Original', alpha=0.5)

    for window in windows:
        ma = df[value_col].rolling(window=window).mean()
        plt.plot(df[date_col], ma, label=f'{window}-day MA', linewidth=2)

    plt.title('Time Series with Moving Averages')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def autocorrelation_plot(data: pd.Series, lags: int = 50):
    """Create autocorrelation plot (ACF)"""
    try:
        from statsmodels.graphics.tsaplots import plot_acf
    except ImportError:
        raise ImportError("statsmodels not installed. Install with: pip install statsmodels")

    fig, ax = plt.subplots(figsize=(12, 6))
    plot_acf(data, lags=lags, ax=ax)
    plt.title('Autocorrelation Function (ACF)')
    plt.tight_layout()
    plt.show()


def partial_autocorrelation_plot(data: pd.Series, lags: int = 50):
    """Create partial autocorrelation plot (PACF)"""
    try:
        from statsmodels.graphics.tsaplots import plot_pacf
    except ImportError:
        raise ImportError("statsmodels not installed. Install with: pip install statsmodels")

    fig, ax = plt.subplots(figsize=(12, 6))
    plot_pacf(data, lags=lags, ax=ax)
    plt.title('Partial Autocorrelation Function (PACF)')
    plt.tight_layout()
    plt.show()


def forecast_plot(df: pd.DataFrame, date_col: str, actual_col: str,
                  forecast_dates: pd.Series, forecast_values: np.ndarray,
                  confidence_intervals: tuple = None):
    """Plot actual vs forecast with confidence intervals"""
    plt.figure(figsize=(12, 6))

    plt.plot(df[date_col], df[actual_col], label='Actual', linewidth=2)
    plt.plot(forecast_dates, forecast_values, label='Forecast', linewidth=2, linestyle='--')

    if confidence_intervals:
        lower, upper = confidence_intervals
        plt.fill_between(forecast_dates, lower, upper, alpha=0.3, label='Confidence Interval')

    plt.title('Forecast vs Actual')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def calendar_heatmap(df: pd.DataFrame, date_col: str, value_col: str):
    """Create calendar heatmap"""
    import seaborn as sns

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month
    df['day'] = df[date_col].dt.day

    pivot = df.pivot_table(values=value_col, index='day', columns='month', aggfunc='mean')

    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot, annot=False, cmap='YlOrRd', cbar_kws={'label': 'Value'})
    plt.title('Calendar Heatmap')
    plt.xlabel('Month')
    plt.ylabel('Day')
    plt.tight_layout()
    plt.show()


def year_over_year_comparison(df: pd.DataFrame, date_col: str, value_col: str):
    """Plot year-over-year comparison"""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df['year'] = df[date_col].dt.year
    df['day_of_year'] = df[date_col].dt.dayofyear

    plt.figure(figsize=(12, 6))
    for year in df['year'].unique():
        year_data = df[df['year'] == year]
        plt.plot(year_data['day_of_year'], year_data[value_col], label=str(year), linewidth=2)

    plt.title('Year-over-Year Comparison')
    plt.xlabel('Day of Year')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
