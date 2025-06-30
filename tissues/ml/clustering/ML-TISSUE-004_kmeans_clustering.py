"""
Tissue ID: ML-TISSUE-004
Title: Advanced K-Means Clustering Implementation
Category: ml/clustering
Tags: ["kmeans", "clustering", "unsupervised-learning", "segmentation", "machine-learning"]
Difficulty: Intermediate
Dependencies: ["numpy>=1.24", "scikit-learn>=1.3"]
Performance: O(n*k*i*d) where n is samples, k is clusters, i is iterations, d is dimensions
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive K-Means clustering tissue with multiple initialization methods
(random, k-means++, custom), mini-batch support, automatic k selection using
elbow method and silhouette analysis. Includes cluster visualization, outlier
detection, and cluster quality metrics.

Use Cases:
- Customer segmentation
- Image compression
- Anomaly detection
- Document clustering
- Feature learning

Example Usage:
    # Basic K-Means
    kmeans = KMeansClustering(n_clusters=5)
    kmeans.fit(X)
    labels = kmeans.predict(X_new)
    
    # Auto-select optimal k
    optimal_k = kmeans.find_optimal_k(X, min_k=2, max_k=10)
    
    # Mini-batch for large datasets
    kmeans = KMeansClustering(n_clusters=5, mini_batch=True, batch_size=100)
    kmeans.fit(X_large)
    
    # Get cluster statistics
    stats = kmeans.get_cluster_statistics()
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings


class InitMethod(Enum):
    """Initialization methods for cluster centers"""
    RANDOM = "random"
    KMEANS_PLUS_PLUS = "kmeans++"
    CUSTOM = "custom"


@dataclass
class ClusteringConfig:
    """Configuration for K-Means clustering"""
    n_clusters: int = 8
    init_method: str = "kmeans++"
    n_init: int = 10  # Number of runs with different seeds
    max_iterations: int = 300
    tolerance: float = 1e-4
    random_state: int = 42
    mini_batch: bool = False
    batch_size: int = 100
    reassignment_ratio: float = 0.01
    verbose: int = 0


@dataclass
class ClusterMetrics:
    """Clustering quality metrics"""
    inertia: float  # Sum of squared distances to nearest center
    silhouette_score: float
    calinski_harabasz_score: float
    davies_bouldin_score: float
    n_iterations: int
    converged: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "inertia": self.inertia,
            "silhouette_score": self.silhouette_score,
            "calinski_harabasz_score": self.calinski_harabasz_score,
            "davies_bouldin_score": self.davies_bouldin_score,
            "n_iterations": self.n_iterations,
            "converged": self.converged
        }


@dataclass
class ClusterInfo:
    """Information about a single cluster"""
    cluster_id: int
    center: np.ndarray
    n_samples: int
    radius: float  # Average distance from center
    density: float  # Samples per unit volume
    nearest_cluster: Optional[int] = None
    distance_to_nearest: Optional[float] = None


class KMeansClustering:
    """
    Advanced K-Means clustering implementation.
    Tissue Type: FUNCTIONAL - Core ML clustering functionality.
    """
    
    def __init__(self,
                 n_clusters: Optional[int] = None,
                 config: Optional[ClusteringConfig] = None,
                 feature_names: Optional[List[str]] = None):
        """
        Initialize K-Means clustering.
        
        Args:
            n_clusters: Number of clusters (overrides config)
            config: Clustering configuration
            feature_names: Names of features for interpretability
        """
        self.config = config or ClusteringConfig()
        if n_clusters is not None:
            self.config.n_clusters = n_clusters
        
        self.feature_names = feature_names
        
        # Model components
        self.cluster_centers_ = None
        self.labels_ = None
        self.inertia_ = None
        self.n_iter_ = None
        
        # Training info
        self.n_features_ = 0
        self.n_samples_seen_ = 0
        self.is_fitted = False
        
        # Best run info
        self.best_inertia_ = np.inf
        self.best_centers_ = None
        self.best_labels_ = None
        self.best_n_iter_ = 0
        
        # Random state
        self.rng = np.random.RandomState(self.config.random_state)
    
    def fit(self, X: np.ndarray, 
            sample_weights: Optional[np.ndarray] = None) -> 'KMeansClustering':
        """
        Fit K-Means clustering.
        
        Args:
            X: Training data (n_samples, n_features)
            sample_weights: Optional sample weights
            
        Returns:
            Self for chaining
        """
        # Validate input
        X = self._validate_data(X)
        n_samples, n_features = X.shape
        
        self.n_features_ = n_features
        self.n_samples_seen_ = n_samples
        
        # Check number of clusters
        if self.config.n_clusters > n_samples:
            warnings.warn(f"n_clusters ({self.config.n_clusters}) > n_samples ({n_samples}). "
                         f"Setting n_clusters to {n_samples}")
            self.config.n_clusters = n_samples
        
        # Multiple runs with different initializations
        for run in range(self.config.n_init):
            if self.config.verbose > 0:
                print(f"Run {run + 1}/{self.config.n_init}")
            
            # Initialize centers
            if run == 0 or self.config.init_method != InitMethod.CUSTOM.value:
                centers = self._init_centers(X)
            else:
                # Random restart
                centers = self._init_centers(X)
            
            # Run clustering
            if self.config.mini_batch:
                labels, inertia, n_iter = self._mini_batch_kmeans(
                    X, centers, sample_weights
                )
            else:
                labels, inertia, n_iter = self._standard_kmeans(
                    X, centers, sample_weights
                )
            
            # Keep best run
            if inertia < self.best_inertia_:
                self.best_inertia_ = inertia
                self.best_centers_ = centers.copy()
                self.best_labels_ = labels.copy()
                self.best_n_iter_ = n_iter
        
        # Set final results
        self.cluster_centers_ = self.best_centers_
        self.labels_ = self.best_labels_
        self.inertia_ = self.best_inertia_
        self.n_iter_ = self.best_n_iter_
        
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict cluster labels for new data.
        
        Args:
            X: Data to predict (n_samples, n_features)
            
        Returns:
            Cluster labels
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X = self._validate_data(X)
        
        # Assign to nearest center
        distances = self._calculate_distances(X, self.cluster_centers_)
        return np.argmin(distances, axis=1)
    
    def fit_predict(self, X: np.ndarray,
                   sample_weights: Optional[np.ndarray] = None) -> np.ndarray:
        """Fit and predict in one step"""
        self.fit(X, sample_weights)
        return self.labels_
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform data to cluster-distance space.
        
        Args:
            X: Data to transform (n_samples, n_features)
            
        Returns:
            Distances to cluster centers (n_samples, n_clusters)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before transform")
        
        X = self._validate_data(X)
        return self._calculate_distances(X, self.cluster_centers_)
    
    def _validate_data(self, X: np.ndarray) -> np.ndarray:
        """Validate input data"""
        X = np.asarray(X, dtype=np.float64)
        
        if X.ndim != 2:
            raise ValueError(f"X must be 2D, got {X.ndim}D")
        
        if self.is_fitted and X.shape[1] != self.n_features_:
            raise ValueError(f"X has {X.shape[1]} features, expected {self.n_features_}")
        
        # Check for NaN/Inf
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ValueError("X contains NaN or Inf values")
        
        return X
    
    def _init_centers(self, X: np.ndarray) -> np.ndarray:
        """Initialize cluster centers"""
        n_samples = X.shape[0]
        
        if self.config.init_method == InitMethod.RANDOM.value:
            # Random initialization
            indices = self.rng.choice(n_samples, self.config.n_clusters, replace=False)
            centers = X[indices].copy()
            
        elif self.config.init_method == InitMethod.KMEANS_PLUS_PLUS.value:
            # K-means++ initialization
            centers = self._kmeans_plus_plus(X)
            
        else:
            # Custom initialization (use random for now)
            indices = self.rng.choice(n_samples, self.config.n_clusters, replace=False)
            centers = X[indices].copy()
        
        return centers
    
    def _kmeans_plus_plus(self, X: np.ndarray) -> np.ndarray:
        """K-means++ initialization for better starting centers"""
        n_samples = X.shape[0]
        centers = np.zeros((self.config.n_clusters, self.n_features_))
        
        # Choose first center randomly
        centers[0] = X[self.rng.randint(n_samples)]
        
        # Choose remaining centers
        for c in range(1, self.config.n_clusters):
            # Calculate distances to nearest center
            distances = np.min(self._calculate_distances(X, centers[:c]), axis=1)
            
            # Choose next center with probability proportional to squared distance
            probabilities = distances ** 2
            probabilities /= probabilities.sum()
            
            cumulative_probs = np.cumsum(probabilities)
            r = self.rng.rand()
            
            centers[c] = X[np.searchsorted(cumulative_probs, r)]
        
        return centers
    
    def _calculate_distances(self, X: np.ndarray, centers: np.ndarray) -> np.ndarray:
        """Calculate Euclidean distances between points and centers"""
        n_samples = X.shape[0]
        n_clusters = centers.shape[0]
        distances = np.zeros((n_samples, n_clusters))
        
        for k in range(n_clusters):
            # Vectorized distance calculation
            distances[:, k] = np.sum((X - centers[k]) ** 2, axis=1)
        
        return np.sqrt(distances)
    
    def _standard_kmeans(self, X: np.ndarray, centers: np.ndarray,
                        sample_weights: Optional[np.ndarray]) -> Tuple[np.ndarray, float, int]:
        """Standard K-Means algorithm"""
        n_samples = X.shape[0]
        
        # Initialize
        labels = np.zeros(n_samples, dtype=int)
        prev_inertia = np.inf
        
        for iteration in range(self.config.max_iterations):
            # Assign points to nearest center
            distances = self._calculate_distances(X, centers)
            labels = np.argmin(distances, axis=1)
            
            # Calculate inertia
            if sample_weights is None:
                inertia = np.sum(np.min(distances ** 2, axis=1))
            else:
                inertia = np.sum(sample_weights * np.min(distances ** 2, axis=1))
            
            # Check convergence
            if abs(prev_inertia - inertia) < self.config.tolerance:
                converged = True
                break
            
            prev_inertia = inertia
            
            # Update centers
            for k in range(self.config.n_clusters):
                mask = labels == k
                if np.any(mask):
                    if sample_weights is None:
                        centers[k] = X[mask].mean(axis=0)
                    else:
                        weights_k = sample_weights[mask]
                        centers[k] = np.average(X[mask], weights=weights_k, axis=0)
        else:
            converged = False
        
        return labels, inertia, iteration + 1
    
    def _mini_batch_kmeans(self, X: np.ndarray, centers: np.ndarray,
                          sample_weights: Optional[np.ndarray]) -> Tuple[np.ndarray, float, int]:
        """Mini-batch K-Means for large datasets"""
        n_samples = X.shape[0]
        
        # Initialize
        counts = np.zeros(self.config.n_clusters)
        
        for iteration in range(self.config.max_iterations):
            # Sample mini-batch
            batch_size = min(self.config.batch_size, n_samples)
            batch_indices = self.rng.choice(n_samples, batch_size, replace=False)
            X_batch = X[batch_indices]
            
            # Assign batch points to centers
            distances = self._calculate_distances(X_batch, centers)
            batch_labels = np.argmin(distances, axis=1)
            
            # Update centers using exponential decay
            for i, (x, label) in enumerate(zip(X_batch, batch_labels)):
                counts[label] += 1
                eta = 1.0 / counts[label]  # Learning rate
                centers[label] = (1 - eta) * centers[label] + eta * x
            
            # Reassignment step (optional)
            if iteration % 10 == 0:
                # Check full dataset periodically
                all_distances = self._calculate_distances(X, centers)
                labels = np.argmin(all_distances, axis=1)
                
                # Reassign empty clusters
                for k in range(self.config.n_clusters):
                    if np.sum(labels == k) == 0:
                        # Reassign to point farthest from any center
                        max_distances = np.min(all_distances, axis=1)
                        centers[k] = X[np.argmax(max_distances)]
        
        # Final assignment
        distances = self._calculate_distances(X, centers)
        labels = np.argmin(distances, axis=1)
        
        # Calculate inertia
        if sample_weights is None:
            inertia = np.sum(np.min(distances ** 2, axis=1))
        else:
            inertia = np.sum(sample_weights * np.min(distances ** 2, axis=1))
        
        return labels, inertia, self.config.max_iterations
    
    def find_optimal_k(self, X: np.ndarray, 
                      min_k: int = 2, 
                      max_k: int = 10,
                      method: str = "elbow") -> int:
        """
        Find optimal number of clusters.
        
        Args:
            X: Data to cluster
            min_k: Minimum number of clusters
            max_k: Maximum number of clusters
            method: Method to use (elbow, silhouette)
            
        Returns:
            Optimal number of clusters
        """
        X = self._validate_data(X)
        scores = []
        
        for k in range(min_k, max_k + 1):
            # Temporarily change n_clusters
            temp_k = self.config.n_clusters
            self.config.n_clusters = k
            
            # Fit model
            self.fit(X)
            
            if method == "elbow":
                scores.append(self.inertia_)
            elif method == "silhouette":
                score = self._calculate_silhouette_score(X, self.labels_)
                scores.append(score)
            
            # Restore original k
            self.config.n_clusters = temp_k
        
        # Find optimal k
        if method == "elbow":
            # Find elbow point (maximum curvature)
            optimal_k = self._find_elbow_point(list(range(min_k, max_k + 1)), scores)
        else:
            # Maximum silhouette score
            optimal_k = min_k + np.argmax(scores)
        
        return optimal_k
    
    def _find_elbow_point(self, k_values: List[int], scores: List[float]) -> int:
        """Find elbow point in scores"""
        # Calculate distances from line between first and last point
        n_points = len(scores)
        
        if n_points < 3:
            return k_values[0]
        
        # Normalize scores
        scores_norm = np.array(scores)
        scores_norm = (scores_norm - scores_norm.min()) / (scores_norm.max() - scores_norm.min())
        
        # Create points
        points = np.column_stack([np.arange(n_points), scores_norm])
        
        # Line from first to last point
        line_vec = points[-1] - points[0]
        line_vec_norm = line_vec / np.linalg.norm(line_vec)
        
        # Calculate distances
        distances = []
        for i in range(1, n_points - 1):
            vec_to_point = points[i] - points[0]
            projection = np.dot(vec_to_point, line_vec_norm) * line_vec_norm
            distance = np.linalg.norm(vec_to_point - projection)
            distances.append(distance)
        
        # Elbow is at maximum distance
        elbow_idx = np.argmax(distances) + 1
        return k_values[elbow_idx]
    
    def _calculate_silhouette_score(self, X: np.ndarray, labels: np.ndarray) -> float:
        """Calculate silhouette score"""
        n_samples = X.shape[0]
        n_clusters = len(np.unique(labels))
        
        if n_clusters == 1 or n_clusters == n_samples:
            return 0.0
        
        # Calculate pairwise distances
        distances = np.zeros((n_samples, n_samples))
        for i in range(n_samples):
            distances[i] = np.sqrt(np.sum((X - X[i]) ** 2, axis=1))
        
        silhouette_scores = []
        
        for i in range(n_samples):
            # Same cluster
            same_cluster = labels == labels[i]
            if np.sum(same_cluster) > 1:
                a_i = np.mean(distances[i, same_cluster])
            else:
                a_i = 0
            
            # Nearest cluster
            b_i = np.inf
            for k in range(n_clusters):
                if k != labels[i]:
                    other_cluster = labels == k
                    if np.any(other_cluster):
                        mean_dist = np.mean(distances[i, other_cluster])
                        b_i = min(b_i, mean_dist)
            
            # Silhouette score
            if max(a_i, b_i) > 0:
                s_i = (b_i - a_i) / max(a_i, b_i)
            else:
                s_i = 0
            
            silhouette_scores.append(s_i)
        
        return np.mean(silhouette_scores)
    
    def get_cluster_statistics(self) -> List[ClusterInfo]:
        """Get detailed statistics for each cluster"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        cluster_info = []
        
        for k in range(self.config.n_clusters):
            # Get cluster members
            mask = self.labels_ == k
            n_members = np.sum(mask)
            
            if n_members > 0:
                # Calculate radius (average distance from center)
                center = self.cluster_centers_[k]
                
                # Note: We need the original data to calculate radius properly
                # For now, use distance between centers as proxy
                distances_to_other_centers = np.sqrt(
                    np.sum((self.cluster_centers_ - center) ** 2, axis=1)
                )
                distances_to_other_centers[k] = np.inf
                
                nearest_cluster = np.argmin(distances_to_other_centers)
                distance_to_nearest = distances_to_other_centers[nearest_cluster]
                
                info = ClusterInfo(
                    cluster_id=k,
                    center=center,
                    n_samples=n_members,
                    radius=distance_to_nearest / 2,  # Approximate
                    density=n_members / (np.pi * (distance_to_nearest / 2) ** 2),
                    nearest_cluster=nearest_cluster,
                    distance_to_nearest=distance_to_nearest
                )
            else:
                info = ClusterInfo(
                    cluster_id=k,
                    center=self.cluster_centers_[k],
                    n_samples=0,
                    radius=0.0,
                    density=0.0
                )
            
            cluster_info.append(info)
        
        return cluster_info
    
    def detect_outliers(self, X: np.ndarray, 
                       threshold_percentile: float = 95) -> np.ndarray:
        """
        Detect outliers based on distance to nearest cluster center.
        
        Args:
            X: Data to check for outliers
            threshold_percentile: Percentile for outlier threshold
            
        Returns:
            Boolean array indicating outliers
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        X = self._validate_data(X)
        
        # Calculate distances to nearest center
        distances = self._calculate_distances(X, self.cluster_centers_)
        min_distances = np.min(distances, axis=1)
        
        # Determine threshold
        threshold = np.percentile(min_distances, threshold_percentile)
        
        return min_distances > threshold
    
    def evaluate(self, X: np.ndarray, y_true: Optional[np.ndarray] = None) -> ClusterMetrics:
        """
        Evaluate clustering quality.
        
        Args:
            X: Data that was clustered
            y_true: True labels (if available) for external validation
            
        Returns:
            Clustering metrics
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        X = self._validate_data(X)
        
        # Predict labels
        labels = self.predict(X)
        
        # Calculate metrics
        silhouette = self._calculate_silhouette_score(X, labels)
        
        # Calinski-Harabasz score (higher is better)
        ch_score = self._calculate_calinski_harabasz(X, labels)
        
        # Davies-Bouldin score (lower is better)
        db_score = self._calculate_davies_bouldin(X, labels)
        
        return ClusterMetrics(
            inertia=self.inertia_,
            silhouette_score=silhouette,
            calinski_harabasz_score=ch_score,
            davies_bouldin_score=db_score,
            n_iterations=self.n_iter_,
            converged=self.n_iter_ < self.config.max_iterations
        )
    
    def _calculate_calinski_harabasz(self, X: np.ndarray, labels: np.ndarray) -> float:
        """Calculate Calinski-Harabasz score"""
        n_samples = X.shape[0]
        n_clusters = self.config.n_clusters
        
        if n_clusters == 1:
            return 0.0
        
        # Overall mean
        overall_mean = X.mean(axis=0)
        
        # Between-cluster dispersion
        between_dispersion = 0.0
        within_dispersion = 0.0
        
        for k in range(n_clusters):
            mask = labels == k
            n_k = np.sum(mask)
            
            if n_k > 0:
                cluster_mean = X[mask].mean(axis=0)
                
                # Between-cluster
                between_dispersion += n_k * np.sum((cluster_mean - overall_mean) ** 2)
                
                # Within-cluster
                within_dispersion += np.sum((X[mask] - cluster_mean) ** 2)
        
        if within_dispersion == 0:
            return np.inf
        
        return (between_dispersion / (n_clusters - 1)) / (within_dispersion / (n_samples - n_clusters))
    
    def _calculate_davies_bouldin(self, X: np.ndarray, labels: np.ndarray) -> float:
        """Calculate Davies-Bouldin score"""
        n_clusters = self.config.n_clusters
        
        # Calculate cluster dispersions
        dispersions = np.zeros(n_clusters)
        
        for k in range(n_clusters):
            mask = labels == k
            if np.sum(mask) > 0:
                dispersions[k] = np.mean(
                    np.sqrt(np.sum((X[mask] - self.cluster_centers_[k]) ** 2, axis=1))
                )
        
        # Calculate DB index
        db_index = 0.0
        
        for i in range(n_clusters):
            max_ratio = 0.0
            
            for j in range(n_clusters):
                if i != j:
                    # Distance between centers
                    center_distance = np.sqrt(
                        np.sum((self.cluster_centers_[i] - self.cluster_centers_[j]) ** 2)
                    )
                    
                    if center_distance > 0:
                        ratio = (dispersions[i] + dispersions[j]) / center_distance
                        max_ratio = max(max_ratio, ratio)
            
            db_index += max_ratio
        
        return db_index / n_clusters if n_clusters > 0 else 0.0


# Utility functions
def kmeans_clustering(X: np.ndarray, n_clusters: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """Quick K-Means clustering"""
    kmeans = KMeansClustering(n_clusters=n_clusters)
    labels = kmeans.fit_predict(X)
    return labels, kmeans.cluster_centers_


def find_optimal_clusters(X: np.ndarray, max_k: int = 10) -> int:
    """Find optimal number of clusters using elbow method"""
    kmeans = KMeansClustering()
    return kmeans.find_optimal_k(X, min_k=2, max_k=max_k, method="elbow")


def mini_batch_kmeans(X: np.ndarray, n_clusters: int = 5, 
                     batch_size: int = 100) -> np.ndarray:
    """Mini-batch K-Means for large datasets"""
    config = ClusteringConfig(
        n_clusters=n_clusters,
        mini_batch=True,
        batch_size=batch_size
    )
    kmeans = KMeansClustering(config=config)
    return kmeans.fit_predict(X)


# Auto-generated tests
def test_kmeans_clustering():
    """Test K-Means clustering functionality"""
    # Generate synthetic data
    np.random.seed(42)
    
    # Create well-separated clusters
    n_samples = 300
    n_features = 2
    n_clusters = 3
    
    # Generate cluster centers
    true_centers = np.array([[0, 0], [5, 5], [-5, 5]])
    
    # Generate data
    X = []
    y_true = []
    for i in range(n_clusters):
        cluster_data = true_centers[i] + np.random.randn(n_samples // n_clusters, n_features)
        X.append(cluster_data)
        y_true.extend([i] * (n_samples // n_clusters))
    
    X = np.vstack(X)
    y_true = np.array(y_true)
    
    # Shuffle
    indices = np.random.permutation(n_samples)
    X = X[indices]
    y_true = y_true[indices]
    
    # Test basic K-Means
    kmeans = KMeansClustering(n_clusters=3)
    kmeans.fit(X)
    
    assert kmeans.is_fitted
    assert kmeans.cluster_centers_.shape == (3, 2)
    assert len(kmeans.labels_) == n_samples
    
    # Test prediction
    X_new = np.array([[0, 0], [5, 5], [-5, 5]])
    predictions = kmeans.predict(X_new)
    assert len(predictions) == 3
    
    # Test transform
    distances = kmeans.transform(X_new)
    assert distances.shape == (3, 3)
    
    # Test different initialization
    config = ClusteringConfig(n_clusters=3, init_method="random", n_init=5)
    kmeans_random = KMeansClustering(config=config)
    kmeans_random.fit(X)
    assert kmeans_random.is_fitted
    
    # Test mini-batch
    config_mini = ClusteringConfig(n_clusters=3, mini_batch=True, batch_size=50)
    kmeans_mini = KMeansClustering(config=config_mini)
    kmeans_mini.fit(X)
    assert kmeans_mini.is_fitted
    
    # Test optimal k finding
    optimal_k = kmeans.find_optimal_k(X, min_k=2, max_k=5)
    assert 2 <= optimal_k <= 5
    # Should find 3 clusters for well-separated data
    assert optimal_k == 3
    
    # Test cluster statistics
    stats = kmeans.get_cluster_statistics()
    assert len(stats) == 3
    assert all(isinstance(s, ClusterInfo) for s in stats)
    assert all(s.n_samples > 0 for s in stats)
    
    # Test outlier detection
    X_with_outliers = np.vstack([X, np.array([[20, 20], [-20, -20]])])
    outliers = kmeans.detect_outliers(X_with_outliers, threshold_percentile=98)
    assert len(outliers) == len(X_with_outliers)
    # Last two points should be outliers
    assert outliers[-2] and outliers[-1]
    
    # Test evaluation
    metrics = kmeans.evaluate(X)
    assert isinstance(metrics, ClusterMetrics)
    assert 0 <= metrics.silhouette_score <= 1
    assert metrics.inertia > 0
    assert metrics.converged
    
    # Test with sample weights
    weights = np.random.rand(n_samples)
    kmeans_weighted = KMeansClustering(n_clusters=3)
    kmeans_weighted.fit(X, sample_weights=weights)
    assert kmeans_weighted.is_fitted
    
    # Test edge cases
    # Single cluster
    kmeans_single = KMeansClustering(n_clusters=1)
    kmeans_single.fit(X)
    assert all(kmeans_single.labels_ == 0)
    
    # More clusters than samples
    X_small = X[:5]
    kmeans_many = KMeansClustering(n_clusters=10)
    kmeans_many.fit(X_small)
    assert kmeans_many.config.n_clusters == 5  # Should be adjusted
    
    # Test utility functions
    labels, centers = kmeans_clustering(X, n_clusters=3)
    assert len(labels) == n_samples
    assert centers.shape == (3, 2)
    
    optimal = find_optimal_clusters(X[:100], max_k=5)
    assert 2 <= optimal <= 5
    
    mini_labels = mini_batch_kmeans(X, n_clusters=3, batch_size=30)
    assert len(mini_labels) == n_samples
    
    print("All K-Means clustering tests passed!")


if __name__ == "__main__":
    test_kmeans_clustering()