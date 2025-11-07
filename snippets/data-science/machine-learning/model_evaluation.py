"""
Model Evaluation Snippets
Production-ready examples for evaluating ML models
"""

from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, confusion_matrix, classification_report,
                             mean_squared_error, mean_absolute_error, r2_score,
                             roc_curve, precision_recall_curve)
import numpy as np


def evaluate_classification_model(y_true, y_pred, y_pred_proba=None):
    """Comprehensive classification model evaluation"""
    results = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='weighted'),
        'recall': recall_score(y_true, y_pred, average='weighted'),
        'f1': f1_score(y_true, y_pred, average='weighted')
    }

    if y_pred_proba is not None:
        results['roc_auc'] = roc_auc_score(y_true, y_pred_proba, multi_class='ovr')

    return results


def print_classification_report(y_true, y_pred, target_names=None):
    """Print detailed classification report"""
    report = classification_report(y_true, y_pred, target_names=target_names)
    print(report)
    return report


def calculate_confusion_matrix(y_true, y_pred):
    """Calculate confusion matrix"""
    cm = confusion_matrix(y_true, y_pred)
    return cm


def evaluate_regression_model(y_true, y_pred):
    """Comprehensive regression model evaluation"""
    results = {
        'mse': mean_squared_error(y_true, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'mae': mean_absolute_error(y_true, y_pred),
        'r2': r2_score(y_true, y_pred)
    }
    return results


def calculate_roc_curve(y_true, y_pred_proba):
    """Calculate ROC curve"""
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    return fpr, tpr, thresholds


def calculate_precision_recall_curve(y_true, y_pred_proba):
    """Calculate precision-recall curve"""
    precision, recall, thresholds = precision_recall_curve(y_true, y_pred_proba)
    return precision, recall, thresholds


def calculate_feature_importance(model, feature_names):
    """Get feature importance from tree-based models"""
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
        feature_importance = dict(zip(feature_names, importance))
        sorted_importance = dict(sorted(feature_importance.items(),
                                        key=lambda x: x[1], reverse=True))
        return sorted_importance
    return None


def cross_validation_scores(model, X, y, cv=5):
    """Get comprehensive cross-validation scores"""
    from sklearn.model_selection import cross_validate

    scoring = ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted']
    scores = cross_validate(model, X, y, cv=cv, scoring=scoring)

    results = {
        'accuracy': scores['test_accuracy'].mean(),
        'precision': scores['test_precision_weighted'].mean(),
        'recall': scores['test_recall_weighted'].mean(),
        'f1': scores['test_f1_weighted'].mean()
    }
    return results


def calculate_log_loss(y_true, y_pred_proba):
    """Calculate log loss (cross-entropy loss)"""
    from sklearn.metrics import log_loss
    return log_loss(y_true, y_pred_proba)


def calculate_cohen_kappa(y_true, y_pred):
    """Calculate Cohen's Kappa score"""
    from sklearn.metrics import cohen_kappa_score
    return cohen_kappa_score(y_true, y_pred)


def calculate_matthews_corrcoef(y_true, y_pred):
    """Calculate Matthews Correlation Coefficient"""
    from sklearn.metrics import matthews_corrcoef
    return matthews_corrcoef(y_true, y_pred)


def calculate_balanced_accuracy(y_true, y_pred):
    """Calculate balanced accuracy (useful for imbalanced datasets)"""
    from sklearn.metrics import balanced_accuracy_score
    return balanced_accuracy_score(y_true, y_pred)


def plot_confusion_matrix_heatmap(y_true, y_pred, labels=None):
    """Plot confusion matrix as heatmap"""
    import matplotlib.pyplot as plt
    import seaborn as sns

    cm = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.show()


def calculate_mape(y_true, y_pred):
    """Calculate Mean Absolute Percentage Error"""
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def calculate_adjusted_r2(y_true, y_pred, n_features):
    """Calculate adjusted R-squared"""
    n = len(y_true)
    r2 = r2_score(y_true, y_pred)
    adjusted_r2 = 1 - (1 - r2) * (n - 1) / (n - n_features - 1)
    return adjusted_r2


def residual_analysis(y_true, y_pred):
    """Perform residual analysis for regression"""
    residuals = y_true - y_pred
    results = {
        'mean_residual': np.mean(residuals),
        'std_residual': np.std(residuals),
        'min_residual': np.min(residuals),
        'max_residual': np.max(residuals)
    }
    return results


def learning_curve_evaluation(model, X, y, cv=5):
    """Evaluate model with learning curves"""
    from sklearn.model_selection import learning_curve

    train_sizes, train_scores, val_scores = learning_curve(
        model, X, y, cv=cv, n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring='accuracy'
    )

    return train_sizes, train_scores, val_scores


def validation_curve_evaluation(model, X, y, param_name, param_range, cv=5):
    """Evaluate model with validation curves"""
    from sklearn.model_selection import validation_curve

    train_scores, val_scores = validation_curve(
        model, X, y, param_name=param_name, param_range=param_range,
        cv=cv, scoring='accuracy', n_jobs=-1
    )

    return train_scores, val_scores
