"""
Dimensionality Reduction Snippets
Production-ready examples for reducing feature dimensions
"""

from sklearn.decomposition import PCA, TruncatedSVD, FastICA, NMF
from sklearn.manifold import TSNE, MDS, Isomap, LocallyLinearEmbedding
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import numpy as np


def pca_reduction(X, n_components=2):
    """Perform PCA dimensionality reduction"""
    pca = PCA(n_components=n_components, random_state=42)
    X_reduced = pca.fit_transform(X)
    return X_reduced, pca


def pca_variance_ratio(X, n_components=None):
    """Analyze explained variance ratio"""
    pca = PCA(n_components=n_components)
    pca.fit(X)

    explained_variance = pca.explained_variance_ratio_
    cumulative_variance = np.cumsum(explained_variance)

    return explained_variance, cumulative_variance


def pca_95_variance(X):
    """Keep components explaining 95% variance"""
    pca = PCA(n_components=0.95, random_state=42)
    X_reduced = pca.fit_transform(X)
    return X_reduced, pca


def incremental_pca(X, n_components=2, batch_size=100):
    """Incremental PCA for large datasets"""
    from sklearn.decomposition import IncrementalPCA

    ipca = IncrementalPCA(n_components=n_components, batch_size=batch_size)
    X_reduced = ipca.fit_transform(X)
    return X_reduced, ipca


def kernel_pca(X, n_components=2, kernel='rbf'):
    """Kernel PCA for non-linear dimensionality reduction"""
    from sklearn.decomposition import KernelPCA

    kpca = KernelPCA(n_components=n_components, kernel=kernel, random_state=42)
    X_reduced = kpca.fit_transform(X)
    return X_reduced, kpca


def tsne_reduction(X, n_components=2, perplexity=30):
    """t-SNE dimensionality reduction (good for visualization)"""
    tsne = TSNE(n_components=n_components, perplexity=perplexity,
                random_state=42, n_jobs=-1)
    X_reduced = tsne.fit_transform(X)
    return X_reduced, tsne


def umap_reduction(X, n_components=2, n_neighbors=15):
    """UMAP dimensionality reduction"""
    try:
        from umap import UMAP
    except ImportError:
        raise ImportError("umap-learn not installed. Install with: pip install umap-learn")

    umap = UMAP(n_components=n_components, n_neighbors=n_neighbors,
                random_state=42)
    X_reduced = umap.fit_transform(X)
    return X_reduced, umap


def truncated_svd(X, n_components=2):
    """Truncated SVD (LSA for text data)"""
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    X_reduced = svd.fit_transform(X)
    return X_reduced, svd


def lda_reduction(X, y, n_components=2):
    """Linear Discriminant Analysis (supervised)"""
    lda = LinearDiscriminantAnalysis(n_components=n_components)
    X_reduced = lda.fit_transform(X, y)
    return X_reduced, lda


def ica_reduction(X, n_components=2):
    """Independent Component Analysis"""
    ica = FastICA(n_components=n_components, random_state=42)
    X_reduced = ica.fit_transform(X)
    return X_reduced, ica


def nmf_reduction(X, n_components=2):
    """Non-negative Matrix Factorization"""
    nmf = NMF(n_components=n_components, random_state=42)
    X_reduced = nmf.fit_transform(X)
    return X_reduced, nmf


def mds_reduction(X, n_components=2):
    """Multidimensional Scaling"""
    mds = MDS(n_components=n_components, random_state=42)
    X_reduced = mds.fit_transform(X)
    return X_reduced, mds


def isomap_reduction(X, n_components=2, n_neighbors=5):
    """Isomap (non-linear dimensionality reduction)"""
    isomap = Isomap(n_components=n_components, n_neighbors=n_neighbors)
    X_reduced = isomap.fit_transform(X)
    return X_reduced, isomap


def lle_reduction(X, n_components=2, n_neighbors=5):
    """Locally Linear Embedding"""
    lle = LocallyLinearEmbedding(n_components=n_components,
                                  n_neighbors=n_neighbors,
                                  random_state=42)
    X_reduced = lle.fit_transform(X)
    return X_reduced, lle


def feature_agglomeration(X, n_clusters=10):
    """Feature Agglomeration (hierarchical clustering of features)"""
    from sklearn.cluster import FeatureAgglomeration

    agglo = FeatureAgglomeration(n_clusters=n_clusters)
    X_reduced = agglo.fit_transform(X)
    return X_reduced, agglo


def autoencoder_reduction(X, encoding_dim=2):
    """Autoencoder for dimensionality reduction (requires TensorFlow/Keras)"""
    try:
        from tensorflow.keras.layers import Input, Dense
        from tensorflow.keras.models import Model
    except ImportError:
        raise ImportError("tensorflow not installed. Install with: pip install tensorflow")

    input_dim = X.shape[1]

    # Encoder
    input_layer = Input(shape=(input_dim,))
    encoded = Dense(encoding_dim, activation='relu')(input_layer)

    # Decoder
    decoded = Dense(input_dim, activation='sigmoid')(encoded)

    # Autoencoder model
    autoencoder = Model(input_layer, decoded)
    encoder = Model(input_layer, encoded)

    autoencoder.compile(optimizer='adam', loss='mse')
    autoencoder.fit(X, X, epochs=50, batch_size=256, verbose=0)

    X_reduced = encoder.predict(X, verbose=0)
    return X_reduced, encoder


def variance_threshold_reduction(X, threshold=0.0):
    """Remove low variance features"""
    from sklearn.feature_selection import VarianceThreshold

    selector = VarianceThreshold(threshold=threshold)
    X_reduced = selector.fit_transform(X)
    return X_reduced, selector


def select_k_best_features(X, y, k=10):
    """Select K best features based on statistical tests"""
    from sklearn.feature_selection import SelectKBest, f_classif

    selector = SelectKBest(f_classif, k=k)
    X_reduced = selector.fit_transform(X, y)
    return X_reduced, selector


def recursive_feature_elimination(X, y, n_features=10):
    """Recursive Feature Elimination"""
    from sklearn.feature_selection import RFE
    from sklearn.ensemble import RandomForestClassifier

    estimator = RandomForestClassifier(n_estimators=50, random_state=42)
    rfe = RFE(estimator, n_features_to_select=n_features)
    X_reduced = rfe.fit_transform(X, y)
    return X_reduced, rfe


def mutual_information_feature_selection(X, y, k=10):
    """Feature selection using mutual information"""
    from sklearn.feature_selection import mutual_info_classif, SelectKBest

    selector = SelectKBest(mutual_info_classif, k=k)
    X_reduced = selector.fit_transform(X, y)
    return X_reduced, selector


def reconstruct_from_pca(X_reduced, pca):
    """Reconstruct original data from PCA-reduced data"""
    X_reconstructed = pca.inverse_transform(X_reduced)
    return X_reconstructed


def sparse_pca(X, n_components=2, alpha=1):
    """Sparse PCA (enforces sparsity in components)"""
    from sklearn.decomposition import SparsePCA

    spca = SparsePCA(n_components=n_components, alpha=alpha, random_state=42)
    X_reduced = spca.fit_transform(X)
    return X_reduced, spca
