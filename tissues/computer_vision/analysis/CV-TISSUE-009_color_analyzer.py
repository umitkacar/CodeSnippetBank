"""
Tissue ID: CV-TISSUE-009
Title: Advanced Color Analysis Engine
Category: computer_vision/analysis
Tags: ["color-analysis", "histogram", "dominant-colors", "palette", "color-space"]
Difficulty: Intermediate
Dependencies: ["opencv-python>=4.5.0", "numpy>=1.19.0", "scipy>=1.7.0"]
Performance: O(n) where n is number of pixels
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A sophisticated color analysis tissue that extracts color information, finds dominant
colors, generates color palettes, and performs color-based segmentation. Supports
multiple color spaces (RGB, HSV, LAB) and provides rich analytics for color-based
applications.

Use Cases:
- Brand color extraction from logos
- Palette generation for design
- Color-based object detection
- Image mood analysis
- Quality control in manufacturing

Example Usage:
    analyzer = ColorAnalyzer(color_space="hsv")
    
    # Get dominant colors
    palette = analyzer.extract_palette(image, n_colors=5)
    
    # Analyze color distribution
    stats = analyzer.analyze_distribution(image)
    
    # Find specific color regions
    mask = analyzer.find_color_regions(image, target_color=(255, 0, 0))
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional, Any, Union
from dataclasses import dataclass
from scipy.spatial import distance
from collections import Counter
import colorsys


@dataclass
class ColorInfo:
    """Container for color information"""
    rgb: Tuple[int, int, int]
    hsv: Tuple[int, int, int]
    lab: Tuple[float, float, float]
    hex: str
    percentage: float
    pixel_count: int
    
    @property
    def brightness(self) -> float:
        """Calculate perceived brightness (0-1)"""
        r, g, b = self.rgb
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    
    @property
    def saturation(self) -> float:
        """Get saturation from HSV (0-1)"""
        return self.hsv[1] / 255.0


class ColorAnalyzer:
    """
    Advanced color analysis engine for comprehensive color information.
    Tissue Type: STRUCTURAL - Analyzes image structure through color.
    """
    
    # Predefined color ranges for common colors (HSV)
    COLOR_RANGES = {
        "red": [(0, 50, 50), (10, 255, 255), (170, 50, 50), (180, 255, 255)],
        "orange": [(11, 50, 50), (25, 255, 255)],
        "yellow": [(26, 50, 50), (35, 255, 255)],
        "green": [(36, 50, 50), (85, 255, 255)],
        "blue": [(86, 50, 50), (125, 255, 255)],
        "purple": [(126, 50, 50), (169, 255, 255)],
        "white": [(0, 0, 200), (180, 30, 255)],
        "black": [(0, 0, 0), (180, 255, 30)],
        "gray": [(0, 0, 31), (180, 30, 199)]
    }
    
    def __init__(self,
                 color_space: str = "rgb",
                 quantization_level: int = 64,
                 min_color_percentage: float = 0.01):
        """
        Initialize color analyzer.
        
        Args:
            color_space: Primary color space ('rgb', 'hsv', 'lab')
            quantization_level: Color quantization for clustering
            min_color_percentage: Minimum percentage to consider a color
        """
        self.color_space = color_space.lower()
        self.quantization_level = quantization_level
        self.min_color_percentage = min_color_percentage
        
        # Statistics
        self.images_analyzed = 0
        self.colors_extracted = 0
    
    def extract_palette(self, image: np.ndarray, 
                       n_colors: int = 5,
                       method: str = "kmeans") -> List[ColorInfo]:
        """
        Extract dominant color palette from image.
        
        Args:
            image: Input image
            n_colors: Number of colors to extract
            method: 'kmeans', 'quantization', or 'histogram'
            
        Returns:
            List of ColorInfo objects
        """
        if image is None or image.size == 0:
            return []
        
        # Convert to RGB if grayscale
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        if method == "kmeans":
            palette = self._extract_kmeans(image, n_colors)
        elif method == "quantization":
            palette = self._extract_quantization(image, n_colors)
        elif method == "histogram":
            palette = self._extract_histogram(image, n_colors)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        self.images_analyzed += 1
        self.colors_extracted += len(palette)
        
        return palette
    
    def _extract_kmeans(self, image: np.ndarray, n_colors: int) -> List[ColorInfo]:
        """Extract colors using K-means clustering"""
        # Reshape image to pixel list
        pixels = image.reshape(-1, 3).astype(np.float32)
        
        # Apply K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
        _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 
                                      10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Count pixels per cluster
        label_counts = Counter(labels.flatten())
        total_pixels = len(labels)
        
        # Create color info
        palette = []
        for i, center in enumerate(centers):
            rgb = tuple(center.astype(int))
            pixel_count = label_counts[i]
            percentage = pixel_count / total_pixels
            
            if percentage >= self.min_color_percentage:
                color_info = self._create_color_info(rgb, pixel_count, percentage)
                palette.append(color_info)
        
        # Sort by percentage
        palette.sort(key=lambda x: x.percentage, reverse=True)
        
        return palette[:n_colors]
    
    def _extract_quantization(self, image: np.ndarray, n_colors: int) -> List[ColorInfo]:
        """Extract colors using color quantization"""
        # Quantize colors
        div = 256 // self.quantization_level
        quantized = (image // div) * div + div // 2
        
        # Count unique colors
        pixels = quantized.reshape(-1, 3)
        unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
        
        # Sort by frequency
        sorted_indices = np.argsort(counts)[::-1]
        
        palette = []
        total_pixels = len(pixels)
        
        for i in range(min(n_colors, len(unique_colors))):
            idx = sorted_indices[i]
            rgb = tuple(unique_colors[idx])
            pixel_count = counts[idx]
            percentage = pixel_count / total_pixels
            
            if percentage >= self.min_color_percentage:
                color_info = self._create_color_info(rgb, pixel_count, percentage)
                palette.append(color_info)
        
        return palette
    
    def _extract_histogram(self, image: np.ndarray, n_colors: int) -> List[ColorInfo]:
        """Extract colors using histogram peaks"""
        # Convert to HSV for better color separation
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Calculate histogram for hue channel
        hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        hist = hist.flatten()
        
        # Find peaks
        peaks = []
        for i in range(1, len(hist) - 1):
            if hist[i] > hist[i-1] and hist[i] > hist[i+1]:
                peaks.append((hist[i], i))
        
        # Sort peaks by magnitude
        peaks.sort(reverse=True)
        
        palette = []
        total_pixels = image.shape[0] * image.shape[1]
        
        for count, hue in peaks[:n_colors]:
            # Find pixels with this hue
            mask = (hsv[:, :, 0] >= hue - 5) & (hsv[:, :, 0] <= hue + 5)
            masked_pixels = image[mask]
            
            if len(masked_pixels) > 0:
                # Get average color
                avg_color = np.mean(masked_pixels, axis=0)
                rgb = tuple(avg_color.astype(int))
                pixel_count = np.sum(mask)
                percentage = pixel_count / total_pixels
                
                if percentage >= self.min_color_percentage:
                    color_info = self._create_color_info(rgb, pixel_count, percentage)
                    palette.append(color_info)
        
        return palette
    
    def analyze_distribution(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze color distribution in image.
        
        Returns:
            Dictionary with distribution statistics
        """
        if image is None or image.size == 0:
            return {}
        
        # Convert to different color spaces
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Calculate statistics for each channel
        stats = {
            "rgb": self._channel_stats(image),
            "hsv": self._channel_stats(hsv),
            "lab": self._channel_stats(lab),
            "dominant_hue": self._find_dominant_hue(hsv),
            "color_diversity": self._calculate_diversity(image),
            "brightness": {
                "mean": np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)),
                "std": np.std(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
            },
            "saturation": {
                "mean": np.mean(hsv[:, :, 1]),
                "std": np.std(hsv[:, :, 1])
            }
        }
        
        return stats
    
    def find_color_regions(self, image: np.ndarray,
                         target_color: Union[Tuple[int, int, int], str],
                         tolerance: int = 30) -> np.ndarray:
        """
        Find regions matching target color.
        
        Args:
            image: Input image
            target_color: RGB tuple or color name
            tolerance: Color matching tolerance
            
        Returns:
            Binary mask of matching regions
        """
        if image is None or image.size == 0:
            return np.zeros((1, 1), dtype=np.uint8)
        
        # Convert to HSV for better color matching
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Get target HSV range
        if isinstance(target_color, str):
            hsv_ranges = self._get_color_range(target_color)
        else:
            # Convert RGB to HSV
            target_hsv = cv2.cvtColor(
                np.uint8([[target_color]]), 
                cv2.COLOR_BGR2HSV
            )[0][0]
            
            # Create range
            lower = np.array([
                max(0, target_hsv[0] - tolerance),
                max(0, target_hsv[1] - tolerance),
                max(0, target_hsv[2] - tolerance)
            ])
            upper = np.array([
                min(180, target_hsv[0] + tolerance),
                min(255, target_hsv[1] + tolerance),
                min(255, target_hsv[2] + tolerance)
            ])
            hsv_ranges = [(lower, upper)]
        
        # Create mask
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        for lower, upper in hsv_ranges:
            mask |= cv2.inRange(hsv, lower, upper)
        
        # Morphological operations to clean up
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return mask
    
    def segment_by_color(self, image: np.ndarray,
                        n_segments: int = 5) -> Tuple[np.ndarray, List[ColorInfo]]:
        """
        Segment image by color similarity.
        
        Returns:
            Segmentation mask and color palette
        """
        # Extract palette
        palette = self.extract_palette(image, n_segments, method="kmeans")
        
        # Create segmentation mask
        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Assign each pixel to nearest color
        pixels = image.reshape(-1, 3)
        
        for i, pixel in enumerate(pixels):
            # Find nearest color in palette
            min_dist = float('inf')
            best_idx = 0
            
            for idx, color_info in enumerate(palette):
                dist = np.linalg.norm(pixel - np.array(color_info.rgb))
                if dist < min_dist:
                    min_dist = dist
                    best_idx = idx
            
            mask.flat[i] = best_idx
        
        mask = mask.reshape(h, w)
        
        return mask, palette
    
    def generate_complementary(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Generate complementary color"""
        # Convert to HSV
        hsv = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_BGR2HSV)[0][0]
        
        # Rotate hue by 180 degrees
        hsv[0] = (hsv[0] + 90) % 180
        
        # Convert back to BGR
        bgr = cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2BGR)[0][0]
        
        return tuple(bgr)
    
    def generate_analogous(self, color: Tuple[int, int, int], 
                         n_colors: int = 3) -> List[Tuple[int, int, int]]:
        """Generate analogous color scheme"""
        colors = []
        
        # Convert to HSV
        hsv = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_BGR2HSV)[0][0]
        
        # Generate colors with similar hues
        hue_step = 30 // n_colors
        
        for i in range(n_colors):
            new_hsv = hsv.copy()
            new_hsv[0] = (hsv[0] + (i - n_colors//2) * hue_step) % 180
            
            # Convert back to BGR
            bgr = cv2.cvtColor(np.uint8([[new_hsv]]), cv2.COLOR_HSV2BGR)[0][0]
            colors.append(tuple(bgr))
        
        return colors
    
    def _create_color_info(self, rgb: Tuple[int, int, int],
                         pixel_count: int, percentage: float) -> ColorInfo:
        """Create ColorInfo object with all color space conversions"""
        # Convert to HSV
        hsv = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_BGR2HSV)[0][0]
        
        # Convert to LAB
        lab = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_BGR2LAB)[0][0]
        
        # Create hex color
        hex_color = "#{:02x}{:02x}{:02x}".format(rgb[2], rgb[1], rgb[0])  # BGR to RGB
        
        return ColorInfo(
            rgb=(rgb[2], rgb[1], rgb[0]),  # Convert BGR to RGB
            hsv=tuple(hsv),
            lab=tuple(lab),
            hex=hex_color,
            percentage=percentage,
            pixel_count=pixel_count
        )
    
    def _channel_stats(self, image: np.ndarray) -> Dict[str, Dict[str, float]]:
        """Calculate statistics for each channel"""
        stats = {}
        channel_names = ["channel_0", "channel_1", "channel_2"]
        
        for i, name in enumerate(channel_names[:image.shape[2]]):
            channel = image[:, :, i]
            stats[name] = {
                "mean": float(np.mean(channel)),
                "std": float(np.std(channel)),
                "min": float(np.min(channel)),
                "max": float(np.max(channel))
            }
        
        return stats
    
    def _find_dominant_hue(self, hsv: np.ndarray) -> int:
        """Find dominant hue in HSV image"""
        hue_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        return int(np.argmax(hue_hist))
    
    def _calculate_diversity(self, image: np.ndarray) -> float:
        """Calculate color diversity score (0-1)"""
        # Quantize colors
        div = 32
        quantized = (image // div) * div
        
        # Count unique colors
        pixels = quantized.reshape(-1, 3)
        unique_colors = len(np.unique(pixels, axis=0))
        
        # Normalize by maximum possible colors
        max_colors = min(len(pixels), (256 // div) ** 3)
        diversity = unique_colors / max_colors
        
        return float(diversity)
    
    def _get_color_range(self, color_name: str) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Get HSV range for named color"""
        if color_name.lower() not in self.COLOR_RANGES:
            raise ValueError(f"Unknown color: {color_name}")
        
        ranges = self.COLOR_RANGES[color_name.lower()]
        hsv_ranges = []
        
        # Convert to numpy arrays
        for i in range(0, len(ranges), 2):
            lower = np.array(ranges[i])
            upper = np.array(ranges[i + 1])
            hsv_ranges.append((lower, upper))
        
        return hsv_ranges
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics"""
        return {
            "images_analyzed": self.images_analyzed,
            "colors_extracted": self.colors_extracted,
            "avg_colors_per_image": (
                self.colors_extracted / self.images_analyzed
                if self.images_analyzed > 0 else 0
            )
        }


# Utility functions
def extract_brand_colors(image: np.ndarray, n_colors: int = 3) -> List[ColorInfo]:
    """Extract brand colors from logo/image"""
    analyzer = ColorAnalyzer(min_color_percentage=0.05)
    return analyzer.extract_palette(image, n_colors, method="kmeans")


def find_matching_pixels(image: np.ndarray, target_color: Tuple[int, int, int],
                        tolerance: int = 20) -> np.ndarray:
    """Find all pixels matching target color"""
    analyzer = ColorAnalyzer()
    return analyzer.find_color_regions(image, target_color, tolerance)


# Auto-generated tests
def test_color_analyzer():
    """Test color analysis functionality"""
    # Create test image with known colors
    test_image = np.zeros((100, 300, 3), dtype=np.uint8)
    test_image[:, :100] = [255, 0, 0]  # Blue
    test_image[:, 100:200] = [0, 255, 0]  # Green
    test_image[:, 200:] = [0, 0, 255]  # Red
    
    analyzer = ColorAnalyzer()
    
    # Test palette extraction
    palette = analyzer.extract_palette(test_image, n_colors=3)
    assert len(palette) == 3
    assert all(isinstance(c, ColorInfo) for c in palette)
    
    # Test color distribution
    stats = analyzer.analyze_distribution(test_image)
    assert "rgb" in stats
    assert "color_diversity" in stats
    
    # Test color region finding
    red_mask = analyzer.find_color_regions(test_image, (255, 0, 0))
    assert red_mask.shape == test_image.shape[:2]
    assert np.any(red_mask > 0)
    
    # Test color segmentation
    mask, palette = analyzer.segment_by_color(test_image, n_segments=3)
    assert mask.shape == test_image.shape[:2]
    assert len(np.unique(mask)) <= 3
    
    # Test color generation
    comp = analyzer.generate_complementary((255, 0, 0))
    assert len(comp) == 3
    
    analogous = analyzer.generate_analogous((255, 0, 0), n_colors=3)
    assert len(analogous) == 3
    
    print("All color analysis tests passed!")


if __name__ == "__main__":
    test_color_analyzer()