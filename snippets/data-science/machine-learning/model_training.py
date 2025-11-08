"""
Model Training Snippets
Production-ready examples for training ML models
"""

from sklearn.linear_model import LogisticRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
import numpy as np


def train_logistic_regression(X_train, y_train):
    """Train logistic regression classifier"""
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train, y_train)
    return model


def train_random_forest_classifier(X_train, y_train, n_estimators=100):
    """Train random forest classifier"""
    model = RandomForestClassifier(n_estimators=n_estimators, random_state=42,
                                    n_jobs=-1)
    model.fit(X_train, y_train)
    return model


def train_random_forest_regressor(X_train, y_train, n_estimators=100):
    """Train random forest regressor"""
    model = RandomForestRegressor(n_estimators=n_estimators, random_state=42,
                                   n_jobs=-1)
    model.fit(X_train, y_train)
    return model


def train_gradient_boosting(X_train, y_train):
    """Train gradient boosting classifier"""
    model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1,
                                        random_state=42)
    model.fit(X_train, y_train)
    return model


def train_xgboost_classifier(X_train, y_train):
    """Train XGBoost classifier"""
    try:
        from xgboost import XGBClassifier
    except ImportError:
        raise ImportError("xgboost not installed. Install with: pip install xgboost")

    model = XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)
    return model


def train_xgboost_regressor(X_train, y_train):
    """Train XGBoost regressor"""
    try:
        from xgboost import XGBRegressor
    except ImportError:
        raise ImportError("xgboost not installed. Install with: pip install xgboost")

    model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)
    return model


def train_lightgbm_classifier(X_train, y_train):
    """Train LightGBM classifier"""
    try:
        from lightgbm import LGBMClassifier
    except ImportError:
        raise ImportError("lightgbm not installed. Install with: pip install lightgbm")

    model = LGBMClassifier(n_estimators=100, learning_rate=0.1, random_state=42, verbose=-1)
    model.fit(X_train, y_train)
    return model


def train_svm_classifier(X_train, y_train, kernel='rbf'):
    """Train SVM classifier"""
    model = SVC(kernel=kernel, random_state=42)
    model.fit(X_train, y_train)
    return model


def train_knn_classifier(X_train, y_train, n_neighbors=5):
    """Train K-Nearest Neighbors classifier"""
    model = KNeighborsClassifier(n_neighbors=n_neighbors)
    model.fit(X_train, y_train)
    return model


def train_decision_tree(X_train, y_train, max_depth=None):
    """Train decision tree classifier"""
    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(X_train, y_train)
    return model


def train_naive_bayes(X_train, y_train):
    """Train Naive Bayes classifier"""
    model = GaussianNB()
    model.fit(X_train, y_train)
    return model


def train_ridge_regression(X_train, y_train, alpha=1.0):
    """Train Ridge regression (L2 regularization)"""
    model = Ridge(alpha=alpha)
    model.fit(X_train, y_train)
    return model


def train_lasso_regression(X_train, y_train, alpha=1.0):
    """Train Lasso regression (L1 regularization)"""
    model = Lasso(alpha=alpha)
    model.fit(X_train, y_train)
    return model


def train_elastic_net(X_train, y_train, alpha=1.0, l1_ratio=0.5):
    """Train Elastic Net (L1 + L2 regularization)"""
    model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio)
    model.fit(X_train, y_train)
    return model


def train_with_early_stopping(X_train, y_train, X_val, y_val):
    """Train XGBoost with early stopping"""
    from xgboost import XGBClassifier

    model = XGBClassifier(n_estimators=1000, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train,
              eval_set=[(X_val, y_val)],
              early_stopping_rounds=10,
              verbose=False)
    return model


def train_with_sample_weights(X_train, y_train, sample_weights):
    """Train model with sample weights"""
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train, sample_weight=sample_weights)
    return model


def train_with_class_weights(X_train, y_train):
    """Train model with class weights for imbalanced data"""
    model = LogisticRegression(class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    return model


def train_neural_network_sklearn(X_train, y_train):
    """Train neural network using scikit-learn MLPClassifier"""
    from sklearn.neural_network import MLPClassifier

    model = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500,
                          random_state=42)
    model.fit(X_train, y_train)
    return model


def train_catboost_classifier(X_train, y_train):
    """Train CatBoost classifier"""
    try:
        from catboost import CatBoostClassifier
    except ImportError:
        raise ImportError("catboost not installed. Install with: pip install catboost")

    model = CatBoostClassifier(iterations=100, learning_rate=0.1,
                                random_state=42, verbose=False)
    model.fit(X_train, y_train)
    return model
