"""
Cross-Validation Snippets
Production-ready examples for model validation
"""

from sklearn.model_selection import (cross_val_score, cross_validate, KFold,
                                     StratifiedKFold, TimeSeriesSplit, LeaveOneOut)
import numpy as np


def simple_cross_validation(model, X, y, cv=5):
    """Perform simple k-fold cross-validation"""
    scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
    return scores


def stratified_cross_validation(model, X, y, n_splits=5):
    """Stratified k-fold cross-validation (preserves class distribution)"""
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
    return scores


def cross_validation_multiple_metrics(model, X, y):
    """Cross-validation with multiple scoring metrics"""
    scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
    scores = cross_validate(model, X, y, cv=5, scoring=scoring,
                            return_train_score=True)
    return scores


def time_series_cross_validation(model, X, y, n_splits=5):
    """Time series cross-validation (no shuffling)"""
    tscv = TimeSeriesSplit(n_splits=n_splits)
    scores = cross_val_score(model, X, y, cv=tscv, scoring='neg_mean_squared_error')
    return scores


def leave_one_out_cv(model, X, y):
    """Leave-One-Out cross-validation"""
    loo = LeaveOneOut()
    scores = cross_val_score(model, X, y, cv=loo, scoring='accuracy')
    return scores


def repeated_kfold_cv(model, X, y, n_splits=5, n_repeats=10):
    """Repeated k-fold cross-validation"""
    from sklearn.model_selection import RepeatedKFold

    rkf = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=42)
    scores = cross_val_score(model, X, y, cv=rkf, scoring='accuracy')
    return scores


def group_kfold_cv(model, X, y, groups):
    """Group k-fold cross-validation (groups stay together)"""
    from sklearn.model_selection import GroupKFold

    gkf = GroupKFold(n_splits=5)
    scores = cross_val_score(model, X, y, cv=gkf, groups=groups, scoring='accuracy')
    return scores


def nested_cross_validation(model, param_grid, X, y):
    """Nested cross-validation for hyperparameter tuning"""
    from sklearn.model_selection import GridSearchCV

    outer_cv = KFold(n_splits=5, shuffle=True, random_state=42)
    inner_cv = KFold(n_splits=3, shuffle=True, random_state=42)

    clf = GridSearchCV(model, param_grid, cv=inner_cv)
    scores = cross_val_score(clf, X, y, cv=outer_cv, scoring='accuracy')
    return scores


def custom_cv_split(X, y, train_size=0.8):
    """Create custom train-test split for cross-validation"""
    from sklearn.model_selection import ShuffleSplit

    cv = ShuffleSplit(n_splits=5, test_size=1-train_size, random_state=42)
    return cv


def cross_val_predict_probabilities(model, X, y):
    """Get cross-validated probability predictions"""
    from sklearn.model_selection import cross_val_predict

    y_pred_proba = cross_val_predict(model, X, y, cv=5, method='predict_proba')
    return y_pred_proba
