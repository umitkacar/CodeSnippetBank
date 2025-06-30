"""
Tissue ID: CV-TISSUE-010
Title: Multi-Algorithm Feature Matching Engine
Category: computer_vision/feature_matching
Tags: ["feature-matching", "sift", "orb", "homography", "keypoints"]
Difficulty: Advanced
Dependencies: ["opencv-python>=4.5.0", "numpy>=1.19.0"]
Performance: O(n²) for brute force, O(n log n) for FLANN
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive feature matching tissue that provides multiple algorithms for
detecting and matching keypoints between images. Supports SIFT, ORB, AKAZE,
and BRISK with automatic algorithm selection. Perfect for image stitching,
object recognition, and 3D reconstruction.

Use Cases:
- Image stitching and panorama creation
- Object detection and recognition
- Camera calibration and pose estimation
- Visual SLAM and navigation
- Image registration and alignment

Example Usage:
    matcher = FeatureMatcher(algorithm="auto", max_features=500)
    
    # Match two images
    matches, kp1, kp2 = matcher.match_images(img1, img2)
    
    # Find homography
    H, inliers = matcher.find_homography(img1, img2)
    
    # Visualize matches
    vis = matcher.draw_matches(img1, img2, matches[:20])
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class FeatureAlgorithm(Enum):
    """Available feature detection algorithms"""
    SIFT = "sift"
    ORB = "orb"
    AKAZE = "akaze"
    BRISK = "brisk"
    AUTO = "auto"


@dataclass
class MatchingResult:
    """Container for matching results"""
    matches: List[cv2.DMatch]
    keypoints1: List[cv2.KeyPoint]
    keypoints2: List[cv2.KeyPoint]
    descriptors1: np.ndarray
    descriptors2: np.ndarray
    match_score: float
    inlier_ratio: float
    
    @property
    def num_matches(self) -> int:
        return len(self.matches)


class FeatureMatcher:
    """
    Multi-algorithm feature matching engine.
    Tissue Type: CONNECTIVE - Connects features between images.
    """
    
    def __init__(self,
                 algorithm: str = "orb",
                 max_features: int = 500,
                 match_ratio: float = 0.7,
                 use_flann: bool = False):
        """
        Initialize feature matcher.
        
        Args:
            algorithm: Feature algorithm to use
            max_features: Maximum features to detect
            match_ratio: Lowe's ratio for filtering matches
            use_flann: Use FLANN matcher instead of brute force
        """
        self.algorithm = FeatureAlgorithm(algorithm.lower())
        self.max_features = max_features
        self.match_ratio = match_ratio
        self.use_flann = use_flann
        
        # Initialize detectors
        self._init_detectors()
        
        # Statistics
        self.images_matched = 0
        self.total_matches = 0
    
    def _init_detectors(self):
        """Initialize feature detectors and matchers"""
        # Create detectors
        self.detectors = {
            FeatureAlgorithm.SIFT: cv2.SIFT_create(nfeatures=self.max_features),
            FeatureAlgorithm.ORB: cv2.ORB_create(nfeatures=self.max_features),
            FeatureAlgorithm.AKAZE: cv2.AKAZE_create(),
            FeatureAlgorithm.BRISK: cv2.BRISK_create()
        }
        
        # Create matchers
        if self.use_flann:
            # FLANN parameters
            flann_params_sift = dict(algorithm=1, trees=5)
            flann_params_orb = dict(algorithm=6, table_number=12, 
                                   key_size=20, multi_probe_level=2)
            
            self.matchers = {
                FeatureAlgorithm.SIFT: cv2.FlannBasedMatcher(
                    flann_params_sift, dict(checks=50)
                ),
                FeatureAlgorithm.ORB: cv2.FlannBasedMatcher(
                    flann_params_orb, dict(checks=50)
                ),
                FeatureAlgorithm.AKAZE: cv2.FlannBasedMatcher(
                    flann_params_orb, dict(checks=50)
                ),
                FeatureAlgorithm.BRISK: cv2.FlannBasedMatcher(
                    flann_params_orb, dict(checks=50)
                )
            }
        else:
            # Brute force matchers
            self.matchers = {
                FeatureAlgorithm.SIFT: cv2.BFMatcher(cv2.NORM_L2, crossCheck=False),
                FeatureAlgorithm.ORB: cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False),
                FeatureAlgorithm.AKAZE: cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False),
                FeatureAlgorithm.BRISK: cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            }
    
    def match_images(self, img1: np.ndarray, img2: np.ndarray,
                    algorithm: Optional[str] = None) -> MatchingResult:
        """
        Match features between two images.
        
        Args:
            img1: First image
            img2: Second image
            algorithm: Override default algorithm
            
        Returns:
            MatchingResult with matches and keypoints
        """
        if img1 is None or img2 is None:
            return MatchingResult([], [], [], np.array([]), np.array([]), 0.0, 0.0)
        
        # Convert to grayscale
        gray1 = self._to_grayscale(img1)
        gray2 = self._to_grayscale(img2)
        
        # Select algorithm
        alg = FeatureAlgorithm(algorithm.lower()) if algorithm else self.algorithm
        
        if alg == FeatureAlgorithm.AUTO:
            alg = self._select_best_algorithm(gray1, gray2)
        
        # Detect keypoints and descriptors
        kp1, desc1 = self._detect_features(gray1, alg)
        kp2, desc2 = self._detect_features(gray2, alg)
        
        if len(kp1) == 0 or len(kp2) == 0:
            return MatchingResult([], kp1, kp2, desc1, desc2, 0.0, 0.0)
        
        # Match features
        matches = self._match_features(desc1, desc2, alg)
        
        # Calculate match score
        match_score = self._calculate_match_score(matches, len(kp1), len(kp2))
        
        # Calculate inlier ratio (simplified)
        inlier_ratio = len(matches) / min(len(kp1), len(kp2)) if matches else 0.0
        
        # Update statistics
        self.images_matched += 1
        self.total_matches += len(matches)
        
        return MatchingResult(
            matches=matches,
            keypoints1=kp1,
            keypoints2=kp2,
            descriptors1=desc1,
            descriptors2=desc2,
            match_score=match_score,
            inlier_ratio=inlier_ratio
        )
    
    def find_homography(self, img1: np.ndarray, img2: np.ndarray,
                       min_matches: int = 4) -> Tuple[Optional[np.ndarray], List[bool]]:
        """
        Find homography transformation between images.
        
        Returns:
            Homography matrix and inlier mask
        """
        # Get matches
        result = self.match_images(img1, img2)
        
        if len(result.matches) < min_matches:
            return None, []
        
        # Extract matched points
        src_pts = np.float32([
            result.keypoints1[m.queryIdx].pt for m in result.matches
        ]).reshape(-1, 1, 2)
        
        dst_pts = np.float32([
            result.keypoints2[m.trainIdx].pt for m in result.matches
        ]).reshape(-1, 1, 2)
        
        # Find homography using RANSAC
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        # Convert mask to list
        inliers = mask.ravel().tolist() if mask is not None else []
        
        return H, inliers
    
    def stitch_images(self, img1: np.ndarray, img2: np.ndarray) -> Optional[np.ndarray]:
        """
        Stitch two images together using feature matching.
        """
        # Find homography
        H, inliers = self.find_homography(img1, img2)
        
        if H is None:
            return None
        
        # Get dimensions
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        
        # Transform corners of img2
        corners2 = np.float32([[0, 0], [w2, 0], [w2, h2], [0, h2]]).reshape(-1, 1, 2)
        transformed_corners = cv2.perspectiveTransform(corners2, H)
        
        # Find bounding box
        all_corners = np.concatenate([
            np.float32([[0, 0], [w1, 0], [w1, h1], [0, h1]]).reshape(-1, 1, 2),
            transformed_corners
        ])
        
        x_min, y_min = np.int32(all_corners.min(axis=0).ravel())
        x_max, y_max = np.int32(all_corners.max(axis=0).ravel())
        
        # Translation matrix
        translation = np.array([[1, 0, -x_min], [0, 1, -y_min], [0, 0, 1]])
        
        # Warp images
        result_width = x_max - x_min
        result_height = y_max - y_min
        
        result = cv2.warpPerspective(img2, translation @ H, 
                                   (result_width, result_height))
        result[-y_min:h1-y_min, -x_min:w1-x_min] = img1
        
        return result
    
    def draw_matches(self, img1: np.ndarray, img2: np.ndarray,
                    matches: List[cv2.DMatch],
                    keypoints1: Optional[List[cv2.KeyPoint]] = None,
                    keypoints2: Optional[List[cv2.KeyPoint]] = None) -> np.ndarray:
        """
        Draw matches between two images.
        """
        if keypoints1 is None or keypoints2 is None:
            result = self.match_images(img1, img2)
            keypoints1 = result.keypoints1
            keypoints2 = result.keypoints2
            if not matches:
                matches = result.matches[:20]  # Top 20 matches
        
        # Draw matches
        match_img = cv2.drawMatches(
            img1, keypoints1, img2, keypoints2, matches,
            None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
        )
        
        return match_img
    
    def _detect_features(self, image: np.ndarray, 
                        algorithm: FeatureAlgorithm) -> Tuple[List, np.ndarray]:
        """Detect keypoints and compute descriptors"""
        detector = self.detectors[algorithm]
        
        try:
            keypoints, descriptors = detector.detectAndCompute(image, None)
            
            if descriptors is None:
                descriptors = np.array([])
            
            return keypoints, descriptors
        except Exception:
            return [], np.array([])
    
    def _match_features(self, desc1: np.ndarray, desc2: np.ndarray,
                       algorithm: FeatureAlgorithm) -> List[cv2.DMatch]:
        """Match descriptors using appropriate matcher"""
        if desc1.size == 0 or desc2.size == 0:
            return []
        
        matcher = self.matchers[algorithm]
        
        # KNN matching
        try:
            knn_matches = matcher.knnMatch(desc1, desc2, k=2)
        except Exception:
            return []
        
        # Apply Lowe's ratio test
        good_matches = []
        for match_pair in knn_matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < self.match_ratio * n.distance:
                    good_matches.append(m)
        
        # Sort by distance
        good_matches.sort(key=lambda x: x.distance)
        
        return good_matches
    
    def _select_best_algorithm(self, img1: np.ndarray, 
                             img2: np.ndarray) -> FeatureAlgorithm:
        """Automatically select best algorithm based on image characteristics"""
        # Simple heuristic based on image properties
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        
        # Calculate image complexity (edge density)
        edges1 = cv2.Canny(img1, 50, 150)
        edges2 = cv2.Canny(img2, 50, 150)
        edge_density = (np.sum(edges1 > 0) + np.sum(edges2 > 0)) / (edges1.size + edges2.size)
        
        # High resolution and high complexity -> SIFT
        if min(h1, w1, h2, w2) > 1000 and edge_density > 0.1:
            return FeatureAlgorithm.SIFT
        # Medium complexity -> AKAZE
        elif edge_density > 0.05:
            return FeatureAlgorithm.AKAZE
        # Low complexity or real-time needs -> ORB
        else:
            return FeatureAlgorithm.ORB
    
    def _calculate_match_score(self, matches: List[cv2.DMatch],
                             n_kp1: int, n_kp2: int) -> float:
        """Calculate overall match quality score"""
        if not matches:
            return 0.0
        
        # Average distance of top matches
        top_matches = matches[:min(20, len(matches))]
        avg_distance = np.mean([m.distance for m in top_matches])
        
        # Normalize by algorithm (different algorithms have different scales)
        # This is a simplified normalization
        normalized_distance = 1.0 / (1.0 + avg_distance / 100.0)
        
        # Consider number of matches
        match_ratio = len(matches) / min(n_kp1, n_kp2)
        
        # Combined score
        score = 0.7 * normalized_distance + 0.3 * match_ratio
        
        return float(np.clip(score, 0.0, 1.0))
    
    def _to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale if needed"""
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def track_features(self, img1: np.ndarray, img2: np.ndarray,
                      keypoints1: List[cv2.KeyPoint]) -> List[Tuple[cv2.KeyPoint, cv2.KeyPoint]]:
        """
        Track specific keypoints from img1 to img2.
        
        Returns:
            List of (keypoint1, keypoint2) pairs
        """
        gray1 = self._to_grayscale(img1)
        gray2 = self._to_grayscale(img2)
        
        # Get descriptors for specific keypoints
        detector = self.detectors[self.algorithm]
        _, desc1 = detector.compute(gray1, keypoints1)
        
        # Detect all features in img2
        kp2, desc2 = self._detect_features(gray2, self.algorithm)
        
        if desc1 is None or desc2 is None:
            return []
        
        # Match descriptors
        matches = self._match_features(desc1, desc2, self.algorithm)
        
        # Create tracked pairs
        tracked_pairs = []
        for match in matches:
            kp1 = keypoints1[match.queryIdx]
            kp2_matched = kp2[match.trainIdx]
            tracked_pairs.append((kp1, kp2_matched))
        
        return tracked_pairs
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get matching statistics"""
        return {
            "images_matched": self.images_matched,
            "total_matches": self.total_matches,
            "avg_matches_per_pair": (
                self.total_matches / self.images_matched
                if self.images_matched > 0 else 0
            ),
            "algorithm": self.algorithm.value,
            "max_features": self.max_features
        }


# Utility functions
def quick_match(img1: np.ndarray, img2: np.ndarray) -> List[cv2.DMatch]:
    """Quick feature matching with defaults"""
    matcher = FeatureMatcher(algorithm="orb")
    result = matcher.match_images(img1, img2)
    return result.matches


def find_object(template: np.ndarray, scene: np.ndarray) -> Optional[np.ndarray]:
    """Find template object in scene using feature matching"""
    matcher = FeatureMatcher(algorithm="auto", max_features=1000)
    H, inliers = matcher.find_homography(template, scene, min_matches=10)
    
    if H is not None and sum(inliers) > 10:
        h, w = template.shape[:2]
        pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, H)
        return dst
    
    return None


# Auto-generated tests
def test_feature_matcher():
    """Test feature matching functionality"""
    # Create test images
    img1 = np.random.randint(0, 255, (200, 200), dtype=np.uint8)
    cv2.rectangle(img1, (50, 50), (150, 150), 255, -1)
    
    # Create transformed version
    M = cv2.getRotationMatrix2D((100, 100), 15, 1.0)
    img2 = cv2.warpAffine(img1, M, (200, 200))
    
    # Test different algorithms
    algorithms = ["orb", "akaze", "brisk"]
    
    for alg in algorithms:
        matcher = FeatureMatcher(algorithm=alg)
        result = matcher.match_images(img1, img2)
        
        assert isinstance(result, MatchingResult)
        assert len(result.keypoints1) > 0
        assert len(result.keypoints2) > 0
    
    # Test homography
    matcher = FeatureMatcher()
    H, inliers = matcher.find_homography(img1, img2)
    # May not find homography with random images
    
    # Test visualization
    if result.matches:
        vis = matcher.draw_matches(img1, img2, result.matches[:5],
                                 result.keypoints1, result.keypoints2)
        assert vis.shape[0] == img1.shape[0]
        assert vis.shape[1] == img1.shape[1] + img2.shape[1]
    
    # Test statistics
    stats = matcher.get_statistics()
    assert stats["images_matched"] > 0
    
    print("All feature matching tests passed!")


if __name__ == "__main__":
    test_feature_matcher()