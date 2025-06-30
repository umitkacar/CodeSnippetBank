"""
Tissue ID: CV-TISSUE-005
Title: Smart Region Blur for Privacy Protection
Category: computer_vision/effects
Tags: ["blur", "privacy", "gaussian", "pixelate", "effects"]
Difficulty: Beginner
Dependencies: ["opencv-python>=4.5.0", "numpy>=1.19.0"]
Performance: O(k²n) where k is kernel size, n is region pixels
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A privacy-focused tissue that applies various blur effects to specific regions
of an image. Supports Gaussian blur, pixelation, and solid color overlay.
Perfect for face anonymization, license plate hiding, and GDPR compliance.

Use Cases:
- Face anonymization in photos/videos
- License plate blurring
- Document redaction
- Privacy-compliant image processing
- Artistic blur effects

Example Usage:
    blurrer = RegionBlur(method="gaussian", strength=0.8)
    
    # Blur single region
    blurred = blurrer.blur_region(image, (x, y, w, h))
    
    # Blur multiple regions
    regions = [(x1, y1, w1, h1), (x2, y2, w2, h2)]
    blurred = blurrer.blur_multiple(image, regions)
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Union, Dict, Any


class RegionBlur:
    """
    Smart region blurring for privacy protection.
    Tissue Type: ENERGETIC - Provides performance-optimized blur effects.
    """
    
    def __init__(self,
                 method: str = "gaussian",
                 strength: float = 0.8,
                 pixelation_size: int = 15):
        """
        Initialize region blur.
        
        Args:
            method: 'gaussian', 'pixelate', 'solid', or 'motion'
            strength: Blur strength (0.0 to 1.0)
            pixelation_size: Size of pixels for pixelate method
        """
        self.method = method
        self.strength = np.clip(strength, 0.0, 1.0)
        self.pixelation_size = max(1, pixelation_size)
        
        # Performance stats
        self.regions_processed = 0
        self.total_pixels_blurred = 0
    
    def blur_region(self, 
                   image: np.ndarray,
                   region: Tuple[int, int, int, int],
                   method: Optional[str] = None) -> np.ndarray:
        """
        Blur a single region in the image.
        
        Args:
            image: Input image
            region: (x, y, width, height) of region to blur
            method: Override default method for this region
            
        Returns:
            Image with blurred region
        """
        if image is None or image.size == 0:
            return image
        
        # Make a copy to avoid modifying original
        result = image.copy()
        x, y, w, h = region
        
        # Validate region bounds
        h_img, w_img = image.shape[:2]
        x = max(0, min(x, w_img - 1))
        y = max(0, min(y, h_img - 1))
        w = min(w, w_img - x)
        h = min(h, h_img - y)
        
        if w <= 0 or h <= 0:
            return result
        
        # Extract region
        roi = result[y:y+h, x:x+w]
        
        # Apply blur method
        blur_method = method or self.method
        
        if blur_method == "gaussian":
            blurred_roi = self._gaussian_blur(roi)
        elif blur_method == "pixelate":
            blurred_roi = self._pixelate(roi)
        elif blur_method == "solid":
            blurred_roi = self._solid_color(roi)
        elif blur_method == "motion":
            blurred_roi = self._motion_blur(roi)
        else:
            raise ValueError(f"Unknown blur method: {blur_method}")
        
        # Replace region
        result[y:y+h, x:x+w] = blurred_roi
        
        # Update stats
        self.regions_processed += 1
        self.total_pixels_blurred += w * h
        
        return result
    
    def blur_multiple(self,
                     image: np.ndarray,
                     regions: List[Tuple[int, int, int, int]],
                     methods: Optional[List[str]] = None) -> np.ndarray:
        """
        Blur multiple regions efficiently.
        
        Args:
            image: Input image
            regions: List of (x, y, width, height) tuples
            methods: Optional list of methods for each region
            
        Returns:
            Image with all regions blurred
        """
        result = image.copy()
        
        if methods is None:
            methods = [self.method] * len(regions)
        
        for region, method in zip(regions, methods):
            result = self.blur_region(result, region, method)
        
        return result
    
    def _gaussian_blur(self, roi: np.ndarray) -> np.ndarray:
        """Apply Gaussian blur to region"""
        # Calculate kernel size based on strength and region size
        min_dimension = min(roi.shape[:2])
        kernel_size = int(min_dimension * self.strength * 0.3)
        kernel_size = max(3, kernel_size)
        
        # Ensure odd kernel size
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # Apply blur
        return cv2.GaussianBlur(roi, (kernel_size, kernel_size), 0)
    
    def _pixelate(self, roi: np.ndarray) -> np.ndarray:
        """Apply pixelation effect"""
        h, w = roi.shape[:2]
        
        # Calculate pixelation size based on strength
        pixel_size = int(self.pixelation_size * self.strength)
        pixel_size = max(1, min(pixel_size, min(h, w)))
        
        # Downscale
        small_h = max(1, h // pixel_size)
        small_w = max(1, w // pixel_size)
        small = cv2.resize(roi, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
        
        # Upscale back
        pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        
        return pixelated
    
    def _solid_color(self, roi: np.ndarray) -> np.ndarray:
        """Replace with solid color (average color of region)"""
        # Calculate average color
        avg_color = cv2.mean(roi)[:3]
        
        # Create solid color image
        solid = np.ones_like(roi)
        if len(roi.shape) == 3:
            for c in range(roi.shape[2]):
                solid[:, :, c] = avg_color[c]
        else:
            solid[:, :] = avg_color[0]
        
        # Blend based on strength
        alpha = self.strength
        blended = cv2.addWeighted(roi, 1 - alpha, solid, alpha, 0)
        
        return blended.astype(roi.dtype)
    
    def _motion_blur(self, roi: np.ndarray) -> np.ndarray:
        """Apply motion blur effect"""
        # Create motion blur kernel
        size = int(15 * self.strength)
        size = max(3, size)
        
        kernel = np.zeros((size, size))
        kernel[size // 2, :] = 1.0
        kernel = kernel / size
        
        # Apply motion blur
        return cv2.filter2D(roi, -1, kernel)
    
    def blur_faces(self, 
                  image: np.ndarray,
                  face_regions: List[Tuple[int, int, int, int]],
                  expand_ratio: float = 1.2) -> np.ndarray:
        """
        Specialized face blurring with region expansion.
        
        Args:
            image: Input image
            face_regions: List of face bounding boxes
            expand_ratio: Expand regions for better coverage
            
        Returns:
            Image with faces blurred
        """
        expanded_regions = []
        
        for x, y, w, h in face_regions:
            # Expand region
            expand_w = int(w * expand_ratio)
            expand_h = int(h * expand_ratio)
            expand_x = x - (expand_w - w) // 2
            expand_y = y - (expand_h - h) // 2
            
            expanded_regions.append((expand_x, expand_y, expand_w, expand_h))
        
        # Use Gaussian blur for natural look
        old_method = self.method
        self.method = "gaussian"
        result = self.blur_multiple(image, expanded_regions)
        self.method = old_method
        
        return result
    
    def create_blur_mask(self,
                        image_shape: Tuple[int, int],
                        regions: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """
        Create a mask showing which areas will be blurred.
        
        Args:
            image_shape: (height, width) of image
            regions: List of regions to blur
            
        Returns:
            Binary mask (255 for blur regions, 0 otherwise)
        """
        mask = np.zeros(image_shape[:2], dtype=np.uint8)
        
        for x, y, w, h in regions:
            mask[y:y+h, x:x+w] = 255
        
        return mask
    
    def adaptive_blur(self,
                     image: np.ndarray,
                     region: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Adaptively choose blur method based on region content.
        """
        x, y, w, h = region
        roi = image[y:y+h, x:x+w]
        
        # Analyze region
        std_dev = np.std(roi)
        
        # High variance = use pixelate to preserve some structure
        if std_dev > 50:
            return self.blur_region(image, region, method="pixelate")
        # Medium variance = Gaussian blur
        elif std_dev > 20:
            return self.blur_region(image, region, method="gaussian")
        # Low variance = solid color is enough
        else:
            return self.blur_region(image, region, method="solid")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get blur operation statistics"""
        return {
            "regions_processed": self.regions_processed,
            "total_pixels_blurred": self.total_pixels_blurred,
            "average_region_size": (
                self.total_pixels_blurred / self.regions_processed 
                if self.regions_processed > 0 else 0
            )
        }


# Utility functions
def blur_faces_in_image(image: np.ndarray, 
                       face_regions: List[Tuple[int, int, int, int]]) -> np.ndarray:
    """Quick function to blur faces with default settings"""
    blurrer = RegionBlur(method="gaussian", strength=0.9)
    return blurrer.blur_faces(image, face_regions)


def create_privacy_compliant_image(image: np.ndarray,
                                 sensitive_regions: List[Tuple[int, int, int, int]]) -> np.ndarray:
    """Create GDPR-compliant version of image"""
    blurrer = RegionBlur(method="pixelate", strength=1.0, pixelation_size=20)
    return blurrer.blur_multiple(image, sensitive_regions)


# Auto-generated tests
def test_region_blur():
    """Test region blur functionality"""
    # Create test image
    test_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    
    # Initialize blurrer
    blurrer = RegionBlur()
    
    # Test single region blur
    region = (50, 50, 100, 100)
    result = blurrer.blur_region(test_image, region)
    assert result.shape == test_image.shape
    assert not np.array_equal(result[50:150, 50:150], test_image[50:150, 50:150])
    
    # Test different methods
    methods = ["gaussian", "pixelate", "solid", "motion"]
    for method in methods:
        blurrer_method = RegionBlur(method=method)
        result = blurrer_method.blur_region(test_image, region)
        assert result.shape == test_image.shape
    
    # Test multiple regions
    regions = [(10, 10, 30, 30), (100, 100, 50, 50)]
    result = blurrer.blur_multiple(test_image, regions)
    assert result.shape == test_image.shape
    
    # Test statistics
    stats = blurrer.get_statistics()
    assert stats["regions_processed"] > 0
    
    print("All region blur tests passed!")


if __name__ == "__main__":
    test_region_blur()