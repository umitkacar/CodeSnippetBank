"""
Face Detection and Recognition
Face detection, recognition, and analysis using multiple methods.
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False


@dataclass
class Face:
    """Container for detected face."""
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    landmarks: Optional[Dict[str, Tuple[int, int]]] = None
    encoding: Optional[np.ndarray] = None
    confidence: float = 1.0


@dataclass
class FaceRecognitionResult:
    """Container for face recognition result."""
    face: Face
    identity: Optional[str] = None
    distance: float = 0.0
    match: bool = False


@dataclass
class FaceAttributes:
    """Container for face attributes."""
    age: Optional[int] = None
    gender: Optional[str] = None
    emotion: Optional[str] = None
    race: Optional[str] = None


class HaarCascadeFaceDetector:
    """Face detection using Haar Cascades (fast, basic)."""

    def __init__(self):
        """Initialize Haar cascade detector."""
        # Load pre-trained cascade
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def detect(self, image_path: str) -> List[Face]:
        """
        Detect faces in image.

        Args:
            image_path: Path to image

        Returns:
            List of Face objects
        """
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces_rects = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        faces = []

        for (x, y, w, h) in faces_rects:
            face = Face(bbox=(x, y, w, h))
            faces.append(face)

        return faces


class DLibFaceDetector:
    """Face detection and recognition using face_recognition library."""

    def __init__(self):
        """Initialize dlib-based detector."""
        if not FACE_RECOGNITION_AVAILABLE:
            raise ImportError("face_recognition not installed")

    def detect(
        self,
        image_path: str,
        model: str = "hog"  # 'hog' or 'cnn'
    ) -> List[Face]:
        """
        Detect faces in image.

        Args:
            image_path: Path to image
            model: Detection model ('hog' or 'cnn')

        Returns:
            List of Face objects
        """
        image = face_recognition.load_image_file(image_path)

        # Detect face locations
        face_locations = face_recognition.face_locations(image, model=model)

        # Get landmarks
        face_landmarks_list = face_recognition.face_landmarks(image)

        # Get encodings
        face_encodings = face_recognition.face_encodings(image, face_locations)

        faces = []

        for (top, right, bottom, left), landmarks, encoding in zip(
            face_locations, face_landmarks_list, face_encodings
        ):
            # Convert to x, y, w, h format
            bbox = (left, top, right - left, bottom - top)

            face = Face(
                bbox=bbox,
                landmarks=landmarks,
                encoding=encoding
            )

            faces.append(face)

        return faces

    def compare_faces(
        self,
        known_encoding: np.ndarray,
        unknown_encoding: np.ndarray,
        tolerance: float = 0.6
    ) -> Tuple[bool, float]:
        """
        Compare two face encodings.

        Args:
            known_encoding: Known face encoding
            unknown_encoding: Unknown face encoding
            tolerance: Match tolerance (lower is stricter)

        Returns:
            Tuple of (is_match, distance)
        """
        # Calculate face distance
        distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]

        is_match = distance <= tolerance

        return is_match, float(distance)


class FaceRecognitionSystem:
    """Complete face recognition system."""

    def __init__(self):
        """Initialize face recognition system."""
        if not FACE_RECOGNITION_AVAILABLE:
            raise ImportError("face_recognition not installed")

        self.detector = DLibFaceDetector()
        self.known_faces: Dict[str, np.ndarray] = {}

    def register_face(
        self,
        name: str,
        image_path: str
    ):
        """
        Register a face with identity.

        Args:
            name: Person's name
            image_path: Path to image
        """
        faces = self.detector.detect(image_path)

        if not faces:
            raise ValueError("No face detected in image")

        if len(faces) > 1:
            raise ValueError("Multiple faces detected, use image with single face")

        # Store encoding
        self.known_faces[name] = faces[0].encoding

    def recognize(
        self,
        image_path: str,
        tolerance: float = 0.6
    ) -> List[FaceRecognitionResult]:
        """
        Recognize faces in image.

        Args:
            image_path: Path to image
            tolerance: Match tolerance

        Returns:
            List of FaceRecognitionResult objects
        """
        # Detect faces
        faces = self.detector.detect(image_path)

        results = []

        for face in faces:
            best_match = None
            best_distance = float('inf')
            is_match = False

            # Compare with known faces
            for name, known_encoding in self.known_faces.items():
                match, distance = self.detector.compare_faces(
                    known_encoding,
                    face.encoding,
                    tolerance
                )

                if distance < best_distance:
                    best_distance = distance
                    best_match = name
                    is_match = match

            result = FaceRecognitionResult(
                face=face,
                identity=best_match if is_match else None,
                distance=best_distance,
                match=is_match
            )

            results.append(result)

        return results


class DeepFaceAnalyzer:
    """Face analysis using DeepFace."""

    def __init__(self):
        """Initialize DeepFace analyzer."""
        if not DEEPFACE_AVAILABLE:
            raise ImportError("deepface not installed")

    def analyze(
        self,
        image_path: str,
        actions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze face attributes.

        Args:
            image_path: Path to image
            actions: List of analyses ('age', 'gender', 'emotion', 'race')

        Returns:
            Analysis results
        """
        if actions is None:
            actions = ['age', 'gender', 'emotion', 'race']

        result = DeepFace.analyze(
            img_path=image_path,
            actions=actions,
            enforce_detection=False
        )

        return result

    def verify(
        self,
        img1_path: str,
        img2_path: str,
        model_name: str = "VGG-Face"
    ) -> Dict[str, Any]:
        """
        Verify if two images are of the same person.

        Args:
            img1_path: Path to first image
            img2_path: Path to second image
            model_name: Model to use

        Returns:
            Verification result
        """
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name=model_name
        )

        return result


class FaceVisualizer:
    """Visualize face detection and recognition results."""

    @staticmethod
    def draw_faces(
        image_path: str,
        faces: List[Face],
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Draw detected faces on image.

        Args:
            image_path: Path to image
            faces: List of Face objects
            output_path: Optional output path

        Returns:
            Annotated image
        """
        image = cv2.imread(image_path)

        for face in faces:
            x, y, w, h = face.bbox

            # Draw rectangle
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Draw landmarks if available
            if face.landmarks:
                for name, points in face.landmarks.items():
                    for point in points:
                        cv2.circle(image, point, 2, (0, 0, 255), -1)

        if output_path:
            cv2.imwrite(output_path, image)

        return image

    @staticmethod
    def draw_recognition_results(
        image_path: str,
        results: List[FaceRecognitionResult],
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """Draw recognition results on image."""
        image = cv2.imread(image_path)

        for result in results:
            x, y, w, h = result.face.bbox

            # Draw box
            color = (0, 255, 0) if result.match else (0, 0, 255)
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

            # Draw label
            label = result.identity if result.identity else "Unknown"
            label += f" ({result.distance:.2f})"

            cv2.putText(
                image,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )

        if output_path:
            cv2.imwrite(output_path, image)

        return image


# Usage Examples
if __name__ == "__main__":
    # Example 1: Haar Cascade Detection
    print("=== Haar Cascade Face Detection ===")

    haar_detector = HaarCascadeFaceDetector()

    # Create test image with face (using a simple circle as placeholder)
    test_img = np.ones((400, 400, 3), dtype=np.uint8) * 255
    cv2.circle(test_img, (200, 200), 100, (0, 0, 0), -1)
    cv2.imwrite("/tmp/test_face.jpg", test_img)

    faces = haar_detector.detect("/tmp/test_face.jpg")
    print(f"Detected {len(faces)} faces")

    # Example 2: Face Recognition System
    if FACE_RECOGNITION_AVAILABLE:
        print("\n=== Face Recognition System ===")

        fr_system = FaceRecognitionSystem()

        print("Face recognition system initialized")
        print("Use fr_system.register_face(name, image_path) to register faces")
        print("Use fr_system.recognize(image_path) to recognize faces")

    # Example 3: DeepFace Analysis
    if DEEPFACE_AVAILABLE:
        print("\n=== DeepFace Analysis ===")

        analyzer = DeepFaceAnalyzer()
        print("DeepFace analyzer initialized")
        print("Use analyzer.analyze(image_path) for age, gender, emotion, race")

    print("\nFace detection and recognition ready!")
