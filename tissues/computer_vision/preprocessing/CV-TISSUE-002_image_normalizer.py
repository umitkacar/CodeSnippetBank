"""
Tissue ID: CV-TISSUE-002
Title: Smart Image Normalizer for CV Pipeline
Category: computer_vision/preprocessing
Tags: ["preprocessing", "normalization", "edge-compatible", "optimization"]
Difficulty: Beginner
Dependencies: ["numpy>=1.19.0", "opencv-python>=4.5.0"]
Performance: O(n) where n is number of pixels
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
An intelligent image preprocessing tissue that normalizes images for optimal
performance in computer vision pipelines. Handles various input formats and
automatically adjusts parameters based on image characteristics.

Use Cases:
- Preprocessing before face/object detection
- Standardizing images from different sources
- Improving model performance
- Reducing computational load on edge devices

Example Usage:
    normalizer = ImageNormalizer()
    processed = normalizer.normalize(image)
    # Now ready for detection/classification
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Union


class ImageNormalizer:
    """
    Smart image normalization for computer vision pipelines.
    Tissue Type: STRUCTURAL - Forms backbone of CV preprocessing.
    """
    
    def __init__(self,
                 target_size: Optional[Tuple[int, int]] = None,
                 maintain_aspect: bool = True,
                 normalize_values: bool = True,
                 adaptive_histogram: bool = False):
        """
        Initialize image normalizer.
        
        Args:
            target_size: Target (width, height) or None for dynamic sizing
            maintain_aspect: Maintain aspect ratio when resizing
            normalize_values: Normalize pixel values to [0, 1]
            adaptive_histogram: Apply adaptive histogram equalization
        """
        self.target_size = target_size
        self.maintain_aspect = maintain_aspect
        self.normalize_values = normalize_values
        self.adaptive_histogram = adaptive_histogram
        
        # Statistics for adaptive processing
        self.stats = {
            "mean_brightness": [],
            "contrast": [],
            "sharpness": []
        }
    
    def normalize(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize image for CV pipeline.
        
        Args:
            image: Input image (any format)
            
        Returns:
            Normalized image ready for processing
        """
        if image is None or image.size == 0:
            raise ValueError("Invalid input image")
        
        # Ensure we have a copy to avoid modifying original
        processed = image.copy()
        
        # Step 1: Ensure correct format
        processed = self._ensure_format(processed)
        
        # Step 2: Resize if needed
        if self.target_size is not None:
            processed = self._smart_resize(processed)
        
        # Step 3: Enhance quality if needed
        processed = self._enhance_quality(processed)
        
        # Step 4: Normalize values
        if self.normalize_values:
            processed = self._normalize_values(processed)
        
        return processed
    
    def _ensure_format(self, image: np.ndarray) -> np.ndarray:
        """Ensure image is in correct format"""
        # Convert to uint8 if needed
        if image.dtype != np.uint8:
            if image.max() <= 1.0:
                image = (image * 255).astype(np.uint8)
            else:
                image = np.clip(image, 0, 255).astype(np.uint8)
        
        # Ensure 3 channels for consistency
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        
        return image
    
    def _smart_resize(self, image: np.ndarray) -> np.ndarray:
        """Intelligently resize image"""
        h, w = image.shape[:2]
        target_w, target_h = self.target_size
        
        if self.maintain_aspect:
            # Calculate scaling factor
            scale = min(target_w / w, target_h / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            # Resize maintaining aspect ratio
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            # Pad to target size
            pad_w = target_w - new_w
            pad_h = target_h - new_h
            
            top = pad_h // 2
            bottom = pad_h - top
            left = pad_w // 2
            right = pad_w - left
            
            # Pad with mean color for better blending
            mean_color = cv2.mean(resized)[:3]
            resized = cv2.copyMakeBorder(
                resized, top, bottom, left, right,
                cv2.BORDER_CONSTANT, value=mean_color
            )
        else:
            # Direct resize
            resized = cv2.resize(image, self.target_size, interpolation=cv2.INTER_AREA)
        
        return resized
    
    def _enhance_quality(self, image: np.ndarray) -> np.ndarray:
        """Enhance image quality adaptively"""
        # Calculate image statistics
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Store statistics
        self.stats["mean_brightness"].append(mean_brightness)
        self.stats["contrast"].append(contrast)
        
        # Apply adaptive histogram equalization if needed
        if self.adaptive_histogram or contrast < 30:
            # Create CLAHE object
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            
            # Apply to each channel
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Adjust brightness if too dark/bright
        if mean_brightness < 50:
            # Brighten dark images
            image = cv2.convertScaleAbs(image, alpha=1.2, beta=20)
        elif mean_brightness > 200:
            # Darken bright images
            image = cv2.convertScaleAbs(image, alpha=0.8, beta=-20)
        
        return image
    
    def _normalize_values(self, image: np.ndarray) -> np.ndarray:
        """Normalize pixel values"""
        # Convert to float32 and normalize to [0, 1]
        normalized = image.astype(np.float32) / 255.0
        
        # Optional: Standardize using ImageNet stats
        # This helps when feeding to pre-trained models
        # mean = np.array([0.485, 0.456, 0.406])
        # std = np.array([0.229, 0.224, 0.225])
        # normalized = (normalized - mean) / std
        
        return normalized
    
    def get_preprocessing_stats(self) -> dict:
        """Get statistics about processed images"""
        stats = {}
        
        for key, values in self.stats.items():
            if values:
                stats[key] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values)
                }
        
        return stats
    
    def adapt_parameters(self):
        """Adapt preprocessing parameters based on statistics"""
        if len(self.stats["contrast"]) > 10:
            avg_contrast = np.mean(self.stats["contrast"][-10:])
            
            # Enable adaptive histogram if consistently low contrast
            if avg_contrast < 40:
                self.adaptive_histogram = True
                print("Enabled adaptive histogram due to low contrast images")


# Utility functions for common preprocessing tasks
def resize_for_edge(image: np.ndarray, max_size: int = 640) -> np.ndarray:
    """Quick resize for edge devices"""
    h, w = image.shape[:2]
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return image


def prepare_batch(images: list, size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """Prepare batch of images for model input"""
    normalizer = ImageNormalizer(target_size=size)
    batch = []
    
    for img in images:
        normalized = normalizer.normalize(img)
        batch.append(normalized)
    
    return np.array(batch)


# Auto-generated tests
def test_image_normalizer():
    """Test image normalization functionality"""
    # Create test images
    test_gray = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    test_color = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    test_rgba = np.random.randint(0, 255, (100, 100, 4), dtype=np.uint8)
    
    normalizer = ImageNormalizer(target_size=(64, 64))
    
    # Test different input formats
    result_gray = normalizer.normalize(test_gray)
    assert result_gray.shape == (64, 64, 3), "Gray image should be converted to BGR"
    
    result_color = normalizer.normalize(test_color)
    assert result_color.shape == (64, 64, 3), "Color image should be resized"
    
    result_rgba = normalizer.normalize(test_rgba)
    assert result_rgba.shape == (64, 64, 3), "RGBA should be converted to BGR"
    
    # Test value normalization
    normalizer_values = ImageNormalizer(normalize_values=True)
    result_norm = normalizer_values.normalize(test_color)
    assert result_norm.max() <= 1.0, "Values should be normalized"
    
    print("All tests passed!")


if __name__ == "__main__":
    test_image_normalizer()