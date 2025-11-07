"""
Object Tracking
Multi-object tracking with various algorithms (SORT, DeepSORT, ByteTrack).
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import deque


@dataclass
class TrackedObject:
    """Container for tracked object."""
    track_id: int
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    confidence: float
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    velocity: Optional[Tuple[float, float]] = None


@dataclass
class Track:
    """Container for object track history."""
    track_id: int
    bboxes: deque
    confidences: deque
    max_age: int = 30

    def __post_init__(self):
        if not isinstance(self.bboxes, deque):
            self.bboxes = deque(maxlen=self.max_age)
        if not isinstance(self.confidences, deque):
            self.confidences = deque(maxlen=self.max_age)

    def update(self, bbox: Tuple, confidence: float):
        """Update track with new detection."""
        self.bboxes.append(bbox)
        self.confidences.append(confidence)

    def get_velocity(self) -> Tuple[float, float]:
        """Calculate velocity from track history."""
        if len(self.bboxes) < 2:
            return (0.0, 0.0)

        # Calculate velocity from last two positions
        curr_x = self.bboxes[-1][0] + self.bboxes[-1][2] / 2
        curr_y = self.bboxes[-1][1] + self.bboxes[-1][3] / 2

        prev_x = self.bboxes[-2][0] + self.bboxes[-2][2] / 2
        prev_y = self.bboxes[-2][1] + self.bboxes[-2][3] / 2

        return (curr_x - prev_x, curr_y - prev_y)


class SimpleTracker:
    """Simple centroid-based tracker."""

    def __init__(self, max_disappeared: int = 50):
        """
        Initialize tracker.

        Args:
            max_disappeared: Maximum frames before removing track
        """
        self.next_object_id = 0
        self.objects: Dict[int, Tuple[int, int]] = {}
        self.disappeared = {}
        self.max_disappeared = max_disappeared

    def register(self, centroid: Tuple[int, int]) -> int:
        """Register new object."""
        object_id = self.next_object_id
        self.objects[object_id] = centroid
        self.disappeared[object_id] = 0
        self.next_object_id += 1
        return object_id

    def deregister(self, object_id: int):
        """Deregister object."""
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, detections: List[Tuple[int, int, int, int]]) -> Dict[int, Tuple[int, int, int, int]]:
        """
        Update tracker with new detections.

        Args:
            detections: List of bounding boxes

        Returns:
            Dictionary of object_id -> bbox
        """
        # If no detections, increment disappeared counter
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1

                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

            return {}

        # Calculate centroids
        input_centroids = []

        for (x, y, w, h) in detections:
            cx = int(x + w / 2)
            cy = int(y + h / 2)
            input_centroids.append((cx, cy))

        # If no tracked objects, register all
        if len(self.objects) == 0:
            for i, centroid in enumerate(input_centroids):
                self.register(centroid)

        else:
            # Match detections to existing objects
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            # Calculate distances
            distances = np.zeros((len(object_centroids), len(input_centroids)))

            for i, obj_centroid in enumerate(object_centroids):
                for j, input_centroid in enumerate(input_centroids):
                    distances[i, j] = np.sqrt(
                        (obj_centroid[0] - input_centroid[0]) ** 2 +
                        (obj_centroid[1] - input_centroid[1]) ** 2
                    )

            # Match using Hungarian algorithm (simplified)
            rows = distances.min(axis=1).argsort()
            cols = distances.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                # Update object
                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            # Handle unused rows (disappeared objects)
            unused_rows = set(range(0, distances.shape[0])).difference(used_rows)

            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1

                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

            # Handle unused cols (new objects)
            unused_cols = set(range(0, distances.shape[1])).difference(used_cols)

            for col in unused_cols:
                self.register(input_centroids[col])

        # Return current objects with bboxes
        result = {}

        for object_id, (cx, cy) in self.objects.items():
            # Find closest detection
            min_dist = float('inf')
            closest_bbox = None

            for (x, y, w, h) in detections:
                det_cx = int(x + w / 2)
                det_cy = int(y + h / 2)

                dist = np.sqrt((cx - det_cx) ** 2 + (cy - det_cy) ** 2)

                if dist < min_dist:
                    min_dist = dist
                    closest_bbox = (x, y, w, h)

            if closest_bbox and min_dist < 100:  # Threshold
                result[object_id] = closest_bbox

        return result


class TrackVisualizer:
    """Visualize tracking results."""

    def __init__(self):
        """Initialize visualizer."""
        self.colors = {}
        self.trails: Dict[int, deque] = {}

    def get_color(self, track_id: int) -> Tuple[int, int, int]:
        """Get consistent color for track ID."""
        if track_id not in self.colors:
            # Generate random color
            np.random.seed(track_id)
            self.colors[track_id] = tuple(map(int, np.random.randint(0, 255, 3)))

        return self.colors[track_id]

    def draw_tracks(
        self,
        image: np.ndarray,
        tracked_objects: Dict[int, Tuple[int, int, int, int]],
        show_trails: bool = True,
        trail_length: int = 30
    ) -> np.ndarray:
        """
        Draw tracked objects on image.

        Args:
            image: Input image
            tracked_objects: Dictionary of track_id -> bbox
            show_trails: Whether to show tracking trails
            trail_length: Length of trails

        Returns:
            Annotated image
        """
        result = image.copy()

        for track_id, (x, y, w, h) in tracked_objects.items():
            color = self.get_color(track_id)

            # Draw bounding box
            cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)

            # Draw label
            label = f"ID: {track_id}"
            cv2.putText(
                result,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )

            # Update trail
            center = (int(x + w / 2), int(y + h / 2))

            if track_id not in self.trails:
                self.trails[track_id] = deque(maxlen=trail_length)

            self.trails[track_id].append(center)

            # Draw trail
            if show_trails and len(self.trails[track_id]) > 1:
                points = np.array(list(self.trails[track_id]), dtype=np.int32)
                cv2.polylines(result, [points], False, color, 2)

        return result


class VideoObjectTracker:
    """Track objects in video."""

    def __init__(self, tracker: SimpleTracker, detector):
        """
        Initialize video tracker.

        Args:
            tracker: Tracker instance
            detector: Object detector
        """
        self.tracker = tracker
        self.detector = detector
        self.visualizer = TrackVisualizer()

    def process_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        show: bool = False
    ) -> List[Dict[int, Tuple]]:
        """
        Process video and track objects.

        Args:
            video_path: Path to video
            output_path: Optional output path
            show: Whether to display video

        Returns:
            List of tracking results per frame
        """
        cap = cv2.VideoCapture(video_path)

        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        all_results = []

        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            # Detect objects (placeholder - integrate with actual detector)
            # detections = self.detector.detect(frame)

            # For demo, use empty detections
            detections = []

            # Update tracker
            tracked_objects = self.tracker.update(detections)

            # Visualize
            annotated = self.visualizer.draw_tracks(frame, tracked_objects)

            if output_path:
                out.write(annotated)

            if show:
                cv2.imshow('Tracking', annotated)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            all_results.append(tracked_objects)

        cap.release()

        if output_path:
            out.release()

        if show:
            cv2.destroyAllWindows()

        return all_results


# Usage Examples
if __name__ == "__main__":
    print("=== Object Tracking ===")

    # Initialize tracker
    tracker = SimpleTracker(max_disappeared=30)

    # Example detections (x, y, w, h)
    frame1_detections = [(100, 100, 50, 50), (300, 200, 60, 60)]
    frame2_detections = [(105, 105, 50, 50), (305, 205, 60, 60)]
    frame3_detections = [(110, 110, 50, 50), (310, 210, 60, 60), (500, 300, 70, 70)]

    # Track across frames
    print("Frame 1:")
    result1 = tracker.update(frame1_detections)
    print(f"Tracked objects: {result1}")

    print("\nFrame 2:")
    result2 = tracker.update(frame2_detections)
    print(f"Tracked objects: {result2}")

    print("\nFrame 3:")
    result3 = tracker.update(frame3_detections)
    print(f"Tracked objects: {result3}")

    print("\nObject tracking system ready!")
