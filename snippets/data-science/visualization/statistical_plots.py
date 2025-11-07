"""
Statistical Plots Snippets
Production-ready examples for statistical visualizations
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from scipy import stats


def qq_plot(data: np.ndarray):
    """Create Q-Q plot to check normality"""
    plt.figure(figsize=(8, 6))
    stats.probplot(data, dist="norm", plot=plt)
    plt.title('Q-Q Plot')
    plt.grid(True)
    plt.show()


def probability_plot(data: np.ndarray):
    """Create probability plot"""
    plt.figure(figsize=(8, 6))
    stats.probplot(data, dist="norm", plot=plt)
    plt.title('Probability Plot')
    plt.show()


def confidence_interval_plot(means: np.ndarray, ci_lower: np.ndarray, ci_upper: np.ndarray, labels: list):
    """Plot confidence intervals"""
    plt.figure(figsize=(10, 6))
    x = np.arange(len(labels))
    plt.errorbar(x, means, yerr=[means - ci_lower, ci_upper - means],
                 fmt='o', capsize=5, capthick=2)
    plt.xticks(x, labels, rotation=45)
    plt.title('Confidence Intervals')
    plt.ylabel('Value')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def correlation_plot_with_significance(df: pd.DataFrame):
    """Plot correlation matrix with significance levels"""
    from scipy.stats import pearsonr

    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True

    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, mask=mask, annot=True, cmap='coolwarm', center=0,
                square=True, linewidths=1)
    plt.title('Correlation Matrix')
    plt.tight_layout()
    plt.show()


def residual_plot_regression(y_true: np.ndarray, y_pred: np.ndarray):
    """Create residual plot for regression"""
    residuals = y_true - y_pred

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Residual vs Predicted
    ax1.scatter(y_pred, residuals, alpha=0.5)
    ax1.axhline(y=0, color='r', linestyle='--')
    ax1.set_xlabel('Predicted Values')
    ax1.set_ylabel('Residuals')
    ax1.set_title('Residual Plot')
    ax1.grid(True)

    # Q-Q plot of residuals
    stats.probplot(residuals, dist="norm", plot=ax2)
    ax2.set_title('Q-Q Plot of Residuals')

    plt.tight_layout()
    plt.show()


def forest_plot(estimates: list, ci_lower: list, ci_upper: list, labels: list):
    """Create forest plot (meta-analysis visualization)"""
    plt.figure(figsize=(10, 8))
    y_pos = np.arange(len(labels))

    plt.errorbar(estimates, y_pos, xerr=[np.array(estimates) - np.array(ci_lower),
                                          np.array(ci_upper) - np.array(estimates)],
                 fmt='s', markersize=8, capsize=5)
    plt.axvline(x=0, color='r', linestyle='--', alpha=0.5)
    plt.yticks(y_pos, labels)
    plt.xlabel('Effect Size')
    plt.title('Forest Plot')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def bland_altman_plot(method1: np.ndarray, method2: np.ndarray):
    """Create Bland-Altman plot (agreement between methods)"""
    mean = np.mean([method1, method2], axis=0)
    diff = method1 - method2
    md = np.mean(diff)
    sd = np.std(diff, ddof=1)

    plt.figure(figsize=(10, 6))
    plt.scatter(mean, diff, alpha=0.5)
    plt.axhline(md, color='red', linestyle='-', label='Mean Difference')
    plt.axhline(md + 1.96*sd, color='red', linestyle='--', label='+1.96 SD')
    plt.axhline(md - 1.96*sd, color='red', linestyle='--', label='-1.96 SD')
    plt.xlabel('Mean of Two Methods')
    plt.ylabel('Difference')
    plt.title('Bland-Altman Plot')
    plt.legend()
    plt.grid(True)
    plt.show()


def roc_curve_plot(fpr: np.ndarray, tpr: np.ndarray, auc_score: float):
    """Create ROC curve plot"""
    plt.figure(figsize=(8, 8))
    plt.plot(fpr, tpr, linewidth=2, label=f'ROC Curve (AUC = {auc_score:.3f})')
    plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.grid(True)
    plt.show()


def precision_recall_curve_plot(precision: np.ndarray, recall: np.ndarray):
    """Create precision-recall curve"""
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, linewidth=2)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.grid(True)
    plt.show()


def learning_curve_plot(train_sizes: np.ndarray, train_scores: np.ndarray, val_scores: np.ndarray):
    """Plot learning curves"""
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)

    plt.figure(figsize=(10, 6))
    plt.plot(train_sizes, train_mean, label='Training Score', marker='o')
    plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.2)
    plt.plot(train_sizes, val_mean, label='Validation Score', marker='s')
    plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.2)
    plt.xlabel('Training Set Size')
    plt.ylabel('Score')
    plt.title('Learning Curves')
    plt.legend()
    plt.grid(True)
    plt.show()
