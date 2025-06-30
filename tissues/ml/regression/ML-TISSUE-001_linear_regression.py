"""
Tissue ID: ML-TISSUE-001
Title: Advanced Linear Regression Suite
Category: ml/regression
Tags: ["linear-regression", "regression", "machine-learning", "prediction", "statistics"]
Difficulty: Intermediate
Dependencies: ["numpy>=1.24", "scikit-learn>=1.3"]
Performance: O(n*p²) for training where n is samples, p is features
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive linear regression tissue that provides multiple implementations
including ordinary least squares (OLS), ridge regression, lasso regression, and
elastic net. Features automatic preprocessing, feature engineering, regularization
tuning, and model diagnostics.

Use Cases:
- Price prediction
- Sales forecasting
- Trend analysis
- Feature importance analysis
- Risk assessment

Example Usage:
    # Basic linear regression
    regressor = LinearRegressor()
    regressor.fit(X_train, y_train)
    predictions = regressor.predict(X_test)
    
    # Ridge regression with cross-validation
    regressor = LinearRegressor(method="ridge", auto_tune=True)
    regressor.fit(X_train, y_train)
    
    # Get feature importance
    importance = regressor.get_feature_importance()
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings


class RegressionMethod(Enum):
    """Available regression methods"""
    OLS = "ols"  # Ordinary Least Squares
    RIDGE = "ridge"  # L2 regularization
    LASSO = "lasso"  # L1 regularization
    ELASTIC_NET = "elastic_net"  # L1 + L2 regularization
    HUBER = "huber"  # Robust to outliers


@dataclass
class RegressionConfig:
    """Configuration for regression"""
    alpha: float = 1.0  # Regularization strength
    l1_ratio: float = 0.5  # Elastic net mixing parameter
    fit_intercept: bool = True
    normalize: bool = True
    max_iterations: int = 1000
    tolerance: float = 1e-4
    random_state: int = 42
    auto_tune: bool = False
    cv_folds: int = 5
    scoring: str = "r2"


@dataclass
class RegressionResult:
    """Result of regression analysis"""
    coefficients: np.ndarray
    intercept: float
    r2_score: float
    mse: float
    rmse: float
    feature_importance: Optional[Dict[str, float]] = None
    residuals: Optional[np.ndarray] = None
    confidence_intervals: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "coefficients": self.coefficients.tolist(),
            "intercept": self.intercept,
            "r2_score": self.r2_score,
            "mse": self.mse,
            "rmse": self.rmse,
            "feature_importance": self.feature_importance
        }


class LinearRegressor:
    """
    Advanced linear regression system with multiple methods.
    Tissue Type: FUNCTIONAL - Core ML regression functionality.
    """
    
    def __init__(self,
                 method: str = "ols",
                 config: Optional[RegressionConfig] = None,
                 feature_names: Optional[List[str]] = None):
        """
        Initialize linear regressor.
        
        Args:
            method: Regression method to use
            config: Configuration options
            feature_names: Names of features for interpretability
        """
        self.method = RegressionMethod(method.lower())
        self.config = config or RegressionConfig()
        self.feature_names = feature_names
        
        # Model components
        self.model = None
        self.coefficients_ = None
        self.intercept_ = None
        self.is_fitted = False
        
        # Preprocessing info
        self.feature_mean_ = None
        self.feature_std_ = None
        self.target_mean_ = None
        self.target_std_ = None
        
        # Statistics
        self.n_features_ = 0
        self.n_samples_seen_ = 0
    
    def fit(self, X: np.ndarray, y: np.ndarray,
            sample_weights: Optional[np.ndarray] = None) -> 'LinearRegressor':
        """
        Fit linear regression model.
        
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
        self.n_samples_seen_, self.n_features_ = X.shape
        
        # Preprocess data
        X_processed, y_processed = self._preprocess(X, y, fit=True)
        
        # Auto-tune hyperparameters if requested
        if self.config.auto_tune and self.method != RegressionMethod.OLS:
            self._auto_tune_hyperparameters(X_processed, y_processed)
        
        # Fit model based on method
        if self.method == RegressionMethod.OLS:
            self._fit_ols(X_processed, y_processed, sample_weights)
        elif self.method == RegressionMethod.RIDGE:
            self._fit_ridge(X_processed, y_processed, sample_weights)
        elif self.method == RegressionMethod.LASSO:
            self._fit_lasso(X_processed, y_processed, sample_weights)
        elif self.method == RegressionMethod.ELASTIC_NET:
            self._fit_elastic_net(X_processed, y_processed, sample_weights)
        elif self.method == RegressionMethod.HUBER:
            self._fit_huber(X_processed, y_processed, sample_weights)
        
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Features to predict (n_samples, n_features)
            
        Returns:
            Predicted values
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Validate input
        X = self._validate_input(X)
        
        # Preprocess
        X_processed, _ = self._preprocess(X, None, fit=False)
        
        # Make predictions
        if hasattr(self.model, 'predict'):
            predictions = self.model.predict(X_processed)
        else:
            # Manual prediction for simple implementations
            predictions = X_processed @ self.coefficients_
            if self.config.fit_intercept:
                predictions += self.intercept_
        
        # Inverse transform if normalized
        if self.config.normalize and self.target_std_ is not None:
            predictions = predictions * self.target_std_ + self.target_mean_
        
        return predictions
    
    def _validate_inputs(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Validate and prepare inputs"""
        # Convert to numpy arrays
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        
        # Check dimensions
        if X.ndim != 2:
            raise ValueError(f"X must be 2D, got {X.ndim}D")
        
        if y.ndim == 2 and y.shape[1] == 1:
            y = y.ravel()
        elif y.ndim != 1:
            raise ValueError(f"y must be 1D or 2D with one column, got shape {y.shape}")
        
        # Check lengths match
        if X.shape[0] != y.shape[0]:
            raise ValueError(f"X and y must have same number of samples: {X.shape[0]} != {y.shape[0]}")
        
        # Check for NaN/Inf
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ValueError("X contains NaN or Inf values")
        
        if np.any(np.isnan(y)) or np.any(np.isinf(y)):
            raise ValueError("y contains NaN or Inf values")
        
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
    
    def _preprocess(self, X: np.ndarray, y: Optional[np.ndarray], 
                   fit: bool) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Preprocess features and target"""
        X_processed = X.copy()
        y_processed = y.copy() if y is not None else None
        
        if self.config.normalize:
            if fit:
                # Fit normalization parameters
                self.feature_mean_ = X.mean(axis=0)
                self.feature_std_ = X.std(axis=0)
                self.feature_std_[self.feature_std_ == 0] = 1  # Avoid division by zero
                
                if y is not None:
                    self.target_mean_ = y.mean()
                    self.target_std_ = y.std()
                    if self.target_std_ == 0:
                        self.target_std_ = 1
            
            # Apply normalization
            X_processed = (X_processed - self.feature_mean_) / self.feature_std_
            
            if y_processed is not None and fit:
                y_processed = (y_processed - self.target_mean_) / self.target_std_
        
        return X_processed, y_processed
    
    def _fit_ols(self, X: np.ndarray, y: np.ndarray, 
                 sample_weights: Optional[np.ndarray]):
        """Fit ordinary least squares"""
        try:
            from sklearn.linear_model import LinearRegression
            
            self.model = LinearRegression(fit_intercept=self.config.fit_intercept)
            self.model.fit(X, y, sample_weight=sample_weights)
            
            self.coefficients_ = self.model.coef_
            self.intercept_ = self.model.intercept_ if self.config.fit_intercept else 0.0
        except ImportError:
            # Manual OLS implementation
            self._fit_ols_manual(X, y, sample_weights)
    
    def _fit_ols_manual(self, X: np.ndarray, y: np.ndarray,
                       sample_weights: Optional[np.ndarray]):
        """Manual OLS implementation using normal equation"""
        n_samples, n_features = X.shape
        
        # Add intercept column if needed
        if self.config.fit_intercept:
            X_with_intercept = np.column_stack([np.ones(n_samples), X])
        else:
            X_with_intercept = X
        
        # Apply sample weights if provided
        if sample_weights is not None:
            W = np.diag(np.sqrt(sample_weights))
            X_weighted = W @ X_with_intercept
            y_weighted = W @ y
        else:
            X_weighted = X_with_intercept
            y_weighted = y
        
        # Normal equation: (X^T X)^(-1) X^T y
        try:
            XtX = X_weighted.T @ X_weighted
            Xty = X_weighted.T @ y_weighted
            
            # Add small regularization for numerical stability
            XtX += np.eye(XtX.shape[0]) * 1e-10
            
            # Solve using Cholesky decomposition for efficiency
            L = np.linalg.cholesky(XtX)
            z = np.linalg.solve(L, Xty)
            params = np.linalg.solve(L.T, z)
        except np.linalg.LinAlgError:
            # Fallback to pseudo-inverse
            params = np.linalg.pinv(X_weighted) @ y_weighted
        
        # Extract coefficients and intercept
        if self.config.fit_intercept:
            self.intercept_ = params[0]
            self.coefficients_ = params[1:]
        else:
            self.intercept_ = 0.0
            self.coefficients_ = params
    
    def _fit_ridge(self, X: np.ndarray, y: np.ndarray,
                   sample_weights: Optional[np.ndarray]):
        """Fit ridge regression"""
        try:
            from sklearn.linear_model import Ridge
            
            self.model = Ridge(
                alpha=self.config.alpha,
                fit_intercept=self.config.fit_intercept,
                max_iter=self.config.max_iterations,
                tol=self.config.tolerance,
                random_state=self.config.random_state
            )
            self.model.fit(X, y, sample_weight=sample_weights)
            
            self.coefficients_ = self.model.coef_
            self.intercept_ = self.model.intercept_ if self.config.fit_intercept else 0.0
        except ImportError:
            # Manual ridge implementation
            self._fit_ridge_manual(X, y, sample_weights)
    
    def _fit_ridge_manual(self, X: np.ndarray, y: np.ndarray,
                         sample_weights: Optional[np.ndarray]):
        """Manual ridge regression implementation"""
        n_samples, n_features = X.shape
        
        # Add intercept column if needed
        if self.config.fit_intercept:
            X_with_intercept = np.column_stack([np.ones(n_samples), X])
            # Don't regularize intercept
            regularization = np.eye(n_features + 1)
            regularization[0, 0] = 0
        else:
            X_with_intercept = X
            regularization = np.eye(n_features)
        
        # Apply sample weights
        if sample_weights is not None:
            W = np.diag(np.sqrt(sample_weights))
            X_weighted = W @ X_with_intercept
            y_weighted = W @ y
        else:
            X_weighted = X_with_intercept
            y_weighted = y
        
        # Ridge solution: (X^T X + alpha*I)^(-1) X^T y
        XtX = X_weighted.T @ X_weighted
        Xty = X_weighted.T @ y_weighted
        
        # Add ridge penalty
        XtX += self.config.alpha * regularization
        
        # Solve
        try:
            params = np.linalg.solve(XtX, Xty)
        except np.linalg.LinAlgError:
            params = np.linalg.pinv(XtX) @ Xty
        
        # Extract coefficients
        if self.config.fit_intercept:
            self.intercept_ = params[0]
            self.coefficients_ = params[1:]
        else:
            self.intercept_ = 0.0
            self.coefficients_ = params
    
    def _fit_lasso(self, X: np.ndarray, y: np.ndarray,
                   sample_weights: Optional[np.ndarray]):
        """Fit lasso regression"""
        try:
            from sklearn.linear_model import Lasso
            
            self.model = Lasso(
                alpha=self.config.alpha,
                fit_intercept=self.config.fit_intercept,
                max_iter=self.config.max_iterations,
                tol=self.config.tolerance,
                random_state=self.config.random_state
            )
            self.model.fit(X, y, sample_weight=sample_weights)
            
            self.coefficients_ = self.model.coef_
            self.intercept_ = self.model.intercept_ if self.config.fit_intercept else 0.0
        except ImportError:
            # Simple coordinate descent implementation
            self._fit_lasso_manual(X, y, sample_weights)
    
    def _fit_lasso_manual(self, X: np.ndarray, y: np.ndarray,
                         sample_weights: Optional[np.ndarray]):
        """Manual lasso using coordinate descent"""
        n_samples, n_features = X.shape
        
        # Initialize coefficients
        self.coefficients_ = np.zeros(n_features)
        self.intercept_ = 0.0
        
        # Center data if fitting intercept
        if self.config.fit_intercept:
            X_mean = X.mean(axis=0)
            y_mean = y.mean()
            X_centered = X - X_mean
            y_centered = y - y_mean
        else:
            X_centered = X
            y_centered = y
        
        # Apply weights
        if sample_weights is not None:
            W = np.sqrt(sample_weights)
            X_weighted = X_centered * W[:, np.newaxis]
            y_weighted = y_centered * W
        else:
            X_weighted = X_centered
            y_weighted = y_centered
        
        # Coordinate descent
        for iteration in range(self.config.max_iterations):
            coeffs_old = self.coefficients_.copy()
            
            for j in range(n_features):
                # Compute residual without feature j
                residual = y_weighted - X_weighted @ self.coefficients_
                residual += X_weighted[:, j] * self.coefficients_[j]
                
                # Compute rho_j
                rho_j = X_weighted[:, j] @ residual
                
                # Soft thresholding
                if rho_j < -self.config.alpha:
                    self.coefficients_[j] = (rho_j + self.config.alpha) / (X_weighted[:, j] @ X_weighted[:, j])
                elif rho_j > self.config.alpha:
                    self.coefficients_[j] = (rho_j - self.config.alpha) / (X_weighted[:, j] @ X_weighted[:, j])
                else:
                    self.coefficients_[j] = 0.0
            
            # Check convergence
            if np.max(np.abs(self.coefficients_ - coeffs_old)) < self.config.tolerance:
                break
        
        # Set intercept
        if self.config.fit_intercept:
            self.intercept_ = y_mean - X_mean @ self.coefficients_
    
    def _fit_elastic_net(self, X: np.ndarray, y: np.ndarray,
                        sample_weights: Optional[np.ndarray]):
        """Fit elastic net regression"""
        try:
            from sklearn.linear_model import ElasticNet
            
            self.model = ElasticNet(
                alpha=self.config.alpha,
                l1_ratio=self.config.l1_ratio,
                fit_intercept=self.config.fit_intercept,
                max_iter=self.config.max_iterations,
                tol=self.config.tolerance,
                random_state=self.config.random_state
            )
            self.model.fit(X, y, sample_weight=sample_weights)
            
            self.coefficients_ = self.model.coef_
            self.intercept_ = self.model.intercept_ if self.config.fit_intercept else 0.0
        except ImportError:
            # Fallback to lasso or ridge based on l1_ratio
            if self.config.l1_ratio > 0.5:
                self._fit_lasso_manual(X, y, sample_weights)
            else:
                self._fit_ridge_manual(X, y, sample_weights)
    
    def _fit_huber(self, X: np.ndarray, y: np.ndarray,
                   sample_weights: Optional[np.ndarray]):
        """Fit Huber regression (robust to outliers)"""
        try:
            from sklearn.linear_model import HuberRegressor
            
            self.model = HuberRegressor(
                epsilon=1.35,  # Default threshold
                max_iter=self.config.max_iterations,
                alpha=self.config.alpha,
                fit_intercept=self.config.fit_intercept
            )
            self.model.fit(X, y, sample_weight=sample_weights)
            
            self.coefficients_ = self.model.coef_
            self.intercept_ = self.model.intercept_ if self.config.fit_intercept else 0.0
        except ImportError:
            # Fallback to OLS with outlier detection
            self._fit_robust_manual(X, y, sample_weights)
    
    def _fit_robust_manual(self, X: np.ndarray, y: np.ndarray,
                          sample_weights: Optional[np.ndarray]):
        """Manual robust regression using iteratively reweighted least squares"""
        # Initial fit with OLS
        self._fit_ols_manual(X, y, sample_weights)
        
        # Iteratively reweight based on residuals
        for _ in range(5):  # Fixed iterations
            # Calculate residuals
            predictions = X @ self.coefficients_
            if self.config.fit_intercept:
                predictions += self.intercept_
            residuals = y - predictions
            
            # Calculate weights based on residuals (Huber weights)
            threshold = 1.345 * np.median(np.abs(residuals))
            weights = np.where(np.abs(residuals) <= threshold, 
                             1.0, 
                             threshold / np.abs(residuals))
            
            # Combine with original sample weights
            if sample_weights is not None:
                weights *= sample_weights
            
            # Refit with new weights
            self._fit_ols_manual(X, y, weights)
    
    def _auto_tune_hyperparameters(self, X: np.ndarray, y: np.ndarray):
        """Auto-tune regularization parameters using cross-validation"""
        try:
            from sklearn.model_selection import GridSearchCV
            from sklearn.linear_model import Ridge, Lasso, ElasticNet
            
            # Define parameter grid
            if self.method == RegressionMethod.RIDGE:
                model = Ridge(fit_intercept=self.config.fit_intercept)
                param_grid = {'alpha': np.logspace(-4, 4, 20)}
            elif self.method == RegressionMethod.LASSO:
                model = Lasso(fit_intercept=self.config.fit_intercept)
                param_grid = {'alpha': np.logspace(-4, 2, 20)}
            elif self.method == RegressionMethod.ELASTIC_NET:
                model = ElasticNet(fit_intercept=self.config.fit_intercept)
                param_grid = {
                    'alpha': np.logspace(-4, 2, 10),
                    'l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9]
                }
            else:
                return
            
            # Grid search
            grid = GridSearchCV(
                model, param_grid,
                cv=self.config.cv_folds,
                scoring=self.config.scoring,
                n_jobs=-1
            )
            grid.fit(X, y)
            
            # Update config with best parameters
            if 'alpha' in grid.best_params_:
                self.config.alpha = grid.best_params_['alpha']
            if 'l1_ratio' in grid.best_params_:
                self.config.l1_ratio = grid.best_params_['l1_ratio']
                
        except ImportError:
            # Simple cross-validation for alpha
            alphas = np.logspace(-4, 2, 10)
            scores = []
            
            for alpha in alphas:
                self.config.alpha = alpha
                cv_scores = self._simple_cross_validate(X, y)
                scores.append(np.mean(cv_scores))
            
            # Select best alpha
            best_idx = np.argmax(scores)
            self.config.alpha = alphas[best_idx]
    
    def _simple_cross_validate(self, X: np.ndarray, y: np.ndarray) -> List[float]:
        """Simple k-fold cross-validation"""
        n_samples = X.shape[0]
        fold_size = n_samples // self.config.cv_folds
        scores = []
        
        for i in range(self.config.cv_folds):
            # Create train/test split
            test_start = i * fold_size
            test_end = (i + 1) * fold_size if i < self.config.cv_folds - 1 else n_samples
            
            test_idx = list(range(test_start, test_end))
            train_idx = list(range(test_start)) + list(range(test_end, n_samples))
            
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Fit and evaluate
            temp_model = LinearRegressor(method=self.method.value)
            temp_model.config = self.config
            temp_model.fit(X_train, y_train)
            
            predictions = temp_model.predict(X_test)
            score = self._calculate_r2(y_test, predictions)
            scores.append(score)
        
        return scores
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> RegressionResult:
        """
        Evaluate model performance.
        
        Args:
            X: Test features
            y: True target values
            
        Returns:
            Regression results with metrics
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before evaluation")
        
        # Make predictions
        predictions = self.predict(X)
        
        # Calculate metrics
        r2_score = self._calculate_r2(y, predictions)
        mse = np.mean((y - predictions) ** 2)
        rmse = np.sqrt(mse)
        
        # Calculate residuals
        residuals = y - predictions
        
        # Get feature importance
        feature_importance = self.get_feature_importance()
        
        return RegressionResult(
            coefficients=self.coefficients_,
            intercept=self.intercept_,
            r2_score=r2_score,
            mse=mse,
            rmse=rmse,
            feature_importance=feature_importance,
            residuals=residuals
        )
    
    def _calculate_r2(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate R-squared score"""
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        
        if ss_tot == 0:
            return 1.0 if ss_res == 0 else 0.0
        
        return 1 - (ss_res / ss_tot)
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance based on coefficients"""
        if not self.is_fitted:
            return None
        
        # Use absolute coefficients as importance
        importance = np.abs(self.coefficients_)
        
        # Normalize
        if importance.sum() > 0:
            importance = importance / importance.sum()
        
        # Create dictionary with feature names
        if self.feature_names:
            return {name: float(imp) for name, imp in zip(self.feature_names, importance)}
        else:
            return {f"feature_{i}": float(imp) for i, imp in enumerate(importance)}
    
    def get_coefficients(self) -> Dict[str, float]:
        """Get coefficients with feature names"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        if self.feature_names:
            return {name: float(coef) for name, coef in zip(self.feature_names, self.coefficients_)}
        else:
            return {f"feature_{i}": float(coef) for i, coef in enumerate(self.coefficients_)}


# Utility functions
def linear_regression(X: np.ndarray, y: np.ndarray, 
                     method: str = "ols") -> Tuple[np.ndarray, float]:
    """Quick linear regression"""
    regressor = LinearRegressor(method=method)
    regressor.fit(X, y)
    return regressor.coefficients_, regressor.intercept_


def ridge_regression_cv(X: np.ndarray, y: np.ndarray) -> LinearRegressor:
    """Ridge regression with automatic cross-validation"""
    config = RegressionConfig(auto_tune=True)
    regressor = LinearRegressor(method="ridge", config=config)
    regressor.fit(X, y)
    return regressor


def feature_selection_lasso(X: np.ndarray, y: np.ndarray, 
                          feature_names: List[str],
                          alpha: float = 1.0) -> List[str]:
    """Select features using Lasso regression"""
    config = RegressionConfig(alpha=alpha)
    regressor = LinearRegressor(method="lasso", config=config, feature_names=feature_names)
    regressor.fit(X, y)
    
    # Get non-zero features
    selected_features = []
    for i, (name, coef) in enumerate(regressor.get_coefficients().items()):
        if abs(coef) > 1e-10:
            selected_features.append(name)
    
    return selected_features


# Auto-generated tests
def test_linear_regressor():
    """Test linear regression functionality"""
    # Generate synthetic data
    np.random.seed(42)
    n_samples, n_features = 100, 5
    X = np.random.randn(n_samples, n_features)
    true_coef = np.array([1.5, -2.0, 0.5, 0.0, 1.0])
    y = X @ true_coef + 0.1 * np.random.randn(n_samples)
    
    # Feature names
    feature_names = [f"feature_{i}" for i in range(n_features)]
    
    # Test OLS
    regressor = LinearRegressor(method="ols", feature_names=feature_names)
    regressor.fit(X, y)
    
    assert regressor.is_fitted
    assert len(regressor.coefficients_) == n_features
    
    # Test prediction
    predictions = regressor.predict(X[:10])
    assert len(predictions) == 10
    
    # Test evaluation
    result = regressor.evaluate(X, y)
    assert result.r2_score > 0.8  # Should fit well
    assert result.rmse < 0.5
    
    # Test Ridge regression
    ridge = LinearRegressor(method="ridge", feature_names=feature_names)
    ridge.fit(X, y)
    assert len(ridge.coefficients_) == n_features
    
    # Test Lasso regression
    lasso = LinearRegressor(method="lasso", feature_names=feature_names)
    lasso.fit(X, y)
    # Lasso should set some coefficients to zero
    zero_coefs = np.sum(np.abs(lasso.coefficients_) < 1e-10)
    assert zero_coefs > 0
    
    # Test feature importance
    importance = regressor.get_feature_importance()
    assert len(importance) == n_features
    assert all(0 <= v <= 1 for v in importance.values())
    
    # Test with sample weights
    weights = np.random.rand(n_samples)
    regressor_weighted = LinearRegressor()
    regressor_weighted.fit(X, y, sample_weights=weights)
    assert regressor_weighted.is_fitted
    
    # Test auto-tuning (mock)
    config = RegressionConfig(auto_tune=True, cv_folds=3)
    ridge_tuned = LinearRegressor(method="ridge", config=config)
    ridge_tuned.fit(X[:50], y[:50])  # Smaller dataset for speed
    assert ridge_tuned.is_fitted
    
    # Test utility functions
    coefs, intercept = linear_regression(X, y)
    assert len(coefs) == n_features
    
    selected = feature_selection_lasso(X, y, feature_names, alpha=0.1)
    assert len(selected) <= n_features
    
    print("All linear regression tests passed!")


if __name__ == "__main__":
    test_linear_regressor()