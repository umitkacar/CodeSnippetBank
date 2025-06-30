"""
Tissue ID: CV-TISSUE-011
Title: Harris Corner Detector
Category: computer_vision/feature_detection
Tags: ["corner-detection", "harris", "feature-points", "keypoints", "edge-optimized"]
Difficulty: Intermediate
Dependencies: ["numpy>=1.24", "opencv-python>=4.8"]
Performance: O(w*h) where w,h are image dimensions
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
High-performance Harris corner detector optimized for edge devices. Detects
corner points in images using the Harris matrix eigenvalue method. Features
adaptive thresholding, non-maximum suppression, and sub-pixel refinement.

Use Cases:
- Feature matching
- Image registration
- 3D reconstruction
- Visual SLAM
- Panorama stitching

Example Usage:
    # Basic corner detection
    detector = HarrisCornerDetector()
    corners = detector.detect(image)
    
    # With custom parameters
    detector = HarrisCornerDetector(
        block_size=5,
        ksize=3,
        k=0.04,
        threshold=0.01
    )
    corners, scores = detector.detect_with_scores(image)
    
    # Sub-pixel refinement
    refined_corners = detector.refine_corners(image, corners)
"""

import numpy as np
import cv2
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class HarrisConfig:
    """Configuration for Harris corner detector"""
    block_size: int = 2  # Neighborhood size
    ksize: int = 3  # Sobel kernel size
    k: float = 0.04  # Harris detector free parameter
    threshold: float = 0.01  # Corner response threshold
    nms_radius: int = 5  # Non-maximum suppression radius
    refine_corners: bool = True  # Enable sub-pixel refinement
    max_corners: Optional[int] = None  # Maximum corners to return


class HarrisCornerDetector:
    """
    Harris corner detector implementation optimized for edge devices.
    Tissue Type: FUNCTIONAL - Pure CV feature detection.
    """
    
    def __init__(self, config: Optional[HarrisConfig] = None):
        """Initialize Harris corner detector"""
        self.config = config or HarrisConfig()
        
        # Pre-compute Sobel kernels for efficiency
        self._init_kernels()
    
    def _init_kernels(self):
        """Initialize Sobel kernels"""
        k = self.config.ksize
        self.sobel_x = cv2.getDerivKernels(1, 0, k)[0] * cv2.getDerivKernels(1, 0, k)[1].T
        self.sobel_y = cv2.getDerivKernels(0, 1, k)[0] * cv2.getDerivKernels(0, 1, k)[1].T
    
    def detect(self, image: np.ndarray) -> List[Tuple[int, int]]:
        """
        Detect corners in image.
        
        Args:
            image: Input image (grayscale or RGB)
            
        Returns:
            List of corner points (x, y)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # Calculate Harris response
        response = self._calculate_harris_response(gray)
        
        # Find corners
        corners = self._find_corners(response)
        
        # Refine if enabled
        if self.config.refine_corners and len(corners) > 0:
            corners = self._refine_corner_positions(gray, corners)
        
        return corners
    
    def detect_with_scores(self, image: np.ndarray) -> Tuple[List[Tuple[int, int]], np.ndarray]:
        """
        Detect corners with response scores.
        
        Args:
            image: Input image
            
        Returns:
            Corner points and their response scores
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        response = self._calculate_harris_response(gray)
        corners = self._find_corners(response)
        
        # Get scores
        scores = []
        for x, y in corners:
            scores.append(response[y, x])
        
        if self.config.refine_corners and len(corners) > 0:
            corners = self._refine_corner_positions(gray, corners)
        
        return corners, np.array(scores)
    
    def _calculate_harris_response(self, gray: np.ndarray) -> np.ndarray:
        """Calculate Harris corner response"""
        # Calculate gradients
        Ix = cv2.filter2D(gray, cv2.CV_32F, self.sobel_x)
        Iy = cv2.filter2D(gray, cv2.CV_32F, self.sobel_y)
        
        # Calculate products of derivatives
        Ixx = Ix * Ix
        Iyy = Iy * Iy
        Ixy = Ix * Iy
        
        # Apply Gaussian weighting
        ksize = (self.config.block_size * 2 + 1, self.config.block_size * 2 + 1)
        Sxx = cv2.GaussianBlur(Ixx, ksize, 0)
        Syy = cv2.GaussianBlur(Iyy, ksize, 0)
        Sxy = cv2.GaussianBlur(Ixy, ksize, 0)
        
        # Calculate Harris response
        # R = det(M) - k * trace(M)^2
        det = Sxx * Syy - Sxy * Sxy
        trace = Sxx + Syy
        response = det - self.config.k * trace * trace
        
        return response
    
    def _find_corners(self, response: np.ndarray) -> List[Tuple[int, int]]:
        """Find corner points from response map"""
        # Threshold response
        threshold = self.config.threshold * response.max()
        corner_mask = response > threshold
        
        # Non-maximum suppression
        corners = []
        radius = self.config.nms_radius
        
        # Find local maxima
        for y in range(radius, response.shape[0] - radius):
            for x in range(radius, response.shape[1] - radius):
                if corner_mask[y, x]:
                    # Check if local maximum
                    local_patch = response[y-radius:y+radius+1, x-radius:x+radius+1]
                    if response[y, x] == local_patch.max():
                        corners.append((x, y))
        
        # Sort by response strength
        corners.sort(key=lambda p: response[p[1], p[0]], reverse=True)
        
        # Limit number of corners
        if self.config.max_corners and len(corners) > self.config.max_corners:
            corners = corners[:self.config.max_corners]
        
        return corners
    
    def _refine_corner_positions(self, gray: np.ndarray, 
                               corners: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Refine corner positions to sub-pixel accuracy"""
        # Convert to float32 array
        corners_array = np.array(corners, dtype=np.float32)
        
        # Sub-pixel refinement criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        # Refine
        cv2.cornerSubPix(gray, corners_array, (5, 5), (-1, -1), criteria)
        
        # Convert back to list of tuples
        refined = [(int(x + 0.5), int(y + 0.5)) for x, y in corners_array]
        
        return refined
    
    def visualize(self, image: np.ndarray, corners: List[Tuple[int, int]], 
                  color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        """
        Visualize detected corners on image.
        
        Args:
            image: Input image
            corners: Corner points
            color: Corner color (BGR)
            
        Returns:
            Image with corners drawn
        """
        vis = image.copy()
        
        for x, y in corners:
            cv2.circle(vis, (x, y), 3, color, -1)
            cv2.circle(vis, (x, y), 8, color, 1)
        
        return vis
    
    def get_corner_descriptors(self, image: np.ndarray, 
                             corners: List[Tuple[int, int]], 
                             patch_size: int = 15) -> np.ndarray:
        """
        Extract patch descriptors around corners.
        
        Args:
            image: Input image
            corners: Corner points
            patch_size: Size of patch to extract
            
        Returns:
            Array of descriptors (n_corners, patch_size, patch_size)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        half_size = patch_size // 2
        descriptors = []
        
        for x, y in corners:
            # Check bounds
            if (y - half_size >= 0 and y + half_size < gray.shape[0] and
                x - half_size >= 0 and x + half_size < gray.shape[1]):
                
                patch = gray[y-half_size:y+half_size+1, x-half_size:x+half_size+1]
                descriptors.append(patch)
        
        return np.array(descriptors) if descriptors else np.array([])
    
    def adapt_to_edge_device(self, device_memory_mb: float) -> 'HarrisCornerDetector':
        """
        Adapt detector for specific edge device constraints.
        
        Args:
            device_memory_mb: Available device memory
            
        Returns:
            Adapted detector instance
        """
        if device_memory_mb < 50:
            # Ultra-low memory device
            self.config.block_size = 1
            self.config.nms_radius = 3
            self.config.refine_corners = False
            self.config.max_corners = 100
        elif device_memory_mb < 200:
            # Low memory device
            self.config.nms_radius = 4
            self.config.max_corners = 500
        
        return self


# Functional API
def detect_harris_corners(image: np.ndarray, 
                         threshold: float = 0.01,
                         max_corners: Optional[int] = None) -> List[Tuple[int, int]]:
    """Quick Harris corner detection"""
    config = HarrisConfig(threshold=threshold, max_corners=max_corners)
    detector = HarrisCornerDetector(config)
    return detector.detect(image)


def harris_corner_strength(image: np.ndarray, k: float = 0.04) -> np.ndarray:
    """Get Harris corner response map"""
    config = HarrisConfig(k=k)
    detector = HarrisCornerDetector(config)
    
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    return detector._calculate_harris_response(gray)


# Auto-generated tests
def test_harris_corner_detector():
    """Test Harris corner detector functionality"""
    # Create test image with corners
    test_image = np.zeros((100, 100), dtype=np.uint8)
    
    # Add some corners (squares)
    cv2.rectangle(test_image, (20, 20), (40, 40), 255, -1)
    cv2.rectangle(test_image, (60, 60), (80, 80), 255, -1)
    
    # Test basic detection
    detector = HarrisCornerDetector()
    corners = detector.detect(test_image)
    
    assert len(corners) > 0, "Should detect corners"
    
    # Test with scores
    corners_scored, scores = detector.detect_with_scores(test_image)
    assert len(corners_scored) == len(scores)
    assert all(s > 0 for s in scores)
    
    # Test configuration
    config = HarrisConfig(threshold=0.001, max_corners=10)
    detector_config = HarrisCornerDetector(config)
    limited_corners = detector_config.detect(test_image)
    assert len(limited_corners) <= 10
    
    # Test RGB image
    rgb_image = np.stack([test_image] * 3, axis=-1)
    rgb_corners = detector.detect(rgb_image)
    assert len(rgb_corners) > 0
    
    # Test edge adaptation
    edge_detector = detector.adapt_to_edge_device(30)  # 30MB device
    assert edge_detector.config.refine_corners == False
    assert edge_detector.config.max_corners == 100
    
    # Test visualization
    vis = detector.visualize(rgb_image, corners[:5])
    assert vis.shape == rgb_image.shape
    
    # Test descriptors
    descriptors = detector.get_corner_descriptors(test_image, corners[:5])
    if len(descriptors) > 0:
        assert descriptors.shape[1] == descriptors.shape[2] == 15
    
    # Test functional API
    quick_corners = detect_harris_corners(test_image, threshold=0.01)
    assert len(quick_corners) > 0
    
    response = harris_corner_strength(test_image)
    assert response.shape == test_image.shape
    
    print("✅ All Harris corner detector tests passed!")


if __name__ == "__main__":
    test_harris_corner_detector()