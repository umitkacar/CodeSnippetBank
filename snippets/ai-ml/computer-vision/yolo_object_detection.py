"""
YOLO Object Detection
YOLOv8/v9 for real-time object detection with production features.
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False


@dataclass
class Detection:
    """Container for detection results."""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    area: float


@dataclass
class DetectionResult:
    """Container for complete detection results."""
    image_path: str
    detections: List[Detection]
    inference_time: float
    image_shape: Tuple[int, int, int]


class YOLODetector:
    """Production-ready YOLO object detector."""

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        device: str = "cpu"
    ):
        """
        Initialize YOLO detector.

        Args:
            model_path: Path to YOLO model weights
            confidence_threshold: Minimum confidence for detections
            iou_threshold: IOU threshold for NMS
            device: Device to run on ('cpu', 'cuda', 'mps')
        """
        if not ULTRALYTICS_AVAILABLE:
            raise ImportError("ultralytics not installed. Install with: pip install ultralytics")

        self.model = YOLO(model_path)
        self.conf_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.device = device

        # Move model to device
        self.model.to(device)

    def detect(
        self,
        image_path: str,
        classes: Optional[List[int]] = None
    ) -> DetectionResult:
        """
        Detect objects in image.

        Args:
            image_path: Path to image file
            classes: Optional list of class IDs to detect

        Returns:
            DetectionResult object
        """
        # Run inference
        results = self.model(
            image_path,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            classes=classes,
            verbose=False
        )

        result = results[0]

        # Parse detections
        detections = []

        for box in result.boxes:
            detection = Detection(
                class_id=int(box.cls[0]),
                class_name=result.names[int(box.cls[0])],
                confidence=float(box.conf[0]),
                bbox=tuple(map(int, box.xyxy[0].tolist())),
                area=float(box.xyxy[0][2] - box.xyxy[0][0]) * float(box.xyxy[0][3] - box.xyxy[0][1])
            )
            detections.append(detection)

        return DetectionResult(
            image_path=image_path,
            detections=detections,
            inference_time=result.speed['inference'],
            image_shape=result.orig_shape
        )

    def detect_batch(
        self,
        image_paths: List[str],
        batch_size: int = 32
    ) -> List[DetectionResult]:
        """
        Detect objects in batch of images.

        Args:
            image_paths: List of image paths
            batch_size: Batch size for inference

        Returns:
            List of DetectionResult objects
        """
        results = []

        for i in range(0, len(image_paths), batch_size):
            batch = image_paths[i:i + batch_size]

            batch_results = self.model(
                batch,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                verbose=False
            )

            for img_path, result in zip(batch, batch_results):
                detections = []

                for box in result.boxes:
                    detection = Detection(
                        class_id=int(box.cls[0]),
                        class_name=result.names[int(box.cls[0])],
                        confidence=float(box.conf[0]),
                        bbox=tuple(map(int, box.xyxy[0].tolist())),
                        area=float(box.xyxy[0][2] - box.xyxy[0][0]) * float(box.xyxy[0][3] - box.xyxy[0][1])
                    )
                    detections.append(detection)

                results.append(DetectionResult(
                    image_path=img_path,
                    detections=detections,
                    inference_time=result.speed['inference'],
                    image_shape=result.orig_shape
                ))

        return results

    def detect_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        show: bool = False
    ) -> List[DetectionResult]:
        """
        Detect objects in video.

        Args:
            video_path: Path to video file
            output_path: Optional output video path
            show: Whether to display video

        Returns:
            List of DetectionResult per frame
        """
        cap = cv2.VideoCapture(video_path)

        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_results = []
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            # Run detection
            results = self.model(
                frame,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                verbose=False
            )

            result = results[0]

            # Parse detections
            detections = []

            for box in result.boxes:
                detection = Detection(
                    class_id=int(box.cls[0]),
                    class_name=result.names[int(box.cls[0])],
                    confidence=float(box.conf[0]),
                    bbox=tuple(map(int, box.xyxy[0].tolist())),
                    area=float(box.xyxy[0][2] - box.xyxy[0][0]) * float(box.xyxy[0][3] - box.xyxy[0][1])
                )
                detections.append(detection)

            frame_results.append(DetectionResult(
                image_path=f"frame_{frame_count}",
                detections=detections,
                inference_time=result.speed['inference'],
                image_shape=result.orig_shape
            ))

            # Draw detections
            annotated = result.plot()

            if output_path:
                out.write(annotated)

            if show:
                cv2.imshow('YOLO Detection', annotated)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            frame_count += 1

        cap.release()

        if output_path:
            out.release()

        if show:
            cv2.destroyAllWindows()

        return frame_results

    def visualize(
        self,
        image_path: str,
        result: DetectionResult,
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Visualize detections on image.

        Args:
            image_path: Path to original image
            result: DetectionResult to visualize
            output_path: Optional output path

        Returns:
            Annotated image
        """
        image = cv2.imread(image_path)

        for det in result.detections:
            x1, y1, x2, y2 = det.bbox

            # Draw box
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw label
            label = f"{det.class_name} {det.confidence:.2f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

            cv2.rectangle(image, (x1, y1 - 20), (x1 + w, y1), (0, 255, 0), -1)
            cv2.putText(
                image,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1
            )

        if output_path:
            cv2.imwrite(output_path, image)

        return image

    def filter_by_class(
        self,
        result: DetectionResult,
        class_names: List[str]
    ) -> DetectionResult:
        """
        Filter detections by class names.

        Args:
            result: DetectionResult to filter
            class_names: List of class names to keep

        Returns:
            Filtered DetectionResult
        """
        filtered_detections = [
            det for det in result.detections
            if det.class_name in class_names
        ]

        return DetectionResult(
            image_path=result.image_path,
            detections=filtered_detections,
            inference_time=result.inference_time,
            image_shape=result.image_shape
        )

    def get_statistics(self, result: DetectionResult) -> Dict[str, Any]:
        """
        Get statistics from detection result.

        Args:
            result: DetectionResult to analyze

        Returns:
            Dictionary of statistics
        """
        class_counts = {}

        for det in result.detections:
            class_counts[det.class_name] = class_counts.get(det.class_name, 0) + 1

        return {
            "total_detections": len(result.detections),
            "class_counts": class_counts,
            "average_confidence": np.mean([d.confidence for d in result.detections]) if result.detections else 0.0,
            "inference_time_ms": result.inference_time
        }


# Usage Examples
if __name__ == "__main__":
    if not ULTRALYTICS_AVAILABLE:
        print("Please install ultralytics: pip install ultralytics")
        exit(1)

    # Initialize detector
    detector = YOLODetector(
        model_path="yolov8n.pt",  # Download automatically if not present
        confidence_threshold=0.25,
        device="cpu"
    )

    # Example 1: Single image detection
    print("=== Single Image Detection ===")

    # Create a test image (or use your own)
    test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    cv2.imwrite("/tmp/test_image.jpg", test_image)

    result = detector.detect("/tmp/test_image.jpg")

    print(f"Image: {result.image_path}")
    print(f"Detections: {len(result.detections)}")
    print(f"Inference time: {result.inference_time:.2f}ms")

    for det in result.detections:
        print(f"  - {det.class_name}: {det.confidence:.2f} at {det.bbox}")

    # Example 2: Get statistics
    print("\n=== Statistics ===")

    stats = detector.get_statistics(result)
    print(f"Total detections: {stats['total_detections']}")
    print(f"Class counts: {stats['class_counts']}")
    print(f"Average confidence: {stats['average_confidence']:.2f}")

    # Example 3: Filter by class
    print("\n=== Filter by Class ===")

    filtered = detector.filter_by_class(result, ["person", "car"])
    print(f"Filtered detections: {len(filtered.detections)}")

    print("\nYOLO detector ready for production use!")
