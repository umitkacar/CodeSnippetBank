"""
Hyperparameter Tuning Snippets
Production-ready examples for optimizing model parameters
"""

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
import numpy as np


def grid_search_cv(model, param_grid, X_train, y_train, cv=5):
    """Perform grid search with cross-validation"""
    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=cv,
        scoring='accuracy',
        n_jobs=-1,
        verbose=1
    )
    grid_search.fit(X_train, y_train)
    return grid_search.best_estimator_, grid_search.best_params_


def randomized_search_cv(model, param_distributions, X_train, y_train, n_iter=100, cv=5):
    """Perform randomized search with cross-validation"""
    random_search = RandomizedSearchCV(
        estimator=model,
        param_distributions=param_distributions,
        n_iter=n_iter,
        cv=cv,
        scoring='accuracy',
        n_jobs=-1,
        random_state=42,
        verbose=1
    )
    random_search.fit(X_train, y_train)
    return random_search.best_estimator_, random_search.best_params_


def random_forest_param_grid():
    """Define parameter grid for Random Forest"""
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2']
    }
    return param_grid


def xgboost_param_grid():
    """Define parameter grid for XGBoost"""
    param_grid = {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.01, 0.1, 0.3],
        'max_depth': [3, 5, 7],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0]
    }
    return param_grid


def logistic_regression_param_grid():
    """Define parameter grid for Logistic Regression"""
    param_grid = {
        'C': [0.001, 0.01, 0.1, 1, 10, 100],
        'penalty': ['l1', 'l2'],
        'solver': ['liblinear', 'saga']
    }
    return param_grid


def svm_param_grid():
    """Define parameter grid for SVM"""
    param_grid = {
        'C': [0.1, 1, 10, 100],
        'gamma': ['scale', 'auto', 0.001, 0.01, 0.1],
        'kernel': ['rbf', 'poly', 'sigmoid']
    }
    return param_grid


def bayesian_optimization():
    """Perform Bayesian optimization for hyperparameter tuning"""
    try:
        from skopt import BayesSearchCV
    except ImportError:
        raise ImportError("scikit-optimize not installed. Install with: pip install scikit-optimize")

    from sklearn.ensemble import RandomForestClassifier

    param_space = {
        'n_estimators': (50, 300),
        'max_depth': (5, 30),
        'min_samples_split': (2, 20),
        'min_samples_leaf': (1, 10)
    }

    bayes_search = BayesSearchCV(
        RandomForestClassifier(random_state=42),
        param_space,
        n_iter=32,
        cv=5,
        n_jobs=-1,
        random_state=42
    )
    return bayes_search


def optuna_optimization(X_train, y_train):
    """Hyperparameter optimization using Optuna"""
    try:
        import optuna
    except ImportError:
        raise ImportError("optuna not installed. Install with: pip install optuna")

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score

    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 300),
            'max_depth': trial.suggest_int('max_depth', 5, 30),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
            'random_state': 42
        }

        model = RandomForestClassifier(**params)
        score = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy').mean()
        return score

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100, show_progress_bar=False)

    return study.best_params, study.best_value


def halving_grid_search():
    """Successive Halving for faster hyperparameter search"""
    try:
        from sklearn.experimental import enable_halving_search_cv  # noqa
        from sklearn.model_selection import HalvingGridSearchCV
        from sklearn.ensemble import RandomForestClassifier
    except ImportError:
        raise ImportError("HalvingGridSearchCV requires scikit-learn >= 0.24")

    param_grid = {
        'n_estimators': [50, 100, 200, 300],
        'max_depth': [5, 10, 20, 30],
        'min_samples_split': [2, 5, 10]
    }

    halving_search = HalvingGridSearchCV(
        RandomForestClassifier(random_state=42),
        param_grid,
        factor=3,
        random_state=42,
        n_jobs=-1
    )
    return halving_search


def nested_cv_with_tuning(model, param_grid, X, y):
    """Nested cross-validation with hyperparameter tuning"""
    from sklearn.model_selection import cross_val_score, KFold

    outer_cv = KFold(n_splits=5, shuffle=True, random_state=42)
    inner_cv = KFold(n_splits=3, shuffle=True, random_state=42)

    clf = GridSearchCV(model, param_grid, cv=inner_cv, scoring='accuracy')
    nested_scores = cross_val_score(clf, X, y, cv=outer_cv, scoring='accuracy')

    return nested_scores


def multi_metric_grid_search(model, param_grid, X_train, y_train):
    """Grid search with multiple scoring metrics"""
    scoring = {
        'accuracy': 'accuracy',
        'precision': 'precision',
        'recall': 'recall',
        'f1': 'f1',
        'roc_auc': 'roc_auc'
    }

    grid_search = GridSearchCV(
        model,
        param_grid,
        cv=5,
        scoring=scoring,
        refit='f1',
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)

    return grid_search
