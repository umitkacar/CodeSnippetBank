"""
Ensemble Methods Snippets
Production-ready examples for ensemble learning
"""

from sklearn.ensemble import (VotingClassifier, VotingRegressor, BaggingClassifier,
                              AdaBoostClassifier, GradientBoostingClassifier,
                              StackingClassifier, RandomForestClassifier)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
import numpy as np


def voting_classifier_hard(X_train, y_train):
    """Create hard voting classifier (majority vote)"""
    clf1 = LogisticRegression(random_state=42)
    clf2 = RandomForestClassifier(n_estimators=50, random_state=42)
    clf3 = SVC(kernel='rbf', random_state=42)

    voting_clf = VotingClassifier(
        estimators=[('lr', clf1), ('rf', clf2), ('svc', clf3)],
        voting='hard'
    )
    voting_clf.fit(X_train, y_train)
    return voting_clf


def voting_classifier_soft(X_train, y_train):
    """Create soft voting classifier (probability averaging)"""
    clf1 = LogisticRegression(random_state=42)
    clf2 = RandomForestClassifier(n_estimators=50, random_state=42)
    clf3 = SVC(kernel='rbf', probability=True, random_state=42)

    voting_clf = VotingClassifier(
        estimators=[('lr', clf1), ('rf', clf2), ('svc', clf3)],
        voting='soft'
    )
    voting_clf.fit(X_train, y_train)
    return voting_clf


def bagging_classifier(X_train, y_train, n_estimators=100):
    """Create bagging classifier"""
    base_clf = DecisionTreeClassifier(random_state=42)
    bagging_clf = BaggingClassifier(
        base_estimator=base_clf,
        n_estimators=n_estimators,
        max_samples=0.8,
        max_features=0.8,
        random_state=42,
        n_jobs=-1
    )
    bagging_clf.fit(X_train, y_train)
    return bagging_clf


def random_forest_ensemble(X_train, y_train, n_estimators=100):
    """Create random forest (bagging with feature randomness)"""
    rf_clf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1
    )
    rf_clf.fit(X_train, y_train)
    return rf_clf


def adaboost_classifier(X_train, y_train, n_estimators=50):
    """Create AdaBoost classifier (sequential boosting)"""
    ada_clf = AdaBoostClassifier(
        base_estimator=DecisionTreeClassifier(max_depth=1),
        n_estimators=n_estimators,
        learning_rate=1.0,
        random_state=42
    )
    ada_clf.fit(X_train, y_train)
    return ada_clf


def gradient_boosting_classifier(X_train, y_train):
    """Create Gradient Boosting classifier"""
    gb_clf = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
        random_state=42
    )
    gb_clf.fit(X_train, y_train)
    return gb_clf


def xgboost_ensemble(X_train, y_train):
    """Create XGBoost ensemble"""
    from xgboost import XGBClassifier

    xgb_clf = XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    xgb_clf.fit(X_train, y_train)
    return xgb_clf


def lightgbm_ensemble(X_train, y_train):
    """Create LightGBM ensemble"""
    from lightgbm import LGBMClassifier

    lgbm_clf = LGBMClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=-1,
        num_leaves=31,
        random_state=42
    )
    lgbm_clf.fit(X_train, y_train)
    return lgbm_clf


def stacking_classifier(X_train, y_train):
    """Create stacking classifier (meta-learning)"""
    estimators = [
        ('rf', RandomForestClassifier(n_estimators=50, random_state=42)),
        ('svc', SVC(kernel='rbf', probability=True, random_state=42))
    ]

    stacking_clf = StackingClassifier(
        estimators=estimators,
        final_estimator=LogisticRegression(),
        cv=5
    )
    stacking_clf.fit(X_train, y_train)
    return stacking_clf


def stacking_with_passthrough(X_train, y_train):
    """Stacking with passthrough (original features + predictions)"""
    estimators = [
        ('rf', RandomForestClassifier(n_estimators=50, random_state=42)),
        ('gb', GradientBoostingClassifier(n_estimators=50, random_state=42))
    ]

    stacking_clf = StackingClassifier(
        estimators=estimators,
        final_estimator=LogisticRegression(),
        cv=5,
        passthrough=True
    )
    stacking_clf.fit(X_train, y_train)
    return stacking_clf


def voting_regressor(X_train, y_train):
    """Create voting regressor"""
    from sklearn.ensemble import VotingRegressor
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.ensemble import RandomForestRegressor

    reg1 = LinearRegression()
    reg2 = Ridge(alpha=1.0)
    reg3 = RandomForestRegressor(n_estimators=50, random_state=42)

    voting_reg = VotingRegressor(
        estimators=[('lr', reg1), ('ridge', reg2), ('rf', reg3)]
    )
    voting_reg.fit(X_train, y_train)
    return voting_reg


def extra_trees_ensemble(X_train, y_train, n_estimators=100):
    """Create Extra Trees ensemble (extremely randomized trees)"""
    from sklearn.ensemble import ExtraTreesClassifier

    et_clf = ExtraTreesClassifier(
        n_estimators=n_estimators,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1
    )
    et_clf.fit(X_train, y_train)
    return et_clf


def weighted_voting_classifier(X_train, y_train):
    """Create weighted voting classifier"""
    clf1 = LogisticRegression(random_state=42)
    clf2 = RandomForestClassifier(n_estimators=50, random_state=42)
    clf3 = GradientBoostingClassifier(n_estimators=50, random_state=42)

    voting_clf = VotingClassifier(
        estimators=[('lr', clf1), ('rf', clf2), ('gb', clf3)],
        voting='soft',
        weights=[1, 2, 2]
    )
    voting_clf.fit(X_train, y_train)
    return voting_clf


def custom_ensemble_averaging(models, X_test):
    """Custom ensemble with simple averaging"""
    predictions = np.array([model.predict_proba(X_test)[:, 1] for model in models])
    avg_predictions = np.mean(predictions, axis=0)
    return (avg_predictions > 0.5).astype(int)


def custom_ensemble_weighted_averaging(models, weights, X_test):
    """Custom ensemble with weighted averaging"""
    predictions = np.array([model.predict_proba(X_test)[:, 1] for model in models])
    weighted_predictions = np.average(predictions, axis=0, weights=weights)
    return (weighted_predictions > 0.5).astype(int)
