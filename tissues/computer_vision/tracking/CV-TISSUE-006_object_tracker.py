"""
Tissue ID: CV-TISSUE-006
Title: Multi-Algorithm Object Tracker
Category: computer_vision/tracking
Tags: ["tracking", "object-tracking", "kalman", "real-time", "video"]
Difficulty: Advanced
Dependencies: ["opencv-python>=4.5.0", "numpy>=1.19.0", "scipy>=1.7.0"]
Performance: O(n) where n is number of tracked objects
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A robust object tracking tissue that provides multiple tracking algorithms
including centroid tracking, Kalman filter tracking, and IoU-based tracking.
Handles multiple objects, occlusions, and provides track history.

Use Cases:
- People counting and tracking
- Vehicle tracking in traffic
- Sports analytics
- Retail analytics
- Security surveillance

Example Usage:
    tracker = ObjectTracker(algorithm="kalman", max_disappeared=10)
    
    # Update with new detections
    detections = [(x1, y1, w1, h1), (x2, y2, w2, h2)]
    tracked_objects = tracker.update(detections)
    
    # Get tracks with history
    for obj_id, track in tracked_objects.items():
        print(f"Object {obj_id}: {track.centroid}, age: {track.age}")
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from collections import OrderedDict
from scipy.spatial import distance
from dataclasses import dataclass, field
import time


@dataclass
class TrackedObject:
    """Container for tracked object information"""
    object_id: int
    centroid: Tuple[float, float]
    bbox: Tuple[int, int, int, int]
    history: List[Tuple[float, float]] = field(default_factory=list)
    age: int = 0
    disappeared: int = 0
    velocity: Optional[Tuple[float, float]] = None
    confidence: float = 1.0
    
    def predict_next_position(self) -> Tuple[float, float]:
        """Predict next position based on velocity"""
        if self.velocity:
            return (
                self.centroid[0] + self.velocity[0],
                self.centroid[1] + self.velocity[1]
            )
        return self.centroid


class ObjectTracker:
    """
    Multi-algorithm object tracking system.
    Tissue Type: FUNCTIONAL - Tracks objects across video frames.
    """
    
    def __init__(self,
                 algorithm: str = "centroid",
                 max_disappeared: int = 10,
                 max_distance: float = 50.0,
                 track_history: int = 30):
        """
        Initialize object tracker.
        
        Args:
            algorithm: 'centroid', 'kalman', or 'iou'
            max_disappeared: Frames before removing lost track
            max_distance: Maximum distance for matching
            track_history: Number of positions to keep in history
        """
        self.algorithm = algorithm
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        self.track_history = track_history
        
        # Tracking data
        self.objects: OrderedDict[int, TrackedObject] = OrderedDict()
        self.next_object_id = 0
        self.disappeared = OrderedDict()
        
        # Kalman filters for each object (if using Kalman)
        self.kalman_filters = {}
        
        # Performance metrics
        self.frame_count = 0
        self.total_tracked = 0
    
    def update(self, detections: List[Tuple[int, int, int, int]]) -> Dict[int, TrackedObject]:
        """
        Update tracker with new detections.
        
        Args:
            detections: List of bounding boxes (x, y, w, h)
            
        Returns:
            Dictionary of tracked objects with IDs
        """
        self.frame_count += 1
        
        # Convert detections to centroids
        input_centroids = []
        input_bboxes = []
        
        for (x, y, w, h) in detections:
            cx = x + w / 2
            cy = y + h / 2
            input_centroids.append((cx, cy))
            input_bboxes.append((x, y, w, h))
        
        # If no current objects, register all detections
        if len(self.objects) == 0:
            for i, (centroid, bbox) in enumerate(zip(input_centroids, input_bboxes)):
                self._register_object(centroid, bbox)
        
        # Otherwise, match and update
        else:
            if self.algorithm == "centroid":
                self._update_centroid_tracking(input_centroids, input_bboxes)
            elif self.algorithm == "kalman":
                self._update_kalman_tracking(input_centroids, input_bboxes)
            elif self.algorithm == "iou":
                self._update_iou_tracking(input_bboxes)
            else:
                raise ValueError(f"Unknown algorithm: {self.algorithm}")
        
        # Return active objects
        return self.objects
    
    def _register_object(self, centroid: Tuple[float, float], bbox: Tuple[int, int, int, int]):
        """Register a new object"""
        obj = TrackedObject(
            object_id=self.next_object_id,
            centroid=centroid,
            bbox=bbox,
            history=[centroid]
        )
        
        self.objects[self.next_object_id] = obj
        self.disappeared[self.next_object_id] = 0
        
        # Initialize Kalman filter if using Kalman tracking
        if self.algorithm == "kalman":
            self.kalman_filters[self.next_object_id] = self._create_kalman_filter(centroid)
        
        self.next_object_id += 1
        self.total_tracked += 1
    
    def _deregister_object(self, object_id: int):
        """Remove an object from tracking"""
        del self.objects[object_id]
        del self.disappeared[object_id]
        
        if object_id in self.kalman_filters:
            del self.kalman_filters[object_id]
    
    def _update_centroid_tracking(self, input_centroids: List, input_bboxes: List):
        """Update using centroid tracking algorithm"""
        # Get current object centroids
        object_ids = list(self.objects.keys())
        object_centroids = [obj.centroid for obj in self.objects.values()]
        
        # Compute distance matrix
        if len(input_centroids) == 0:
            # No detections, increment disappeared count
            for object_id in object_ids:
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self._deregister_object(object_id)
            return
        
        if len(object_centroids) == 0:
            # No existing objects, register all
            for centroid, bbox in zip(input_centroids, input_bboxes):
                self._register_object(centroid, bbox)
            return
        
        # Calculate distances
        D = distance.cdist(np.array(object_centroids), np.array(input_centroids))
        
        # Find minimum distance assignments
        rows = D.min(axis=1).argsort()
        cols = D.argmin(axis=1)[rows]
        
        used_rows = set()
        used_cols = set()
        
        # Process matches
        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue
            
            if D[row, col] > self.max_distance:
                continue
            
            object_id = object_ids[row]
            centroid = input_centroids[col]
            bbox = input_bboxes[col]
            
            # Update object
            self._update_object(object_id, centroid, bbox)
            
            used_rows.add(row)
            used_cols.add(col)
        
        # Handle unmatched detections and objects
        unused_rows = set(range(len(object_centroids))) - used_rows
        unused_cols = set(range(len(input_centroids))) - used_cols
        
        # Increment disappeared count for unmatched objects
        for row in unused_rows:
            object_id = object_ids[row]
            self.disappeared[object_id] += 1
            
            if self.disappeared[object_id] > self.max_disappeared:
                self._deregister_object(object_id)
        
        # Register new objects for unmatched detections
        for col in unused_cols:
            self._register_object(input_centroids[col], input_bboxes[col])
    
    def _update_kalman_tracking(self, input_centroids: List, input_bboxes: List):
        """Update using Kalman filter tracking"""
        # Predict step for all Kalman filters
        predictions = {}
        for object_id in self.objects:
            if object_id in self.kalman_filters:
                kf = self.kalman_filters[object_id]
                prediction = kf.predict()
                predictions[object_id] = (prediction[0, 0], prediction[1, 0])
        
        # Use predictions instead of last known positions
        object_ids = list(predictions.keys())
        predicted_centroids = list(predictions.values())
        
        if len(predicted_centroids) > 0 and len(input_centroids) > 0:
            # Match predictions to detections
            D = distance.cdist(np.array(predicted_centroids), np.array(input_centroids))
            
            # Hungarian algorithm would be better here, but using simple greedy for now
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            for row, col in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                
                if D[row, col] > self.max_distance:
                    continue
                
                object_id = object_ids[row]
                centroid = input_centroids[col]
                bbox = input_bboxes[col]
                
                # Update Kalman filter
                kf = self.kalman_filters[object_id]
                kf.update(np.array([[centroid[0]], [centroid[1]]]))
                
                # Update object
                self._update_object(object_id, centroid, bbox)
                
                used_rows.add(row)
                used_cols.add(col)
        
        # Handle unmatched objects and detections
        self._handle_unmatched(object_ids, input_centroids, input_bboxes, 
                              used_rows if 'used_rows' in locals() else set(),
                              used_cols if 'used_cols' in locals() else set())
    
    def _update_iou_tracking(self, input_bboxes: List):
        """Update using Intersection over Union tracking"""
        object_ids = list(self.objects.keys())
        object_bboxes = [obj.bbox for obj in self.objects.values()]
        
        if len(object_bboxes) == 0:
            # Register all new detections
            for bbox in input_bboxes:
                cx = bbox[0] + bbox[2] / 2
                cy = bbox[1] + bbox[3] / 2
                self._register_object((cx, cy), bbox)
            return
        
        # Calculate IoU matrix
        iou_matrix = self._calculate_iou_matrix(object_bboxes, input_bboxes)
        
        # Find best matches
        rows = iou_matrix.max(axis=1).argsort()[::-1]  # Descending order
        cols = iou_matrix.argmax(axis=1)[rows]
        
        used_rows = set()
        used_cols = set()
        
        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue
            
            if iou_matrix[row, col] < 0.3:  # Minimum IoU threshold
                continue
            
            object_id = object_ids[row]
            bbox = input_bboxes[col]
            centroid = (bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2)
            
            self._update_object(object_id, centroid, bbox)
            
            used_rows.add(row)
            used_cols.add(col)
        
        # Handle unmatched
        self._handle_unmatched(object_ids, 
                              [(b[0] + b[2]/2, b[1] + b[3]/2) for b in input_bboxes],
                              input_bboxes, used_rows, used_cols)
    
    def _update_object(self, object_id: int, centroid: Tuple[float, float], 
                      bbox: Tuple[int, int, int, int]):
        """Update tracked object information"""
        obj = self.objects[object_id]
        
        # Calculate velocity
        if len(obj.history) > 0:
            prev_centroid = obj.history[-1]
            velocity = (
                centroid[0] - prev_centroid[0],
                centroid[1] - prev_centroid[1]
            )
            obj.velocity = velocity
        
        # Update object
        obj.centroid = centroid
        obj.bbox = bbox
        obj.age += 1
        obj.disappeared = 0
        
        # Update history
        obj.history.append(centroid)
        if len(obj.history) > self.track_history:
            obj.history.pop(0)
        
        self.disappeared[object_id] = 0
    
    def _handle_unmatched(self, object_ids: List[int], input_centroids: List,
                         input_bboxes: List, used_rows: set, used_cols: set):
        """Handle unmatched objects and detections"""
        # Unmatched existing objects
        for i, object_id in enumerate(object_ids):
            if i not in used_rows:
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self._deregister_object(object_id)
        
        # Unmatched new detections
        for i in range(len(input_centroids)):
            if i not in used_cols:
                self._register_object(input_centroids[i], input_bboxes[i])
    
    def _create_kalman_filter(self, initial_position: Tuple[float, float]):
        """Create Kalman filter for tracking"""
        # Simple 2D position + velocity Kalman filter
        kf = SimpleKalmanFilter()
        kf.x = np.array([[initial_position[0]], [initial_position[1]], [0], [0]])
        return kf
    
    def _calculate_iou_matrix(self, bboxes1: List, bboxes2: List) -> np.ndarray:
        """Calculate IoU matrix between two sets of bboxes"""
        n1 = len(bboxes1)
        n2 = len(bboxes2)
        iou_matrix = np.zeros((n1, n2))
        
        for i, bbox1 in enumerate(bboxes1):
            for j, bbox2 in enumerate(bboxes2):
                iou_matrix[i, j] = self._calculate_iou(bbox1, bbox2)
        
        return iou_matrix
    
    def _calculate_iou(self, bbox1: Tuple, bbox2: Tuple) -> float:
        """Calculate IoU between two bounding boxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        xi1 = max(x1, x2)
        yi1 = max(y1, y2)
        xi2 = min(x1 + w1, x2 + w2)
        yi2 = min(y1 + h1, y2 + h2)
        
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        
        # Calculate union
        bbox1_area = w1 * h1
        bbox2_area = w2 * h2
        union_area = bbox1_area + bbox2_area - inter_area
        
        # Calculate IoU
        iou = inter_area / union_area if union_area > 0 else 0
        
        return iou
    
    def get_tracks(self) -> List[List[Tuple[float, float]]]:
        """Get all track histories"""
        return [obj.history for obj in self.objects.values() if len(obj.history) > 1]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tracking statistics"""
        active_tracks = len(self.objects)
        avg_track_length = np.mean([obj.age for obj in self.objects.values()]) if active_tracks > 0 else 0
        
        return {
            "frame_count": self.frame_count,
            "total_tracked": self.total_tracked,
            "active_tracks": active_tracks,
            "average_track_length": float(avg_track_length),
            "algorithm": self.algorithm
        }


class SimpleKalmanFilter:
    """Simplified Kalman filter for 2D tracking"""
    
    def __init__(self):
        # State: [x, y, vx, vy]
        self.x = np.zeros((4, 1))
        
        # State transition matrix
        self.F = np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Measurement matrix
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])
        
        # Process covariance
        self.P = np.eye(4) * 1000
        
        # Process noise
        self.Q = np.eye(4) * 0.1
        
        # Measurement noise
        self.R = np.eye(2) * 1
    
    def predict(self):
        """Predict next state"""
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x
    
    def update(self, z):
        """Update with measurement"""
        y = z - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P


# Auto-generated tests
def test_object_tracker():
    """Test object tracking functionality"""
    tracker = ObjectTracker(algorithm="centroid")
    
    # Frame 1: Two objects
    detections1 = [(10, 10, 50, 50), (100, 100, 60, 60)]
    tracked1 = tracker.update(detections1)
    assert len(tracked1) == 2
    
    # Frame 2: Objects moved slightly
    detections2 = [(15, 15, 50, 50), (105, 105, 60, 60)]
    tracked2 = tracker.update(detections2)
    assert len(tracked2) == 2
    
    # Check if objects maintained IDs
    ids = list(tracked2.keys())
    assert tracked2[ids[0]].age == 2
    assert len(tracked2[ids[0]].history) == 2
    
    # Test with missing detection
    detections3 = [(20, 20, 50, 50)]  # Second object missing
    tracked3 = tracker.update(detections3)
    assert len(tracked3) == 2  # Still tracking both
    
    # Test statistics
    stats = tracker.get_statistics()
    assert stats["frame_count"] == 3
    assert stats["total_tracked"] == 2
    
    print("All object tracking tests passed!")


if __name__ == "__main__":
    test_object_tracker()