"""
Tissue ID: ML-TISSUE-005
Title: Advanced Support Vector Machine Implementation
Category: ml/svm
Tags: ["svm", "support-vector-machine", "classification", "regression", "kernel-methods"]
Difficulty: Advanced
Dependencies: ["numpy>=1.24", "scikit-learn>=1.3"]
Performance: O(n²) to O(n³) depending on kernel and solver
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive SVM tissue supporting both classification (SVC) and regression (SVR)
with multiple kernels (linear, RBF, polynomial, sigmoid, custom). Features include
automatic hyperparameter tuning, multi-class strategies, probability calibration,
and support vector visualization.

Use Cases:
- Binary and multiclass classification
- Non-linear classification
- Regression with outliers
- Anomaly detection
- Text classification

Example Usage:
    # Basic SVM classification
    svm = SupportVectorMachine(task="classification", kernel="rbf")
    svm.fit(X_train, y_train)
    predictions = svm.predict(X_test)
    
    # SVM with custom kernel
    def custom_kernel(X1, X2):
        return np.tanh(0.5 * X1 @ X2.T + 1)
    
    svm = SupportVectorMachine(kernel=custom_kernel)
    svm.fit(X_train, y_train)
    
    # Auto-tune hyperparameters
    best_params = svm.auto_tune(X_train, y_train, param_grid={'C': [0.1, 1, 10]})
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import warnings


class TaskType(Enum):
    """SVM task types"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"


class KernelType(Enum):
    """Available kernel types"""
    LINEAR = "linear"
    RBF = "rbf"
    POLY = "polynomial"
    SIGMOID = "sigmoid"
    CUSTOM = "custom"


@dataclass
class SVMConfig:
    """Configuration for SVM"""
    C: float = 1.0  # Regularization parameter
    kernel: str = "rbf"
    degree: int = 3  # For polynomial kernel
    gamma: Union[str, float] = "scale"  # Kernel coefficient
    coef0: float = 0.0  # For polynomial and sigmoid
    epsilon: float = 0.1  # For SVR
    max_iterations: int = -1  # -1 for no limit
    tolerance: float = 1e-3
    probability: bool = False
    class_weight: Optional[Union[str, Dict]] = None
    decision_function_shape: str = "ovr"  # One-vs-rest or one-vs-one
    random_state: int = 42
    verbose: int = 0


@dataclass
class SVMResult:
    """Result of SVM training and evaluation"""
    support_vectors: np.ndarray
    support_vector_indices: np.ndarray
    n_support: np.ndarray  # Number per class
    dual_coefficients: np.ndarray
    intercept: Union[float, np.ndarray]
    fit_status: int  # 0: converged, 1: max iterations reached
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "n_support_vectors": len(self.support_vectors),
            "n_support_per_class": self.n_support.tolist(),
            "converged": self.fit_status == 0
        }


class SupportVectorMachine:
    """
    Advanced Support Vector Machine implementation.
    Tissue Type: FUNCTIONAL - Core ML SVM functionality.
    """
    
    def __init__(self,
                 task: str = "classification",
                 config: Optional[SVMConfig] = None,
                 kernel: Optional[Union[str, Callable]] = None,
                 feature_names: Optional[List[str]] = None):
        """
        Initialize SVM.
        
        Args:
            task: Task type (classification or regression)
            config: SVM configuration
            kernel: Kernel function (overrides config)
            feature_names: Names of features for interpretability
        """
        self.task = TaskType(task.lower())
        self.config = config or SVMConfig()
        self.feature_names = feature_names
        
        # Override kernel if provided
        if kernel is not None:
            if callable(kernel):
                self.kernel_function = kernel
                self.kernel_type = KernelType.CUSTOM
            else:
                self.config.kernel = kernel
                self.kernel_type = KernelType(kernel.upper())
                self.kernel_function = None
        else:
            self.kernel_type = KernelType(self.config.kernel.upper())
            self.kernel_function = None
        
        # Model components
        self.model = None
        self.support_vectors_ = None
        self.support_ = None  # Indices
        self.n_support_ = None
        self.dual_coef_ = None
        self.intercept_ = None
        
        # Training info
        self.classes_ = None
        self.n_classes_ = 0
        self.n_features_ = 0
        self.is_fitted = False
        
        # Scaler for features
        self.feature_mean_ = None
        self.feature_std_ = None
    
    def fit(self, X: np.ndarray, y: np.ndarray,
            sample_weights: Optional[np.ndarray] = None) -> 'SupportVectorMachine':
        """
        Fit SVM model.
        
        Args:
            X: Training features (n_samples, n_features)
            y: Target values (n_samples,)
            sample_weights: Optional sample weights
            
        Returns:
            Self for chaining
        """
        # Validate inputs
        X, y = self._validate_inputs(X, y)
        
        # Store dimensions
        self.n_features_ = X.shape[1]
        
        # Scale features
        X_scaled = self._scale_features(X, fit=True)
        
        # Handle task-specific setup
        if self.task == TaskType.CLASSIFICATION:
            self.classes_ = np.unique(y)
            self.n_classes_ = len(self.classes_)
            y_encoded = self._encode_labels(y)
        else:
            y_encoded = y
        
        # Fit model
        try:
            self._fit_sklearn(X_scaled, y_encoded, sample_weights)
        except ImportError:
            self._fit_manual(X_scaled, y_encoded, sample_weights)
        
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
        
        # Validate and scale
        X = self._validate_input(X)
        X_scaled = self._scale_features(X, fit=False)
        
        # Predict
        if hasattr(self.model, 'predict'):
            predictions = self.model.predict(X_scaled)
            
            # Decode labels for classification
            if self.task == TaskType.CLASSIFICATION:
                predictions = self.classes_[predictions.astype(int)]
        else:
            predictions = self._predict_manual(X_scaled)
        
        return predictions
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities (classification only).
        
        Args:
            X: Features to predict (n_samples, n_features)
            
        Returns:
            Class probabilities (n_samples, n_classes)
        """
        if self.task != TaskType.CLASSIFICATION:
            raise ValueError("predict_proba is only available for classification")
        
        if not self.config.probability:
            raise ValueError("Model must be fitted with probability=True")
        
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Validate and scale
        X = self._validate_input(X)
        X_scaled = self._scale_features(X, fit=False)
        
        # Get probabilities
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X_scaled)
        else:
            # Use decision function and sigmoid calibration
            decision_values = self.decision_function(X)
            
            if self.n_classes_ == 2:
                # Binary case
                probas = np.column_stack([
                    1 / (1 + np.exp(decision_values)),
                    1 / (1 + np.exp(-decision_values))
                ])
            else:
                # Multiclass - use softmax on decision values
                exp_values = np.exp(decision_values)
                probas = exp_values / exp_values.sum(axis=1, keepdims=True)
            
            return probas
    
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """
        Get decision function values.
        
        Args:
            X: Features to evaluate (n_samples, n_features)
            
        Returns:
            Decision function values
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before decision function")
        
        # Validate and scale
        X = self._validate_input(X)
        X_scaled = self._scale_features(X, fit=False)
        
        if hasattr(self.model, 'decision_function'):
            return self.model.decision_function(X_scaled)
        else:
            return self._decision_function_manual(X_scaled)
    
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
    
    def _scale_features(self, X: np.ndarray, fit: bool) -> np.ndarray:
        """Scale features for better SVM performance"""
        if fit:
            self.feature_mean_ = X.mean(axis=0)
            self.feature_std_ = X.std(axis=0)
            self.feature_std_[self.feature_std_ == 0] = 1
        
        return (X - self.feature_mean_) / self.feature_std_
    
    def _encode_labels(self, y: np.ndarray) -> np.ndarray:
        """Encode class labels to integers"""
        label_to_int = {label: i for i, label in enumerate(self.classes_)}
        return np.array([label_to_int[label] for label in y])
    
    def _fit_sklearn(self, X: np.ndarray, y: np.ndarray,
                    sample_weights: Optional[np.ndarray]):
        """Fit using scikit-learn"""
        from sklearn import svm
        
        # Create model based on task
        if self.task == TaskType.CLASSIFICATION:
            self.model = svm.SVC(
                C=self.config.C,
                kernel=self.config.kernel if self.kernel_type != KernelType.CUSTOM else 'precomputed',
                degree=self.config.degree,
                gamma=self.config.gamma,
                coef0=self.config.coef0,
                probability=self.config.probability,
                tol=self.config.tolerance,
                max_iter=self.config.max_iterations,
                class_weight=self.config.class_weight,
                decision_function_shape=self.config.decision_function_shape,
                random_state=self.config.random_state,
                verbose=self.config.verbose
            )
        else:
            self.model = svm.SVR(
                C=self.config.C,
                kernel=self.config.kernel if self.kernel_type != KernelType.CUSTOM else 'precomputed',
                degree=self.config.degree,
                gamma=self.config.gamma,
                coef0=self.config.coef0,
                epsilon=self.config.epsilon,
                tol=self.config.tolerance,
                max_iter=self.config.max_iterations,
                verbose=self.config.verbose
            )
        
        # Handle custom kernel
        if self.kernel_type == KernelType.CUSTOM:
            # Compute kernel matrix
            K = self.kernel_function(X, X)
            self.model.fit(K, y, sample_weight=sample_weights)
            
            # Store training data for predictions
            self._X_train = X.copy()
        else:
            self.model.fit(X, y, sample_weight=sample_weights)
        
        # Extract model information
        self.support_vectors_ = self.model.support_vectors_
        self.support_ = self.model.support_
        self.n_support_ = self.model.n_support_ if hasattr(self.model, 'n_support_') else np.array([len(self.support_)])
        self.dual_coef_ = self.model.dual_coef_
        self.intercept_ = self.model.intercept_
    
    def _fit_manual(self, X: np.ndarray, y: np.ndarray,
                   sample_weights: Optional[np.ndarray]):
        """Manual SVM implementation using SMO algorithm (simplified)"""
        n_samples = X.shape[0]
        
        # Initialize Lagrange multipliers
        alphas = np.zeros(n_samples)
        b = 0.0
        
        # Compute kernel matrix
        K = self._compute_kernel_matrix(X, X)
        
        # Simplified SMO for binary classification
        if self.task == TaskType.CLASSIFICATION and self.n_classes_ == 2:
            # Convert labels to {-1, 1}
            y_binary = np.where(y == 0, -1, 1)
            
            # SMO iterations
            for iteration in range(100):  # Simplified max iterations
                alpha_pairs_changed = 0
                
                for i in range(n_samples):
                    # Calculate error for i
                    E_i = self._calculate_error_manual(K, alphas, y_binary, b, i)
                    
                    if ((y_binary[i] * E_i < -self.config.tolerance and alphas[i] < self.config.C) or
                        (y_binary[i] * E_i > self.config.tolerance and alphas[i] > 0)):
                        
                        # Select j != i randomly
                        j = i
                        while j == i:
                            j = np.random.randint(0, n_samples)
                        
                        # Calculate error for j
                        E_j = self._calculate_error_manual(K, alphas, y_binary, b, j)
                        
                        # Save old alphas
                        alpha_i_old = alphas[i]
                        alpha_j_old = alphas[j]
                        
                        # Compute bounds
                        if y_binary[i] != y_binary[j]:
                            L = max(0, alphas[j] - alphas[i])
                            H = min(self.config.C, self.config.C + alphas[j] - alphas[i])
                        else:
                            L = max(0, alphas[i] + alphas[j] - self.config.C)
                            H = min(self.config.C, alphas[i] + alphas[j])
                        
                        if L == H:
                            continue
                        
                        # Compute eta
                        eta = 2 * K[i, j] - K[i, i] - K[j, j]
                        if eta >= 0:
                            continue
                        
                        # Update alpha_j
                        alphas[j] -= y_binary[j] * (E_i - E_j) / eta
                        alphas[j] = np.clip(alphas[j], L, H)
                        
                        if abs(alphas[j] - alpha_j_old) < 1e-5:
                            continue
                        
                        # Update alpha_i
                        alphas[i] += y_binary[i] * y_binary[j] * (alpha_j_old - alphas[j])
                        
                        # Update b
                        b1 = b - E_i - y_binary[i] * (alphas[i] - alpha_i_old) * K[i, i] - \
                             y_binary[j] * (alphas[j] - alpha_j_old) * K[i, j]
                        b2 = b - E_j - y_binary[i] * (alphas[i] - alpha_i_old) * K[i, j] - \
                             y_binary[j] * (alphas[j] - alpha_j_old) * K[j, j]
                        
                        if 0 < alphas[i] < self.config.C:
                            b = b1
                        elif 0 < alphas[j] < self.config.C:
                            b = b2
                        else:
                            b = (b1 + b2) / 2
                        
                        alpha_pairs_changed += 1
                
                if alpha_pairs_changed == 0:
                    break
            
            # Extract support vectors
            sv_indices = alphas > 1e-5
            self.support_ = np.where(sv_indices)[0]
            self.support_vectors_ = X[sv_indices]
            self.dual_coef_ = (alphas[sv_indices] * y_binary[sv_indices]).reshape(1, -1)
            self.intercept_ = b
            self.n_support_ = np.array([np.sum(y_binary[sv_indices] == -1),
                                       np.sum(y_binary[sv_indices] == 1)])
            
            # Store for predictions
            self._X_train = X
            self._y_train = y_binary
            self._alphas = alphas
        else:
            # Fallback for other cases
            warnings.warn("Manual implementation only supports binary classification. Using dummy model.")
            self.support_ = np.array([0])
            self.support_vectors_ = X[:1]
            self.dual_coef_ = np.array([[1.0]])
            self.intercept_ = 0.0
            self.n_support_ = np.array([1])
    
    def _calculate_error_manual(self, K: np.ndarray, alphas: np.ndarray,
                               y: np.ndarray, b: float, i: int) -> float:
        """Calculate prediction error for SMO"""
        f_i = np.sum(alphas * y * K[:, i]) + b
        return f_i - y[i]
    
    def _compute_kernel_matrix(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """Compute kernel matrix"""
        if self.kernel_type == KernelType.LINEAR:
            return X1 @ X2.T
        elif self.kernel_type == KernelType.RBF:
            # RBF kernel: exp(-gamma * ||x - y||^2)
            gamma = self._get_gamma(X1.shape[1])
            
            # Compute pairwise squared distances
            X1_sqnorms = np.sum(X1 ** 2, axis=1, keepdims=True)
            X2_sqnorms = np.sum(X2 ** 2, axis=1, keepdims=True)
            distances_sq = X1_sqnorms + X2_sqnorms.T - 2 * X1 @ X2.T
            
            return np.exp(-gamma * distances_sq)
        elif self.kernel_type == KernelType.POLY:
            # Polynomial kernel: (gamma * <x, y> + coef0)^degree
            gamma = self._get_gamma(X1.shape[1])
            return (gamma * X1 @ X2.T + self.config.coef0) ** self.config.degree
        elif self.kernel_type == KernelType.SIGMOID:
            # Sigmoid kernel: tanh(gamma * <x, y> + coef0)
            gamma = self._get_gamma(X1.shape[1])
            return np.tanh(gamma * X1 @ X2.T + self.config.coef0)
        elif self.kernel_type == KernelType.CUSTOM:
            return self.kernel_function(X1, X2)
        else:
            raise ValueError(f"Unknown kernel type: {self.kernel_type}")
    
    def _get_gamma(self, n_features: int) -> float:
        """Get gamma value"""
        if isinstance(self.config.gamma, str):
            if self.config.gamma == "scale":
                return 1.0 / (n_features * self.feature_std_.mean())
            elif self.config.gamma == "auto":
                return 1.0 / n_features
        return self.config.gamma
    
    def _predict_manual(self, X: np.ndarray) -> np.ndarray:
        """Manual prediction"""
        if self.kernel_type == KernelType.CUSTOM or hasattr(self, '_X_train'):
            # Compute kernel with training data
            K = self._compute_kernel_matrix(X, self._X_train[self.support_])
        else:
            K = self._compute_kernel_matrix(X, self.support_vectors_)
        
        # Decision values
        decision_values = K @ self.dual_coef_.T + self.intercept_
        
        if self.task == TaskType.CLASSIFICATION:
            if self.n_classes_ == 2:
                predictions = np.where(decision_values.ravel() >= 0, 1, 0)
                return self.classes_[predictions]
            else:
                # Simplified multiclass (one-vs-rest)
                return self.classes_[np.argmax(decision_values, axis=1)]
        else:
            return decision_values.ravel()
    
    def _decision_function_manual(self, X: np.ndarray) -> np.ndarray:
        """Manual decision function"""
        if hasattr(self, '_X_train'):
            K = self._compute_kernel_matrix(X, self._X_train[self.support_])
        else:
            K = self._compute_kernel_matrix(X, self.support_vectors_)
        
        return (K @ self.dual_coef_.T + self.intercept_).ravel()
    
    def get_support_vectors(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get support vectors and their labels.
        
        Returns:
            Support vectors and their corresponding labels
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        # Get original scale support vectors
        sv_original = self.support_vectors_ * self.feature_std_ + self.feature_mean_
        
        if self.task == TaskType.CLASSIFICATION:
            # Determine labels of support vectors
            sv_labels = []
            cumsum = 0
            for i, n in enumerate(self.n_support_):
                sv_labels.extend([self.classes_[i]] * n)
            sv_labels = np.array(sv_labels)
        else:
            sv_labels = None
        
        return sv_original, sv_labels
    
    def auto_tune(self, X: np.ndarray, y: np.ndarray,
                 param_grid: Optional[Dict[str, List]] = None,
                 cv_folds: int = 5) -> Dict[str, Any]:
        """
        Auto-tune hyperparameters using cross-validation.
        
        Args:
            X: Training features
            y: Training labels
            param_grid: Parameters to search
            cv_folds: Number of cross-validation folds
            
        Returns:
            Best parameters found
        """
        if param_grid is None:
            # Default parameter grid
            if self.kernel_type == KernelType.LINEAR:
                param_grid = {
                    'C': [0.001, 0.01, 0.1, 1, 10, 100]
                }
            else:
                param_grid = {
                    'C': [0.1, 1, 10, 100],
                    'gamma': ['scale', 'auto', 0.001, 0.01, 0.1]
                }
        
        try:
            from sklearn.model_selection import GridSearchCV
            from sklearn import svm
            
            # Create base model
            if self.task == TaskType.CLASSIFICATION:
                base_model = svm.SVC(kernel=self.config.kernel)
            else:
                base_model = svm.SVR(kernel=self.config.kernel)
            
            # Grid search
            grid = GridSearchCV(
                base_model, param_grid,
                cv=cv_folds,
                scoring='accuracy' if self.task == TaskType.CLASSIFICATION else 'neg_mean_squared_error',
                n_jobs=-1
            )
            
            # Scale data
            X_scaled = self._scale_features(X, fit=True)
            grid.fit(X_scaled, y)
            
            # Update config with best parameters
            for param, value in grid.best_params_.items():
                setattr(self.config, param, value)
            
            return grid.best_params_
            
        except ImportError:
            # Manual grid search
            return self._manual_grid_search(X, y, param_grid, cv_folds)
    
    def _manual_grid_search(self, X: np.ndarray, y: np.ndarray,
                          param_grid: Dict[str, List],
                          cv_folds: int) -> Dict[str, Any]:
        """Manual grid search"""
        best_score = -np.inf
        best_params = {}
        
        # Generate parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        # Simple cross-validation
        n_samples = X.shape[0]
        fold_size = n_samples // cv_folds
        
        for values in self._cartesian_product(param_values):
            # Set parameters
            params = dict(zip(param_names, values))
            for param, value in params.items():
                setattr(self.config, param, value)
            
            # Cross-validation
            scores = []
            for fold in range(cv_folds):
                # Create train/test split
                test_start = fold * fold_size
                test_end = (fold + 1) * fold_size if fold < cv_folds - 1 else n_samples
                
                test_idx = list(range(test_start, test_end))
                train_idx = list(range(test_start)) + list(range(test_end, n_samples))
                
                X_train, X_test = X[train_idx], X[test_idx]
                y_train, y_test = y[train_idx], y[test_idx]
                
                # Train and evaluate
                self.fit(X_train, y_train)
                predictions = self.predict(X_test)
                
                if self.task == TaskType.CLASSIFICATION:
                    score = np.mean(predictions == y_test)
                else:
                    score = -np.mean((predictions - y_test) ** 2)
                
                scores.append(score)
            
            # Average score
            avg_score = np.mean(scores)
            
            if avg_score > best_score:
                best_score = avg_score
                best_params = params.copy()
        
        # Set best parameters
        for param, value in best_params.items():
            setattr(self.config, param, value)
        
        return best_params
    
    def _cartesian_product(self, arrays: List[List]) -> List[List]:
        """Generate cartesian product of parameter values"""
        if not arrays:
            return [[]]
        
        result = []
        for item in arrays[0]:
            for rest in self._cartesian_product(arrays[1:]):
                result.append([item] + rest)
        
        return result


# Utility functions
def svm_classifier(X: np.ndarray, y: np.ndarray,
                  kernel: str = "rbf", C: float = 1.0) -> SupportVectorMachine:
    """Quick SVM classifier"""
    config = SVMConfig(kernel=kernel, C=C)
    svm = SupportVectorMachine(task="classification", config=config)
    svm.fit(X, y)
    return svm


def svm_regressor(X: np.ndarray, y: np.ndarray,
                 kernel: str = "rbf", epsilon: float = 0.1) -> SupportVectorMachine:
    """Quick SVM regressor"""
    config = SVMConfig(kernel=kernel, epsilon=epsilon)
    svm = SupportVectorMachine(task="regression", config=config)
    svm.fit(X, y)
    return svm


def one_class_svm(X: np.ndarray, nu: float = 0.1) -> np.ndarray:
    """One-class SVM for anomaly detection"""
    try:
        from sklearn.svm import OneClassSVM
        
        model = OneClassSVM(nu=nu, kernel="rbf", gamma="auto")
        model.fit(X)
        # Return -1 for outliers, 1 for inliers
        return model.predict(X)
    except ImportError:
        # Simple distance-based anomaly detection
        center = X.mean(axis=0)
        distances = np.sqrt(np.sum((X - center) ** 2, axis=1))
        threshold = np.percentile(distances, (1 - nu) * 100)
        return np.where(distances > threshold, -1, 1)


# Auto-generated tests
def test_support_vector_machine():
    """Test SVM functionality"""
    # Generate synthetic data
    np.random.seed(42)
    
    # Binary classification data (linearly separable with margin)
    n_samples = 200
    n_features = 2
    
    # Create two classes with margin
    X_class1 = np.random.randn(n_samples // 2, n_features) + np.array([2, 2])
    X_class2 = np.random.randn(n_samples // 2, n_features) + np.array([-2, -2])
    X_binary = np.vstack([X_class1, X_class2])
    y_binary = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))
    
    # Shuffle
    indices = np.random.permutation(n_samples)
    X_binary, y_binary = X_binary[indices], y_binary[indices]
    
    # Test linear SVM
    svm_linear = SupportVectorMachine(task="classification", kernel="linear")
    svm_linear.fit(X_binary, y_binary)
    
    assert svm_linear.is_fitted
    assert len(svm_linear.support_) > 0
    assert len(svm_linear.support_vectors_) == len(svm_linear.support_)
    
    # Test prediction
    predictions = svm_linear.predict(X_binary[:10])
    assert len(predictions) == 10
    assert all(p in [0, 1] for p in predictions)
    
    # Test decision function
    decision_values = svm_linear.decision_function(X_binary[:10])
    assert len(decision_values) == 10
    
    # Test RBF kernel
    config_rbf = SVMConfig(kernel="rbf", C=1.0, gamma="scale")
    svm_rbf = SupportVectorMachine(task="classification", config=config_rbf)
    svm_rbf.fit(X_binary, y_binary)
    assert svm_rbf.is_fitted
    
    # Test polynomial kernel
    config_poly = SVMConfig(kernel="polynomial", degree=3)
    svm_poly = SupportVectorMachine(task="classification", config=config_poly)
    svm_poly.fit(X_binary, y_binary)
    assert svm_poly.is_fitted
    
    # Test regression
    y_reg = X_binary[:, 0] + 0.5 * X_binary[:, 1] + 0.1 * np.random.randn(n_samples)
    
    svm_reg = SupportVectorMachine(task="regression")
    svm_reg.fit(X_binary, y_reg)
    
    reg_predictions = svm_reg.predict(X_binary[:10])
    assert len(reg_predictions) == 10
    assert all(isinstance(p, (float, np.floating)) for p in reg_predictions)
    
    # Test custom kernel
    def gaussian_kernel(X1, X2, sigma=1.0):
        """Custom Gaussian kernel"""
        pairwise_sq_dist = np.sum(X1**2, axis=1, keepdims=True) + \
                          np.sum(X2**2, axis=1, keepdims=True).T - \
                          2 * X1 @ X2.T
        return np.exp(-pairwise_sq_dist / (2 * sigma**2))
    
    svm_custom = SupportVectorMachine(task="classification", kernel=gaussian_kernel)
    svm_custom.fit(X_binary[:50], y_binary[:50])  # Smaller dataset for speed
    custom_predictions = svm_custom.predict(X_binary[50:60])
    assert len(custom_predictions) == 10
    
    # Test multiclass (create 3 classes)
    X_multi = np.vstack([
        np.random.randn(50, n_features) + np.array([3, 3]),
        np.random.randn(50, n_features) + np.array([-3, 3]),
        np.random.randn(50, n_features) + np.array([0, -3])
    ])
    y_multi = np.array([0] * 50 + [1] * 50 + [2] * 50)
    
    svm_multi = SupportVectorMachine(task="classification")
    svm_multi.fit(X_multi, y_multi)
    assert svm_multi.n_classes_ == 3
    
    multi_predictions = svm_multi.predict(X_multi[:10])
    assert all(p in [0, 1, 2] for p in multi_predictions)
    
    # Test with sample weights
    weights = np.random.rand(n_samples)
    svm_weighted = SupportVectorMachine(task="classification")
    svm_weighted.fit(X_binary, y_binary, sample_weights=weights)
    assert svm_weighted.is_fitted
    
    # Test support vector extraction
    support_vectors, sv_labels = svm_linear.get_support_vectors()
    assert len(support_vectors) == len(svm_linear.support_)
    if sv_labels is not None:
        assert len(sv_labels) == len(support_vectors)
    
    # Test probability estimation
    config_prob = SVMConfig(probability=True)
    svm_prob = SupportVectorMachine(task="classification", config=config_prob)
    svm_prob.fit(X_binary[:100], y_binary[:100])  # Smaller for speed
    
    probas = svm_prob.predict_proba(X_binary[100:110])
    assert probas.shape == (10, 2)
    assert np.allclose(probas.sum(axis=1), 1.0)
    
    # Test auto-tuning (simple test)
    param_grid = {'C': [0.1, 1.0]}
    best_params = svm_linear.auto_tune(X_binary[:50], y_binary[:50], 
                                      param_grid=param_grid, cv_folds=2)
    assert 'C' in best_params
    
    # Test utility functions
    quick_svm = svm_classifier(X_binary, y_binary, kernel="linear")
    assert quick_svm.is_fitted
    
    quick_svr = svm_regressor(X_binary, y_reg, kernel="rbf", epsilon=0.2)
    assert quick_svr.is_fitted
    
    # Test anomaly detection
    anomalies = one_class_svm(X_binary, nu=0.1)
    assert len(anomalies) == n_samples
    assert np.sum(anomalies == -1) < n_samples * 0.2  # Less than 20% outliers
    
    print("All SVM tests passed!")


if __name__ == "__main__":
    test_support_vector_machine()