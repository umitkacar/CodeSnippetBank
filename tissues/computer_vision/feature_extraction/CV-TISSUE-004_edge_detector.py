"""
Tissue ID: CV-TISSUE-004
Title: Multi-Algorithm Edge Detection
Category: computer_vision/feature_extraction
Tags: ["edge-detection", "canny", "sobel", "feature-extraction"]
Difficulty: Intermediate
Dependencies: ["opencv-python>=4.5.0", "numpy>=1.19.0"]
Performance: O(n) where n is number of pixels
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A versatile edge detection tissue that provides multiple algorithms (Canny, Sobel,
Laplacian) with automatic parameter tuning. Perfect for feature extraction,
object boundary detection, and preprocessing for other CV tasks.

Use Cases:
- Object boundary detection
- Document edge detection  
- Feature extraction for ML
- Preprocessing for segmentation
- Quality control in manufacturing

Example Usage:
    detector = EdgeDetector(algorithm="auto")
    edges = detector.detect(image)
    
    # Get edges with specific algorithm
    canny_edges = detector.detect_canny(image, auto_tune=True)
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Dict, Any


class EdgeDetector:
    """
    Multi-algorithm edge detection with automatic tuning.
    Tissue Type: FUNCTIONAL - Extracts edge features from images.
    """
    
    def __init__(self,
                 algorithm: str = "canny",
                 blur_kernel: int = 5,
                 auto_tune: bool = True):
        """
        Initialize edge detector.
        
        Args:
            algorithm: 'canny', 'sobel', 'laplacian', or 'auto'
            blur_kernel: Gaussian blur kernel size (must be odd)
            auto_tune: Automatically tune parameters based on image
        """
        self.algorithm = algorithm
        self.blur_kernel = blur_kernel if blur_kernel % 2 == 1 else blur_kernel + 1
        self.auto_tune = auto_tune
        
        # Store detection history for parameter tuning
        self.detection_history = []
    
    def detect(self, image: np.ndarray) -> np.ndarray:
        """
        Detect edges using specified algorithm.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Binary edge map
        """
        if image is None or image.size == 0:
            return np.zeros((1, 1), dtype=np.uint8)
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply Gaussian blur to reduce noise
        if self.blur_kernel > 1:
            gray = cv2.GaussianBlur(gray, (self.blur_kernel, self.blur_kernel), 0)
        
        # Select algorithm
        if self.algorithm == "auto":
            return self._auto_detect(gray)
        elif self.algorithm == "canny":
            return self.detect_canny(gray)
        elif self.algorithm == "sobel":
            return self.detect_sobel(gray)
        elif self.algorithm == "laplacian":
            return self.detect_laplacian(gray)
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
    
    def detect_canny(self, gray: np.ndarray, 
                    low_threshold: Optional[int] = None,
                    high_threshold: Optional[int] = None) -> np.ndarray:
        """
        Canny edge detection with automatic threshold tuning.
        """
        if self.auto_tune and (low_threshold is None or high_threshold is None):
            # Calculate thresholds using Otsu's method
            median_intensity = np.median(gray)
            sigma = 0.33
            
            low_threshold = int(max(0, (1.0 - sigma) * median_intensity))
            high_threshold = int(min(255, (1.0 + sigma) * median_intensity))
        else:
            low_threshold = low_threshold or 50
            high_threshold = high_threshold or 150
        
        edges = cv2.Canny(gray, low_threshold, high_threshold)
        
        # Store parameters for learning
        self.detection_history.append({
            "algorithm": "canny",
            "low_threshold": low_threshold,
            "high_threshold": high_threshold,
            "edge_density": np.sum(edges > 0) / edges.size
        })
        
        return edges
    
    def detect_sobel(self, gray: np.ndarray,
                    ksize: int = 3,
                    threshold: Optional[int] = None) -> np.ndarray:
        """
        Sobel edge detection for gradient-based edges.
        """
        # Calculate gradients
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
        
        # Calculate magnitude
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Auto-threshold if needed
        if threshold is None and self.auto_tune:
            threshold = np.mean(magnitude) + np.std(magnitude)
        else:
            threshold = threshold or 100
        
        # Create binary edge map
        edges = (magnitude > threshold).astype(np.uint8) * 255
        
        return edges
    
    def detect_laplacian(self, gray: np.ndarray,
                        ksize: int = 3,
                        threshold: Optional[int] = None) -> np.ndarray:
        """
        Laplacian edge detection for second-derivative edges.
        """
        # Apply Laplacian
        laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=ksize)
        
        # Take absolute value
        laplacian_abs = np.absolute(laplacian)
        
        # Auto-threshold if needed
        if threshold is None and self.auto_tune:
            threshold = np.mean(laplacian_abs) + 2 * np.std(laplacian_abs)
        else:
            threshold = threshold or 30
        
        # Create binary edge map
        edges = (laplacian_abs > threshold).astype(np.uint8) * 255
        
        return edges
    
    def _auto_detect(self, gray: np.ndarray) -> np.ndarray:
        """
        Automatically select best algorithm based on image characteristics.
        """
        # Analyze image characteristics
        intensity_std = np.std(gray)
        
        # High contrast images work well with Canny
        if intensity_std > 30:
            return self.detect_canny(gray)
        # Low contrast might benefit from Sobel
        elif intensity_std > 15:
            return self.detect_sobel(gray)
        # Very low contrast, try Laplacian
        else:
            return self.detect_laplacian(gray)
    
    def detect_multi_scale(self, image: np.ndarray,
                          scales: list = [1.0, 0.5, 0.25]) -> np.ndarray:
        """
        Multi-scale edge detection for robust results.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        h, w = gray.shape
        combined_edges = np.zeros((h, w), dtype=np.float32)
        
        for scale in scales:
            # Resize image
            scaled_h = int(h * scale)
            scaled_w = int(w * scale)
            scaled = cv2.resize(gray, (scaled_w, scaled_h))
            
            # Detect edges
            edges = self.detect(scaled)
            
            # Resize back and accumulate
            edges_resized = cv2.resize(edges, (w, h))
            combined_edges += edges_resized.astype(np.float32) * scale
        
        # Normalize and threshold
        combined_edges = (combined_edges / len(scales))
        return (combined_edges > 127).astype(np.uint8) * 255
    
    def get_edge_orientation(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get edge magnitude and orientation using Sobel.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Calculate gradients
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate magnitude and angle
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        orientation = np.arctan2(grad_y, grad_x)
        
        return magnitude, orientation
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get edge detection statistics from history.
        """
        if not self.detection_history:
            return {}
        
        edge_densities = [h["edge_density"] for h in self.detection_history]
        
        return {
            "avg_edge_density": np.mean(edge_densities),
            "std_edge_density": np.std(edge_densities),
            "detections_count": len(self.detection_history),
            "most_used_algorithm": max(
                set(h["algorithm"] for h in self.detection_history),
                key=lambda x: sum(1 for h in self.detection_history if h["algorithm"] == x)
            )
        }


# Utility functions
def detect_document_edges(image: np.ndarray) -> np.ndarray:
    """Specialized edge detection for documents"""
    detector = EdgeDetector(algorithm="canny", blur_kernel=3)
    edges = detector.detect(image)
    
    # Apply morphological operations to connect edges
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    return edges


def extract_edge_features(image: np.ndarray) -> Dict[str, np.ndarray]:
    """Extract multiple edge features for ML"""
    detector = EdgeDetector()
    
    return {
        "canny": detector.detect_canny(image),
        "sobel": detector.detect_sobel(image),
        "laplacian": detector.detect_laplacian(image),
        "multi_scale": detector.detect_multi_scale(image)
    }


# Auto-generated tests
def test_edge_detector():
    """Test edge detection functionality"""
    # Create test image with edges
    test_image = np.zeros((100, 100), dtype=np.uint8)
    cv2.rectangle(test_image, (20, 20), (80, 80), 255, -1)
    
    detector = EdgeDetector()
    
    # Test different algorithms
    canny_edges = detector.detect_canny(test_image)
    assert canny_edges.shape == test_image.shape
    assert np.any(canny_edges > 0), "Should detect edges"
    
    sobel_edges = detector.detect_sobel(test_image)
    assert sobel_edges.shape == test_image.shape
    
    laplacian_edges = detector.detect_laplacian(test_image)
    assert laplacian_edges.shape == test_image.shape
    
    # Test auto detection
    detector_auto = EdgeDetector(algorithm="auto")
    auto_edges = detector_auto.detect(test_image)
    assert auto_edges.shape == test_image.shape
    
    # Test multi-scale
    multi_edges = detector.detect_multi_scale(test_image)
    assert multi_edges.shape == test_image.shape
    
    print("All edge detection tests passed!")


if __name__ == "__main__":
    test_edge_detector()