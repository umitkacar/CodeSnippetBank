# Data Science Code Snippets

A comprehensive collection of 700+ production-ready Data Science code snippets organized by category.

## Directory Structure

```
data-science/
├── pandas/          (10 files, 214 snippets)
├── numpy/           (8 files, 231 snippets)
├── visualization/   (9 files, 130 snippets)
└── machine-learning/ (9 files, 146 snippets)
```

## Categories Overview

### 1. Pandas (214 snippets)

**Files:**
- `data_loading.py` - 20 snippets for loading data from various sources
- `data_cleaning.py` - 21 snippets for cleaning and preparing data
- `transformations.py` - 21 snippets for data transformations
- `aggregations.py` - 21 snippets for grouping and aggregating data
- `time_series.py` - 20 snippets for time series analysis
- `merging_joining.py` - 20 snippets for combining datasets
- `pivot_tables.py` - 20 snippets for reshaping and pivot operations
- `window_functions.py` - 21 snippets for rolling/window calculations
- `performance_optimization.py` - 20 snippets for optimizing pandas code
- `csv_excel_handling.py` - 30 snippets for CSV/Excel operations

**Key Topics:**
- Data loading from CSV, Excel, JSON, SQL, Parquet, etc.
- Missing value handling, outlier detection, data cleaning
- Feature transformations, encoding, scaling
- GroupBy operations, aggregations, statistics
- Time series operations, date features, resampling
- Merging, joining, concatenating DataFrames
- Pivot tables, melting, reshaping
- Rolling windows, cumulative operations
- Memory optimization, performance tuning
- Import/export operations

### 2. NumPy (231 snippets)

**Files:**
- `array_operations.py` - 30 snippets for array creation and manipulation
- `linear_algebra.py` - 30 snippets for linear algebra operations
- `statistical_functions.py` - 32 snippets for statistical calculations
- `broadcasting.py` - 20 snippets for broadcasting operations
- `vectorization.py` - 30 snippets for vectorized operations
- `random_sampling.py` - 30 snippets for random number generation
- `matrix_operations.py` - 45 snippets for matrix operations
- `performance_tricks.py` - 14 snippets for optimizing NumPy code

**Key Topics:**
- Array creation, reshaping, indexing, slicing
- Matrix operations, decompositions, solving systems
- Statistical functions, distributions, correlations
- Broadcasting for efficient computations
- Vectorization techniques
- Random sampling from various distributions
- Matrix manipulation, transformations
- Performance optimization techniques

### 3. Visualization (130 snippets)

**Files:**
- `matplotlib_plots.py` - 20 snippets for Matplotlib visualizations
- `seaborn_visualizations.py` - 25 snippets for Seaborn statistical plots
- `plotly_interactive.py` - 25 snippets for interactive Plotly charts
- `bokeh_dashboards.py` - 12 snippets for Bokeh dashboards
- `altair_charts.py` - 10 snippets for Altair declarative visualizations
- `statistical_plots.py` - 10 snippets for statistical visualizations
- `time_series_plots.py` - 10 snippets for time series visualizations
- `heatmaps.py` - 10 snippets for heatmap visualizations
- `3d_visualizations.py` - 10 snippets for 3D plots

**Key Topics:**
- Line plots, scatter plots, bar charts, histograms
- Statistical visualizations (box plots, violin plots, distributions)
- Interactive plots with hover tools, zooming, panning
- Dashboards and multi-plot layouts
- Time series visualizations, decomposition plots
- Heatmaps, correlation matrices
- 3D scatter, surface, wireframe plots
- Customization, styling, themes

### 4. Machine Learning (146 snippets)

**Files:**
- `sklearn_pipelines.py` - 15 snippets for ML pipelines
- `feature_engineering.py` - 23 snippets for feature engineering
- `model_training.py` - 20 snippets for training models
- `cross_validation.py` - 11 snippets for model validation
- `hyperparameter_tuning.py` - 11 snippets for hyperparameter optimization
- `model_evaluation.py` - 20 snippets for model evaluation
- `ensemble_methods.py` - 16 snippets for ensemble learning
- `clustering.py` - 19 snippets for unsupervised clustering
- `dimensionality_reduction.py` - 25 snippets for dimensionality reduction

**Key Topics:**
- Scikit-learn pipelines, preprocessing, transformers
- Feature creation, selection, encoding, scaling
- Training classifiers and regressors
- Cross-validation strategies
- Grid search, random search, Bayesian optimization
- Evaluation metrics, confusion matrices, ROC curves
- Voting, bagging, boosting, stacking
- K-means, DBSCAN, hierarchical clustering
- PCA, t-SNE, UMAP, LDA

## Usage Examples

### Pandas Example
```python
from snippets.data_science.pandas.data_loading import load_csv_with_options
from snippets.data_science.pandas.data_cleaning import remove_duplicates

df = load_csv_with_options('data.csv')
df = remove_duplicates(df)
```

### NumPy Example
```python
from snippets.data_science.numpy.array_operations import create_zeros_array
from snippets.data_science.numpy.statistical_functions import calculate_mean

arr = create_zeros_array((100, 10))
mean = calculate_mean(arr)
```

### Visualization Example
```python
from snippets.data_science.visualization.matplotlib_plots import scatter_plot
import numpy as np

x = np.random.randn(100)
y = np.random.randn(100)
scatter_plot(x, y)
```

### Machine Learning Example
```python
from snippets.data_science.machine_learning.model_training import train_random_forest_classifier
from snippets.data_science.machine_learning.model_evaluation import evaluate_classification_model

model = train_random_forest_classifier(X_train, y_train)
y_pred = model.predict(X_test)
results = evaluate_classification_model(y_test, y_pred)
```

## Features

- **Production-Ready**: All snippets are tested and follow best practices
- **Type Hints**: Functions include type hints for better IDE support
- **Documentation**: Each function has clear docstrings
- **Modular**: Easy to import and use individual functions
- **Comprehensive**: Covers all major data science operations
- **Up-to-Date**: Uses modern libraries and techniques

## Requirements

```
pandas >= 1.3.0
numpy >= 1.21.0
matplotlib >= 3.4.0
seaborn >= 0.11.0
plotly >= 5.0.0
bokeh >= 2.4.0
altair >= 4.2.0
scikit-learn >= 1.0.0
scipy >= 1.7.0
```

Optional for specific features:
```
xgboost >= 1.5.0
lightgbm >= 3.3.0
catboost >= 1.0.0
umap-learn >= 0.5.0
optuna >= 2.10.0
```

## Total Statistics

- **Total Files**: 36 Python files
- **Total Snippets**: 721 functions
- **Lines of Code**: ~7,000+
- **Categories**: 4 main categories
- **Subcategories**: 36 topic areas

## File Organization

Each category is organized into focused files:
- Each file contains 10-30 related functions
- Functions are well-documented with docstrings
- Type hints provided for better code completion
- Import statements included in each file
- Production-ready, battle-tested code

## Contributing

These snippets are designed to be:
- Easy to understand and modify
- Copy-paste ready for projects
- Extensible for custom needs
- Compatible with modern data science workflows

## License

These snippets are provided as educational resources and can be freely used in your projects.
