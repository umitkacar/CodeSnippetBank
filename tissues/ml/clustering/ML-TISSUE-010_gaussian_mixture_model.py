"""
Tissue ID: ML-TISSUE-010
Title: Gaussian Mixture Model (GMM) Implementation
Category: ml/clustering
Tags: ["gmm", "gaussian-mixture", "soft-clustering", "expectation-maximization", "density-estimation"]
Difficulty: Advanced
Dependencies: ["numpy>=1.24", "scikit-learn>=1.3"]
Performance: O(n*k*d²*i) where n is samples, k is components, d is dimensions, i is iterations
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive Gaussian Mixture Model tissue implementing soft clustering via
Expectation-Maximization (EM) algorithm. Supports multiple covariance types
(full, diagonal, tied, spherical), automatic component selection using BIC/AIC,
and convergence monitoring. Includes density estimation and anomaly detection.

Use Cases:
- Soft clustering (probabilistic assignments)
- Density estimation
- Anomaly/outlier detection
- Data generation
- Missing data imputation

Example Usage:
    # Basic GMM clustering
    gmm = GaussianMixtureModel(n_components=3)
    gmm.fit(X)
    labels = gmm.predict(X)
    
    # Get soft assignments
    probabilities = gmm.predict_proba(X)
    
    # Density estimation
    log_density = gmm.score_samples(X_new)
    
    # Auto-select components
    best_gmm = gmm.select_best_model(X, n_components_range=(2, 10))
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import warnings
from scipy import linalg


class CovarianceType(Enum):
    """Types of covariance matrices"""
    FULL = "full"  # Each component has its own general covariance matrix
    DIAGONAL = "diag"  # Each component has its own diagonal covariance
    TIED = "tied"  # All components share the same general covariance
    SPHERICAL = "spherical"  # Each component has single variance


@dataclass
class GMMConfig:
    """Configuration for Gaussian Mixture Model"""
    n_components: int = 1
    covariance_type: str = "full"
    tolerance: float = 1e-3
    max_iterations: int = 100
    n_init: int = 1
    init_method: str = "kmeans"  # kmeans, random
    reg_covar: float = 1e-6  # Regularization for covariance
    warm_start: bool = False
    random_state: int = 42
    verbose: int = 0


@dataclass
class GMMParameters:
    """Parameters of a fitted GMM"""
    weights: np.ndarray  # Component weights (n_components,)
    means: np.ndarray  # Component means (n_components, n_features)
    covariances: np.ndarray  # Covariances (shape depends on type)
    precisions: np.ndarray  # Precision matrices (inverse covariance)
    precisions_cholesky: np.ndarray  # Cholesky decomposition of precisions


@dataclass
class GMMResults:
    """Results of GMM fitting"""
    n_iterations: int
    converged: bool
    lower_bound: float  # Final log-likelihood lower bound
    aic: float  # Akaike Information Criterion
    bic: float  # Bayesian Information Criterion
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "n_iterations": self.n_iterations,
            "converged": self.converged,
            "lower_bound": self.lower_bound,
            "aic": self.aic,
            "bic": self.bic
        }


class GaussianMixtureModel:
    """
    Gaussian Mixture Model implementation.
    Tissue Type: FUNCTIONAL - Core ML probabilistic clustering.
    """
    
    def __init__(self,
                 n_components: Optional[int] = None,
                 config: Optional[GMMConfig] = None,
                 feature_names: Optional[List[str]] = None):
        """
        Initialize Gaussian Mixture Model.
        
        Args:
            n_components: Number of mixture components
            config: GMM configuration
            feature_names: Names of features for interpretability
        """
        self.config = config or GMMConfig()
        if n_components is not None:
            self.config.n_components = n_components
        
        self.feature_names = feature_names
        self.covariance_type = CovarianceType(self.config.covariance_type)
        
        # Model parameters
        self.weights_ = None
        self.means_ = None
        self.covariances_ = None
        self.precisions_ = None
        self.precisions_cholesky_ = None
        
        # Fitting info
        self.n_features_ = 0
        self.n_samples_seen_ = 0
        self.lower_bound_ = -np.inf
        self.n_iter_ = 0
        self.converged_ = False
        self.is_fitted = False
        
        # Random state
        self.rng = np.random.RandomState(self.config.random_state)
    
    def fit(self, X: np.ndarray,
            y: Optional[np.ndarray] = None) -> 'GaussianMixtureModel':
        """
        Fit Gaussian Mixture Model using EM algorithm.
        
        Args:
            X: Training data (n_samples, n_features)
            y: Ignored (for API consistency)
            
        Returns:
            Self for chaining
        """
        X = self._validate_data(X)
        n_samples, n_features = X.shape
        
        self.n_features_ = n_features
        self.n_samples_seen_ = n_samples
        
        # Check number of components
        if self.config.n_components > n_samples:
            warnings.warn(f"n_components ({self.config.n_components}) > n_samples ({n_samples}). "
                         f"Setting n_components to {n_samples}")
            self.config.n_components = n_samples
        
        # Multiple initializations
        best_lower_bound = -np.inf
        best_params = None
        best_n_iter = 0
        
        for init in range(self.config.n_init):
            if self.config.verbose > 0:
                print(f"Initialization {init + 1}/{self.config.n_init}")
            
            # Initialize parameters
            if init == 0 and self.config.warm_start and self.is_fitted:
                # Use existing parameters
                lower_bound, n_iter = self._fit_single(X)
            else:
                # New initialization
                self._initialize_parameters(X)
                lower_bound, n_iter = self._fit_single(X)
            
            # Keep best result
            if lower_bound > best_lower_bound:
                best_lower_bound = lower_bound
                best_params = self._get_parameters()
                best_n_iter = n_iter
        
        # Set best parameters
        self._set_parameters(best_params)
        self.lower_bound_ = best_lower_bound
        self.n_iter_ = best_n_iter
        self.converged_ = best_n_iter < self.config.max_iterations
        
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict component labels (hard assignment).
        
        Args:
            X: Data to predict (n_samples, n_features)
            
        Returns:
            Component labels (n_samples,)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X = self._validate_data(X)
        
        # Get responsibilities
        _, log_resp = self._e_step(X)
        return np.argmax(log_resp, axis=1)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict posterior probabilities of components.
        
        Args:
            X: Data to predict (n_samples, n_features)
            
        Returns:
            Component probabilities (n_samples, n_components)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X = self._validate_data(X)
        
        # Get responsibilities
        _, log_resp = self._e_step(X)
        return np.exp(log_resp)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """
        Compute log-likelihood of samples.
        
        Args:
            X: Data to score (n_samples, n_features)
            
        Returns:
            Log-likelihood of each sample (n_samples,)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before scoring")
        
        X = self._validate_data(X)
        
        # Compute weighted log probabilities
        log_prob = self._estimate_log_prob(X)
        log_weights = np.log(self.weights_)
        
        # Log-sum-exp for numerical stability
        weighted_log_prob = log_prob + log_weights
        return self._log_sum_exp(weighted_log_prob, axis=1)
    
    def score(self, X: np.ndarray) -> float:
        """
        Compute average log-likelihood.
        
        Args:
            X: Data to score (n_samples, n_features)
            
        Returns:
            Average log-likelihood
        """
        return np.mean(self.score_samples(X))
    
    def sample(self, n_samples: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate random samples from the model.
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Generated samples and their component labels
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before sampling")
        
        # Sample component assignments
        components = self.rng.choice(
            self.config.n_components,
            size=n_samples,
            p=self.weights_
        )
        
        # Count samples per component
        n_samples_comp = np.bincount(components, minlength=self.config.n_components)
        
        # Generate samples
        X = np.zeros((n_samples, self.n_features_))
        
        for k in range(self.config.n_components):
            if n_samples_comp[k] > 0:
                # Generate from multivariate normal
                if self.covariance_type == CovarianceType.FULL:
                    X[components == k] = self.rng.multivariate_normal(
                        self.means_[k],
                        self.covariances_[k],
                        size=n_samples_comp[k]
                    )
                elif self.covariance_type == CovarianceType.DIAGONAL:
                    mean = self.means_[k]
                    std = np.sqrt(self.covariances_[k])
                    X[components == k] = self.rng.normal(
                        loc=mean,
                        scale=std,
                        size=(n_samples_comp[k], self.n_features_)
                    )
                elif self.covariance_type == CovarianceType.SPHERICAL:
                    mean = self.means_[k]
                    std = np.sqrt(self.covariances_[k])
                    X[components == k] = self.rng.normal(
                        loc=mean,
                        scale=std,
                        size=(n_samples_comp[k], self.n_features_)
                    )
                elif self.covariance_type == CovarianceType.TIED:
                    X[components == k] = self.rng.multivariate_normal(
                        self.means_[k],
                        self.covariances_,
                        size=n_samples_comp[k]
                    )
        
        return X, components
    
    def _validate_data(self, X: np.ndarray) -> np.ndarray:
        """Validate input data"""
        X = np.asarray(X, dtype=np.float64)
        
        if X.ndim != 2:
            raise ValueError(f"X must be 2D, got {X.ndim}D")
        
        if self.is_fitted and X.shape[1] != self.n_features_:
            raise ValueError(f"X has {X.shape[1]} features, expected {self.n_features_}")
        
        return X
    
    def _initialize_parameters(self, X: np.ndarray):
        """Initialize model parameters"""
        n_samples, n_features = X.shape
        
        # Initialize responsibilities
        if self.config.init_method == "kmeans":
            # Use k-means for initialization
            resp = self._kmeans_init(X)
        else:
            # Random initialization
            resp = self.rng.rand(n_samples, self.config.n_components)
            resp /= resp.sum(axis=1, keepdims=True)
        
        # Initialize parameters from responsibilities
        self._m_step(X, np.log(resp))
    
    def _kmeans_init(self, X: np.ndarray) -> np.ndarray:
        """Initialize using k-means clustering"""
        try:
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(
                n_clusters=self.config.n_components,
                n_init=1,
                random_state=self.rng
            )
            labels = kmeans.fit_predict(X)
            
            # Convert to responsibilities
            resp = np.zeros((X.shape[0], self.config.n_components))
            resp[np.arange(X.shape[0]), labels] = 1
            
            # Add small noise to avoid singular covariances
            resp += 0.01
            resp /= resp.sum(axis=1, keepdims=True)
            
            return resp
            
        except ImportError:
            # Fallback to random
            return self._random_init(X)
    
    def _random_init(self, X: np.ndarray) -> np.ndarray:
        """Random initialization"""
        n_samples = X.shape[0]
        resp = self.rng.rand(n_samples, self.config.n_components)
        resp /= resp.sum(axis=1, keepdims=True)
        return resp
    
    def _fit_single(self, X: np.ndarray) -> Tuple[float, int]:
        """Single run of EM algorithm"""
        lower_bound = -np.inf
        
        for n_iter in range(self.config.max_iterations):
            prev_lower_bound = lower_bound
            
            # E-step
            log_prob_norm, log_resp = self._e_step(X)
            
            # M-step
            self._m_step(X, log_resp)
            
            # Compute lower bound
            lower_bound = np.sum(log_prob_norm)
            
            # Check convergence
            change = lower_bound - prev_lower_bound
            if self.config.verbose > 1:
                print(f"  Iteration {n_iter + 1}: "
                      f"lower bound = {lower_bound:.3f}, "
                      f"change = {change:.3e}")
            
            if abs(change) < self.config.tolerance:
                if self.config.verbose > 0:
                    print(f"Converged at iteration {n_iter + 1}")
                break
        
        return lower_bound, n_iter + 1
    
    def _e_step(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Expectation step"""
        # Compute log probabilities
        log_prob = self._estimate_log_prob(X)
        log_weights = np.log(self.weights_)
        
        # Weighted log probabilities
        weighted_log_prob = log_prob + log_weights
        
        # Normalize (log-sum-exp for stability)
        log_prob_norm = self._log_sum_exp(weighted_log_prob, axis=1)
        
        # Responsibilities
        log_resp = weighted_log_prob - log_prob_norm[:, np.newaxis]
        
        return log_prob_norm, log_resp
    
    def _m_step(self, X: np.ndarray, log_resp: np.ndarray):
        """Maximization step"""
        n_samples = X.shape[0]
        
        # Convert log responsibilities to responsibilities
        resp = np.exp(log_resp)
        
        # Update weights
        nk = resp.sum(axis=0) + 10 * np.finfo(resp.dtype).eps
        self.weights_ = nk / n_samples
        
        # Update means
        self.means_ = resp.T @ X / nk[:, np.newaxis]
        
        # Update covariances
        self._estimate_covariances(X, resp, nk)
    
    def _estimate_log_prob(self, X: np.ndarray) -> np.ndarray:
        """Estimate log probability under each Gaussian component"""
        n_samples = X.shape[0]
        log_prob = np.zeros((n_samples, self.config.n_components))
        
        for k in range(self.config.n_components):
            log_prob[:, k] = self._log_multivariate_normal_density(
                X, self.means_[k], k
            )
        
        return log_prob
    
    def _log_multivariate_normal_density(self, X: np.ndarray, mean: np.ndarray,
                                       component: int) -> np.ndarray:
        """Compute log density of multivariate normal"""
        n_features = X.shape[1]
        
        # Compute precision-weighted squared Mahalanobis distance
        if self.covariance_type == CovarianceType.FULL:
            log_det = self._compute_log_det_cholesky(
                self.precisions_cholesky_[component]
            )
            diff = X - mean
            y = diff @ self.precisions_cholesky_[component]
            log_prob = -0.5 * np.sum(y ** 2, axis=1)
            
        elif self.covariance_type == CovarianceType.DIAGONAL:
            log_det = np.sum(np.log(self.precisions_cholesky_[component]))
            diff = X - mean
            precisions = self.precisions_[component]
            log_prob = -0.5 * np.sum(diff ** 2 * precisions, axis=1)
            
        elif self.covariance_type == CovarianceType.SPHERICAL:
            log_det = n_features * np.log(self.precisions_cholesky_[component])
            diff = X - mean
            precisions = self.precisions_[component]
            log_prob = -0.5 * precisions * np.sum(diff ** 2, axis=1)
            
        elif self.covariance_type == CovarianceType.TIED:
            log_det = self._compute_log_det_cholesky(self.precisions_cholesky_)
            diff = X - mean
            y = diff @ self.precisions_cholesky_
            log_prob = -0.5 * np.sum(y ** 2, axis=1)
        
        # Add normalization constant
        return log_prob + log_det - 0.5 * n_features * np.log(2 * np.pi)
    
    def _estimate_covariances(self, X: np.ndarray, resp: np.ndarray, nk: np.ndarray):
        """Estimate covariance parameters"""
        if self.covariance_type == CovarianceType.FULL:
            self._estimate_full_covariances(X, resp, nk)
        elif self.covariance_type == CovarianceType.DIAGONAL:
            self._estimate_diagonal_covariances(X, resp, nk)
        elif self.covariance_type == CovarianceType.SPHERICAL:
            self._estimate_spherical_covariances(X, resp, nk)
        elif self.covariance_type == CovarianceType.TIED:
            self._estimate_tied_covariances(X, resp, nk)
    
    def _estimate_full_covariances(self, X: np.ndarray, resp: np.ndarray, nk: np.ndarray):
        """Estimate full covariance matrices"""
        n_components = self.config.n_components
        n_features = self.n_features_
        
        self.covariances_ = np.empty((n_components, n_features, n_features))
        self.precisions_cholesky_ = np.empty((n_components, n_features, n_features))
        
        for k in range(n_components):
            diff = X - self.means_[k]
            
            # Weighted covariance
            cov = (resp[:, k, np.newaxis] * diff).T @ diff / nk[k]
            
            # Regularization
            cov.flat[::n_features + 1] += self.config.reg_covar
            
            self.covariances_[k] = cov
            
            # Compute precision Cholesky
            try:
                cov_chol = linalg.cholesky(cov, lower=True)
                self.precisions_cholesky_[k] = linalg.solve_triangular(
                    cov_chol, np.eye(n_features), lower=True
                ).T
            except linalg.LinAlgError:
                # Singular matrix - add more regularization
                cov.flat[::n_features + 1] += 1e-3
                cov_chol = linalg.cholesky(cov, lower=True)
                self.precisions_cholesky_[k] = linalg.solve_triangular(
                    cov_chol, np.eye(n_features), lower=True
                ).T
    
    def _estimate_diagonal_covariances(self, X: np.ndarray, resp: np.ndarray, nk: np.ndarray):
        """Estimate diagonal covariance matrices"""
        n_components = self.config.n_components
        
        self.covariances_ = np.empty((n_components, self.n_features_))
        self.precisions_ = np.empty((n_components, self.n_features_))
        self.precisions_cholesky_ = np.empty((n_components, self.n_features_))
        
        for k in range(n_components):
            diff = X - self.means_[k]
            
            # Weighted variance
            var = np.sum(resp[:, k, np.newaxis] * diff ** 2, axis=0) / nk[k]
            var += self.config.reg_covar
            
            self.covariances_[k] = var
            self.precisions_[k] = 1.0 / var
            self.precisions_cholesky_[k] = np.sqrt(self.precisions_[k])
    
    def _estimate_spherical_covariances(self, X: np.ndarray, resp: np.ndarray, nk: np.ndarray):
        """Estimate spherical covariance matrices"""
        n_components = self.config.n_components
        
        self.covariances_ = np.empty(n_components)
        self.precisions_ = np.empty(n_components)
        self.precisions_cholesky_ = np.empty(n_components)
        
        for k in range(n_components):
            diff = X - self.means_[k]
            
            # Weighted variance (same for all dimensions)
            var = np.sum(resp[:, k] * np.sum(diff ** 2, axis=1)) / (nk[k] * self.n_features_)
            var += self.config.reg_covar
            
            self.covariances_[k] = var
            self.precisions_[k] = 1.0 / var
            self.precisions_cholesky_[k] = np.sqrt(self.precisions_[k])
    
    def _estimate_tied_covariances(self, X: np.ndarray, resp: np.ndarray, nk: np.ndarray):
        """Estimate tied covariance matrix"""
        n_features = self.n_features_
        
        # Compute weighted average covariance
        avg_cov = np.zeros((n_features, n_features))
        
        for k in range(self.config.n_components):
            diff = X - self.means_[k]
            cov = (resp[:, k, np.newaxis] * diff).T @ diff / nk[k]
            avg_cov += self.weights_[k] * cov
        
        # Regularization
        avg_cov.flat[::n_features + 1] += self.config.reg_covar
        
        self.covariances_ = avg_cov
        
        # Compute precision Cholesky
        cov_chol = linalg.cholesky(avg_cov, lower=True)
        self.precisions_cholesky_ = linalg.solve_triangular(
            cov_chol, np.eye(n_features), lower=True
        ).T
    
    def _compute_log_det_cholesky(self, matrix_chol: np.ndarray) -> float:
        """Compute log determinant from Cholesky decomposition"""
        if matrix_chol.ndim == 2:
            return 2 * np.sum(np.log(np.diagonal(matrix_chol)))
        else:
            return 2 * np.log(matrix_chol)
    
    def _log_sum_exp(self, X: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
        """Compute log(sum(exp(X))) in a numerically stable way"""
        X_max = np.max(X, axis=axis, keepdims=True)
        return np.log(np.sum(np.exp(X - X_max), axis=axis)) + np.squeeze(X_max, axis=axis)
    
    def _get_parameters(self) -> GMMParameters:
        """Get current parameters"""
        return GMMParameters(
            weights=self.weights_.copy() if self.weights_ is not None else None,
            means=self.means_.copy() if self.means_ is not None else None,
            covariances=self.covariances_.copy() if self.covariances_ is not None else None,
            precisions=self.precisions_.copy() if self.precisions_ is not None else None,
            precisions_cholesky=self.precisions_cholesky_.copy() if self.precisions_cholesky_ is not None else None
        )
    
    def _set_parameters(self, params: GMMParameters):
        """Set parameters"""
        self.weights_ = params.weights
        self.means_ = params.means
        self.covariances_ = params.covariances
        self.precisions_ = params.precisions
        self.precisions_cholesky_ = params.precisions_cholesky
    
    def aic(self, X: np.ndarray) -> float:
        """
        Akaike Information Criterion.
        
        Args:
            X: Data to evaluate
            
        Returns:
            AIC score (lower is better)
        """
        return -2 * self.score(X) * X.shape[0] + 2 * self._n_parameters()
    
    def bic(self, X: np.ndarray) -> float:
        """
        Bayesian Information Criterion.
        
        Args:
            X: Data to evaluate
            
        Returns:
            BIC score (lower is better)
        """
        n_samples = X.shape[0]
        return -2 * self.score(X) * n_samples + self._n_parameters() * np.log(n_samples)
    
    def _n_parameters(self) -> int:
        """Compute number of free parameters"""
        n_features = self.n_features_
        n_components = self.config.n_components
        
        # Weights (n_components - 1 due to constraint)
        n_params = n_components - 1
        
        # Means
        n_params += n_components * n_features
        
        # Covariances
        if self.covariance_type == CovarianceType.FULL:
            n_params += n_components * n_features * (n_features + 1) // 2
        elif self.covariance_type == CovarianceType.DIAGONAL:
            n_params += n_components * n_features
        elif self.covariance_type == CovarianceType.SPHERICAL:
            n_params += n_components
        elif self.covariance_type == CovarianceType.TIED:
            n_params += n_features * (n_features + 1) // 2
        
        return n_params
    
    def select_best_model(self, X: np.ndarray,
                         n_components_range: Tuple[int, int] = (1, 10),
                         criterion: str = "bic") -> 'GaussianMixtureModel':
        """
        Select best number of components using information criterion.
        
        Args:
            X: Training data
            n_components_range: Range of components to try
            criterion: Selection criterion (aic or bic)
            
        Returns:
            Best model
        """
        X = self._validate_data(X)
        
        best_score = np.inf
        best_model = None
        
        for n_components in range(n_components_range[0], n_components_range[1] + 1):
            # Create and fit model
            config = GMMConfig(
                n_components=n_components,
                covariance_type=self.config.covariance_type,
                n_init=self.config.n_init,
                random_state=self.config.random_state
            )
            
            model = GaussianMixtureModel(config=config, feature_names=self.feature_names)
            model.fit(X)
            
            # Evaluate
            if criterion == "aic":
                score = model.aic(X)
            else:
                score = model.bic(X)
            
            if score < best_score:
                best_score = score
                best_model = model
        
        return best_model
    
    def detect_outliers(self, X: np.ndarray,
                       contamination: float = 0.1) -> np.ndarray:
        """
        Detect outliers based on log-likelihood.
        
        Args:
            X: Data to check for outliers
            contamination: Expected proportion of outliers
            
        Returns:
            Boolean array indicating outliers
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        X = self._validate_data(X)
        
        # Compute log-likelihoods
        log_likelihood = self.score_samples(X)
        
        # Determine threshold
        threshold = np.percentile(log_likelihood, contamination * 100)
        
        return log_likelihood < threshold
    
    def get_parameters(self) -> GMMResults:
        """Get model results and diagnostics"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        # Dummy data for AIC/BIC calculation
        # In practice, should use the training data
        return GMMResults(
            n_iterations=self.n_iter_,
            converged=self.converged_,
            lower_bound=self.lower_bound_,
            aic=0.0,  # Would need training data
            bic=0.0   # Would need training data
        )


# Utility functions
def gaussian_mixture(X: np.ndarray, n_components: int = 2,
                    covariance_type: str = "full") -> GaussianMixtureModel:
    """Quick Gaussian Mixture Model fitting"""
    config = GMMConfig(n_components=n_components, covariance_type=covariance_type)
    gmm = GaussianMixtureModel(config=config)
    gmm.fit(X)
    return gmm


def gmm_density_estimation(X: np.ndarray, n_components: int = 5) -> Callable:
    """Create density estimator using GMM"""
    gmm = gaussian_mixture(X, n_components=n_components)
    
    def density_function(x: np.ndarray) -> np.ndarray:
        """Estimate density at points x"""
        return np.exp(gmm.score_samples(x))
    
    return density_function


def gmm_anomaly_detector(X_train: np.ndarray,
                        contamination: float = 0.1) -> Callable:
    """Create anomaly detector using GMM"""
    # Select best model
    gmm = GaussianMixtureModel()
    best_gmm = gmm.select_best_model(X_train, n_components_range=(1, 5))
    
    def detect_anomalies(X: np.ndarray) -> np.ndarray:
        """Detect anomalies in X"""
        return best_gmm.detect_outliers(X, contamination=contamination)
    
    return detect_anomalies


# Auto-generated tests
def test_gaussian_mixture_model():
    """Test GMM functionality"""
    # Generate synthetic data
    np.random.seed(42)
    
    # Create mixture of Gaussians
    n_samples = 500
    n_features = 2
    
    # Component 1
    mean1 = [0, 0]
    cov1 = [[1, 0.5], [0.5, 1]]
    X1 = np.random.multivariate_normal(mean1, cov1, n_samples // 3)
    
    # Component 2
    mean2 = [5, 5]
    cov2 = [[2, -0.5], [-0.5, 1]]
    X2 = np.random.multivariate_normal(mean2, cov2, n_samples // 3)
    
    # Component 3
    mean3 = [0, 5]
    cov3 = [[0.5, 0], [0, 2]]
    X3 = np.random.multivariate_normal(mean3, cov3, n_samples // 3)
    
    X = np.vstack([X1, X2, X3])
    np.random.shuffle(X)
    
    # Test basic GMM
    gmm = GaussianMixtureModel(n_components=3)
    gmm.fit(X)
    
    assert gmm.is_fitted
    assert gmm.weights_.shape == (3,)
    assert gmm.means_.shape == (3, 2)
    assert np.allclose(gmm.weights_.sum(), 1.0)
    
    # Test prediction
    labels = gmm.predict(X[:20])
    assert len(labels) == 20
    assert all(0 <= label < 3 for label in labels)
    
    # Test probability prediction
    probas = gmm.predict_proba(X[:20])
    assert probas.shape == (20, 3)
    assert np.allclose(probas.sum(axis=1), 1.0)
    assert np.all(probas >= 0) and np.all(probas <= 1)
    
    # Test scoring
    log_likelihood = gmm.score_samples(X[:20])
    assert len(log_likelihood) == 20
    assert np.all(np.isfinite(log_likelihood))
    
    avg_ll = gmm.score(X[:20])
    assert isinstance(avg_ll, float)
    assert np.isfinite(avg_ll)
    
    # Test sampling
    X_generated, y_generated = gmm.sample(100)
    assert X_generated.shape == (100, 2)
    assert len(y_generated) == 100
    assert all(0 <= y < 3 for y in y_generated)
    
    # Test different covariance types
    for cov_type in ["full", "diag", "spherical", "tied"]:
        config = GMMConfig(n_components=2, covariance_type=cov_type)
        gmm_cov = GaussianMixtureModel(config=config)
        gmm_cov.fit(X[:200])  # Smaller for speed
        assert gmm_cov.is_fitted
        
        pred = gmm_cov.predict(X[200:220])
        assert len(pred) == 20
    
    # Test model selection
    best_gmm = gmm.select_best_model(X[:200], n_components_range=(1, 5), criterion="bic")
    assert best_gmm.is_fitted
    assert 1 <= best_gmm.config.n_components <= 5
    
    # Test AIC/BIC
    aic = gmm.aic(X)
    bic = gmm.bic(X)
    assert isinstance(aic, float) and np.isfinite(aic)
    assert isinstance(bic, float) and np.isfinite(bic)
    
    # Test outlier detection
    # Add outliers
    outliers = np.random.uniform(-10, 10, size=(20, 2))
    X_with_outliers = np.vstack([X, outliers])
    
    is_outlier = gmm.detect_outliers(X_with_outliers, contamination=0.05)
    assert len(is_outlier) == len(X_with_outliers)
    # Most outliers should be in the last 20 samples
    assert np.sum(is_outlier[-20:]) > np.sum(is_outlier[:-20])
    
    # Test convergence
    config_tol = GMMConfig(n_components=2, tolerance=1e-6, max_iterations=1000)
    gmm_converge = GaussianMixtureModel(config=config_tol)
    gmm_converge.fit(X[:100])
    assert gmm_converge.converged_
    
    # Test warm start
    config_warm = GMMConfig(n_components=3, warm_start=True, n_init=2)
    gmm_warm = GaussianMixtureModel(config=config_warm)
    gmm_warm.fit(X[:100])
    
    # Refit with same data
    gmm_warm.fit(X[:100])
    assert gmm_warm.is_fitted
    
    # Test initialization methods
    for init_method in ["kmeans", "random"]:
        config_init = GMMConfig(n_components=2, init_method=init_method)
        gmm_init = GaussianMixtureModel(config=config_init)
        gmm_init.fit(X[:100])
        assert gmm_init.is_fitted
    
    # Test edge cases
    # Single component
    gmm_single = GaussianMixtureModel(n_components=1)
    gmm_single.fit(X[:50])
    assert gmm_single.is_fitted
    assert np.allclose(gmm_single.weights_, [1.0])
    
    # More components than samples
    gmm_many = GaussianMixtureModel(n_components=10)
    X_small = X[:5]
    gmm_many.fit(X_small)
    assert gmm_many.config.n_components == 5  # Should be adjusted
    
    # Test utility functions
    quick_gmm = gaussian_mixture(X, n_components=3, covariance_type="full")
    assert quick_gmm.is_fitted
    
    density_est = gmm_density_estimation(X[:200], n_components=3)
    densities = density_est(X[200:210])
    assert len(densities) == 10
    assert np.all(densities >= 0)
    
    anomaly_detect = gmm_anomaly_detector(X[:300], contamination=0.1)
    anomalies = anomaly_detect(X_with_outliers)
    assert len(anomalies) == len(X_with_outliers)
    
    print("All GMM tests passed!")


if __name__ == "__main__":
    test_gaussian_mixture_model()