"""
NumPy Random Sampling Snippets
Production-ready examples for random number generation
"""

try:
    import numpy as np
    from typing import Tuple
except ImportError as e:
    raise ImportError(f"Required package not installed: {e}. Install with: pip install numpy")


def set_random_seed(seed: int = 42):
    """Set random seed for reproducibility"""
    np.random.seed(seed)


def random_uniform(low: float = 0.0, high: float = 1.0, size: Tuple = (10,)) -> np.ndarray:
    """Generate random numbers from uniform distribution"""
    return np.random.uniform(low, high, size)


def random_normal(mean: float = 0.0, std: float = 1.0, size: Tuple = (10,)) -> np.ndarray:
    """Generate random numbers from normal (Gaussian) distribution"""
    return np.random.normal(mean, std, size)


def random_integers(low: int, high: int, size: Tuple = (10,)) -> np.ndarray:
    """Generate random integers in range [low, high)"""
    return np.random.randint(low, high, size)


def random_choice(arr: np.ndarray, size: int = 1, replace: bool = True) -> np.ndarray:
    """Randomly sample elements from array"""
    return np.random.choice(arr, size=size, replace=replace)


def random_choice_with_probabilities(arr: np.ndarray, probs: np.ndarray, size: int = 1) -> np.ndarray:
    """Sample with custom probabilities"""
    return np.random.choice(arr, size=size, p=probs)


def shuffle_array(arr: np.ndarray) -> np.ndarray:
    """Shuffle array in-place"""
    shuffled = arr.copy()
    np.random.shuffle(shuffled)
    return shuffled


def random_permutation(n: int) -> np.ndarray:
    """Generate random permutation of integers 0 to n-1"""
    return np.random.permutation(n)


def random_exponential(scale: float = 1.0, size: Tuple = (10,)) -> np.ndarray:
    """Generate random numbers from exponential distribution"""
    return np.random.exponential(scale, size)


def random_poisson(lam: float = 1.0, size: Tuple = (10,)) -> np.ndarray:
    """Generate random numbers from Poisson distribution"""
    return np.random.poisson(lam, size)


def random_binomial(n: int, p: float, size: Tuple = (10,)) -> np.ndarray:
    """Generate random numbers from binomial distribution"""
    return np.random.binomial(n, p, size)


def random_beta(alpha: float, beta: float, size: Tuple = (10,)) -> np.ndarray:
    """Generate random numbers from beta distribution"""
    return np.random.beta(alpha, beta, size)


def random_gamma(shape: float, scale: float = 1.0, size: Tuple = (10,)) -> np.ndarray:
    """Generate random numbers from gamma distribution"""
    return np.random.gamma(shape, scale, size)


def random_chi_square(df: int, size: Tuple = (10,)) -> np.ndarray:
    """Generate random numbers from chi-square distribution"""
    return np.random.chisquare(df, size)


def random_multivariate_normal(mean: np.ndarray, cov: np.ndarray, size: int = 1) -> np.ndarray:
    """Generate samples from multivariate normal distribution"""
    return np.random.multivariate_normal(mean, cov, size)


def random_lognormal(mean: float = 0.0, sigma: float = 1.0, size: Tuple = (10,)) -> np.ndarray:
    """Generate random numbers from lognormal distribution"""
    return np.random.lognormal(mean, sigma, size)


def random_standard_normal(size: Tuple = (10,)) -> np.ndarray:
    """Generate standard normal random numbers (mean=0, std=1)"""
    return np.random.standard_normal(size)


def random_laplace(loc: float = 0.0, scale: float = 1.0, size: Tuple = (10,)) -> np.ndarray:
    """Generate random numbers from Laplace distribution"""
    return np.random.laplace(loc, scale, size)


def random_geometric(p: float, size: Tuple = (10,)) -> np.ndarray:
    """Generate random numbers from geometric distribution"""
    return np.random.geometric(p, size)


def random_weibull(a: float, size: Tuple = (10,)) -> np.ndarray:
    """Generate random numbers from Weibull distribution"""
    return np.random.weibull(a, size)


def bootstrap_sample(arr: np.ndarray, n_samples: int = 1000) -> np.ndarray:
    """Generate bootstrap samples"""
    return np.random.choice(arr, size=n_samples, replace=True)


def stratified_sample(arr: np.ndarray, labels: np.ndarray, n_per_class: int = 10) -> np.ndarray:
    """Stratified sampling (equal samples per class)"""
    samples = []
    for label in np.unique(labels):
        class_indices = np.where(labels == label)[0]
        sampled_indices = np.random.choice(class_indices, size=n_per_class, replace=False)
        samples.append(arr[sampled_indices])
    return np.vstack(samples)


def train_test_split_random(arr: np.ndarray, test_size: float = 0.2) -> Tuple[np.ndarray, np.ndarray]:
    """Random train-test split"""
    n = len(arr)
    indices = np.random.permutation(n)
    split_idx = int(n * (1 - test_size))
    train_indices = indices[:split_idx]
    test_indices = indices[split_idx:]
    return arr[train_indices], arr[test_indices]


def random_sample_indices(n: int, sample_size: int, replace: bool = False) -> np.ndarray:
    """Generate random sample indices"""
    return np.random.choice(n, size=sample_size, replace=replace)


def monte_carlo_simulation(n_simulations: int = 10000) -> np.ndarray:
    """Run Monte Carlo simulation"""
    results = np.random.uniform(0, 1, n_simulations)
    return results


def random_walk_1d(steps: int = 1000, step_size: float = 1.0) -> np.ndarray:
    """Generate 1D random walk"""
    steps_array = np.random.choice([-1, 1], size=steps) * step_size
    return np.cumsum(steps_array)


def random_walk_2d(steps: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
    """Generate 2D random walk"""
    angles = np.random.uniform(0, 2*np.pi, steps)
    x = np.cumsum(np.cos(angles))
    y = np.cumsum(np.sin(angles))
    return x, y


def random_correlation_matrix(n: int) -> np.ndarray:
    """Generate random positive semi-definite correlation matrix"""
    A = np.random.randn(n, n)
    corr = np.dot(A, A.T)
    # Normalize to correlation matrix
    D = np.diag(1.0 / np.sqrt(np.diag(corr)))
    return np.dot(D, np.dot(corr, D))
