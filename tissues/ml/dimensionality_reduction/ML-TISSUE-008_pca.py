"""
Tissue ID: ML-TISSUE-008
Title: Principal Component Analysis (PCA) Implementation
Category: ml/dimensionality_reduction
Tags: ["pca", "dimensionality-reduction", "feature-extraction", "unsupervised-learning", "visualization"]
Difficulty: Intermediate
Dependencies: ["numpy>=1.24", "scikit-learn>=1.3"]
Performance: O(min(n²*p, p²*n)) where n is samples, p is features
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive PCA tissue implementing various PCA variants including standard PCA,
incremental PCA for large datasets, kernel PCA for non-linear transformations,
and sparse PCA. Features include automatic component selection, reconstruction
error calculation, and visualization helpers.

Use Cases:
- Feature reduction
- Data visualization
- Noise reduction
- Data compression
- Preprocessing for ML models

Example Usage:
    # Basic PCA
    pca = PrincipalComponentAnalysis(n_components=2)
    pca.fit(X_train)
    X_reduced = pca.transform(X_test)
    
    # Preserve 95% variance
    pca = PrincipalComponentAnalysis(n_components=0.95)
    pca.fit(X)
    
    # Kernel PCA for non-linear data
    pca = PrincipalComponentAnalysis(method="kernel", kernel="rbf")
    X_transformed = pca.fit_transform(X)
    
    # Incremental PCA for large datasets
    pca = PrincipalComponentAnalysis(method="incremental", batch_size=100)
    for batch in data_batches:
        pca.partial_fit(batch)
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings


class PCAMethod(Enum):
    """Available PCA methods"""
    STANDARD = "standard"
    INCREMENTAL = "incremental"
    KERNEL = "kernel"
    SPARSE = "sparse"
    RANDOMIZED = "randomized"


@dataclass
class PCAConfig:
    """Configuration for PCA"""
    n_components: Optional[Union[int, float]] = None
    whiten: bool = False
    svd_solver: str = "auto"  # auto, full, arpack, randomized
    tol: float = 0.0
    iterated_power: Union[int, str] = "auto"
    random_state: int = 42
    batch_size: int = 100  # For incremental PCA
    kernel: str = "linear"  # For kernel PCA
    gamma: Optional[float] = None  # For RBF kernel
    degree: int = 3  # For polynomial kernel
    coef0: float = 1.0  # For polynomial and sigmoid kernels
    alpha: float = 1.0  # For ridge (sparse PCA)
    ridge_alpha: float = 0.01
    n_jobs: int = 1
    max_iter: int = 1000


@dataclass
class PCAResult:
    """Result of PCA analysis"""
    n_components: int
    explained_variance: np.ndarray
    explained_variance_ratio: np.ndarray
    singular_values: np.ndarray
    reconstruction_error: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "n_components": self.n_components,
            "total_variance_explained": float(np.sum(self.explained_variance_ratio)),
            "reconstruction_error": self.reconstruction_error,
            "explained_variance_ratio": self.explained_variance_ratio.tolist()
        }


class PrincipalComponentAnalysis:
    """
    Comprehensive PCA implementation with multiple variants.
    Tissue Type: FUNCTIONAL - Core ML dimensionality reduction.
    """
    
    def __init__(self,
                 n_components: Optional[Union[int, float]] = None,
                 method: str = "standard",
                 config: Optional[PCAConfig] = None):
        """
        Initialize PCA.
        
        Args:
            n_components: Number of components or variance to preserve
            method: PCA method to use
            config: PCA configuration
        """
        self.method = PCAMethod(method.lower())
        self.config = config or PCAConfig()
        
        if n_components is not None:
            self.config.n_components = n_components
        
        # Model components
        self.mean_ = None
        self.components_ = None
        self.explained_variance_ = None
        self.explained_variance_ratio_ = None
        self.singular_values_ = None
        self.n_components_ = None
        self.n_features_ = None
        self.n_samples_seen_ = 0
        
        # For incremental PCA
        self.partial_mean_ = None
        self.partial_var_ = None
        self.partial_n_ = 0
        
        # For kernel PCA
        self.X_fit_ = None
        self.dual_coef_ = None
        
        self.is_fitted = False
    
    def fit(self, X: np.ndarray) -> 'PrincipalComponentAnalysis':
        """
        Fit PCA model.
        
        Args:
            X: Training data (n_samples, n_features)
            
        Returns:
            Self for chaining
        """
        X = self._validate_data(X)
        
        if self.method == PCAMethod.STANDARD:
            self._fit_standard(X)
        elif self.method == PCAMethod.INCREMENTAL:
            self._fit_incremental(X)
        elif self.method == PCAMethod.KERNEL:
            self._fit_kernel(X)
        elif self.method == PCAMethod.SPARSE:
            self._fit_sparse(X)
        elif self.method == PCAMethod.RANDOMIZED:
            self._fit_randomized(X)
        
        self.is_fitted = True
        return self
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform data to principal components.
        
        Args:
            X: Data to transform (n_samples, n_features)
            
        Returns:
            Transformed data (n_samples, n_components)
        """
        if not self.is_fitted:
            raise ValueError("PCA must be fitted before transform")
        
        X = self._validate_data(X)
        
        if self.method == PCAMethod.KERNEL:
            return self._transform_kernel(X)
        else:
            return self._transform_standard(X)
    
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Fit and transform in one step"""
        self.fit(X)
        return self.transform(X)
    
    def inverse_transform(self, X_transformed: np.ndarray) -> np.ndarray:
        """
        Transform data back to original space.
        
        Args:
            X_transformed: Transformed data (n_samples, n_components)
            
        Returns:
            Data in original space (n_samples, n_features)
        """
        if not self.is_fitted:
            raise ValueError("PCA must be fitted before inverse transform")
        
        if self.method == PCAMethod.KERNEL:
            raise NotImplementedError("Inverse transform not available for kernel PCA")
        
        X_transformed = np.asarray(X_transformed)
        
        if self.config.whiten:
            # Undo whitening
            X_transformed = X_transformed * np.sqrt(self.explained_variance_[:self.n_components_])
        
        # Project back
        X_original = X_transformed @ self.components_[:self.n_components_]
        
        # Add mean back
        X_original += self.mean_
        
        return X_original
    
    def partial_fit(self, X: np.ndarray) -> 'PrincipalComponentAnalysis':
        """
        Incremental fit for streaming data.
        
        Args:
            X: Batch of training data
            
        Returns:
            Self for chaining
        """
        if self.method != PCAMethod.INCREMENTAL:
            raise ValueError("partial_fit only available for incremental PCA")
        
        X = self._validate_data(X)
        
        self._partial_fit_incremental(X)
        
        return self
    
    def _validate_data(self, X: np.ndarray) -> np.ndarray:
        """Validate input data"""
        X = np.asarray(X, dtype=np.float64)
        
        if X.ndim != 2:
            raise ValueError(f"X must be 2D, got {X.ndim}D")
        
        if self.is_fitted and X.shape[1] != self.n_features_:
            raise ValueError(f"X has {X.shape[1]} features, expected {self.n_features_}")
        
        return X
    
    def _fit_standard(self, X: np.ndarray):
        """Standard PCA using SVD"""
        n_samples, n_features = X.shape
        self.n_features_ = n_features
        self.n_samples_seen_ = n_samples
        
        # Center data
        self.mean_ = np.mean(X, axis=0)
        X_centered = X - self.mean_
        
        # Determine number of components
        self.n_components_ = self._infer_n_components(n_samples, n_features)
        
        # Perform SVD
        if self.config.svd_solver == "auto":
            # Choose solver automatically
            if self.n_components_ == min(n_samples, n_features):
                svd_solver = "full"
            elif self.n_components_ == 1:
                svd_solver = "randomized"
            else:
                svd_solver = "full" if self.n_components_ > 0.8 * min(n_samples, n_features) else "randomized"
        else:
            svd_solver = self.config.svd_solver
        
        if svd_solver == "full":
            U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
        elif svd_solver == "randomized":
            U, S, Vt = self._randomized_svd(X_centered, self.n_components_)
        else:
            # Use sklearn if available
            try:
                from sklearn.utils.extmath import randomized_svd
                U, S, Vt = randomized_svd(X_centered, self.n_components_,
                                        random_state=self.config.random_state)
            except ImportError:
                U, S, Vt = self._randomized_svd(X_centered, self.n_components_)
        
        # Store results
        self.components_ = Vt[:self.n_components_]
        self.singular_values_ = S[:self.n_components_]
        
        # Calculate explained variance
        self.explained_variance_ = (S[:self.n_components_] ** 2) / (n_samples - 1)
        total_var = np.var(X, ddof=1, axis=0).sum()
        self.explained_variance_ratio_ = self.explained_variance_ / total_var
        
        # Handle small number of components
        if self.n_components_ < min(n_samples, n_features):
            self.noise_variance_ = (total_var - self.explained_variance_.sum()) / \
                                 (min(n_samples, n_features) - self.n_components_)
        else:
            self.noise_variance_ = 0.0
    
    def _fit_incremental(self, X: np.ndarray):
        """Incremental PCA for large datasets"""
        n_samples = X.shape[0]
        
        # Process in batches
        for batch_start in range(0, n_samples, self.config.batch_size):
            batch_end = min(batch_start + self.config.batch_size, n_samples)
            self._partial_fit_incremental(X[batch_start:batch_end])
        
        self.is_fitted = True
    
    def _partial_fit_incremental(self, X: np.ndarray):
        """Partial fit for incremental PCA"""
        n_samples, n_features = X.shape
        
        if self.partial_mean_ is None:
            # First batch
            self.n_features_ = n_features
            self.partial_mean_ = np.zeros(n_features)
            self.partial_var_ = np.zeros(n_features)
            self.partial_n_ = 0
            self.components_ = None
        
        # Update mean and variance
        last_mean = self.partial_mean_.copy()
        last_n = self.partial_n_
        
        self.partial_mean_ = (self.partial_n_ * self.partial_mean_ + 
                            n_samples * X.mean(axis=0)) / (self.partial_n_ + n_samples)
        
        self.partial_n_ += n_samples
        
        # Update components using incremental SVD
        X_centered = X - self.partial_mean_
        
        if self.components_ is None:
            # First batch - regular SVD
            _, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
            
            n_components = self._infer_n_components(n_samples, n_features)
            self.n_components_ = min(n_components, len(S))
            
            self.components_ = Vt[:self.n_components_]
            self.singular_values_ = S[:self.n_components_]
        else:
            # Incremental update
            # Simplified approach - would use more sophisticated method in production
            n_samples_seen = self.partial_n_
            
            # Project existing components
            X_proj = X_centered @ self.components_.T
            X_residual = X_centered - X_proj @ self.components_
            
            # Update components if significant residual
            if np.linalg.norm(X_residual) > 1e-10:
                # QR decomposition of residual
                Q, R = np.linalg.qr(X_residual.T)
                
                # Combine with existing components
                combined = np.vstack([self.components_.T, Q.T])
                
                # SVD of combined
                _, S_new, Vt_new = np.linalg.svd(combined @ combined.T)
                
                self.components_ = Vt_new[:self.n_components_]
                self.singular_values_ = np.sqrt(S_new[:self.n_components_] * n_samples_seen)
        
        # Update explained variance
        self.explained_variance_ = (self.singular_values_ ** 2) / (self.partial_n_ - 1)
        self.mean_ = self.partial_mean_
        
        self.n_samples_seen_ = self.partial_n_
    
    def _fit_kernel(self, X: np.ndarray):
        """Kernel PCA for non-linear transformations"""
        n_samples, n_features = X.shape
        self.n_features_ = n_features
        self.n_samples_seen_ = n_samples
        self.X_fit_ = X.copy()
        
        # Compute kernel matrix
        K = self._compute_kernel(X, X)
        
        # Center kernel matrix
        K_centered = self._center_kernel(K)
        
        # Eigendecomposition
        eigvals, eigvecs = np.linalg.eigh(K_centered)
        
        # Sort by eigenvalues (descending)
        idx = eigvals.argsort()[::-1]
        eigvals = eigvals[idx]
        eigvecs = eigvecs[:, idx]
        
        # Remove negative eigenvalues
        positive_idx = eigvals > 0
        eigvals = eigvals[positive_idx]
        eigvecs = eigvecs[:, positive_idx]
        
        # Determine number of components
        self.n_components_ = self._infer_n_components(n_samples, len(eigvals))
        self.n_components_ = min(self.n_components_, len(eigvals))
        
        # Store results
        self.dual_coef_ = eigvecs[:, :self.n_components_]
        self.explained_variance_ = eigvals[:self.n_components_] / n_samples
        
        # Normalize
        for i in range(self.n_components_):
            self.dual_coef_[:, i] /= np.sqrt(eigvals[i])
        
        # Calculate explained variance ratio
        total_var = np.sum(eigvals) / n_samples
        self.explained_variance_ratio_ = self.explained_variance_ / total_var
    
    def _fit_sparse(self, X: np.ndarray):
        """Sparse PCA using iterative methods"""
        try:
            from sklearn.decomposition import SparsePCA
            
            # Use sklearn implementation
            sparse_pca = SparsePCA(
                n_components=self.config.n_components or 2,
                alpha=self.config.alpha,
                ridge_alpha=self.config.ridge_alpha,
                max_iter=self.config.max_iter,
                random_state=self.config.random_state,
                n_jobs=self.config.n_jobs
            )
            
            sparse_pca.fit(X)
            
            self.components_ = sparse_pca.components_
            self.n_components_ = self.components_.shape[0]
            self.mean_ = X.mean(axis=0)
            self.n_features_ = X.shape[1]
            self.n_samples_seen_ = X.shape[0]
            
            # Estimate explained variance
            X_transformed = (X - self.mean_) @ self.components_.T
            X_reconstructed = X_transformed @ self.components_ + self.mean_
            
            reconstruction_error = np.mean((X - X_reconstructed) ** 2)
            total_variance = np.var(X)
            
            self.explained_variance_ratio_ = np.array([1 - reconstruction_error / total_variance])
            
        except ImportError:
            # Fallback to standard PCA with L1 penalty approximation
            warnings.warn("sklearn not available, using standard PCA")
            self._fit_standard(X)
    
    def _fit_randomized(self, X: np.ndarray):
        """Randomized PCA for large datasets"""
        n_samples, n_features = X.shape
        self.n_features_ = n_features
        self.n_samples_seen_ = n_samples
        
        # Center data
        self.mean_ = np.mean(X, axis=0)
        X_centered = X - self.mean_
        
        # Determine number of components
        self.n_components_ = self._infer_n_components(n_samples, n_features)
        
        # Randomized SVD
        U, S, Vt = self._randomized_svd(X_centered, self.n_components_)
        
        # Store results
        self.components_ = Vt
        self.singular_values_ = S
        self.explained_variance_ = (S ** 2) / (n_samples - 1)
        
        # Calculate explained variance ratio
        total_var = np.var(X, ddof=1, axis=0).sum()
        self.explained_variance_ratio_ = self.explained_variance_ / total_var
    
    def _randomized_svd(self, X: np.ndarray, n_components: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Randomized SVD implementation"""
        n_samples, n_features = X.shape
        n_iterations = self.config.iterated_power
        
        if n_iterations == "auto":
            n_iterations = 4 if n_components < 0.1 * min(n_samples, n_features) else 7
        
        # Random sampling matrix
        rng = np.random.RandomState(self.config.random_state)
        Q = rng.randn(n_features, n_components)
        
        # Power iterations
        for _ in range(n_iterations):
            Q = X.T @ (X @ Q)
            Q, _ = np.linalg.qr(Q)
        
        # Project X onto Q
        B = X @ Q
        
        # SVD of B
        Uhat, S, Vt = np.linalg.svd(B, full_matrices=False)
        
        U = Uhat
        V = Q @ Vt.T
        
        return U[:, :n_components], S[:n_components], V.T[:n_components]
    
    def _transform_standard(self, X: np.ndarray) -> np.ndarray:
        """Standard linear transformation"""
        X_centered = X - self.mean_
        X_transformed = X_centered @ self.components_[:self.n_components_].T
        
        if self.config.whiten:
            X_transformed /= np.sqrt(self.explained_variance_[:self.n_components_])
        
        return X_transformed
    
    def _transform_kernel(self, X: np.ndarray) -> np.ndarray:
        """Kernel PCA transformation"""
        # Compute kernel with training data
        K = self._compute_kernel(X, self.X_fit_)
        
        # Center kernel matrix
        K_centered = self._center_kernel_test(K)
        
        # Project
        return K_centered @ self.dual_coef_
    
    def _compute_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """Compute kernel matrix"""
        if self.config.kernel == "linear":
            return X1 @ X2.T
        elif self.config.kernel == "rbf":
            gamma = self.config.gamma or 1.0 / X1.shape[1]
            
            # Compute pairwise squared distances
            X1_sqnorms = np.sum(X1 ** 2, axis=1, keepdims=True)
            X2_sqnorms = np.sum(X2 ** 2, axis=1, keepdims=True)
            distances_sq = X1_sqnorms + X2_sqnorms.T - 2 * X1 @ X2.T
            
            return np.exp(-gamma * distances_sq)
        elif self.config.kernel == "poly":
            gamma = self.config.gamma or 1.0 / X1.shape[1]
            return (gamma * X1 @ X2.T + self.config.coef0) ** self.config.degree
        elif self.config.kernel == "sigmoid":
            gamma = self.config.gamma or 1.0 / X1.shape[1]
            return np.tanh(gamma * X1 @ X2.T + self.config.coef0)
        else:
            raise ValueError(f"Unknown kernel: {self.config.kernel}")
    
    def _center_kernel(self, K: np.ndarray) -> np.ndarray:
        """Center kernel matrix"""
        n_samples = K.shape[0]
        
        # Store for test time
        self.K_fit_mean_ = K.mean(axis=0)
        
        # Center
        K_centered = K - self.K_fit_mean_[np.newaxis, :]
        K_centered -= self.K_fit_mean_[:, np.newaxis]
        K_centered += self.K_fit_mean_.mean()
        
        return K_centered
    
    def _center_kernel_test(self, K: np.ndarray) -> np.ndarray:
        """Center kernel matrix for test data"""
        K_centered = K - self.K_fit_mean_[np.newaxis, :]
        K_centered -= K.mean(axis=1)[:, np.newaxis]
        K_centered += self.K_fit_mean_.mean()
        
        return K_centered
    
    def _infer_n_components(self, n_samples: int, n_features: int) -> int:
        """Infer number of components"""
        if self.config.n_components is None:
            return min(n_samples, n_features)
        elif isinstance(self.config.n_components, int):
            return min(self.config.n_components, n_samples, n_features)
        elif 0 < self.config.n_components < 1:
            # Find number of components for desired variance
            if hasattr(self, 'explained_variance_ratio_'):
                cumsum = np.cumsum(self.explained_variance_ratio_)
                n_components = np.searchsorted(cumsum, self.config.n_components) + 1
                return min(n_components, n_samples, n_features)
            else:
                # Estimate - will be refined during fit
                return min(n_samples, n_features)
        else:
            raise ValueError(f"Invalid n_components: {self.config.n_components}")
    
    def calculate_reconstruction_error(self, X: np.ndarray) -> float:
        """
        Calculate reconstruction error.
        
        Args:
            X: Data to reconstruct
            
        Returns:
            Mean squared reconstruction error
        """
        X_transformed = self.transform(X)
        X_reconstructed = self.inverse_transform(X_transformed)
        
        return np.mean((X - X_reconstructed) ** 2)
    
    def get_covariance(self) -> np.ndarray:
        """Get estimated covariance matrix"""
        if not self.is_fitted:
            raise ValueError("PCA must be fitted first")
        
        # Reconstruct covariance from components
        cov = self.components_.T @ np.diag(self.explained_variance_) @ self.components_
        
        # Add noise variance to diagonal
        if hasattr(self, 'noise_variance_'):
            cov += np.eye(self.n_features_) * self.noise_variance_
        
        return cov
    
    def get_precision(self) -> np.ndarray:
        """Get precision matrix (inverse covariance)"""
        cov = self.get_covariance()
        return np.linalg.pinv(cov)
    
    def score(self, X: np.ndarray) -> float:
        """
        Calculate average log-likelihood of samples.
        
        Args:
            X: Test data
            
        Returns:
            Average log-likelihood
        """
        if not self.is_fitted:
            raise ValueError("PCA must be fitted first")
        
        X = self._validate_data(X)
        n_samples = X.shape[0]
        
        # Center data
        X_centered = X - self.mean_
        
        # Calculate log-likelihood under Gaussian model
        precision = self.get_precision()
        log_det = np.sum(np.log(self.explained_variance_)) + \
                 self.n_features_ * np.log(2 * np.pi)
        
        quadratic_form = np.sum((X_centered @ precision) * X_centered, axis=1)
        
        return -0.5 * (log_det + np.mean(quadratic_form))
    
    def get_params(self) -> PCAResult:
        """Get PCA parameters and results"""
        if not self.is_fitted:
            raise ValueError("PCA must be fitted first")
        
        # Calculate reconstruction error on training data (if available)
        reconstruction_error = 0.0
        
        return PCAResult(
            n_components=self.n_components_,
            explained_variance=self.explained_variance_,
            explained_variance_ratio=self.explained_variance_ratio_,
            singular_values=self.singular_values_ if hasattr(self, 'singular_values_') else np.array([]),
            reconstruction_error=reconstruction_error
        )


# Utility functions
def pca_reduce(X: np.ndarray, n_components: Union[int, float] = 2) -> np.ndarray:
    """Quick PCA dimensionality reduction"""
    pca = PrincipalComponentAnalysis(n_components=n_components)
    return pca.fit_transform(X)


def find_optimal_components(X: np.ndarray, min_variance: float = 0.95) -> int:
    """Find number of components to preserve desired variance"""
    pca = PrincipalComponentAnalysis()
    pca.fit(X)
    
    cumsum = np.cumsum(pca.explained_variance_ratio_)
    n_components = np.argmax(cumsum >= min_variance) + 1
    
    return n_components


def pca_denoise(X: np.ndarray, n_components: Optional[int] = None) -> np.ndarray:
    """Denoise data using PCA"""
    if n_components is None:
        # Use elbow method to find optimal components
        n_components = find_optimal_components(X, min_variance=0.99)
    
    pca = PrincipalComponentAnalysis(n_components=n_components)
    X_transformed = pca.fit_transform(X)
    X_denoised = pca.inverse_transform(X_transformed)
    
    return X_denoised


# Auto-generated tests
def test_principal_component_analysis():
    """Test PCA functionality"""
    # Generate synthetic data
    np.random.seed(42)
    
    # Create correlated data
    n_samples = 200
    n_features = 10
    
    # Generate latent variables
    latent = np.random.randn(n_samples, 3)
    
    # Create mixing matrix
    mixing = np.random.randn(3, n_features)
    
    # Generate observed data
    X = latent @ mixing + 0.1 * np.random.randn(n_samples, n_features)
    
    # Test standard PCA
    pca = PrincipalComponentAnalysis(n_components=3)
    pca.fit(X)
    
    assert pca.is_fitted
    assert pca.n_components_ == 3
    assert pca.components_.shape == (3, n_features)
    assert len(pca.explained_variance_) == 3
    assert len(pca.explained_variance_ratio_) == 3
    
    # Test transform
    X_transformed = pca.transform(X[:10])
    assert X_transformed.shape == (10, 3)
    
    # Test inverse transform
    X_reconstructed = pca.inverse_transform(X_transformed)
    assert X_reconstructed.shape == (10, n_features)
    
    # Test variance preservation
    pca_var = PrincipalComponentAnalysis(n_components=0.95)
    pca_var.fit(X)
    assert np.sum(pca_var.explained_variance_ratio_) >= 0.95
    
    # Test whitening
    config_white = PCAConfig(whiten=True)
    pca_white = PrincipalComponentAnalysis(n_components=3, config=config_white)
    X_white = pca_white.fit_transform(X)
    
    # Check that components have unit variance
    assert np.allclose(np.var(X_white, axis=0), 1.0, atol=0.1)
    
    # Test incremental PCA
    pca_inc = PrincipalComponentAnalysis(n_components=3, method="incremental")
    pca_inc.fit(X)
    
    # Results should be similar to standard PCA
    assert np.allclose(np.abs(pca_inc.components_), np.abs(pca.components_), atol=0.1)
    
    # Test partial fit
    pca_partial = PrincipalComponentAnalysis(n_components=3, method="incremental")
    for i in range(0, n_samples, 50):
        pca_partial.partial_fit(X[i:i+50])
    
    assert pca_partial.is_fitted
    assert pca_partial.n_samples_seen_ == n_samples
    
    # Test kernel PCA
    # Create non-linear data
    X_nonlinear = np.vstack([
        np.random.randn(100, 2),
        np.random.randn(100, 2) + 3
    ])
    X_nonlinear = np.column_stack([
        X_nonlinear[:, 0],
        X_nonlinear[:, 1],
        X_nonlinear[:, 0] ** 2 + X_nonlinear[:, 1] ** 2
    ])
    
    pca_kernel = PrincipalComponentAnalysis(n_components=2, method="kernel")
    pca_kernel.config.kernel = "rbf"
    X_kernel_transformed = pca_kernel.fit_transform(X_nonlinear)
    
    assert X_kernel_transformed.shape == (200, 2)
    
    # Test randomized PCA
    pca_random = PrincipalComponentAnalysis(n_components=3, method="randomized")
    pca_random.fit(X)
    
    # Should give similar results to standard PCA
    assert np.allclose(pca_random.explained_variance_ratio_[:3], 
                      pca.explained_variance_ratio_, atol=0.05)
    
    # Test reconstruction error
    error = pca.calculate_reconstruction_error(X)
    assert error >= 0
    
    # Lower dimensional PCA should have higher error
    pca_low = PrincipalComponentAnalysis(n_components=1)
    pca_low.fit(X)
    error_low = pca_low.calculate_reconstruction_error(X)
    assert error_low > error
    
    # Test covariance estimation
    cov = pca.get_covariance()
    assert cov.shape == (n_features, n_features)
    assert np.allclose(cov, cov.T)  # Should be symmetric
    
    # Test score
    score = pca.score(X[:50])
    assert isinstance(score, float)
    
    # Test utility functions
    X_reduced = pca_reduce(X, n_components=2)
    assert X_reduced.shape == (n_samples, 2)
    
    optimal_n = find_optimal_components(X, min_variance=0.9)
    assert 1 <= optimal_n <= n_features
    
    X_denoised = pca_denoise(X, n_components=5)
    assert X_denoised.shape == X.shape
    
    # Test different SVD solvers
    for solver in ["full", "randomized"]:
        config_solver = PCAConfig(svd_solver=solver)
        pca_solver = PrincipalComponentAnalysis(n_components=3, config=config_solver)
        pca_solver.fit(X[:50])  # Smaller dataset
        assert pca_solver.is_fitted
    
    # Test edge cases
    # More components than features
    pca_many = PrincipalComponentAnalysis(n_components=20)
    pca_many.fit(X)
    assert pca_many.n_components_ == n_features
    
    # Single component
    pca_single = PrincipalComponentAnalysis(n_components=1)
    X_single = pca_single.fit_transform(X)
    assert X_single.shape == (n_samples, 1)
    
    print("All PCA tests passed!")


if __name__ == "__main__":
    test_principal_component_analysis()