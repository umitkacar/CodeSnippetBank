"""
Clustering Snippets
Production-ready examples for unsupervised clustering
"""

from sklearn.cluster import (KMeans, DBSCAN, AgglomerativeClustering,
                             MeanShift, SpectralClustering, Birch)
from sklearn.mixture import GaussianMixture
import numpy as np


def kmeans_clustering(X, n_clusters=3):
    """Perform K-Means clustering"""
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    return labels, kmeans


def kmeans_with_elbow_method(X, max_clusters=10):
    """Find optimal K using elbow method"""
    inertias = []
    K_range = range(1, max_clusters + 1)

    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X)
        inertias.append(kmeans.inertia_)

    return K_range, inertias


def dbscan_clustering(X, eps=0.5, min_samples=5):
    """Perform DBSCAN clustering (density-based)"""
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X)
    return labels, dbscan


def hierarchical_clustering(X, n_clusters=3, linkage='ward'):
    """Perform hierarchical (agglomerative) clustering"""
    agg_clustering = AgglomerativeClustering(
        n_clusters=n_clusters,
        linkage=linkage
    )
    labels = agg_clustering.fit_predict(X)
    return labels, agg_clustering


def mean_shift_clustering(X, bandwidth=None):
    """Perform Mean Shift clustering"""
    if bandwidth is None:
        from sklearn.cluster import estimate_bandwidth
        bandwidth = estimate_bandwidth(X, quantile=0.2)

    mean_shift = MeanShift(bandwidth=bandwidth)
    labels = mean_shift.fit_predict(X)
    return labels, mean_shift


def gaussian_mixture_clustering(X, n_components=3):
    """Perform Gaussian Mixture Model clustering"""
    gmm = GaussianMixture(n_components=n_components, random_state=42)
    labels = gmm.fit_predict(X)
    return labels, gmm


def spectral_clustering(X, n_clusters=3):
    """Perform spectral clustering"""
    spectral = SpectralClustering(
        n_clusters=n_clusters,
        affinity='nearest_neighbors',
        random_state=42
    )
    labels = spectral.fit_predict(X)
    return labels, spectral


def birch_clustering(X, n_clusters=3):
    """Perform BIRCH clustering (memory-efficient)"""
    birch = Birch(n_clusters=n_clusters)
    labels = birch.fit_predict(X)
    return labels, birch


def silhouette_score_evaluation(X, labels):
    """Calculate silhouette score for clustering evaluation"""
    from sklearn.metrics import silhouette_score
    score = silhouette_score(X, labels)
    return score


def davies_bouldin_score_evaluation(X, labels):
    """Calculate Davies-Bouldin score (lower is better)"""
    from sklearn.metrics import davies_bouldin_score
    score = davies_bouldin_score(X, labels)
    return score


def calinski_harabasz_score_evaluation(X, labels):
    """Calculate Calinski-Harabasz score (higher is better)"""
    from sklearn.metrics import calinski_harabasz_score
    score = calinski_harabasz_score(X, labels)
    return score


def find_optimal_clusters_silhouette(X, max_clusters=10):
    """Find optimal number of clusters using silhouette score"""
    from sklearn.metrics import silhouette_score

    silhouette_scores = []
    K_range = range(2, max_clusters + 1)

    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        score = silhouette_score(X, labels)
        silhouette_scores.append(score)

    return K_range, silhouette_scores


def mini_batch_kmeans(X, n_clusters=3, batch_size=100):
    """Perform Mini-Batch K-Means (faster for large datasets)"""
    from sklearn.cluster import MiniBatchKMeans

    mbk = MiniBatchKMeans(
        n_clusters=n_clusters,
        batch_size=batch_size,
        random_state=42
    )
    labels = mbk.fit_predict(X)
    return labels, mbk


def affinity_propagation_clustering(X):
    """Perform Affinity Propagation clustering"""
    from sklearn.cluster import AffinityPropagation

    ap = AffinityPropagation(random_state=42)
    labels = ap.fit_predict(X)
    return labels, ap


def optics_clustering(X, min_samples=5):
    """Perform OPTICS clustering"""
    from sklearn.cluster import OPTICS

    optics = OPTICS(min_samples=min_samples)
    labels = optics.fit_predict(X)
    return labels, optics


def hierarchical_dendrogram(X):
    """Create dendrogram for hierarchical clustering"""
    from scipy.cluster.hierarchy import dendrogram, linkage
    import matplotlib.pyplot as plt

    linkage_matrix = linkage(X, method='ward')

    plt.figure(figsize=(12, 8))
    dendrogram(linkage_matrix)
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('Sample Index')
    plt.ylabel('Distance')
    plt.show()

    return linkage_matrix


def cluster_centers_analysis(X, labels, n_clusters):
    """Analyze cluster centers and statistics"""
    centers = []
    sizes = []

    for i in range(n_clusters):
        cluster_points = X[labels == i]
        centers.append(cluster_points.mean(axis=0))
        sizes.append(len(cluster_points))

    return np.array(centers), sizes


def outlier_detection_with_clustering(X, contamination=0.1):
    """Detect outliers using clustering-based methods"""
    from sklearn.ensemble import IsolationForest

    iso_forest = IsolationForest(contamination=contamination, random_state=42)
    outlier_labels = iso_forest.fit_predict(X)
    return outlier_labels
