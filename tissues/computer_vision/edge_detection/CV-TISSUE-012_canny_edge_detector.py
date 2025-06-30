"""
Tissue ID: CV-TISSUE-012
Title: Canny Edge Detector with Auto-Thresholding
Category: computer_vision/edge_detection
Tags: ["edge-detection", "canny", "auto-threshold", "gradient", "edge-optimized"]
Difficulty: Intermediate
Dependencies: ["numpy>=1.24", "opencv-python>=4.8"]
Performance: O(w*h) where w,h are image dimensions
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
Advanced Canny edge detector with automatic threshold selection using Otsu's method.
Features multi-scale edge detection, edge linking, and hysteresis tracking. Optimized
for edge devices with adaptive parameter selection.

Use Cases:
- Object boundary detection
- Lane detection
- Medical image analysis
- Document scanning
- Quality inspection

Example Usage:
    # Basic edge detection
    detector = CannyEdgeDetector()
    edges = detector.detect(image)
    
    # With auto-thresholding
    detector = CannyEdgeDetector(auto_threshold=True)
    edges = detector.detect(image)
    
    # Multi-scale detection
    edges_multiscale = detector.detect_multiscale(image, scales=[0.5, 1.0, 2.0])
    
    # Get edge strength map
    edges, magnitude = detector.detect_with_magnitude(image)
"""

import numpy as np
import cv2
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class CannyConfig:
    """Configuration for Canny edge detector"""
    low_threshold: Optional[float] = None  # Lower threshold (None for auto)
    high_threshold: Optional[float] = None  # Upper threshold (None for auto)
    kernel_size: int = 3  # Sobel kernel size
    sigma: float = 1.0  # Gaussian blur sigma
    auto_threshold: bool = True  # Enable automatic thresholding
    l2_gradient: bool = True  # Use L2 norm for gradient
    edge_linking: bool = True  # Enable edge linking
    min_edge_length: int = 10  # Minimum edge length to keep


class CannyEdgeDetector:
    """
    Advanced Canny edge detector with auto-thresholding.
    Tissue Type: FUNCTIONAL - Pure CV edge detection.
    """
    
    def __init__(self, config: Optional[CannyConfig] = None):
        """Initialize Canny edge detector"""
        self.config = config or CannyConfig()
        
        # Cache for multi-scale processing
        self._scale_cache = {}
    
    def detect(self, image: np.ndarray) -> np.ndarray:
        """
        Detect edges in image.
        
        Args:
            image: Input image (grayscale or RGB)
            
        Returns:
            Binary edge map
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # Apply Gaussian blur
        if self.config.sigma > 0:
            ksize = int(2 * np.ceil(3 * self.config.sigma) + 1)
            gray = cv2.GaussianBlur(gray, (ksize, ksize), self.config.sigma)
        
        # Determine thresholds
        low_thresh, high_thresh = self._get_thresholds(gray)
        
        # Apply Canny edge detection
        edges = cv2.Canny(
            gray, 
            low_thresh, 
            high_thresh,
            apertureSize=self.config.kernel_size,
            L2gradient=self.config.l2_gradient
        )
        
        # Post-processing
        if self.config.edge_linking:
            edges = self._link_edges(edges)
        
        if self.config.min_edge_length > 0:
            edges = self._remove_small_edges(edges)
        
        return edges
    
    def detect_with_magnitude(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect edges and return gradient magnitude.
        
        Args:
            image: Input image
            
        Returns:
            Edge map and gradient magnitude
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # Apply Gaussian blur
        if self.config.sigma > 0:
            ksize = int(2 * np.ceil(3 * self.config.sigma) + 1)
            gray = cv2.GaussianBlur(gray, (ksize, ksize), self.config.sigma)
        
        # Calculate gradients
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=self.config.kernel_size)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=self.config.kernel_size)
        
        # Calculate magnitude
        if self.config.l2_gradient:
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
        else:
            magnitude = np.abs(grad_x) + np.abs(grad_y)
        
        # Detect edges
        edges = self.detect(image)
        
        return edges, magnitude
    
    def detect_multiscale(self, image: np.ndarray, 
                         scales: List[float] = [0.5, 1.0, 2.0]) -> np.ndarray:
        """
        Detect edges at multiple scales.
        
        Args:
            image: Input image
            scales: List of scale factors
            
        Returns:
            Combined edge map
        """
        h, w = image.shape[:2]
        combined_edges = np.zeros((h, w), dtype=np.float32)
        
        for scale in scales:
            # Resize image
            if scale != 1.0:
                scaled_h = int(h * scale)
                scaled_w = int(w * scale)
                scaled_image = cv2.resize(image, (scaled_w, scaled_h))
            else:
                scaled_image = image
            
            # Detect edges
            edges = self.detect(scaled_image).astype(np.float32)
            
            # Resize back to original size
            if scale != 1.0:
                edges = cv2.resize(edges, (w, h))
            
            # Weight by scale (finer scales get higher weight)
            weight = 1.0 / scale
            combined_edges += edges * weight
        
        # Normalize and threshold
        combined_edges = combined_edges / len(scales)
        return (combined_edges > 128).astype(np.uint8) * 255
    
    def _get_thresholds(self, gray: np.ndarray) -> Tuple[float, float]:
        """Get edge detection thresholds"""
        if self.config.auto_threshold:
            # Use Otsu's method for automatic threshold
            otsu_thresh, _ = cv2.threshold(
                gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            
            # Set thresholds based on Otsu
            low_thresh = 0.5 * otsu_thresh
            high_thresh = otsu_thresh
        else:
            # Use configured thresholds or defaults
            if self.config.low_threshold is None:
                # Calculate based on image statistics
                v = np.median(gray)
                sigma = 0.33
                low_thresh = int(max(0, (1.0 - sigma) * v))
                high_thresh = int(min(255, (1.0 + sigma) * v))
            else:
                low_thresh = self.config.low_threshold
                high_thresh = self.config.high_threshold or 2 * low_thresh
        
        return low_thresh, high_thresh
    
    def _link_edges(self, edges: np.ndarray) -> np.ndarray:
        """Link broken edges using morphological operations"""
        # Create structuring element for dilation
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        
        # Dilate then erode to connect nearby edges
        linked = cv2.dilate(edges, kernel, iterations=1)
        linked = cv2.erode(linked, kernel, iterations=1)
        
        return linked
    
    def _remove_small_edges(self, edges: np.ndarray) -> np.ndarray:
        """Remove small edge segments"""
        # Find connected components
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(edges, connectivity=8)
        
        # Create output image
        result = np.zeros_like(edges)
        
        # Keep only components larger than threshold
        for i in range(1, num_labels):  # Skip background (0)
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= self.config.min_edge_length:
                result[labels == i] = 255
        
        return result
    
    def get_edge_orientation(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get edge orientation map.
        
        Args:
            image: Input image
            
        Returns:
            Edge map and orientation map (in radians)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # Apply Gaussian blur
        if self.config.sigma > 0:
            ksize = int(2 * np.ceil(3 * self.config.sigma) + 1)
            gray = cv2.GaussianBlur(gray, (ksize, ksize), self.config.sigma)
        
        # Calculate gradients
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=self.config.kernel_size)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=self.config.kernel_size)
        
        # Calculate orientation
        orientation = np.arctan2(grad_y, grad_x)
        
        # Get edges
        edges = self.detect(image)
        
        # Mask orientation with edges
        orientation_masked = orientation * (edges > 0)
        
        return edges, orientation_masked
    
    def visualize_edges(self, image: np.ndarray, edges: np.ndarray,
                       color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        """
        Visualize edges on original image.
        
        Args:
            image: Original image
            edges: Edge map
            color: Edge color (BGR)
            
        Returns:
            Visualization image
        """
        # Ensure 3-channel image
        if len(image.shape) == 2:
            vis = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            vis = image.copy()
        
        # Apply edges
        vis[edges > 0] = color
        
        return vis
    
    def adapt_to_edge_device(self, device_memory_mb: float) -> 'CannyEdgeDetector':
        """
        Adapt detector for specific edge device constraints.
        
        Args:
            device_memory_mb: Available device memory
            
        Returns:
            Adapted detector instance
        """
        if device_memory_mb < 50:
            # Ultra-low memory device
            self.config.sigma = 0.5
            self.config.edge_linking = False
            self.config.min_edge_length = 20
        elif device_memory_mb < 200:
            # Low memory device
            self.config.min_edge_length = 15
        
        return self


# Functional API
def detect_canny_edges(image: np.ndarray,
                      low_threshold: Optional[float] = None,
                      high_threshold: Optional[float] = None,
                      auto_threshold: bool = True) -> np.ndarray:
    """Quick Canny edge detection"""
    config = CannyConfig(
        low_threshold=low_threshold,
        high_threshold=high_threshold,
        auto_threshold=auto_threshold
    )
    detector = CannyEdgeDetector(config)
    return detector.detect(image)


def canny_multiscale(image: np.ndarray,
                    scales: List[float] = [0.5, 1.0, 2.0]) -> np.ndarray:
    """Multi-scale Canny edge detection"""
    detector = CannyEdgeDetector()
    return detector.detect_multiscale(image, scales)


# Auto-generated tests
def test_canny_edge_detector():
    """Test Canny edge detector functionality"""
    # Create test image with edges
    test_image = np.zeros((100, 100), dtype=np.uint8)
    
    # Add shapes with edges
    cv2.rectangle(test_image, (20, 20), (80, 80), 255, 2)
    cv2.circle(test_image, (50, 50), 20, 255, 2)
    cv2.line(test_image, (10, 10), (90, 90), 255, 2)
    
    # Test basic detection
    detector = CannyEdgeDetector()
    edges = detector.detect(test_image)
    
    assert edges.shape == test_image.shape
    assert np.any(edges > 0), "Should detect edges"
    
    # Test with magnitude
    edges_mag, magnitude = detector.detect_with_magnitude(test_image)
    assert magnitude.shape == test_image.shape
    assert np.max(magnitude) > 0
    
    # Test manual thresholds
    config = CannyConfig(low_threshold=50, high_threshold=150, auto_threshold=False)
    detector_manual = CannyEdgeDetector(config)
    edges_manual = detector_manual.detect(test_image)
    assert np.any(edges_manual > 0)
    
    # Test RGB image
    rgb_image = np.stack([test_image] * 3, axis=-1)
    edges_rgb = detector.detect(rgb_image)
    assert edges_rgb.shape == test_image.shape
    
    # Test multi-scale
    edges_multi = detector.detect_multiscale(test_image, scales=[0.5, 1.0, 1.5])
    assert edges_multi.shape == test_image.shape
    
    # Test edge orientation
    edges_orient, orientation = detector.get_edge_orientation(test_image)
    assert orientation.shape == test_image.shape
    
    # Test edge adaptation
    edge_detector = detector.adapt_to_edge_device(30)  # 30MB device
    assert edge_detector.config.edge_linking == False
    
    # Test visualization
    vis = detector.visualize_edges(rgb_image, edges)
    assert vis.shape == rgb_image.shape
    
    # Test functional API
    quick_edges = detect_canny_edges(test_image)
    assert np.any(quick_edges > 0)
    
    multi_edges = canny_multiscale(test_image)
    assert multi_edges.shape == test_image.shape
    
    # Test edge linking
    config_link = CannyConfig(edge_linking=True)
    detector_link = CannyEdgeDetector(config_link)
    edges_linked = detector_link.detect(test_image)
    assert np.any(edges_linked > 0)
    
    print("✅ All Canny edge detector tests passed!")


if __name__ == "__main__":
    test_canny_edge_detector()