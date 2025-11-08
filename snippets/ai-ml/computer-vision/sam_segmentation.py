"""
SAM (Segment Anything Model) Segmentation
Automatic and prompt-based image segmentation using Meta's SAM.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    import numpy as np

try:
    from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
    import torch
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False
    # Create placeholder if torch not available
    try:
        import torch
    except ImportError:
        pass


@dataclass
class Mask:
    """Container for segmentation mask."""
    segmentation: np.ndarray
    area: int
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    predicted_iou: float
    stability_score: float
    crop_box: Optional[Tuple[int, int, int, int]] = None


@dataclass
class SegmentationResult:
    """Container for segmentation results."""
    masks: List[Mask]
    image_shape: Tuple[int, int]
    num_masks: int


class SAMSegmenter:
    """Production-ready SAM segmentation."""

    def __init__(
        self,
        model_type: str = "vit_h",
        checkpoint_path: str = "sam_vit_h_4b8939.pth",
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """
        Initialize SAM segmenter.

        Args:
            model_type: SAM model type ('vit_h', 'vit_l', 'vit_b')
            checkpoint_path: Path to SAM checkpoint
            device: Device to run on
        """
        if not CV2_AVAILABLE:
            raise ImportError("opencv-python not installed. Install with: pip install opencv-python")
        if not SAM_AVAILABLE:
            raise ImportError("segment-anything not installed. Install with: pip install segment-anything")

        self.device = device
        self.model = sam_model_registry[model_type](checkpoint=checkpoint_path)
        self.model.to(device=self.device)

        # Initialize automatic mask generator
        self.mask_generator = SamAutomaticMaskGenerator(self.model)

        # Initialize predictor for prompt-based segmentation
        self.predictor = SamPredictor(self.model)

    def segment_automatic(
        self,
        image_path: str,
        min_mask_region_area: int = 0,
        points_per_side: int = 32
    ) -> SegmentationResult:
        """
        Automatic segmentation of entire image.

        Args:
            image_path: Path to image
            min_mask_region_area: Minimum mask area
            points_per_side: Number of points per side for grid

        Returns:
            SegmentationResult
        """
        # Read image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Generate masks
        masks = self.mask_generator.generate(image_rgb)

        # Convert to Mask objects
        mask_objects = []

        for mask_dict in masks:
            if mask_dict['area'] < min_mask_region_area:
                continue

            mask_obj = Mask(
                segmentation=mask_dict['segmentation'],
                area=int(mask_dict['area']),
                bbox=tuple(map(int, mask_dict['bbox'])),
                predicted_iou=float(mask_dict['predicted_iou']),
                stability_score=float(mask_dict['stability_score']),
                crop_box=tuple(map(int, mask_dict.get('crop_box', [0, 0, 0, 0])))
            )
            mask_objects.append(mask_obj)

        return SegmentationResult(
            masks=mask_objects,
            image_shape=image_rgb.shape[:2],
            num_masks=len(mask_objects)
        )

    def segment_with_points(
        self,
        image_path: str,
        point_coords: List[Tuple[int, int]],
        point_labels: List[int]  # 1 for foreground, 0 for background
    ) -> SegmentationResult:
        """
        Segment using point prompts.

        Args:
            image_path: Path to image
            point_coords: List of (x, y) coordinates
            point_labels: List of labels (1=foreground, 0=background)

        Returns:
            SegmentationResult
        """
        # Read image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Set image
        self.predictor.set_image(image_rgb)

        # Convert to numpy arrays
        point_coords = np.array(point_coords)
        point_labels = np.array(point_labels)

        # Predict
        masks, scores, logits = self.predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels,
            multimask_output=True
        )

        # Convert to Mask objects
        mask_objects = []

        for mask, score in zip(masks, scores):
            # Calculate bbox
            y_indices, x_indices = np.where(mask)

            if len(x_indices) > 0:
                x_min, x_max = x_indices.min(), x_indices.max()
                y_min, y_max = y_indices.min(), y_indices.max()
                bbox = (int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min))
            else:
                bbox = (0, 0, 0, 0)

            mask_obj = Mask(
                segmentation=mask,
                area=int(mask.sum()),
                bbox=bbox,
                predicted_iou=float(score),
                stability_score=float(score)
            )
            mask_objects.append(mask_obj)

        return SegmentationResult(
            masks=mask_objects,
            image_shape=image_rgb.shape[:2],
            num_masks=len(mask_objects)
        )

    def segment_with_box(
        self,
        image_path: str,
        box: Tuple[int, int, int, int]  # x1, y1, x2, y2
    ) -> SegmentationResult:
        """
        Segment using box prompt.

        Args:
            image_path: Path to image
            box: Bounding box (x1, y1, x2, y2)

        Returns:
            SegmentationResult
        """
        # Read image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Set image
        self.predictor.set_image(image_rgb)

        # Convert box to numpy array
        box_array = np.array(box)

        # Predict
        masks, scores, logits = self.predictor.predict(
            box=box_array,
            multimask_output=False
        )

        # Convert to Mask objects
        mask_objects = []

        for mask, score in zip(masks, scores):
            mask_obj = Mask(
                segmentation=mask,
                area=int(mask.sum()),
                bbox=box,
                predicted_iou=float(score),
                stability_score=float(score)
            )
            mask_objects.append(mask_obj)

        return SegmentationResult(
            masks=mask_objects,
            image_shape=image_rgb.shape[:2],
            num_masks=len(mask_objects)
        )

    def visualize(
        self,
        image_path: str,
        result: SegmentationResult,
        output_path: Optional[str] = None,
        show_boxes: bool = True
    ) -> np.ndarray:
        """
        Visualize segmentation results.

        Args:
            image_path: Path to original image
            result: SegmentationResult to visualize
            output_path: Optional output path
            show_boxes: Whether to show bounding boxes

        Returns:
            Annotated image
        """
        image = cv2.imread(image_path)

        # Create overlay
        overlay = image.copy()

        for i, mask in enumerate(result.masks):
            # Generate random color
            color = np.random.randint(0, 255, 3).tolist()

            # Apply mask
            overlay[mask.segmentation] = color

            # Draw bbox
            if show_boxes:
                x, y, w, h = mask.bbox
                cv2.rectangle(overlay, (x, y), (x + w, y + h), color, 2)

        # Blend with original
        alpha = 0.5
        annotated = cv2.addWeighted(image, 1 - alpha, overlay, alpha, 0)

        if output_path:
            cv2.imwrite(output_path, annotated)

        return annotated

    def get_largest_mask(self, result: SegmentationResult) -> Optional[Mask]:
        """Get mask with largest area."""
        if not result.masks:
            return None

        return max(result.masks, key=lambda m: m.area)

    def filter_by_area(
        self,
        result: SegmentationResult,
        min_area: int,
        max_area: Optional[int] = None
    ) -> SegmentationResult:
        """
        Filter masks by area.

        Args:
            result: SegmentationResult to filter
            min_area: Minimum area
            max_area: Optional maximum area

        Returns:
            Filtered SegmentationResult
        """
        filtered_masks = []

        for mask in result.masks:
            if mask.area >= min_area:
                if max_area is None or mask.area <= max_area:
                    filtered_masks.append(mask)

        return SegmentationResult(
            masks=filtered_masks,
            image_shape=result.image_shape,
            num_masks=len(filtered_masks)
        )

    def extract_foreground(
        self,
        image_path: str,
        mask: Mask,
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Extract foreground using mask.

        Args:
            image_path: Path to image
            mask: Mask to use
            output_path: Optional output path

        Returns:
            Foreground image
        """
        image = cv2.imread(image_path)

        # Create result with transparency
        result = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
        result[..., :3] = image
        result[..., 3] = mask.segmentation.astype(np.uint8) * 255

        if output_path:
            cv2.imwrite(output_path, result)

        return result


# Usage Examples
if __name__ == "__main__":
    if not CV2_AVAILABLE:
        print("Error: opencv-python not installed")
        print("Install with: pip install opencv-python")
        exit(1)

    if not SAM_AVAILABLE:
        print("Error: segment-anything not installed")
        print("Install with: pip install segment-anything")
        exit(1)

    print("SAM Segmentation Examples")
    print("Note: Download SAM checkpoint first:")
    print("wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth")

    # Example setup (requires checkpoint)
    # segmenter = SAMSegmenter(
    #     model_type="vit_h",
    #     checkpoint_path="sam_vit_h_4b8939.pth"
    # )

    # Example 1: Automatic segmentation
    # result = segmenter.segment_automatic("image.jpg")
    # print(f"Found {result.num_masks} masks")

    # Example 2: Point-based segmentation
    # result = segmenter.segment_with_points(
    #     "image.jpg",
    #     point_coords=[(100, 200), (300, 400)],
    #     point_labels=[1, 1]  # Both foreground
    # )

    # Example 3: Box-based segmentation
    # result = segmenter.segment_with_box(
    #     "image.jpg",
    #     box=(100, 100, 400, 400)
    # )

    # Example 4: Visualize
    # annotated = segmenter.visualize("image.jpg", result, "output.jpg")

    print("\nSAM segmentation ready for use!")
