"""
Unit tests for Computer Vision tissues.

Testing Strategy:
1. Test each tissue independently
2. Verify error handling
3. Check performance constraints
4. Validate output formats
"""

import pytest
import numpy as np
import cv2
import sys
import os
from typing import List, Tuple

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tissues.computer_vision.detection.CV_TISSUE_001_face_detector import FaceDetector
from tissues.computer_vision.preprocessing.CV_TISSUE_002_image_normalizer import ImageNormalizer
from tissues.computer_vision.connective.CV_TISSUE_003_result_aggregator import ResultAggregator


class TestFaceDetectorTissue:
    """Test CV-TISSUE-001: Face Detector"""
    
    @pytest.fixture
    def detector(self):
        """Create face detector instance"""
        return FaceDetector(confidence_threshold=0.5)
    
    @pytest.fixture
    def test_images(self):
        """Generate test images"""
        return {
            "empty": np.zeros((480, 640, 3), dtype=np.uint8),
            "noise": np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
            "small": np.zeros((100, 100, 3), dtype=np.uint8),
            "grayscale": np.zeros((480, 640), dtype=np.uint8),
            "large": np.zeros((1920, 1080, 3), dtype=np.uint8)
        }
    
    def test_detector_initialization(self, detector):
        """Test detector initializes correctly"""
        assert detector is not None
        assert detector.confidence_threshold == 0.5
        assert detector.min_face_size == (30, 30)
        assert detector.backend in ["haar", "dnn", "auto"]
    
    def test_detect_empty_image(self, detector, test_images):
        """Test detection on empty image"""
        result = detector.detect(test_images["empty"])
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_detect_invalid_input(self, detector):
        """Test error handling for invalid inputs"""
        assert detector.detect(None) == []
        assert detector.detect(np.array([])) == []
        
        # Test with wrong shape
        invalid = np.zeros((10,), dtype=np.uint8)
        result = detector.detect(invalid)
        assert result == []
    
    def test_detect_output_format(self, detector, test_images):
        """Test output format is correct"""
        # Even if no faces detected, format should be consistent
        result = detector.detect(test_images["noise"])
        assert isinstance(result, list)
        
        # If faces detected, check format
        if len(result) > 0:
            face = result[0]
            assert len(face) == 5  # x, y, w, h, confidence
            x, y, w, h, conf = face
            assert all(isinstance(v, (int, np.integer)) for v in [x, y, w, h])
            assert isinstance(conf, (float, np.floating))
            assert 0 <= conf <= 1
    
    def test_detect_largest(self, detector, test_images):
        """Test detect_largest functionality"""
        result = detector.detect_largest(test_images["empty"])
        assert result is None
        
        # Mock detection with multiple faces
        detector.detect = lambda img: [(10, 10, 50, 50, 0.9), (100, 100, 100, 100, 0.8)]
        largest = detector.detect_largest(test_images["empty"])
        assert largest == (100, 100, 100, 100, 0.8)  # Larger area
    
    @pytest.mark.performance
    def test_detector_performance(self, detector, test_images):
        """Test detector meets performance requirements"""
        import time
        
        # Test on standard size image
        start = time.time()
        for _ in range(10):
            detector.detect(test_images["empty"])
        elapsed = time.time() - start
        
        fps = 10 / elapsed
        assert fps > 30, f"Detector too slow: {fps:.2f} FPS, expected > 30 FPS"


class TestImageNormalizerTissue:
    """Test CV-TISSUE-002: Image Normalizer"""
    
    @pytest.fixture
    def normalizer(self):
        """Create normalizer instance"""
        return ImageNormalizer(target_size=(224, 224))
    
    def test_normalizer_initialization(self):
        """Test normalizer configuration"""
        norm = ImageNormalizer(
            target_size=(640, 480),
            maintain_aspect=False,
            normalize_values=True
        )
        assert norm.target_size == (640, 480)
        assert norm.maintain_aspect == False
        assert norm.normalize_values == True
    
    def test_normalize_different_formats(self, normalizer):
        """Test normalization of different image formats"""
        # Grayscale
        gray = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        result = normalizer.normalize(gray)
        assert result.shape == (224, 224, 3)
        
        # RGB
        rgb = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = normalizer.normalize(rgb)
        assert result.shape == (224, 224, 3)
        
        # RGBA
        rgba = np.random.randint(0, 255, (100, 100, 4), dtype=np.uint8)
        result = normalizer.normalize(rgba)
        assert result.shape == (224, 224, 3)
    
    def test_normalize_aspect_ratio(self):
        """Test aspect ratio preservation"""
        normalizer = ImageNormalizer(
            target_size=(224, 224),
            maintain_aspect=True
        )
        
        # Wide image
        wide = np.zeros((100, 200, 3), dtype=np.uint8)
        result = normalizer.normalize(wide)
        assert result.shape == (224, 224, 3)
        
        # Tall image
        tall = np.zeros((200, 100, 3), dtype=np.uint8)
        result = normalizer.normalize(tall)
        assert result.shape == (224, 224, 3)
    
    def test_normalize_values(self):
        """Test value normalization"""
        normalizer = ImageNormalizer(normalize_values=True)
        
        # Test uint8 input
        img = np.array([[[255, 128, 0]]], dtype=np.uint8)
        result = normalizer.normalize(img)
        assert result.max() <= 1.0
        assert result.min() >= 0.0
        
        # Test float input
        img_float = np.array([[[1.0, 0.5, 0.0]]], dtype=np.float32)
        result = normalizer.normalize(img_float)
        assert result.dtype == np.float32
    
    def test_error_handling(self, normalizer):
        """Test error handling"""
        with pytest.raises(ValueError):
            normalizer.normalize(None)
        
        with pytest.raises(ValueError):
            normalizer.normalize(np.array([]))
    
    def test_statistics_tracking(self, normalizer):
        """Test preprocessing statistics"""
        # Process several images
        for _ in range(5):
            img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            normalizer.normalize(img)
        
        stats = normalizer.get_preprocessing_stats()
        assert "mean_brightness" in stats
        assert "contrast" in stats


class TestResultAggregatorTissue:
    """Test CV-TISSUE-003: Result Aggregator"""
    
    @pytest.fixture
    def aggregator(self):
        """Create aggregator instance"""
        return ResultAggregator()
    
    def test_aggregator_initialization(self, aggregator):
        """Test aggregator setup"""
        assert aggregator.mode == "sequential"
        assert aggregator.keep_history == True
        assert len(aggregator.results) == 0
    
    def test_add_result(self, aggregator):
        """Test adding results"""
        # Add successful result
        aggregator.add_result("test_stage", {"data": "test"})
        assert "test_stage" in aggregator.results
        assert aggregator.results["test_stage"].success == True
        
        # Add failed result
        aggregator.add_result(
            "failed_stage", 
            None, 
            success=False, 
            error_message="Test error"
        )
        assert aggregator.results["failed_stage"].success == False
    
    def test_aggregate_formats(self, aggregator):
        """Test different aggregation formats"""
        # Add test data
        aggregator.add_result("stage1", [1, 2, 3])
        aggregator.add_result("stage2", {"key": "value"})
        
        # Test dict format
        dict_result = aggregator.aggregate(format="dict")
        assert dict_result["stage1"] == [1, 2, 3]
        assert dict_result["stage2"] == {"key": "value"}
        
        # Test list format
        list_result = aggregator.aggregate(format="list")
        assert len(list_result) == 2
        
        # Test pipeline format
        pipeline_result = aggregator.aggregate(format="pipeline")
        assert "stages" in pipeline_result
        assert "flow" in pipeline_result
    
    def test_error_handling_aggregation(self, aggregator):
        """Test aggregation with errors"""
        aggregator.add_result("good", "data")
        aggregator.add_result("bad", None, success=False, error_message="Error")
        
        assert aggregator.has_errors() == True
        errors = aggregator.get_errors()
        assert "bad" in errors
        
        successful = aggregator.filter_successful()
        assert len(successful) == 1
        assert "good" in successful
    
    def test_summary_generation(self, aggregator):
        """Test summary statistics"""
        aggregator.add_result("s1", "data1")
        aggregator.add_result("s2", "data2")
        aggregator.add_result("s3", None, success=False)
        
        summary = aggregator.get_summary()
        assert summary["total_stages"] == 3
        assert summary["successful_stages"] == 2
        assert summary["failed_stages"] == 1
        assert summary["success_rate"] == 2/3


@pytest.mark.integration
class TestTissueIntegration:
    """Test tissues working together"""
    
    def test_normalizer_to_detector_flow(self):
        """Test data flow from normalizer to detector"""
        # Create tissues
        normalizer = ImageNormalizer(target_size=(640, 480))
        detector = FaceDetector()
        
        # Create test image
        raw_image = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        
        # Process through pipeline
        normalized = normalizer.normalize(raw_image)
        faces = detector.detect(normalized)
        
        # Verify flow
        assert normalized.shape == (480, 640, 3)
        assert isinstance(faces, list)
    
    def test_full_pipeline_flow(self):
        """Test complete pipeline with aggregator"""
        normalizer = ImageNormalizer()
        detector = FaceDetector()
        aggregator = ResultAggregator()
        
        # Test image
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Pipeline execution
        try:
            normalized = normalizer.normalize(image)
            aggregator.add_result("normalization", normalized)
        except Exception as e:
            aggregator.add_result("normalization", None, success=False, error_message=str(e))
        
        try:
            faces = detector.detect(normalized)
            aggregator.add_result("detection", faces)
        except Exception as e:
            aggregator.add_result("detection", None, success=False, error_message=str(e))
        
        # Check results
        result = aggregator.aggregate()
        assert "_metadata" in result
        assert result["_summary"]["total_stages"] == 2


def run_tests():
    """Run all tests with pytest"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()