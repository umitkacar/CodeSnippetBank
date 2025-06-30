"""
Tissue ID: CV-TISSUE-003  
Title: Result Aggregator for Multi-Stage CV Pipelines
Category: computer_vision/connective
Tags: ["aggregator", "pipeline", "connector", "results"]
Difficulty: Beginner
Dependencies: ["numpy>=1.19.0"]
Performance: O(n) where n is number of results
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A connective tissue that aggregates results from multiple CV operations,
enabling smooth data flow between different processing stages. Perfect for
building complex pipelines from simple tissues.

Use Cases:
- Combining detection results from multiple detectors
- Merging preprocessing and detection outputs
- Creating unified results for downstream processing
- Building modular CV pipelines

Example Usage:
    aggregator = ResultAggregator()
    aggregator.add_result("preprocessing", preprocessed_data)
    aggregator.add_result("detection", detection_results)
    combined = aggregator.aggregate()
"""

import numpy as np
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProcessingResult:
    """Container for processing results with metadata"""
    stage_name: str
    data: Any
    timestamp: float
    metadata: Dict[str, Any]
    success: bool = True
    error_message: Optional[str] = None


class ResultAggregator:
    """
    Aggregates results from multiple CV processing stages.
    Tissue Type: CONNECTIVE - Bonds different processing stages together.
    """
    
    def __init__(self, 
                 mode: str = "sequential",
                 keep_history: bool = True):
        """
        Initialize result aggregator.
        
        Args:
            mode: 'sequential' or 'parallel' aggregation mode
            keep_history: Whether to keep processing history
        """
        self.mode = mode
        self.keep_history = keep_history
        self.results: Dict[str, ProcessingResult] = {}
        self.history: List[ProcessingResult] = []
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "total_stages": 0,
            "successful_stages": 0
        }
    
    def add_result(self, 
                   stage_name: str, 
                   data: Any,
                   metadata: Optional[Dict[str, Any]] = None,
                   success: bool = True,
                   error_message: Optional[str] = None) -> 'ResultAggregator':
        """
        Add a processing result from a stage.
        
        Args:
            stage_name: Name of the processing stage
            data: Result data from the stage
            metadata: Optional metadata about the result
            success: Whether the stage succeeded
            error_message: Error message if failed
            
        Returns:
            Self for chaining
        """
        result = ProcessingResult(
            stage_name=stage_name,
            data=data,
            timestamp=datetime.now().timestamp(),
            metadata=metadata or {},
            success=success,
            error_message=error_message
        )
        
        # Store result
        self.results[stage_name] = result
        
        # Update history
        if self.keep_history:
            self.history.append(result)
        
        # Update metadata
        self.metadata["total_stages"] += 1
        if success:
            self.metadata["successful_stages"] += 1
        
        return self
    
    def aggregate(self, 
                  format: str = "dict",
                  include_metadata: bool = True) -> Union[Dict[str, Any], List[Any]]:
        """
        Aggregate all results into specified format.
        
        Args:
            format: Output format ('dict', 'list', 'pipeline')
            include_metadata: Whether to include metadata
            
        Returns:
            Aggregated results in specified format
        """
        if format == "dict":
            return self._aggregate_dict(include_metadata)
        elif format == "list":
            return self._aggregate_list(include_metadata)
        elif format == "pipeline":
            return self._aggregate_pipeline(include_metadata)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def _aggregate_dict(self, include_metadata: bool) -> Dict[str, Any]:
        """Aggregate as dictionary"""
        output = {}
        
        for stage_name, result in self.results.items():
            if result.success:
                output[stage_name] = result.data
            else:
                output[stage_name] = {"error": result.error_message}
        
        if include_metadata:
            output["_metadata"] = self.metadata
            output["_summary"] = self.get_summary()
        
        return output
    
    def _aggregate_list(self, include_metadata: bool) -> List[Any]:
        """Aggregate as ordered list"""
        # Sort by timestamp to maintain order
        sorted_results = sorted(
            self.results.values(),
            key=lambda r: r.timestamp
        )
        
        output = []
        for result in sorted_results:
            if include_metadata:
                output.append({
                    "stage": result.stage_name,
                    "data": result.data if result.success else None,
                    "success": result.success,
                    "metadata": result.metadata
                })
            else:
                if result.success:
                    output.append(result.data)
        
        return output
    
    def _aggregate_pipeline(self, include_metadata: bool) -> Dict[str, Any]:
        """Aggregate for pipeline processing"""
        # Create a pipeline-friendly format
        pipeline_data = {
            "input": None,
            "stages": {},
            "output": None,
            "flow": []
        }
        
        # Track data flow
        for stage_name, result in self.results.items():
            pipeline_data["stages"][stage_name] = {
                "data": result.data if result.success else None,
                "success": result.success,
                "duration": result.metadata.get("duration", 0)
            }
            pipeline_data["flow"].append(stage_name)
        
        # Set input/output based on first/last stages
        if self.history:
            pipeline_data["input"] = self.history[0].data
            pipeline_data["output"] = self.history[-1].data if self.history[-1].success else None
        
        if include_metadata:
            pipeline_data["metadata"] = self.metadata
        
        return pipeline_data
    
    def get_stage_result(self, stage_name: str) -> Optional[Any]:
        """Get result from specific stage"""
        if stage_name in self.results:
            result = self.results[stage_name]
            return result.data if result.success else None
        return None
    
    def get_summary(self) -> Dict[str, Any]:
        """Get processing summary"""
        return {
            "total_stages": self.metadata["total_stages"],
            "successful_stages": self.metadata["successful_stages"],
            "failed_stages": self.metadata["total_stages"] - self.metadata["successful_stages"],
            "success_rate": (
                self.metadata["successful_stages"] / self.metadata["total_stages"]
                if self.metadata["total_stages"] > 0 else 0
            ),
            "stages": list(self.results.keys()),
            "mode": self.mode
        }
    
    def merge_with(self, other: 'ResultAggregator') -> 'ResultAggregator':
        """Merge with another aggregator"""
        for stage_name, result in other.results.items():
            # Avoid overwriting existing results
            unique_name = stage_name
            counter = 1
            while unique_name in self.results:
                unique_name = f"{stage_name}_{counter}"
                counter += 1
            
            self.add_result(
                unique_name,
                result.data,
                result.metadata,
                result.success,
                result.error_message
            )
        
        return self
    
    def filter_successful(self) -> Dict[str, Any]:
        """Get only successful results"""
        return {
            stage: result.data
            for stage, result in self.results.items()
            if result.success
        }
    
    def has_errors(self) -> bool:
        """Check if any stage failed"""
        return any(not result.success for result in self.results.values())
    
    def get_errors(self) -> Dict[str, str]:
        """Get all error messages"""
        return {
            stage: result.error_message
            for stage, result in self.results.items()
            if not result.success and result.error_message
        }


# Utility functions for common aggregation patterns
def combine_detections(detections_list: List[List[tuple]]) -> List[tuple]:
    """Combine detection results from multiple sources"""
    aggregator = ResultAggregator()
    
    for i, detections in enumerate(detections_list):
        aggregator.add_result(f"detector_{i}", detections)
    
    # Combine all detections
    all_detections = []
    for result in aggregator.filter_successful().values():
        all_detections.extend(result)
    
    return all_detections


def create_pipeline_result(stages: Dict[str, Any]) -> Dict[str, Any]:
    """Create a pipeline result from stage outputs"""
    aggregator = ResultAggregator(mode="sequential")
    
    for stage_name, data in stages.items():
        aggregator.add_result(stage_name, data)
    
    return aggregator.aggregate(format="pipeline")


# Auto-generated tests
def test_result_aggregator():
    """Test result aggregation functionality"""
    aggregator = ResultAggregator()
    
    # Add some results
    aggregator.add_result("preprocessing", {"image": "normalized"})
    aggregator.add_result("detection", [{"face": 1}, {"face": 2}])
    aggregator.add_result("failed_stage", None, success=False, error_message="Test error")
    
    # Test different aggregation formats
    dict_result = aggregator.aggregate(format="dict", include_metadata=False)
    assert "preprocessing" in dict_result
    assert "detection" in dict_result
    assert "failed_stage" in dict_result
    
    list_result = aggregator.aggregate(format="list", include_metadata=False)
    assert len(list_result) == 2  # Only successful stages
    
    pipeline_result = aggregator.aggregate(format="pipeline")
    assert "stages" in pipeline_result
    assert len(pipeline_result["flow"]) == 3
    
    # Test summary
    summary = aggregator.get_summary()
    assert summary["total_stages"] == 3
    assert summary["successful_stages"] == 2
    assert summary["success_rate"] == 2/3
    
    # Test error handling
    assert aggregator.has_errors() == True
    errors = aggregator.get_errors()
    assert "failed_stage" in errors
    
    print("All tests passed!")


if __name__ == "__main__":
    test_result_aggregator()