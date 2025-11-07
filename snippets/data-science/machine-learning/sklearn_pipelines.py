"""
Scikit-learn Pipeline Snippets
Production-ready examples for ML pipelines
"""

from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pandas as pd


def basic_pipeline():
    """Create basic preprocessing and modeling pipeline"""
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression())
    ])
    return pipeline


def preprocessing_pipeline():
    """Create preprocessing pipeline"""
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])
    return pipeline


def numeric_pipeline():
    """Pipeline for numeric features"""
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    return numeric_transformer


def categorical_pipeline():
    """Pipeline for categorical features"""
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    return categorical_transformer


def column_transformer_pipeline(numeric_features: list, categorical_features: list):
    """Create column transformer for mixed data types"""
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    return preprocessor


def full_pipeline_with_model(numeric_features: list, categorical_features: list):
    """Complete pipeline with preprocessing and model"""
    preprocessor = column_transformer_pipeline(numeric_features, categorical_features)

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    return pipeline


def make_pipeline_shorthand():
    """Create pipeline using make_pipeline (no need to name steps)"""
    pipeline = make_pipeline(
        SimpleImputer(strategy='mean'),
        StandardScaler(),
        LogisticRegression()
    )
    return pipeline


def pipeline_with_feature_selection():
    """Pipeline with feature selection"""
    from sklearn.feature_selection import SelectKBest, f_classif

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('feature_selection', SelectKBest(f_classif, k=10)),
        ('classifier', LogisticRegression())
    ])
    return pipeline


def pipeline_with_pca():
    """Pipeline with PCA dimensionality reduction"""
    from sklearn.decomposition import PCA

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('pca', PCA(n_components=0.95)),
        ('classifier', LogisticRegression())
    ])
    return pipeline


def pipeline_with_custom_transformer():
    """Pipeline with custom transformer"""
    from sklearn.base import BaseEstimator, TransformerMixin

    class CustomTransformer(BaseEstimator, TransformerMixin):
        def fit(self, X, y=None):
            return self

        def transform(self, X):
            return X ** 2

    pipeline = Pipeline([
        ('custom', CustomTransformer()),
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression())
    ])
    return pipeline


def nested_pipeline():
    """Create nested pipeline"""
    preprocessing = Pipeline([
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])

    full_pipeline = Pipeline([
        ('preprocessing', preprocessing),
        ('classifier', LogisticRegression())
    ])
    return full_pipeline


def pipeline_for_text_classification():
    """Pipeline for text classification"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000)),
        ('classifier', MultinomialNB())
    ])
    return pipeline


def pipeline_with_multiple_models():
    """Pipeline with model selection"""
    from sklearn.model_selection import GridSearchCV

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression())
    ])

    param_grid = [
        {
            'classifier': [LogisticRegression()],
            'classifier__C': [0.1, 1, 10]
        },
        {
            'classifier': [RandomForestClassifier()],
            'classifier__n_estimators': [50, 100, 200]
        }
    ]

    grid_search = GridSearchCV(pipeline, param_grid, cv=5)
    return grid_search


def pipeline_with_caching():
    """Pipeline with caching for faster repeated fits"""
    from tempfile import mkdtemp
    from shutil import rmtree

    cachedir = mkdtemp()
    pipeline = Pipeline([
        ('imputer', SimpleImputer()),
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression())
    ], memory=cachedir)

    return pipeline
