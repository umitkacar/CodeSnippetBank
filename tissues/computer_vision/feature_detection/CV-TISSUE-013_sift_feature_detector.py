"""
Tissue ID: CV-TISSUE-013
Title: SIFT Feature Detector and Descriptor
Category: computer_vision/feature_detection
Tags: ["sift", "feature-detection", "keypoints", "descriptors", "scale-invariant"]
Difficulty: Advanced
Dependencies: ["numpy>=1.24", "opencv-python>=4.8"]
Performance: O(n*s) where n is pixels, s is scales
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
Scale-Invariant Feature Transform (SIFT) implementation optimized for edge devices.
Detects keypoints and computes descriptors that are invariant to scale, rotation,
and illumination changes. Features adaptive parameter tuning and memory-efficient
processing.

Use Cases:
- Image matching
- Object recognition
- Panorama stitching
- 3D reconstruction
- Visual SLAM

Example Usage:
    # Basic SIFT detection
    sift = SIFTFeatureDetector()
    keypoints, descriptors = sift.detect_and_compute(image)
    
    # With custom parameters
    sift = SIFTFeatureDetector(
        n_features=500,
        n_octave_layers=3,
        contrast_threshold=0.04
    )
    kp, desc = sift.detect_and_compute(image)
    
    # Match features between images
    matches = sift.match_features(desc1, desc2)
"""

import numpy as np
import cv2
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class SIFTConfig:
    """Configuration for SIFT feature detector"""
    n_features: int = 0  # 0 means no limit
    n_octave_layers: int = 3  # Number of layers in each octave
    contrast_threshold: float = 0.04  # Contrast threshold
    edge_threshold: float = 10  # Edge threshold
    sigma: float = 1.6  # Gaussian sigma
    enable_precise_upscale: bool = True  # Enable precise keypoint localization
    root_sift: bool = False  # Use RootSIFT variant


class SIFTFeatureDetector:
    """
    SIFT feature detector and descriptor implementation.
    Tissue Type: FUNCTIONAL - Pure CV feature detection.
    """
    
    def __init__(self, config: Optional[SIFTConfig] = None):
        """Initialize SIFT detector"""
        self.config = config or SIFTConfig()
        
        # Initialize SIFT detector
        self._init_detector()
    
    def _init_detector(self):
        """Initialize OpenCV SIFT detector"""
        self.detector = cv2.SIFT_create(
            nfeatures=self.config.n_features,
            nOctaveLayers=self.config.n_octave_layers,
            contrastThreshold=self.config.contrast_threshold,
            edgeThreshold=self.config.edge_threshold,
            sigma=self.config.sigma
        )
    
    def detect(self, image: np.ndarray) -> List[cv2.KeyPoint]:
        """
        Detect keypoints in image.
        
        Args:
            image: Input image (grayscale or RGB)
            
        Returns:
            List of keypoints
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # Detect keypoints
        keypoints = self.detector.detect(gray, None)
        
        # Sort by response strength
        keypoints = sorted(keypoints, key=lambda x: x.response, reverse=True)
        
        # Limit number if specified
        if self.config.n_features > 0 and len(keypoints) > self.config.n_features:
            keypoints = keypoints[:self.config.n_features]
        
        return keypoints
    
    def compute(self, image: np.ndarray, 
               keypoints: List[cv2.KeyPoint]) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """
        Compute descriptors for given keypoints.
        
        Args:
            image: Input image
            keypoints: Detected keypoints
            
        Returns:
            Keypoints and descriptors
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # Compute descriptors
        keypoints, descriptors = self.detector.compute(gray, keypoints)
        
        # Apply RootSIFT if enabled
        if self.config.root_sift and descriptors is not None:
            descriptors = self._apply_root_sift(descriptors)
        
        return keypoints, descriptors
    
    def detect_and_compute(self, image: np.ndarray) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """
        Detect keypoints and compute descriptors.
        
        Args:
            image: Input image
            
        Returns:
            Keypoints and descriptors
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        
        # Detect and compute
        keypoints, descriptors = self.detector.detectAndCompute(gray, None)
        
        # Sort by response
        if keypoints:
            sorted_indices = np.argsort([kp.response for kp in keypoints])[::-1]
            keypoints = [keypoints[i] for i in sorted_indices]
            if descriptors is not None:
                descriptors = descriptors[sorted_indices]
        
        # Limit features
        if self.config.n_features > 0 and len(keypoints) > self.config.n_features:
            keypoints = keypoints[:self.config.n_features]
            if descriptors is not None:
                descriptors = descriptors[:self.config.n_features]
        
        # Apply RootSIFT
        if self.config.root_sift and descriptors is not None:
            descriptors = self._apply_root_sift(descriptors)
        
        return keypoints, descriptors
    
    def _apply_root_sift(self, descriptors: np.ndarray) -> np.ndarray:
        """Apply RootSIFT transformation"""
        # L1 normalize
        descriptors = descriptors / (np.sum(descriptors, axis=1, keepdims=True) + 1e-7)
        # Square root
        descriptors = np.sqrt(descriptors)
        return descriptors
    
    def match_features(self, desc1: np.ndarray, desc2: np.ndarray,
                      ratio_threshold: float = 0.7) -> List[Tuple[int, int, float]]:
        """
        Match descriptors using ratio test.
        
        Args:
            desc1: First set of descriptors
            desc2: Second set of descriptors
            ratio_threshold: Lowe's ratio test threshold
            
        Returns:
            List of matches (idx1, idx2, distance)
        """
        if desc1 is None or desc2 is None or len(desc1) == 0 or len(desc2) == 0:
            return []
        
        # Create matcher
        if desc1.dtype == np.uint8:
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        else:
            matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        
        # Find k=2 nearest neighbors
        matches = matcher.knnMatch(desc1, desc2, k=2)
        
        # Apply ratio test
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < ratio_threshold * n.distance:
                    good_matches.append((m.queryIdx, m.trainIdx, m.distance))
        
        return good_matches
    
    def visualize_keypoints(self, image: np.ndarray, 
                           keypoints: List[cv2.KeyPoint],
                           color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        """
        Visualize keypoints on image.
        
        Args:
            image: Input image
            keypoints: Keypoints to visualize
            color: Keypoint color (BGR)
            
        Returns:
            Visualization image
        """
        vis = cv2.drawKeypoints(
            image, keypoints, None,
            color=color,
            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )
        return vis
    
    def visualize_matches(self, img1: np.ndarray, kp1: List[cv2.KeyPoint],
                         img2: np.ndarray, kp2: List[cv2.KeyPoint],
                         matches: List[Tuple[int, int, float]],
                         n_matches: int = 50) -> np.ndarray:
        """
        Visualize feature matches between images.
        
        Args:
            img1, img2: Images
            kp1, kp2: Keypoints
            matches: Match list
            n_matches: Number of matches to show
            
        Returns:
            Visualization image
        """
        # Convert matches to DMatch objects
        dmatches = []
        for idx1, idx2, dist in matches[:n_matches]:
            dm = cv2.DMatch()
            dm.queryIdx = idx1
            dm.trainIdx = idx2
            dm.distance = dist
            dmatches.append(dm)
        
        # Draw matches
        vis = cv2.drawMatches(img1, kp1, img2, kp2, dmatches, None,
                             flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        return vis
    
    def get_keypoint_statistics(self, keypoints: List[cv2.KeyPoint]) -> Dict[str, float]:
        """
        Get statistics about detected keypoints.
        
        Args:
            keypoints: List of keypoints
            
        Returns:
            Statistics dictionary
        """
        if not keypoints:
            return {
                'count': 0,
                'avg_size': 0,
                'avg_response': 0,
                'size_std': 0
            }
        
        sizes = [kp.size for kp in keypoints]
        responses = [kp.response for kp in keypoints]
        
        return {
            'count': len(keypoints),
            'avg_size': np.mean(sizes),
            'avg_response': np.mean(responses),
            'size_std': np.std(sizes),
            'min_response': np.min(responses),
            'max_response': np.max(responses)
        }
    
    def filter_keypoints_by_response(self, keypoints: List[cv2.KeyPoint],
                                   min_response: float) -> List[cv2.KeyPoint]:
        """Filter keypoints by minimum response"""
        return [kp for kp in keypoints if kp.response >= min_response]
    
    def adapt_to_edge_device(self, device_memory_mb: float) -> 'SIFTFeatureDetector':
        """
        Adapt detector for specific edge device constraints.
        
        Args:
            device_memory_mb: Available device memory
            
        Returns:
            Adapted detector instance
        """
        if device_memory_mb < 50:
            # Ultra-low memory device
            self.config.n_features = 100
            self.config.n_octave_layers = 2
            self.config.enable_precise_upscale = False
        elif device_memory_mb < 200:
            # Low memory device
            self.config.n_features = 300
            self.config.n_octave_layers = 3
        elif device_memory_mb < 500:
            # Medium memory device
            self.config.n_features = 500
        
        # Reinitialize detector
        self._init_detector()
        
        return self


# Functional API
def detect_sift_features(image: np.ndarray,
                        n_features: int = 500) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
    """Quick SIFT feature detection"""
    config = SIFTConfig(n_features=n_features)
    detector = SIFTFeatureDetector(config)
    return detector.detect_and_compute(image)


def match_sift_features(img1: np.ndarray, img2: np.ndarray,
                       n_features: int = 500,
                       ratio_threshold: float = 0.7) -> List[Tuple[int, int, float]]:
    """Match SIFT features between two images"""
    detector = SIFTFeatureDetector(SIFTConfig(n_features=n_features))
    
    kp1, desc1 = detector.detect_and_compute(img1)
    kp2, desc2 = detector.detect_and_compute(img2)
    
    return detector.match_features(desc1, desc2, ratio_threshold)


# Auto-generated tests
def test_sift_feature_detector():
    """Test SIFT feature detector functionality"""
    # Create test image with features
    test_image = np.zeros((200, 200), dtype=np.uint8)
    
    # Add some patterns
    cv2.rectangle(test_image, (50, 50), (150, 150), 255, -1)
    cv2.circle(test_image, (100, 100), 30, 0, -1)
    
    # Add texture
    noise = np.random.randint(0, 50, test_image.shape, dtype=np.uint8)
    test_image = cv2.add(test_image, noise)
    
    # Test basic detection
    detector = SIFTFeatureDetector()
    keypoints = detector.detect(test_image)
    
    assert len(keypoints) > 0, "Should detect keypoints"
    assert all(isinstance(kp, cv2.KeyPoint) for kp in keypoints)
    
    # Test detect and compute
    kp, desc = detector.detect_and_compute(test_image)
    assert len(kp) > 0
    assert desc is not None
    assert desc.shape[0] == len(kp)
    assert desc.shape[1] == 128  # SIFT descriptor size
    
    # Test with limited features
    config = SIFTConfig(n_features=50)
    detector_limited = SIFTFeatureDetector(config)
    kp_limited, desc_limited = detector_limited.detect_and_compute(test_image)
    assert len(kp_limited) <= 50
    
    # Test RGB image
    rgb_image = np.stack([test_image] * 3, axis=-1)
    kp_rgb, desc_rgb = detector.detect_and_compute(rgb_image)
    assert len(kp_rgb) > 0
    
    # Test RootSIFT
    config_root = SIFTConfig(root_sift=True)
    detector_root = SIFTFeatureDetector(config_root)
    kp_root, desc_root = detector_root.detect_and_compute(test_image)
    if desc_root is not None:
        assert np.all(desc_root >= 0)  # RootSIFT values are non-negative
    
    # Test matching
    # Create slightly transformed image
    M = cv2.getRotationMatrix2D((100, 100), 15, 1.0)
    test_image2 = cv2.warpAffine(test_image, M, (200, 200))
    
    kp2, desc2 = detector.detect_and_compute(test_image2)
    if desc is not None and desc2 is not None:
        matches = detector.match_features(desc, desc2)
        assert isinstance(matches, list)
    
    # Test statistics
    stats = detector.get_keypoint_statistics(kp)
    assert stats['count'] == len(kp)
    assert stats['avg_size'] > 0
    
    # Test filtering
    filtered_kp = detector.filter_keypoints_by_response(kp, min_response=0.01)
    assert len(filtered_kp) <= len(kp)
    
    # Test visualization
    vis_kp = detector.visualize_keypoints(rgb_image, kp[:20])
    assert vis_kp.shape == rgb_image.shape
    
    # Test edge adaptation
    edge_detector = detector.adapt_to_edge_device(30)  # 30MB device
    assert edge_detector.config.n_features == 100
    
    # Test functional API
    quick_kp, quick_desc = detect_sift_features(test_image, n_features=100)
    assert len(quick_kp) <= 100
    
    print("✅ All SIFT feature detector tests passed!")


if __name__ == "__main__":
    test_sift_feature_detector()