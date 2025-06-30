"""
Tissue ID: ML-TISSUE-002
Title: Advanced Logistic Regression Classifier
Category: ml/classification
Tags: ["logistic-regression", "classification", "machine-learning", "binary-classification", "multiclass"]
Difficulty: Intermediate
Dependencies: ["numpy>=1.24", "scikit-learn>=1.3"]
Performance: O(n*p*i) where n is samples, p is features, i is iterations
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive logistic regression tissue supporting binary and multiclass
classification with multiple solvers (gradient descent, Newton-Raphson, L-BFGS).
Features regularization (L1, L2, Elastic Net), class balancing, probability
calibration, and model interpretation tools.

Use Cases:
- Binary classification (yes/no, true/false)
- Multiclass classification
- Probability estimation
- Risk scoring
- Feature selection

Example Usage:
    # Binary classification
    classifier = LogisticClassifier()
    classifier.fit(X_train, y_train)
    predictions = classifier.predict(X_test)
    probabilities = classifier.predict_proba(X_test)
    
    # Multiclass with regularization
    classifier = LogisticClassifier(
        multi_class="multinomial",
        penalty="l2",
        C=0.1
    )
    classifier.fit(X_train, y_train)
    
    # Feature importance
    importance = classifier.get_feature_importance()
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings


class Solver(Enum):
    """Available optimization solvers"""
    GRADIENT_DESCENT = "gradient_descent"
    NEWTON = "newton"
    LBFGS = "lbfgs"
    SAG = "sag"  # Stochastic Average Gradient
    SAGA = "saga"  # SAGA (supports L1)


class Penalty(Enum):
    """Regularization penalties"""
    NONE = "none"
    L1 = "l1"
    L2 = "l2"
    ELASTIC_NET = "elasticnet"


class MultiClassStrategy(Enum):
    """Multiclass strategies"""
    OVR = "ovr"  # One-vs-Rest
    MULTINOMIAL = "multinomial"  # Softmax


@dataclass
class LogisticConfig:
    """Configuration for logistic regression"""
    penalty: str = "l2"
    C: float = 1.0  # Inverse regularization strength
    l1_ratio: float = 0.5  # For elastic net
    fit_intercept: bool = True
    max_iterations: int = 1000
    tolerance: float = 1e-4
    solver: str = "lbfgs"
    multi_class: str = "ovr"
    class_weight: Optional[Union[str, Dict]] = None
    random_state: int = 42
    warm_start: bool = False
    verbose: int = 0


@dataclass
class ClassificationMetrics:
    """Classification performance metrics"""
    accuracy: float
    precision: Dict[Any, float]
    recall: Dict[Any, float]
    f1_score: Dict[Any, float]
    auc_roc: Optional[float] = None
    confusion_matrix: Optional[np.ndarray] = None
    classification_report: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "auc_roc": self.auc_roc
        }


class LogisticClassifier:
    """
    Advanced logistic regression classifier.
    Tissue Type: FUNCTIONAL - Core ML classification functionality.
    """
    
    def __init__(self,
                 config: Optional[LogisticConfig] = None,
                 feature_names: Optional[List[str]] = None):
        """
        Initialize logistic classifier.
        
        Args:
            config: Configuration options
            feature_names: Names of features for interpretability
        """
        self.config = config or LogisticConfig()
        self.feature_names = feature_names
        
        # Model components
        self.model = None
        self.coefficients_ = None
        self.intercept_ = None
        self.classes_ = None
        self.is_fitted = False
        
        # For manual implementation
        self.weights_ = None
        self.feature_mean_ = None
        self.feature_std_ = None
        
        # Statistics
        self.n_features_ = 0
        self.n_classes_ = 0
        self.n_iter_ = 0
    
    def fit(self, X: np.ndarray, y: np.ndarray,
            sample_weights: Optional[np.ndarray] = None) -> 'LogisticClassifier':
        """
        Fit logistic regression model.
        
        Args:
            X: Training features (n_samples, n_features)
            y: Target labels (n_samples,)
            sample_weights: Optional sample weights
            
        Returns:
            Self for chaining
        """
        # Validate inputs
        X, y = self._validate_inputs(X, y)
        
        # Store dimensions
        self.n_features_ = X.shape[1]
        self.classes_ = np.unique(y)
        self.n_classes_ = len(self.classes_)
        
        # Encode labels
        y_encoded = self._encode_labels(y)
        
        # Handle class weights
        sample_weights = self._compute_sample_weights(y, sample_weights)
        
        # Preprocess features
        X_scaled = self._preprocess_features(X, fit=True)
        
        # Fit model
        try:
            self._fit_sklearn(X_scaled, y_encoded, sample_weights)
        except ImportError:
            self._fit_manual(X_scaled, y_encoded, sample_weights)
        
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels.
        
        Args:
            X: Features to predict (n_samples, n_features)
            
        Returns:
            Predicted class labels
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Get probabilities
        probas = self.predict_proba(X)
        
        # Convert to class labels
        if self.n_classes_ == 2:
            predictions = (probas[:, 1] >= 0.5).astype(int)
        else:
            predictions = np.argmax(probas, axis=1)
        
        # Decode labels
        return self.classes_[predictions]
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.
        
        Args:
            X: Features to predict (n_samples, n_features)
            
        Returns:
            Class probabilities (n_samples, n_classes)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Validate and preprocess
        X = self._validate_input(X)
        X_scaled = self._preprocess_features(X, fit=False)
        
        # Get probabilities
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X_scaled)
        else:
            return self._predict_proba_manual(X_scaled)
    
    def _validate_inputs(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Validate training inputs"""
        # Convert to numpy arrays
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y)
        
        # Check dimensions
        if X.ndim != 2:
            raise ValueError(f"X must be 2D, got {X.ndim}D")
        
        if y.ndim != 1:
            raise ValueError(f"y must be 1D, got {y.ndim}D")
        
        # Check lengths match
        if X.shape[0] != y.shape[0]:
            raise ValueError(f"X and y must have same number of samples")
        
        # Check for NaN/Inf
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ValueError("X contains NaN or Inf values")
        
        return X, y
    
    def _validate_input(self, X: np.ndarray) -> np.ndarray:
        """Validate single input"""
        X = np.asarray(X, dtype=np.float64)
        
        if X.ndim == 1:
            X = X.reshape(1, -1)
        elif X.ndim != 2:
            raise ValueError(f"X must be 1D or 2D, got {X.ndim}D")
        
        if X.shape[1] != self.n_features_:
            raise ValueError(f"X has {X.shape[1]} features, expected {self.n_features_}")
        
        return X
    
    def _encode_labels(self, y: np.ndarray) -> np.ndarray:
        """Encode labels to integers"""
        label_to_int = {label: i for i, label in enumerate(self.classes_)}
        return np.array([label_to_int[label] for label in y])
    
    def _compute_sample_weights(self, y: np.ndarray, 
                              sample_weights: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """Compute sample weights including class balancing"""
        if self.config.class_weight is None:
            return sample_weights
        
        # Calculate class weights
        if self.config.class_weight == "balanced":
            # Compute balanced weights
            unique_classes, class_counts = np.unique(y, return_counts=True)
            n_samples = len(y)
            n_classes = len(unique_classes)
            
            class_weights = {}
            for cls, count in zip(unique_classes, class_counts):
                class_weights[cls] = n_samples / (n_classes * count)
        else:
            class_weights = self.config.class_weight
        
        # Apply class weights
        weights = np.ones(len(y))
        for i, label in enumerate(y):
            if label in class_weights:
                weights[i] = class_weights[label]
        
        # Combine with sample weights
        if sample_weights is not None:
            weights *= sample_weights
        
        return weights
    
    def _preprocess_features(self, X: np.ndarray, fit: bool) -> np.ndarray:
        """Standardize features"""
        if fit:
            self.feature_mean_ = X.mean(axis=0)
            self.feature_std_ = X.std(axis=0)
            self.feature_std_[self.feature_std_ == 0] = 1
        
        return (X - self.feature_mean_) / self.feature_std_
    
    def _fit_sklearn(self, X: np.ndarray, y: np.ndarray, 
                    sample_weights: Optional[np.ndarray]):
        """Fit using scikit-learn"""
        from sklearn.linear_model import LogisticRegression
        
        # Map solver names
        solver_map = {
            "gradient_descent": "saga",
            "newton": "newton-cg",
            "lbfgs": "lbfgs",
            "sag": "sag",
            "saga": "saga"
        }
        
        solver = solver_map.get(self.config.solver, "lbfgs")
        
        # Create model
        self.model = LogisticRegression(
            penalty=self.config.penalty if self.config.penalty != "none" else None,
            C=self.config.C,
            fit_intercept=self.config.fit_intercept,
            max_iter=self.config.max_iterations,
            tol=self.config.tolerance,
            solver=solver,
            multi_class=self.config.multi_class,
            random_state=self.config.random_state,
            warm_start=self.config.warm_start,
            verbose=self.config.verbose,
            n_jobs=-1
        )
        
        # Fit model
        self.model.fit(X, y, sample_weight=sample_weights)
        
        # Extract coefficients
        if self.n_classes_ == 2:
            self.coefficients_ = self.model.coef_[0]
            self.intercept_ = self.model.intercept_[0] if self.config.fit_intercept else 0.0
        else:
            self.coefficients_ = self.model.coef_
            self.intercept_ = self.model.intercept_ if self.config.fit_intercept else np.zeros(self.n_classes_)
        
        self.n_iter_ = self.model.n_iter_
    
    def _fit_manual(self, X: np.ndarray, y: np.ndarray,
                   sample_weights: Optional[np.ndarray]):
        """Manual implementation using gradient descent"""
        n_samples, n_features = X.shape
        
        # Initialize weights
        if self.n_classes_ == 2:
            # Binary classification
            self.weights_ = np.zeros(n_features + (1 if self.config.fit_intercept else 0))
            self._fit_binary_manual(X, y, sample_weights)
        else:
            # Multiclass
            self.weights_ = np.zeros((self.n_classes_, n_features + (1 if self.config.fit_intercept else 0)))
            self._fit_multiclass_manual(X, y, sample_weights)
    
    def _fit_binary_manual(self, X: np.ndarray, y: np.ndarray,
                          sample_weights: Optional[np.ndarray]):
        """Manual binary logistic regression"""
        n_samples, n_features = X.shape
        
        # Add intercept column
        if self.config.fit_intercept:
            X = np.column_stack([np.ones(n_samples), X])
        
        # Initialize weights
        weights = self.weights_
        
        # Learning rate
        learning_rate = 0.01
        
        # Gradient descent
        for iteration in range(self.config.max_iterations):
            # Forward pass
            z = X @ weights
            y_pred = self._sigmoid(z)
            
            # Calculate gradient
            error = y_pred - y
            if sample_weights is not None:
                error *= sample_weights
            
            gradient = X.T @ error / n_samples
            
            # Add regularization
            if self.config.penalty == "l2":
                reg_term = self.config.C * weights
                if self.config.fit_intercept:
                    reg_term[0] = 0  # Don't regularize intercept
                gradient += reg_term
            
            # Update weights
            weights -= learning_rate * gradient
            
            # Check convergence
            if np.linalg.norm(gradient) < self.config.tolerance:
                self.n_iter_ = iteration + 1
                break
        else:
            self.n_iter_ = self.config.max_iterations
        
        # Store results
        self.weights_ = weights
        if self.config.fit_intercept:
            self.intercept_ = weights[0]
            self.coefficients_ = weights[1:]
        else:
            self.intercept_ = 0.0
            self.coefficients_ = weights
    
    def _fit_multiclass_manual(self, X: np.ndarray, y: np.ndarray,
                              sample_weights: Optional[np.ndarray]):
        """Manual multiclass logistic regression"""
        if self.config.multi_class == "ovr":
            # One-vs-Rest
            for class_idx in range(self.n_classes_):
                # Create binary problem
                y_binary = (y == class_idx).astype(int)
                
                # Fit binary classifier
                self.weights_ = self.weights_[class_idx]
                self._fit_binary_manual(X, y_binary, sample_weights)
                self.weights_[class_idx] = self.weights_
        else:
            # Multinomial (softmax)
            self._fit_softmax_manual(X, y, sample_weights)
    
    def _fit_softmax_manual(self, X: np.ndarray, y: np.ndarray,
                           sample_weights: Optional[np.ndarray]):
        """Manual softmax regression"""
        n_samples, n_features = X.shape
        
        # Add intercept
        if self.config.fit_intercept:
            X = np.column_stack([np.ones(n_samples), X])
        
        # One-hot encode y
        y_onehot = np.zeros((n_samples, self.n_classes_))
        y_onehot[np.arange(n_samples), y] = 1
        
        # Learning rate
        learning_rate = 0.01
        
        # Gradient descent
        for iteration in range(self.config.max_iterations):
            # Forward pass
            z = X @ self.weights_.T
            y_pred = self._softmax(z)
            
            # Calculate gradient
            error = y_pred - y_onehot
            if sample_weights is not None:
                error *= sample_weights[:, np.newaxis]
            
            gradient = error.T @ X / n_samples
            
            # Add L2 regularization
            if self.config.penalty == "l2":
                reg_term = self.config.C * self.weights_
                if self.config.fit_intercept:
                    reg_term[:, 0] = 0
                gradient += reg_term
            
            # Update weights
            self.weights_ -= learning_rate * gradient
            
            # Check convergence
            if np.linalg.norm(gradient) < self.config.tolerance:
                self.n_iter_ = iteration + 1
                break
        else:
            self.n_iter_ = self.config.max_iterations
        
        # Extract coefficients
        if self.config.fit_intercept:
            self.intercept_ = self.weights_[:, 0]
            self.coefficients_ = self.weights_[:, 1:]
        else:
            self.intercept_ = np.zeros(self.n_classes_)
            self.coefficients_ = self.weights_
    
    def _sigmoid(self, z: np.ndarray) -> np.ndarray:
        """Sigmoid activation function"""
        # Clip to prevent overflow
        z = np.clip(z, -500, 500)
        return 1 / (1 + np.exp(-z))
    
    def _softmax(self, z: np.ndarray) -> np.ndarray:
        """Softmax activation function"""
        # Subtract max for numerical stability
        z_shifted = z - np.max(z, axis=1, keepdims=True)
        exp_z = np.exp(z_shifted)
        return exp_z / np.sum(exp_z, axis=1, keepdims=True)
    
    def _predict_proba_manual(self, X: np.ndarray) -> np.ndarray:
        """Manual probability prediction"""
        n_samples = X.shape[0]
        
        # Add intercept
        if self.config.fit_intercept:
            X = np.column_stack([np.ones(n_samples), X])
        
        if self.n_classes_ == 2:
            # Binary classification
            z = X @ np.concatenate([[self.intercept_], self.coefficients_])
            prob_positive = self._sigmoid(z)
            probas = np.column_stack([1 - prob_positive, prob_positive])
        else:
            # Multiclass
            if self.config.multi_class == "ovr":
                # One-vs-Rest
                probas = np.zeros((n_samples, self.n_classes_))
                for i in range(self.n_classes_):
                    weights = np.concatenate([[self.intercept_[i]], self.coefficients_[i]])
                    z = X @ weights
                    probas[:, i] = self._sigmoid(z)
                # Normalize
                probas = probas / probas.sum(axis=1, keepdims=True)
            else:
                # Softmax
                z = X @ self.weights_.T
                probas = self._softmax(z)
        
        return probas
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> ClassificationMetrics:
        """
        Evaluate model performance.
        
        Args:
            X: Test features
            y: True labels
            
        Returns:
            Classification metrics
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before evaluation")
        
        # Make predictions
        y_pred = self.predict(X)
        y_proba = self.predict_proba(X)
        
        # Calculate metrics
        accuracy = np.mean(y_pred == y)
        
        # Per-class metrics
        precision = {}
        recall = {}
        f1_score = {}
        
        for class_label in self.classes_:
            true_positive = np.sum((y == class_label) & (y_pred == class_label))
            false_positive = np.sum((y != class_label) & (y_pred == class_label))
            false_negative = np.sum((y == class_label) & (y_pred != class_label))
            
            # Precision
            if true_positive + false_positive > 0:
                precision[class_label] = true_positive / (true_positive + false_positive)
            else:
                precision[class_label] = 0.0
            
            # Recall
            if true_positive + false_negative > 0:
                recall[class_label] = true_positive / (true_positive + false_negative)
            else:
                recall[class_label] = 0.0
            
            # F1 Score
            if precision[class_label] + recall[class_label] > 0:
                f1_score[class_label] = 2 * precision[class_label] * recall[class_label] / \
                                       (precision[class_label] + recall[class_label])
            else:
                f1_score[class_label] = 0.0
        
        # AUC-ROC for binary classification
        auc_roc = None
        if self.n_classes_ == 2:
            auc_roc = self._calculate_auc_roc(y, y_proba[:, 1])
        
        # Confusion matrix
        confusion_matrix = self._calculate_confusion_matrix(y, y_pred)
        
        return ClassificationMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            auc_roc=auc_roc,
            confusion_matrix=confusion_matrix
        )
    
    def _calculate_auc_roc(self, y_true: np.ndarray, y_scores: np.ndarray) -> float:
        """Calculate AUC-ROC score"""
        # Sort by scores
        sorted_indices = np.argsort(y_scores)[::-1]
        y_true_sorted = y_true[sorted_indices]
        
        # Calculate TPR and FPR
        tpr = []
        fpr = []
        
        n_positive = np.sum(y_true == self.classes_[1])
        n_negative = np.sum(y_true == self.classes_[0])
        
        tp = 0
        fp = 0
        
        for i in range(len(y_true_sorted)):
            if y_true_sorted[i] == self.classes_[1]:
                tp += 1
            else:
                fp += 1
            
            tpr.append(tp / n_positive if n_positive > 0 else 0)
            fpr.append(fp / n_negative if n_negative > 0 else 0)
        
        # Calculate AUC using trapezoidal rule
        auc = 0
        for i in range(1, len(fpr)):
            auc += (fpr[i] - fpr[i-1]) * (tpr[i] + tpr[i-1]) / 2
        
        return auc
    
    def _calculate_confusion_matrix(self, y_true: np.ndarray, 
                                  y_pred: np.ndarray) -> np.ndarray:
        """Calculate confusion matrix"""
        n_classes = len(self.classes_)
        matrix = np.zeros((n_classes, n_classes), dtype=int)
        
        for i, true_label in enumerate(self.classes_):
            for j, pred_label in enumerate(self.classes_):
                matrix[i, j] = np.sum((y_true == true_label) & (y_pred == pred_label))
        
        return matrix
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance based on coefficients"""
        if not self.is_fitted:
            return None
        
        # For binary classification
        if self.n_classes_ == 2:
            importance = np.abs(self.coefficients_)
        else:
            # Average absolute coefficients across classes
            importance = np.mean(np.abs(self.coefficients_), axis=0)
        
        # Normalize
        if importance.sum() > 0:
            importance = importance / importance.sum()
        
        # Create dictionary
        if self.feature_names:
            return {name: float(imp) for name, imp in zip(self.feature_names, importance)}
        else:
            return {f"feature_{i}": float(imp) for i, imp in enumerate(importance)}
    
    def get_coefficients(self) -> Dict[str, Any]:
        """Get coefficients with feature names"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        if self.n_classes_ == 2:
            # Binary classification
            if self.feature_names:
                return {name: float(coef) for name, coef in 
                       zip(self.feature_names, self.coefficients_)}
            else:
                return {f"feature_{i}": float(coef) for i, coef in 
                       enumerate(self.coefficients_)}
        else:
            # Multiclass
            result = {}
            for class_idx, class_label in enumerate(self.classes_):
                class_coefs = {}
                for feat_idx, coef in enumerate(self.coefficients_[class_idx]):
                    feat_name = self.feature_names[feat_idx] if self.feature_names else f"feature_{feat_idx}"
                    class_coefs[feat_name] = float(coef)
                result[f"class_{class_label}"] = class_coefs
            return result


# Utility functions
def logistic_regression(X: np.ndarray, y: np.ndarray,
                       penalty: str = "l2", C: float = 1.0) -> LogisticClassifier:
    """Quick logistic regression"""
    config = LogisticConfig(penalty=penalty, C=C)
    classifier = LogisticClassifier(config=config)
    classifier.fit(X, y)
    return classifier


def predict_probability(classifier: LogisticClassifier, X: np.ndarray,
                       class_label: Any = None) -> np.ndarray:
    """Get probability for specific class"""
    probas = classifier.predict_proba(X)
    
    if class_label is not None:
        # Find class index
        class_idx = np.where(classifier.classes_ == class_label)[0]
        if len(class_idx) == 0:
            raise ValueError(f"Unknown class label: {class_label}")
        return probas[:, class_idx[0]]
    
    return probas


def cross_validate_logistic(X: np.ndarray, y: np.ndarray,
                          cv_folds: int = 5) -> Dict[str, float]:
    """Cross-validate logistic regression"""
    n_samples = X.shape[0]
    fold_size = n_samples // cv_folds
    
    scores = []
    
    for i in range(cv_folds):
        # Create train/test split
        test_start = i * fold_size
        test_end = (i + 1) * fold_size if i < cv_folds - 1 else n_samples
        
        test_idx = list(range(test_start, test_end))
        train_idx = list(range(test_start)) + list(range(test_end, n_samples))
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Train and evaluate
        classifier = LogisticClassifier()
        classifier.fit(X_train, y_train)
        metrics = classifier.evaluate(X_test, y_test)
        scores.append(metrics.accuracy)
    
    return {
        "mean_accuracy": np.mean(scores),
        "std_accuracy": np.std(scores),
        "scores": scores
    }


# Auto-generated tests
def test_logistic_classifier():
    """Test logistic regression functionality"""
    # Generate synthetic binary classification data
    np.random.seed(42)
    n_samples, n_features = 200, 4
    
    # Create two Gaussian clusters
    X1 = np.random.randn(n_samples // 2, n_features) + np.array([2, 2, 2, 2])
    X2 = np.random.randn(n_samples // 2, n_features) + np.array([-2, -2, -2, -2])
    X_binary = np.vstack([X1, X2])
    y_binary = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))
    
    # Shuffle
    indices = np.random.permutation(n_samples)
    X_binary, y_binary = X_binary[indices], y_binary[indices]
    
    # Test binary classification
    classifier = LogisticClassifier()
    classifier.fit(X_binary, y_binary)
    
    assert classifier.is_fitted
    assert len(classifier.coefficients_) == n_features
    assert classifier.n_classes_ == 2
    
    # Test prediction
    predictions = classifier.predict(X_binary[:10])
    assert len(predictions) == 10
    assert all(p in [0, 1] for p in predictions)
    
    # Test probability prediction
    probas = classifier.predict_proba(X_binary[:10])
    assert probas.shape == (10, 2)
    assert np.allclose(probas.sum(axis=1), 1.0)
    
    # Test evaluation
    metrics = classifier.evaluate(X_binary, y_binary)
    assert metrics.accuracy > 0.8  # Should classify well
    assert len(metrics.precision) == 2
    assert metrics.auc_roc is not None
    
    # Test with regularization
    config = LogisticConfig(penalty="l2", C=0.1)
    classifier_reg = LogisticClassifier(config=config)
    classifier_reg.fit(X_binary, y_binary)
    assert classifier_reg.is_fitted
    
    # Test multiclass classification
    # Create 3 clusters
    X_multi = np.vstack([
        np.random.randn(50, n_features) + np.array([3, 3, 3, 3]),
        np.random.randn(50, n_features) + np.array([-3, -3, 3, 3]),
        np.random.randn(50, n_features) + np.array([0, 0, -3, -3])
    ])
    y_multi = np.array([0] * 50 + [1] * 50 + [2] * 50)
    
    # Shuffle
    indices = np.random.permutation(150)
    X_multi, y_multi = X_multi[indices], y_multi[indices]
    
    # Test multiclass
    config_multi = LogisticConfig(multi_class="multinomial")
    classifier_multi = LogisticClassifier(config=config_multi)
    classifier_multi.fit(X_multi, y_multi)
    
    assert classifier_multi.n_classes_ == 3
    predictions_multi = classifier_multi.predict(X_multi[:10])
    assert all(p in [0, 1, 2] for p in predictions_multi)
    
    # Test class balancing
    # Create imbalanced dataset
    X_imbalanced = np.vstack([X1[:10], X2])  # 10 vs 100 samples
    y_imbalanced = np.array([0] * 10 + [1] * 100)
    
    config_balanced = LogisticConfig(class_weight="balanced")
    classifier_balanced = LogisticClassifier(config=config_balanced)
    classifier_balanced.fit(X_imbalanced, y_imbalanced)
    assert classifier_balanced.is_fitted
    
    # Test feature importance
    importance = classifier.get_feature_importance()
    assert len(importance) == n_features
    assert all(0 <= v <= 1 for v in importance.values())
    assert abs(sum(importance.values()) - 1.0) < 1e-6
    
    # Test utility functions
    quick_clf = logistic_regression(X_binary, y_binary)
    assert quick_clf.is_fitted
    
    class_1_proba = predict_probability(quick_clf, X_binary[:5], class_label=1)
    assert len(class_1_proba) == 5
    
    cv_results = cross_validate_logistic(X_binary, y_binary, cv_folds=3)
    assert "mean_accuracy" in cv_results
    assert cv_results["mean_accuracy"] > 0.7
    
    print("All logistic regression tests passed!")


if __name__ == "__main__":
    test_logistic_classifier()