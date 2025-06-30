"""
Tissue ID: CV-TISSUE-008
Title: Advanced Image Augmentation Suite
Category: computer_vision/transformation
Tags: ["augmentation", "data-augmentation", "transforms", "training", "preprocessing"]
Difficulty: Intermediate
Dependencies: ["opencv-python>=4.5.0", "numpy>=1.19.0"]
Performance: O(n) where n is number of pixels
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive image augmentation tissue that provides various transformation
techniques for data augmentation in ML/DL pipelines. Includes geometric transforms,
color adjustments, noise injection, and custom augmentation pipelines.

Use Cases:
- Training data augmentation for ML models
- Synthetic data generation
- Image preprocessing for robustness
- Testing model invariance
- Creative image effects

Example Usage:
    augmenter = ImageAugmenter(seed=42)
    
    # Single augmentation
    augmented = augmenter.random_augment(image, strength=0.5)
    
    # Custom pipeline
    pipeline = augmenter.create_pipeline([
        ("rotate", {"angle": 15}),
        ("brightness", {"factor": 1.2}),
        ("gaussian_noise", {"intensity": 0.1})
    ])
    result = augmenter.apply_pipeline(image, pipeline)
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Callable
from dataclasses import dataclass
import random


@dataclass
class AugmentationConfig:
    """Configuration for augmentation parameters"""
    rotation_range: Tuple[float, float] = (-30, 30)
    scale_range: Tuple[float, float] = (0.8, 1.2)
    shear_range: Tuple[float, float] = (-0.2, 0.2)
    brightness_range: Tuple[float, float] = (0.7, 1.3)
    contrast_range: Tuple[float, float] = (0.7, 1.3)
    saturation_range: Tuple[float, float] = (0.7, 1.3)
    hue_shift_range: Tuple[int, int] = (-20, 20)
    noise_intensity: float = 0.1
    blur_kernel_range: Tuple[int, int] = (3, 7)


class ImageAugmenter:
    """
    Advanced image augmentation suite for ML/DL pipelines.
    Tissue Type: ENERGETIC - Provides efficient transformations.
    """
    
    def __init__(self,
                 config: Optional[AugmentationConfig] = None,
                 seed: Optional[int] = None,
                 preserve_range: bool = True):
        """
        Initialize image augmenter.
        
        Args:
            config: Augmentation configuration
            seed: Random seed for reproducibility
            preserve_range: Keep pixel values in original range
        """
        self.config = config or AugmentationConfig()
        self.preserve_range = preserve_range
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Available augmentations
        self.augmentations = {
            "rotate": self.rotate,
            "scale": self.scale,
            "shear": self.shear,
            "flip_horizontal": self.flip_horizontal,
            "flip_vertical": self.flip_vertical,
            "brightness": self.brightness,
            "contrast": self.contrast,
            "saturation": self.saturation,
            "hue_shift": self.hue_shift,
            "gaussian_noise": self.gaussian_noise,
            "salt_pepper_noise": self.salt_pepper_noise,
            "gaussian_blur": self.gaussian_blur,
            "motion_blur": self.motion_blur,
            "elastic_transform": self.elastic_transform,
            "cutout": self.cutout
        }
        
        # Statistics
        self.augmentations_applied = 0
        self.images_processed = 0
    
    def random_augment(self, image: np.ndarray, 
                      strength: float = 0.5,
                      num_augmentations: int = 3) -> np.ndarray:
        """
        Apply random augmentations to image.
        
        Args:
            image: Input image
            strength: Overall strength (0-1)
            num_augmentations: Number of augmentations to apply
            
        Returns:
            Augmented image
        """
        if image is None or image.size == 0:
            return image
        
        # Select random augmentations
        selected = random.sample(list(self.augmentations.keys()), 
                               min(num_augmentations, len(self.augmentations)))
        
        result = image.copy()
        
        for aug_name in selected:
            # Generate random parameters based on strength
            params = self._get_random_params(aug_name, strength)
            result = self.augmentations[aug_name](result, **params)
            self.augmentations_applied += 1
        
        self.images_processed += 1
        return result
    
    def rotate(self, image: np.ndarray, angle: float = 0.0) -> np.ndarray:
        """Rotate image by given angle"""
        if angle == 0:
            angle = random.uniform(*self.config.rotation_range)
        
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        
        # Rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Rotate with black fill
        rotated = cv2.warpAffine(image, M, (w, h), 
                               borderMode=cv2.BORDER_REFLECT_101)
        
        return rotated
    
    def scale(self, image: np.ndarray, factor: float = 1.0) -> np.ndarray:
        """Scale image by given factor"""
        if factor == 1.0:
            factor = random.uniform(*self.config.scale_range)
        
        h, w = image.shape[:2]
        new_h, new_w = int(h * factor), int(w * factor)
        
        # Scale image
        scaled = cv2.resize(image, (new_w, new_h))
        
        # Crop or pad to original size
        if factor > 1.0:
            # Crop center
            start_y = (new_h - h) // 2
            start_x = (new_w - w) // 2
            result = scaled[start_y:start_y+h, start_x:start_x+w]
        else:
            # Pad with reflection
            pad_y = (h - new_h) // 2
            pad_x = (w - new_w) // 2
            result = cv2.copyMakeBorder(scaled, pad_y, h-new_h-pad_y, 
                                      pad_x, w-new_w-pad_x,
                                      cv2.BORDER_REFLECT_101)
        
        return result
    
    def shear(self, image: np.ndarray, shear_x: float = 0.0, 
              shear_y: float = 0.0) -> np.ndarray:
        """Apply shear transformation"""
        if shear_x == 0.0:
            shear_x = random.uniform(*self.config.shear_range)
        if shear_y == 0.0:
            shear_y = random.uniform(*self.config.shear_range)
        
        h, w = image.shape[:2]
        
        # Shear matrix
        M = np.array([[1, shear_x, 0],
                      [shear_y, 1, 0]], dtype=np.float32)
        
        # Apply shear
        sheared = cv2.warpAffine(image, M, (w, h),
                               borderMode=cv2.BORDER_REFLECT_101)
        
        return sheared
    
    def flip_horizontal(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """Flip image horizontally"""
        return cv2.flip(image, 1)
    
    def flip_vertical(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """Flip image vertically"""
        return cv2.flip(image, 0)
    
    def brightness(self, image: np.ndarray, factor: float = 1.0) -> np.ndarray:
        """Adjust image brightness"""
        if factor == 1.0:
            factor = random.uniform(*self.config.brightness_range)
        
        # Convert to float for calculation
        result = image.astype(np.float32) * factor
        
        if self.preserve_range:
            result = np.clip(result, 0, 255)
        
        return result.astype(image.dtype)
    
    def contrast(self, image: np.ndarray, factor: float = 1.0) -> np.ndarray:
        """Adjust image contrast"""
        if factor == 1.0:
            factor = random.uniform(*self.config.contrast_range)
        
        # Calculate mean
        mean = np.mean(image, axis=(0, 1), keepdims=True)
        
        # Adjust contrast
        result = (image.astype(np.float32) - mean) * factor + mean
        
        if self.preserve_range:
            result = np.clip(result, 0, 255)
        
        return result.astype(image.dtype)
    
    def saturation(self, image: np.ndarray, factor: float = 1.0) -> np.ndarray:
        """Adjust color saturation (color images only)"""
        if len(image.shape) != 3 or image.shape[2] != 3:
            return image
        
        if factor == 1.0:
            factor = random.uniform(*self.config.saturation_range)
        
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Adjust saturation
        hsv[:, :, 1] *= factor
        
        if self.preserve_range:
            hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        
        # Convert back
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result
    
    def hue_shift(self, image: np.ndarray, shift: int = 0) -> np.ndarray:
        """Shift image hue (color images only)"""
        if len(image.shape) != 3 or image.shape[2] != 3:
            return image
        
        if shift == 0:
            shift = random.randint(*self.config.hue_shift_range)
        
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.int16)
        
        # Shift hue
        hsv[:, :, 0] += shift
        hsv[:, :, 0] = hsv[:, :, 0] % 180  # Wrap around
        
        # Convert back
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result
    
    def gaussian_noise(self, image: np.ndarray, intensity: float = 0.0) -> np.ndarray:
        """Add Gaussian noise"""
        if intensity == 0.0:
            intensity = self.config.noise_intensity
        
        # Generate noise
        noise = np.random.normal(0, intensity * 255, image.shape)
        
        # Add noise
        result = image.astype(np.float32) + noise
        
        if self.preserve_range:
            result = np.clip(result, 0, 255)
        
        return result.astype(image.dtype)
    
    def salt_pepper_noise(self, image: np.ndarray, amount: float = 0.05) -> np.ndarray:
        """Add salt and pepper noise"""
        result = image.copy()
        
        # Generate random positions
        mask = np.random.random(image.shape[:2])
        
        # Salt (white)
        result[mask < amount/2] = 255
        
        # Pepper (black)
        result[mask > 1 - amount/2] = 0
        
        return result
    
    def gaussian_blur(self, image: np.ndarray, kernel_size: int = 0) -> np.ndarray:
        """Apply Gaussian blur"""
        if kernel_size == 0:
            kernel_size = random.randrange(*self.config.blur_kernel_range, 2)
        
        # Ensure odd kernel size
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    
    def motion_blur(self, image: np.ndarray, size: int = 15, 
                   angle: float = 0.0) -> np.ndarray:
        """Apply motion blur"""
        if angle == 0.0:
            angle = random.uniform(0, 360)
        
        # Create motion blur kernel
        kernel = np.zeros((size, size))
        kernel[size // 2, :] = 1.0
        
        # Rotate kernel
        M = cv2.getRotationMatrix2D((size // 2, size // 2), angle, 1)
        kernel = cv2.warpAffine(kernel, M, (size, size))
        kernel = kernel / np.sum(kernel)
        
        # Apply blur
        return cv2.filter2D(image, -1, kernel)
    
    def elastic_transform(self, image: np.ndarray, alpha: float = 50, 
                         sigma: float = 5) -> np.ndarray:
        """Apply elastic deformation"""
        h, w = image.shape[:2]
        
        # Random displacement fields
        dx = np.random.randn(h, w) * alpha
        dy = np.random.randn(h, w) * alpha
        
        # Smooth the displacement fields
        dx = cv2.GaussianBlur(dx, (0, 0), sigma)
        dy = cv2.GaussianBlur(dy, (0, 0), sigma)
        
        # Create mesh grid
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        
        # Apply displacement
        map_x = (x + dx).astype(np.float32)
        map_y = (y + dy).astype(np.float32)
        
        # Remap image
        result = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REFLECT_101)
        
        return result
    
    def cutout(self, image: np.ndarray, num_holes: int = 1, 
              max_size: int = 40) -> np.ndarray:
        """Apply cutout augmentation (random black squares)"""
        result = image.copy()
        h, w = image.shape[:2]
        
        for _ in range(num_holes):
            # Random size
            hole_size = random.randint(10, max_size)
            
            # Random position
            x = random.randint(0, w - hole_size)
            y = random.randint(0, h - hole_size)
            
            # Cut out region
            result[y:y+hole_size, x:x+hole_size] = 0
        
        return result
    
    def create_pipeline(self, operations: List[Tuple[str, Dict[str, Any]]]) -> List:
        """Create custom augmentation pipeline"""
        pipeline = []
        
        for op_name, params in operations:
            if op_name in self.augmentations:
                pipeline.append((self.augmentations[op_name], params))
            else:
                print(f"Warning: Unknown operation '{op_name}'")
        
        return pipeline
    
    def apply_pipeline(self, image: np.ndarray, pipeline: List) -> np.ndarray:
        """Apply augmentation pipeline to image"""
        result = image.copy()
        
        for aug_func, params in pipeline:
            result = aug_func(result, **params)
            self.augmentations_applied += 1
        
        self.images_processed += 1
        return result
    
    def _get_random_params(self, aug_name: str, strength: float) -> Dict[str, Any]:
        """Generate random parameters for augmentation"""
        params = {}
        
        # Scale parameters by strength
        if aug_name == "rotate":
            angle_range = self.config.rotation_range
            params["angle"] = random.uniform(
                angle_range[0] * strength, 
                angle_range[1] * strength
            )
        elif aug_name == "scale":
            # Interpolate between 1.0 and configured range
            scale_range = self.config.scale_range
            params["factor"] = 1.0 + (random.uniform(
                scale_range[0] - 1.0,
                scale_range[1] - 1.0
            ) * strength)
        elif aug_name in ["brightness", "contrast", "saturation"]:
            params["factor"] = 1.0 + (random.uniform(-0.3, 0.3) * strength)
        elif aug_name == "gaussian_noise":
            params["intensity"] = self.config.noise_intensity * strength
        
        return params
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get augmentation statistics"""
        return {
            "images_processed": self.images_processed,
            "augmentations_applied": self.augmentations_applied,
            "avg_augmentations_per_image": (
                self.augmentations_applied / self.images_processed
                if self.images_processed > 0 else 0
            )
        }


# Utility functions
def augment_batch(images: List[np.ndarray], strength: float = 0.5) -> List[np.ndarray]:
    """Augment a batch of images"""
    augmenter = ImageAugmenter()
    return [augmenter.random_augment(img, strength) for img in images]


def create_training_pipeline() -> List:
    """Create standard training augmentation pipeline"""
    augmenter = ImageAugmenter()
    return augmenter.create_pipeline([
        ("flip_horizontal", {}),
        ("rotate", {"angle": 0}),  # Random rotation
        ("brightness", {"factor": 0}),  # Random brightness
        ("gaussian_noise", {"intensity": 0.05})
    ])


# Auto-generated tests
def test_image_augmenter():
    """Test image augmentation functionality"""
    # Create test image
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    augmenter = ImageAugmenter(seed=42)
    
    # Test individual augmentations
    for aug_name in augmenter.augmentations:
        aug_func = augmenter.augmentations[aug_name]
        result = aug_func(test_image)
        assert result.shape == test_image.shape
        assert result.dtype == test_image.dtype
    
    # Test random augmentation
    augmented = augmenter.random_augment(test_image, strength=0.5)
    assert augmented.shape == test_image.shape
    
    # Test pipeline
    pipeline = augmenter.create_pipeline([
        ("rotate", {"angle": 15}),
        ("brightness", {"factor": 1.2})
    ])
    result = augmenter.apply_pipeline(test_image, pipeline)
    assert result.shape == test_image.shape
    
    # Test statistics
    stats = augmenter.get_statistics()
    assert stats["images_processed"] > 0
    assert stats["augmentations_applied"] > 0
    
    print("All image augmentation tests passed!")


if __name__ == "__main__":
    test_image_augmenter()