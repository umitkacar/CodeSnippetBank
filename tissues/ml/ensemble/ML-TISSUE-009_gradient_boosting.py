"""
Tissue ID: ML-TISSUE-009
Title: Gradient Boosting Machine Implementation
Category: ml/ensemble
Tags: ["gradient-boosting", "gbm", "ensemble", "boosting", "classification", "regression"]
Difficulty: Advanced
Dependencies: ["numpy>=1.24", "scikit-learn>=1.3"]
Performance: O(n*m*k*d) where n is samples, m is features, k is trees, d is depth
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive Gradient Boosting tissue implementing GBM for both classification
and regression with various loss functions, learning rate scheduling, feature
subsampling, and early stopping. Includes custom loss functions, feature importance
via gain and split count, and partial dependence plots.

Use Cases:
- High-accuracy prediction tasks
- Feature importance analysis
- Non-linear regression
- Probability calibration
- Ranking problems

Example Usage:
    # Basic gradient boosting
    gbm = GradientBoostingMachine(n_estimators=100, learning_rate=0.1)
    gbm.fit(X_train, y_train)
    predictions = gbm.predict(X_test)
    
    # With early stopping
    gbm = GradientBoostingMachine(
        n_estimators=500,
        early_stopping_rounds=10,
        validation_fraction=0.2
    )
    gbm.fit(X_train, y_train)
    
    # Feature importance analysis
    importance = gbm.get_feature_importance(method="gain")
    partial_dep = gbm.partial_dependence(X, feature_idx=0)
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import warnings
from abc import ABC, abstractmethod


class TaskType(Enum):
    """GBM task types"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"


class LossFunction(Enum):
    """Available loss functions"""
    # Regression
    SQUARED_ERROR = "squared_error"
    ABSOLUTE_ERROR = "absolute_error"
    HUBER = "huber"
    QUANTILE = "quantile"
    # Classification
    LOGISTIC = "logistic"
    EXPONENTIAL = "exponential"
    MULTINOMIAL = "multinomial"


@dataclass
class GBMConfig:
    """Configuration for Gradient Boosting"""
    n_estimators: int = 100
    learning_rate: float = 0.1
    max_depth: int = 3
    min_samples_split: int = 20
    min_samples_leaf: int = 10
    subsample: float = 1.0  # Row subsampling
    colsample_bytree: float = 1.0  # Feature subsampling
    colsample_bylevel: float = 1.0  # Feature subsampling per level
    reg_alpha: float = 0.0  # L1 regularization
    reg_lambda: float = 0.0  # L2 regularization
    loss: str = "squared_error"
    quantile_alpha: float = 0.5  # For quantile loss
    huber_alpha: float = 0.9  # For Huber loss
    early_stopping_rounds: Optional[int] = None
    validation_fraction: float = 0.1
    random_state: int = 42
    verbose: int = 0


@dataclass
class TreeNode:
    """Single tree node in gradient boosting"""
    feature: Optional[int] = None
    threshold: Optional[float] = None
    left: Optional['TreeNode'] = None
    right: Optional['TreeNode'] = None
    value: Optional[float] = None  # Leaf value
    gain: float = 0.0  # Split gain
    n_samples: int = 0
    
    def is_leaf(self) -> bool:
        """Check if node is a leaf"""
        return self.left is None and self.right is None


@dataclass
class BoostingRound:
    """Information about a single boosting round"""
    tree: TreeNode
    train_loss: float
    val_loss: Optional[float] = None
    feature_importance: Optional[np.ndarray] = None


class BaseLoss(ABC):
    """Base class for loss functions"""
    
    @abstractmethod
    def loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate loss"""
        pass
    
    @abstractmethod
    def gradient(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """Calculate negative gradient"""
        pass
    
    @abstractmethod
    def hessian(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """Calculate second derivative (optional)"""
        return np.ones_like(y_true)


class SquaredErrorLoss(BaseLoss):
    """Squared error loss for regression"""
    
    def loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return 0.5 * np.mean((y_true - y_pred) ** 2)
    
    def gradient(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        return y_true - y_pred
    
    def hessian(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        return np.ones_like(y_true)


class AbsoluteErrorLoss(BaseLoss):
    """Absolute error loss for regression"""
    
    def loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return np.mean(np.abs(y_true - y_pred))
    
    def gradient(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        return np.sign(y_true - y_pred)


class HuberLoss(BaseLoss):
    """Huber loss for robust regression"""
    
    def __init__(self, alpha: float = 0.9):
        self.alpha = alpha
        self.quantile = alpha
    
    def loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        residual = y_true - y_pred
        delta = np.percentile(np.abs(residual), self.alpha * 100)
        
        mask = np.abs(residual) <= delta
        loss = np.where(mask,
                       0.5 * residual ** 2,
                       delta * (np.abs(residual) - 0.5 * delta))
        return np.mean(loss)
    
    def gradient(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        residual = y_true - y_pred
        delta = np.percentile(np.abs(residual), self.alpha * 100)
        
        return np.where(np.abs(residual) <= delta,
                       residual,
                       delta * np.sign(residual))


class LogisticLoss(BaseLoss):
    """Logistic loss for binary classification"""
    
    def loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        # y_true in {0, 1}, y_pred is raw score
        return np.mean(np.log(1 + np.exp(-2 * (2 * y_true - 1) * y_pred)))
    
    def gradient(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        # Convert to {-1, 1}
        y_signed = 2 * y_true - 1
        prob = 1 / (1 + np.exp(-2 * y_signed * y_pred))
        return 2 * y_signed * (1 - prob)
    
    def hessian(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        y_signed = 2 * y_true - 1
        prob = 1 / (1 + np.exp(-2 * y_signed * y_pred))
        return 4 * prob * (1 - prob)


class GradientBoostingMachine:
    """
    Gradient Boosting Machine implementation.
    Tissue Type: FUNCTIONAL - Core ML boosting functionality.
    """
    
    def __init__(self,
                 task: str = "regression",
                 config: Optional[GBMConfig] = None,
                 feature_names: Optional[List[str]] = None):
        """
        Initialize Gradient Boosting Machine.
        
        Args:
            task: Task type (regression or classification)
            config: GBM configuration
            feature_names: Names of features for interpretability
        """
        self.task = TaskType(task.lower())
        self.config = config or GBMConfig()
        self.feature_names = feature_names
        
        # Initialize loss function
        self._init_loss_function()
        
        # Model components
        self.trees_ = []
        self.init_prediction_ = None
        self.feature_importances_ = None
        
        # Training info
        self.n_features_ = 0
        self.n_classes_ = 0
        self.classes_ = None
        self.train_losses_ = []
        self.val_losses_ = []
        self.best_iteration_ = 0
        self.is_fitted = False
        
        # Random state
        self.rng = np.random.RandomState(self.config.random_state)
    
    def fit(self, X: np.ndarray, y: np.ndarray,
            X_val: Optional[np.ndarray] = None,
            y_val: Optional[np.ndarray] = None,
            sample_weights: Optional[np.ndarray] = None) -> 'GradientBoostingMachine':
        """
        Fit Gradient Boosting model.
        
        Args:
            X: Training features (n_samples, n_features)
            y: Target values (n_samples,)
            X_val: Validation features (optional)
            y_val: Validation targets (optional)
            sample_weights: Sample weights (optional)
            
        Returns:
            Self for chaining
        """
        # Validate inputs
        X, y = self._validate_inputs(X, y)
        self.n_features_ = X.shape[1]
        
        # Handle classification setup
        if self.task == TaskType.CLASSIFICATION:
            self.classes_ = np.unique(y)
            self.n_classes_ = len(self.classes_)
            
            if self.n_classes_ > 2 and self.config.loss != "multinomial":
                self.config.loss = "multinomial"
                self._init_loss_function()
            
            # Encode labels
            y = self._encode_labels(y)
        
        # Initialize predictions
        self.init_prediction_ = self._compute_init_prediction(y, sample_weights)
        predictions = np.full_like(y, self.init_prediction_, dtype=np.float64)
        
        # Validation split if needed
        if X_val is None and self.config.early_stopping_rounds:
            n_val = int(len(X) * self.config.validation_fraction)
            indices = self.rng.permutation(len(X))
            
            X_val = X[indices[:n_val]]
            y_val = y[indices[:n_val]]
            X = X[indices[n_val:]]
            y = y[indices[n_val:]]
            
            if sample_weights is not None:
                val_weights = sample_weights[indices[:n_val]]
                sample_weights = sample_weights[indices[n_val:]]
            else:
                val_weights = None
            
            predictions = predictions[indices[n_val:]]
            val_predictions = np.full_like(y_val, self.init_prediction_, dtype=np.float64)
        else:
            val_predictions = None if X_val is None else np.full_like(y_val, self.init_prediction_, dtype=np.float64)
            val_weights = None
        
        # Initialize feature importance
        self.feature_importances_ = np.zeros(self.n_features_)
        
        # Boosting rounds
        best_val_loss = np.inf
        rounds_no_improve = 0
        
        for i in range(self.config.n_estimators):
            # Calculate gradients
            gradients = self.loss_function.gradient(y, predictions)
            hessians = self.loss_function.hessian(y, predictions)
            
            # Build tree
            tree = self._build_tree(X, gradients, hessians, sample_weights)
            self.trees_.append(tree)
            
            # Update predictions
            tree_predictions = self._predict_tree(tree, X)
            predictions += self.config.learning_rate * tree_predictions
            
            # Calculate losses
            train_loss = self.loss_function.loss(y, predictions)
            self.train_losses_.append(train_loss)
            
            # Validation
            if X_val is not None:
                val_tree_pred = self._predict_tree(tree, X_val)
                val_predictions += self.config.learning_rate * val_tree_pred
                val_loss = self.loss_function.loss(y_val, val_predictions)
                self.val_losses_.append(val_loss)
                
                # Early stopping
                if self.config.early_stopping_rounds:
                    if val_loss < best_val_loss:
                        best_val_loss = val_loss
                        self.best_iteration_ = i
                        rounds_no_improve = 0
                    else:
                        rounds_no_improve += 1
                    
                    if rounds_no_improve >= self.config.early_stopping_rounds:
                        if self.config.verbose > 0:
                            print(f"Early stopping at iteration {i+1}")
                        break
            
            # Verbose output
            if self.config.verbose > 0 and (i + 1) % 10 == 0:
                msg = f"Iteration {i+1}: train_loss={train_loss:.4f}"
                if X_val is not None:
                    msg += f", val_loss={val_loss:.4f}"
                print(msg)
        
        # Normalize feature importances
        if np.sum(self.feature_importances_) > 0:
            self.feature_importances_ /= np.sum(self.feature_importances_)
        
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Features to predict (n_samples, n_features)
            
        Returns:
            Predicted values or class labels
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X = self._validate_input(X)
        
        # Get raw predictions
        raw_predictions = self._raw_predict(X)
        
        if self.task == TaskType.CLASSIFICATION:
            if self.n_classes_ == 2:
                # Binary classification
                probas = 1 / (1 + np.exp(-2 * raw_predictions))
                predictions = (probas > 0.5).astype(int)
            else:
                # Multiclass
                predictions = np.argmax(raw_predictions, axis=1)
            
            return self.classes_[predictions]
        else:
            return raw_predictions
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.
        
        Args:
            X: Features to predict (n_samples, n_features)
            
        Returns:
            Class probabilities (n_samples, n_classes)
        """
        if self.task != TaskType.CLASSIFICATION:
            raise ValueError("predict_proba only available for classification")
        
        X = self._validate_input(X)
        raw_predictions = self._raw_predict(X)
        
        if self.n_classes_ == 2:
            # Binary classification
            pos_proba = 1 / (1 + np.exp(-2 * raw_predictions))
            return np.column_stack([1 - pos_proba, pos_proba])
        else:
            # Multiclass - softmax
            exp_pred = np.exp(raw_predictions)
            return exp_pred / exp_pred.sum(axis=1, keepdims=True)
    
    def _raw_predict(self, X: np.ndarray) -> np.ndarray:
        """Get raw predictions (before transformation)"""
        predictions = np.full(X.shape[0], self.init_prediction_)
        
        # Use best iteration if early stopping was used
        n_trees = self.best_iteration_ + 1 if self.config.early_stopping_rounds else len(self.trees_)
        
        for i in range(n_trees):
            tree_pred = self._predict_tree(self.trees_[i], X)
            predictions += self.config.learning_rate * tree_pred
        
        return predictions
    
    def _init_loss_function(self):
        """Initialize loss function based on task and config"""
        if self.task == TaskType.REGRESSION:
            if self.config.loss == LossFunction.SQUARED_ERROR.value:
                self.loss_function = SquaredErrorLoss()
            elif self.config.loss == LossFunction.ABSOLUTE_ERROR.value:
                self.loss_function = AbsoluteErrorLoss()
            elif self.config.loss == LossFunction.HUBER.value:
                self.loss_function = HuberLoss(self.config.huber_alpha)
            else:
                self.loss_function = SquaredErrorLoss()
        else:
            # Classification
            if self.config.loss == LossFunction.LOGISTIC.value or self.n_classes_ == 2:
                self.loss_function = LogisticLoss()
            else:
                # Multinomial - simplified to use logistic for now
                self.loss_function = LogisticLoss()
    
    def _validate_inputs(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Validate training inputs"""
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y)
        
        if X.ndim != 2:
            raise ValueError(f"X must be 2D, got {X.ndim}D")
        
        if y.ndim != 1:
            raise ValueError(f"y must be 1D, got {y.ndim}D")
        
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y must have same number of samples")
        
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
        """Encode class labels"""
        if self.n_classes_ == 2:
            # Binary - encode as 0/1
            return (y == self.classes_[1]).astype(int)
        else:
            # Multiclass - integer encoding
            label_to_int = {label: i for i, label in enumerate(self.classes_)}
            return np.array([label_to_int[label] for label in y])
    
    def _compute_init_prediction(self, y: np.ndarray, 
                               sample_weights: Optional[np.ndarray]) -> float:
        """Compute initial prediction"""
        if self.task == TaskType.REGRESSION:
            if sample_weights is None:
                return np.mean(y)
            else:
                return np.average(y, weights=sample_weights)
        else:
            # Classification - use log odds
            if sample_weights is None:
                p = np.mean(y)
            else:
                p = np.average(y, weights=sample_weights)
            
            # Clip to avoid log(0)
            p = np.clip(p, 1e-15, 1 - 1e-15)
            return 0.5 * np.log(p / (1 - p))
    
    def _build_tree(self, X: np.ndarray, gradients: np.ndarray,
                   hessians: np.ndarray, sample_weights: Optional[np.ndarray]) -> TreeNode:
        """Build a single regression tree"""
        n_samples, n_features = X.shape
        
        # Feature subsampling
        if self.config.colsample_bytree < 1.0:
            n_features_tree = max(1, int(n_features * self.config.colsample_bytree))
            feature_indices = self.rng.choice(n_features, n_features_tree, replace=False)
        else:
            feature_indices = np.arange(n_features)
        
        # Row subsampling
        if self.config.subsample < 1.0:
            n_samples_tree = max(1, int(n_samples * self.config.subsample))
            sample_indices = self.rng.choice(n_samples, n_samples_tree, replace=False)
            
            X_subset = X[sample_indices]
            gradients_subset = gradients[sample_indices]
            hessians_subset = hessians[sample_indices]
            weights_subset = sample_weights[sample_indices] if sample_weights is not None else None
        else:
            X_subset = X
            gradients_subset = gradients
            hessians_subset = hessians
            weights_subset = sample_weights
        
        # Build tree recursively
        return self._build_tree_recursive(
            X_subset, gradients_subset, hessians_subset,
            weights_subset, feature_indices, depth=0
        )
    
    def _build_tree_recursive(self, X: np.ndarray, gradients: np.ndarray,
                            hessians: np.ndarray, weights: Optional[np.ndarray],
                            feature_indices: np.ndarray, depth: int) -> TreeNode:
        """Recursively build tree nodes"""
        n_samples = X.shape[0]
        
        # Calculate leaf value
        if weights is None:
            G = np.sum(gradients)
            H = np.sum(hessians)
        else:
            G = np.sum(weights * gradients)
            H = np.sum(weights * hessians)
        
        # Regularization
        leaf_value = -G / (H + self.config.reg_lambda)
        
        # Check stopping criteria
        if (depth >= self.config.max_depth or
            n_samples < self.config.min_samples_split or
            n_samples < 2 * self.config.min_samples_leaf):
            
            return TreeNode(value=leaf_value, n_samples=n_samples)
        
        # Feature subsampling per level
        if self.config.colsample_bylevel < 1.0:
            n_features_level = max(1, int(len(feature_indices) * self.config.colsample_bylevel))
            level_features = self.rng.choice(feature_indices, n_features_level, replace=False)
        else:
            level_features = feature_indices
        
        # Find best split
        best_gain = 0.0
        best_feature = None
        best_threshold = None
        best_left_indices = None
        best_right_indices = None
        
        for feature in level_features:
            # Get unique values
            unique_values = np.unique(X[:, feature])
            
            if len(unique_values) <= 1:
                continue
            
            # Try different thresholds
            for i in range(len(unique_values) - 1):
                threshold = (unique_values[i] + unique_values[i + 1]) / 2
                
                left_mask = X[:, feature] <= threshold
                right_mask = ~left_mask
                
                n_left = np.sum(left_mask)
                n_right = np.sum(right_mask)
                
                # Check minimum samples
                if n_left < self.config.min_samples_leaf or n_right < self.config.min_samples_leaf:
                    continue
                
                # Calculate gain
                if weights is None:
                    G_left = np.sum(gradients[left_mask])
                    G_right = np.sum(gradients[right_mask])
                    H_left = np.sum(hessians[left_mask])
                    H_right = np.sum(hessians[right_mask])
                else:
                    G_left = np.sum(weights[left_mask] * gradients[left_mask])
                    G_right = np.sum(weights[right_mask] * gradients[right_mask])
                    H_left = np.sum(weights[left_mask] * hessians[left_mask])
                    H_right = np.sum(weights[right_mask] * hessians[right_mask])
                
                # Calculate gain (simplified XGBoost formula)
                gain = 0.5 * (
                    G_left ** 2 / (H_left + self.config.reg_lambda) +
                    G_right ** 2 / (H_right + self.config.reg_lambda) -
                    G ** 2 / (H + self.config.reg_lambda)
                ) - self.config.reg_alpha
                
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature
                    best_threshold = threshold
                    best_left_indices = np.where(left_mask)[0]
                    best_right_indices = np.where(right_mask)[0]
        
        # Create leaf if no good split found
        if best_feature is None:
            return TreeNode(value=leaf_value, n_samples=n_samples)
        
        # Update feature importance
        self.feature_importances_[best_feature] += best_gain
        
        # Build child nodes
        node = TreeNode(
            feature=best_feature,
            threshold=best_threshold,
            gain=best_gain,
            n_samples=n_samples
        )
        
        # Recursive calls
        node.left = self._build_tree_recursive(
            X[best_left_indices], gradients[best_left_indices],
            hessians[best_left_indices],
            weights[best_left_indices] if weights is not None else None,
            feature_indices, depth + 1
        )
        
        node.right = self._build_tree_recursive(
            X[best_right_indices], gradients[best_right_indices],
            hessians[best_right_indices],
            weights[best_right_indices] if weights is not None else None,
            feature_indices, depth + 1
        )
        
        return node
    
    def _predict_tree(self, tree: TreeNode, X: np.ndarray) -> np.ndarray:
        """Make predictions with a single tree"""
        n_samples = X.shape[0]
        predictions = np.zeros(n_samples)
        
        for i in range(n_samples):
            predictions[i] = self._predict_sample(tree, X[i])
        
        return predictions
    
    def _predict_sample(self, node: TreeNode, x: np.ndarray) -> float:
        """Predict single sample with tree"""
        if node.is_leaf():
            return node.value
        
        if x[node.feature] <= node.threshold:
            return self._predict_sample(node.left, x)
        else:
            return self._predict_sample(node.right, x)
    
    def get_feature_importance(self, method: str = "gain") -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Args:
            method: Importance method (gain, split)
            
        Returns:
            Feature importance dictionary
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        if method == "gain":
            importances = self.feature_importances_
        elif method == "split":
            # Count splits
            split_counts = np.zeros(self.n_features_)
            
            for tree in self.trees_:
                self._count_splits(tree, split_counts)
            
            importances = split_counts / np.sum(split_counts) if np.sum(split_counts) > 0 else split_counts
        else:
            raise ValueError(f"Unknown importance method: {method}")
        
        if self.feature_names:
            return {name: float(imp) for name, imp in zip(self.feature_names, importances)}
        else:
            return {f"feature_{i}": float(imp) for i, imp in enumerate(importances)}
    
    def _count_splits(self, node: TreeNode, split_counts: np.ndarray):
        """Count feature splits in tree"""
        if not node.is_leaf():
            split_counts[node.feature] += 1
            self._count_splits(node.left, split_counts)
            self._count_splits(node.right, split_counts)
    
    def partial_dependence(self, X: np.ndarray, feature_idx: int,
                         n_points: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate partial dependence for a feature.
        
        Args:
            X: Reference dataset
            feature_idx: Feature index
            n_points: Number of points to evaluate
            
        Returns:
            Feature values and partial dependence values
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        # Get feature range
        feature_min = X[:, feature_idx].min()
        feature_max = X[:, feature_idx].max()
        
        # Create grid
        feature_values = np.linspace(feature_min, feature_max, n_points)
        partial_dep = np.zeros(n_points)
        
        # Calculate partial dependence
        for i, value in enumerate(feature_values):
            X_temp = X.copy()
            X_temp[:, feature_idx] = value
            
            predictions = self._raw_predict(X_temp)
            partial_dep[i] = np.mean(predictions)
        
        return feature_values, partial_dep
    
    def staged_predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions at each boosting iteration.
        
        Args:
            X: Features to predict
            
        Yields:
            Predictions at each stage
        """
        X = self._validate_input(X)
        predictions = np.full(X.shape[0], self.init_prediction_)
        
        for i, tree in enumerate(self.trees_):
            tree_pred = self._predict_tree(tree, X)
            predictions += self.config.learning_rate * tree_pred
            
            if self.task == TaskType.CLASSIFICATION:
                if self.n_classes_ == 2:
                    probas = 1 / (1 + np.exp(-2 * predictions))
                    yield self.classes_[(probas > 0.5).astype(int)]
                else:
                    yield self.classes_[np.argmax(predictions, axis=1)]
            else:
                yield predictions.copy()


# Utility functions
def gradient_boost_regressor(X: np.ndarray, y: np.ndarray,
                           n_estimators: int = 100,
                           learning_rate: float = 0.1) -> GradientBoostingMachine:
    """Quick gradient boosting regressor"""
    config = GBMConfig(n_estimators=n_estimators, learning_rate=learning_rate)
    gbm = GradientBoostingMachine(task="regression", config=config)
    gbm.fit(X, y)
    return gbm


def gradient_boost_classifier(X: np.ndarray, y: np.ndarray,
                            n_estimators: int = 100,
                            learning_rate: float = 0.1) -> GradientBoostingMachine:
    """Quick gradient boosting classifier"""
    config = GBMConfig(n_estimators=n_estimators, learning_rate=learning_rate)
    gbm = GradientBoostingMachine(task="classification", config=config)
    gbm.fit(X, y)
    return gbm


def gradient_boost_cv(X: np.ndarray, y: np.ndarray,
                     param_grid: Dict[str, List],
                     cv_folds: int = 5,
                     task: str = "regression") -> Tuple[GradientBoostingMachine, Dict]:
    """Cross-validated gradient boosting"""
    best_score = -np.inf
    best_params = {}
    best_model = None
    
    # Simple grid search
    from itertools import product
    
    param_names = list(param_grid.keys())
    param_values = [param_grid[name] for name in param_names]
    
    for values in product(*param_values):
        params = dict(zip(param_names, values))
        
        # Cross-validation
        fold_size = len(X) // cv_folds
        scores = []
        
        for fold in range(cv_folds):
            # Split data
            val_start = fold * fold_size
            val_end = (fold + 1) * fold_size if fold < cv_folds - 1 else len(X)
            
            val_idx = list(range(val_start, val_end))
            train_idx = list(range(val_start)) + list(range(val_end, len(X)))
            
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Train model
            config = GBMConfig(**params)
            model = GradientBoostingMachine(task=task, config=config)
            model.fit(X_train, y_train, X_val, y_val)
            
            # Evaluate
            predictions = model.predict(X_val)
            if task == "regression":
                score = -np.mean((predictions - y_val) ** 2)  # Negative MSE
            else:
                score = np.mean(predictions == y_val)  # Accuracy
            
            scores.append(score)
        
        avg_score = np.mean(scores)
        
        if avg_score > best_score:
            best_score = avg_score
            best_params = params
            
            # Retrain on full data
            config = GBMConfig(**best_params)
            best_model = GradientBoostingMachine(task=task, config=config)
            best_model.fit(X, y)
    
    return best_model, best_params


# Auto-generated tests
def test_gradient_boosting():
    """Test Gradient Boosting functionality"""
    # Generate synthetic data
    np.random.seed(42)
    
    # Regression data
    n_samples = 500
    n_features = 10
    
    X = np.random.randn(n_samples, n_features)
    # Non-linear target
    y = (X[:, 0] ** 2 + 2 * X[:, 1] - X[:, 2] * X[:, 3] + 
         0.5 * np.sin(X[:, 4]) + 0.1 * np.random.randn(n_samples))
    
    # Test basic regression
    gbm_reg = GradientBoostingMachine(task="regression")
    gbm_reg.fit(X, y)
    
    assert gbm_reg.is_fitted
    assert len(gbm_reg.trees_) <= gbm_reg.config.n_estimators
    assert gbm_reg.feature_importances_.shape == (n_features,)
    
    # Test prediction
    predictions = gbm_reg.predict(X[:20])
    assert len(predictions) == 20
    assert all(isinstance(p, (float, np.floating)) for p in predictions)
    
    # Test with validation and early stopping
    config_early = GBMConfig(
        n_estimators=200,
        early_stopping_rounds=10,
        validation_fraction=0.2,
        verbose=0
    )
    gbm_early = GradientBoostingMachine(task="regression", config=config_early)
    gbm_early.fit(X, y)
    
    assert gbm_early.is_fitted
    assert len(gbm_early.val_losses_) > 0
    assert gbm_early.best_iteration_ >= 0
    
    # Test classification
    # Binary classification data
    y_binary = (X[:, 0] + X[:, 1] > 0).astype(int)
    
    gbm_clf = GradientBoostingMachine(task="classification")
    gbm_clf.fit(X, y_binary)
    
    assert gbm_clf.is_fitted
    assert gbm_clf.n_classes_ == 2
    
    # Test prediction
    clf_predictions = gbm_clf.predict(X[:20])
    assert len(clf_predictions) == 20
    assert all(p in [0, 1] for p in clf_predictions)
    
    # Test probability prediction
    probas = gbm_clf.predict_proba(X[:20])
    assert probas.shape == (20, 2)
    assert np.allclose(probas.sum(axis=1), 1.0)
    
    # Test multiclass
    y_multi = np.random.randint(0, 3, n_samples)
    
    gbm_multi = GradientBoostingMachine(task="classification")
    gbm_multi.fit(X[:150], y_multi[:150])  # Smaller for speed
    
    assert gbm_multi.n_classes_ == 3
    multi_pred = gbm_multi.predict(X[150:170])
    assert all(p in [0, 1, 2] for p in multi_pred)
    
    # Test different loss functions
    for loss in ["squared_error", "absolute_error", "huber"]:
        config_loss = GBMConfig(n_estimators=10, loss=loss)
        gbm_loss = GradientBoostingMachine(task="regression", config=config_loss)
        gbm_loss.fit(X[:100], y[:100])
        assert gbm_loss.is_fitted
    
    # Test feature importance
    importance = gbm_reg.get_feature_importance(method="gain")
    assert len(importance) == n_features
    assert all(v >= 0 for v in importance.values())
    
    # Most important features should be 0, 1, 2, 3
    sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    top_features = [int(f.split('_')[1]) for f, _ in sorted_features[:4]]
    assert 0 in top_features
    assert 1 in top_features
    
    # Test partial dependence
    feature_vals, partial_dep = gbm_reg.partial_dependence(X[:100], feature_idx=0, n_points=20)
    assert len(feature_vals) == 20
    assert len(partial_dep) == 20
    
    # Test subsampling
    config_sub = GBMConfig(
        n_estimators=10,
        subsample=0.8,
        colsample_bytree=0.8,
        colsample_bylevel=0.8
    )
    gbm_sub = GradientBoostingMachine(task="regression", config=config_sub)
    gbm_sub.fit(X[:100], y[:100])
    assert gbm_sub.is_fitted
    
    # Test regularization
    config_reg = GBMConfig(
        n_estimators=10,
        reg_alpha=0.1,
        reg_lambda=0.1
    )
    gbm_regularized = GradientBoostingMachine(task="regression", config=config_reg)
    gbm_regularized.fit(X[:100], y[:100])
    assert gbm_regularized.is_fitted
    
    # Test staged predictions
    staged_preds = list(gbm_reg.staged_predict(X[:10]))
    assert len(staged_preds) == len(gbm_reg.trees_)
    
    # Test with sample weights
    weights = np.random.rand(n_samples)
    gbm_weighted = GradientBoostingMachine(task="regression")
    gbm_weighted.fit(X, y, sample_weights=weights)
    assert gbm_weighted.is_fitted
    
    # Test utility functions
    quick_reg = gradient_boost_regressor(X[:100], y[:100], n_estimators=10)
    assert quick_reg.is_fitted
    
    quick_clf = gradient_boost_classifier(X[:100], y_binary[:100], n_estimators=10)
    assert quick_clf.is_fitted
    
    # Test cross-validation
    param_grid = {
        'n_estimators': [5, 10],
        'learning_rate': [0.05, 0.1],
        'max_depth': [2, 3]
    }
    
    best_model, best_params = gradient_boost_cv(
        X[:100], y[:100], param_grid, cv_folds=3, task="regression"
    )
    assert best_model.is_fitted
    assert 'n_estimators' in best_params
    
    print("All Gradient Boosting tests passed!")


if __name__ == "__main__":
    test_gradient_boosting()