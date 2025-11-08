"""
OCR with Tesseract and EasyOCR
Text extraction from images using multiple OCR engines.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    import numpy as np

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False


@dataclass
class TextDetection:
    """Container for detected text."""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, w, h or x1, y1, x2, y2
    language: Optional[str] = None


@dataclass
class OCRResult:
    """Container for OCR results."""
    detections: List[TextDetection]
    full_text: str
    image_path: str
    processing_time: float


class TesseractOCR:
    """Tesseract OCR wrapper."""

    def __init__(
        self,
        lang: str = "eng",
        psm: int = 3,  # Page segmentation mode
        oem: int = 3   # OCR Engine mode
    ):
        """
        Initialize Tesseract OCR.

        Args:
            lang: Language code(s) (e.g., 'eng', 'eng+fra')
            psm: Page segmentation mode (0-13)
            oem: OCR engine mode (0-3)
        """
        if not CV2_AVAILABLE:
            raise ImportError("opencv-python not installed. Install with: pip install opencv-python")
        if not TESSERACT_AVAILABLE:
            raise ImportError("pytesseract not installed. Install with: pip install pytesseract")

        self.lang = lang
        self.config = f"--psm {psm} --oem {oem}"

    def extract_text(
        self,
        image_path: str,
        preprocess: bool = True
    ) -> OCRResult:
        """
        Extract text from image.

        Args:
            image_path: Path to image
            preprocess: Whether to preprocess image

        Returns:
            OCRResult
        """
        import time

        start_time = time.time()

        # Read image
        image = cv2.imread(image_path)

        if preprocess:
            image = self._preprocess(image)

        # Extract text
        full_text = pytesseract.image_to_string(
            image,
            lang=self.lang,
            config=self.config
        )

        # Get detailed data
        data = pytesseract.image_to_data(
            image,
            lang=self.lang,
            config=self.config,
            output_type=pytesseract.Output.DICT
        )

        # Parse detections
        detections = []

        for i in range(len(data['text'])):
            text = data['text'][i].strip()

            if not text:
                continue

            confidence = float(data['conf'][i])

            if confidence < 0:
                continue

            bbox = (
                int(data['left'][i]),
                int(data['top'][i]),
                int(data['width'][i]),
                int(data['height'][i])
            )

            detection = TextDetection(
                text=text,
                confidence=confidence / 100.0,  # Convert to 0-1
                bbox=bbox,
                language=self.lang
            )

            detections.append(detection)

        processing_time = time.time() - start_time

        return OCRResult(
            detections=detections,
            full_text=full_text.strip(),
            image_path=image_path,
            processing_time=processing_time
        )

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)

        # Threshold
        _, thresh = cv2.threshold(
            denoised,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        return thresh


class EasyOCRWrapper:
    """EasyOCR wrapper."""

    def __init__(
        self,
        languages: List[str] = None,
        gpu: bool = False
    ):
        """
        Initialize EasyOCR.

        Args:
            languages: List of language codes
            gpu: Whether to use GPU
        """
        if not CV2_AVAILABLE:
            raise ImportError("opencv-python not installed. Install with: pip install opencv-python")
        if not EASYOCR_AVAILABLE:
            raise ImportError("easyocr not installed. Install with: pip install easyocr")

        if languages is None:
            languages = ['en']

        self.reader = easyocr.Reader(languages, gpu=gpu)

    def extract_text(
        self,
        image_path: str,
        detail: int = 1  # 0 = simple, 1 = detailed
    ) -> OCRResult:
        """
        Extract text from image.

        Args:
            image_path: Path to image
            detail: Detail level (0 or 1)

        Returns:
            OCRResult
        """
        import time

        start_time = time.time()

        # Read and process
        results = self.reader.readtext(image_path, detail=detail)

        detections = []
        full_text_parts = []

        for result in results:
            if detail == 1:
                bbox_points, text, confidence = result

                # Convert bbox points to x, y, w, h
                bbox_points = np.array(bbox_points)
                x_min = int(bbox_points[:, 0].min())
                y_min = int(bbox_points[:, 1].min())
                x_max = int(bbox_points[:, 0].max())
                y_max = int(bbox_points[:, 1].max())

                bbox = (x_min, y_min, x_max - x_min, y_max - y_min)

                detection = TextDetection(
                    text=text,
                    confidence=float(confidence),
                    bbox=bbox
                )

                detections.append(detection)
                full_text_parts.append(text)

        processing_time = time.time() - start_time

        return OCRResult(
            detections=detections,
            full_text=" ".join(full_text_parts),
            image_path=image_path,
            processing_time=processing_time
        )


class MultiEngineOCR:
    """Combine multiple OCR engines for better accuracy."""

    def __init__(self, use_tesseract: bool = True, use_easyocr: bool = True):
        """
        Initialize multi-engine OCR.

        Args:
            use_tesseract: Use Tesseract
            use_easyocr: Use EasyOCR
        """
        self.engines = []

        if use_tesseract and TESSERACT_AVAILABLE:
            self.engines.append(('tesseract', TesseractOCR()))

        if use_easyocr and EASYOCR_AVAILABLE:
            self.engines.append(('easyocr', EasyOCRWrapper()))

        if not self.engines:
            raise ValueError("No OCR engines available")

    def extract_text(
        self,
        image_path: str,
        consensus: bool = True
    ) -> OCRResult:
        """
        Extract text using multiple engines.

        Args:
            image_path: Path to image
            consensus: Use consensus from multiple engines

        Returns:
            Combined OCRResult
        """
        results = []

        for engine_name, engine in self.engines:
            try:
                result = engine.extract_text(image_path)
                results.append(result)
            except Exception as e:
                print(f"{engine_name} failed: {e}")

        if not results:
            raise ValueError("All OCR engines failed")

        if len(results) == 1:
            return results[0]

        # Combine results
        all_detections = []

        for result in results:
            all_detections.extend(result.detections)

        # Get consensus text (simple approach: use longest)
        full_text = max([r.full_text for r in results], key=len)

        avg_time = np.mean([r.processing_time for r in results])

        return OCRResult(
            detections=all_detections,
            full_text=full_text,
            image_path=image_path,
            processing_time=avg_time
        )


class OCRPostProcessor:
    """Post-process OCR results."""

    @staticmethod
    def filter_by_confidence(
        result: OCRResult,
        min_confidence: float = 0.5
    ) -> OCRResult:
        """Filter detections by confidence threshold."""
        filtered = [
            det for det in result.detections
            if det.confidence >= min_confidence
        ]

        return OCRResult(
            detections=filtered,
            full_text=" ".join([d.text for d in filtered]),
            image_path=result.image_path,
            processing_time=result.processing_time
        )

    @staticmethod
    def merge_lines(result: OCRResult) -> str:
        """Merge detections into lines."""
        if not result.detections:
            return ""

        # Sort by y-coordinate
        sorted_dets = sorted(result.detections, key=lambda d: d.bbox[1])

        lines = []
        current_line = []
        current_y = sorted_dets[0].bbox[1]

        for det in sorted_dets:
            y = det.bbox[1]

            # Check if same line (within threshold)
            if abs(y - current_y) < 20:
                current_line.append(det)
            else:
                # New line
                if current_line:
                    # Sort by x-coordinate
                    current_line.sort(key=lambda d: d.bbox[0])
                    line_text = " ".join([d.text for d in current_line])
                    lines.append(line_text)

                current_line = [det]
                current_y = y

        # Add last line
        if current_line:
            current_line.sort(key=lambda d: d.bbox[0])
            line_text = " ".join([d.text for d in current_line])
            lines.append(line_text)

        return "\n".join(lines)

    @staticmethod
    def visualize(
        image_path: str,
        result: OCRResult,
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """Visualize OCR results."""
        image = cv2.imread(image_path)

        for det in result.detections:
            x, y, w, h = det.bbox

            # Draw rectangle
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Draw text
            label = f"{det.text} ({det.confidence:.2f})"
            cv2.putText(
                image,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1
            )

        if output_path:
            cv2.imwrite(output_path, image)

        return image


# Usage Examples
if __name__ == "__main__":
    if not CV2_AVAILABLE:
        print("Error: opencv-python not installed")
        print("Install with: pip install opencv-python")
        exit(1)

    # Example 1: Tesseract OCR
    if TESSERACT_AVAILABLE:
        print("=== Tesseract OCR ===")

        tesseract = TesseractOCR(lang="eng")

        # Create test image with text
        test_img = np.ones((100, 400, 3), dtype=np.uint8) * 255
        cv2.putText(
            test_img,
            "Hello World!",
            (50, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 0),
            2
        )
        cv2.imwrite("/tmp/test_ocr.jpg", test_img)

        result = tesseract.extract_text("/tmp/test_ocr.jpg")

        print(f"Full text: {result.full_text}")
        print(f"Detections: {len(result.detections)}")
        print(f"Processing time: {result.processing_time:.2f}s")

    # Example 2: EasyOCR
    if EASYOCR_AVAILABLE:
        print("\n=== EasyOCR ===")

        easy_ocr = EasyOCRWrapper(languages=['en'])

        result = easy_ocr.extract_text("/tmp/test_ocr.jpg")

        print(f"Full text: {result.full_text}")
        print(f"Detections: {len(result.detections)}")

    # Example 3: Post-processing
    if TESSERACT_AVAILABLE or EASYOCR_AVAILABLE:
        print("\n=== Post-Processing ===")

        processor = OCRPostProcessor()

        # Filter by confidence
        filtered = processor.filter_by_confidence(result, min_confidence=0.7)
        print(f"High-confidence detections: {len(filtered.detections)}")

        # Merge lines
        merged_text = processor.merge_lines(result)
        print(f"Merged text:\n{merged_text}")

    print("\nOCR engines ready!")
