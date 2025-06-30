"""
CodeSnippetBank Tissue Quality Framework
========================================

This framework ensures every tissue meets the highest quality standards for Edge LLMs.
It provides comprehensive profiling, benchmarking, and optimization capabilities.

Key Features:
- Performance profiling (time, memory, CPU)
- Edge device compatibility testing
- Battery consumption estimation
- Token efficiency analysis
- Composition compatibility matrix
- Quality scoring system
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import psutil
import tracemalloc
import json
import os
from pathlib import Path


class QualityDimension(Enum):
    """Dimensions of tissue quality"""
    PERFORMANCE = "performance"
    MEMORY = "memory"
    BATTERY = "battery"
    TOKEN_EFFICIENCY = "token_efficiency"
    EDGE_COMPATIBILITY = "edge_compatibility"
    COMPOSABILITY = "composability"
    RELIABILITY = "reliability"
    MAINTAINABILITY = "maintainability"


class EdgeDevice(Enum):
    """Common edge device profiles"""
    RASPBERRY_PI_ZERO = "rpi_zero"  # 512MB RAM, 1GHz
    RASPBERRY_PI_4 = "rpi_4"  # 4GB RAM, 1.5GHz
    JETSON_NANO = "jetson_nano"  # 4GB RAM, GPU
    MOBILE_LOW = "mobile_low"  # 2GB RAM
    MOBILE_MID = "mobile_mid"  # 4GB RAM
    MOBILE_HIGH = "mobile_high"  # 8GB RAM
    ARDUINO_ESP32 = "esp32"  # 520KB RAM
    CORAL_TPU = "coral_tpu"  # Edge TPU


@dataclass
class DeviceProfile:
    """Edge device hardware profile"""
    name: str
    ram_mb: int
    cpu_cores: int
    cpu_freq_mhz: int
    has_gpu: bool
    has_tpu: bool
    battery_mah: Optional[int] = None
    storage_mb: int = 1024


# Edge device profiles database
EDGE_PROFILES = {
    EdgeDevice.RASPBERRY_PI_ZERO: DeviceProfile(
        name="Raspberry Pi Zero W",
        ram_mb=512,
        cpu_cores=1,
        cpu_freq_mhz=1000,
        has_gpu=False,
        has_tpu=False,
        storage_mb=8192
    ),
    EdgeDevice.RASPBERRY_PI_4: DeviceProfile(
        name="Raspberry Pi 4",
        ram_mb=4096,
        cpu_cores=4,
        cpu_freq_mhz=1500,
        has_gpu=True,
        has_tpu=False,
        storage_mb=32768
    ),
    EdgeDevice.JETSON_NANO: DeviceProfile(
        name="NVIDIA Jetson Nano",
        ram_mb=4096,
        cpu_cores=4,
        cpu_freq_mhz=1430,
        has_gpu=True,
        has_tpu=False,
        storage_mb=16384
    ),
    EdgeDevice.MOBILE_LOW: DeviceProfile(
        name="Low-end Mobile",
        ram_mb=2048,
        cpu_cores=4,
        cpu_freq_mhz=1400,
        has_gpu=True,
        has_tpu=False,
        battery_mah=3000,
        storage_mb=16384
    ),
    EdgeDevice.MOBILE_MID: DeviceProfile(
        name="Mid-range Mobile",
        ram_mb=4096,
        cpu_cores=8,
        cpu_freq_mhz=2000,
        has_gpu=True,
        has_tpu=False,
        battery_mah=4000,
        storage_mb=64000
    ),
    EdgeDevice.ARDUINO_ESP32: DeviceProfile(
        name="ESP32",
        ram_mb=0.5,  # 520KB
        cpu_cores=2,
        cpu_freq_mhz=240,
        has_gpu=False,
        has_tpu=False,
        storage_mb=4
    )
}


@dataclass
class PerformanceMetrics:
    """Performance measurement results"""
    execution_time_ms: float
    memory_peak_mb: float
    memory_allocated_mb: float
    cpu_percent: float
    token_count: int
    operations_per_second: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_time_ms": round(self.execution_time_ms, 2),
            "memory_peak_mb": round(self.memory_peak_mb, 2),
            "memory_allocated_mb": round(self.memory_allocated_mb, 2),
            "cpu_percent": round(self.cpu_percent, 2),
            "token_count": self.token_count,
            "ops_per_second": round(self.operations_per_second, 2)
        }


@dataclass
class QualityScore:
    """Comprehensive quality score for a tissue"""
    overall_score: float  # 0-100
    dimension_scores: Dict[QualityDimension, float]
    edge_compatibility: Dict[EdgeDevice, bool]
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def is_edge_ready(self) -> bool:
        """Check if tissue is ready for edge deployment"""
        return self.overall_score >= 80 and len(self.warnings) == 0
    
    def get_compatible_devices(self) -> List[EdgeDevice]:
        """Get list of compatible edge devices"""
        return [device for device, compatible in self.edge_compatibility.items() if compatible]


class TissueProfiler:
    """Profile tissue performance and resource usage"""
    
    def __init__(self):
        self.process = psutil.Process()
    
    def profile_tissue(self, 
                      tissue_func: Callable,
                      test_data: Any,
                      iterations: int = 100) -> PerformanceMetrics:
        """
        Profile a tissue function's performance.
        
        Args:
            tissue_func: The tissue function to profile
            test_data: Test data for the function
            iterations: Number of iterations for accurate measurement
            
        Returns:
            Performance metrics
        """
        # Warm up
        for _ in range(10):
            tissue_func(test_data)
        
        # Memory profiling
        tracemalloc.start()
        memory_before = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # CPU profiling
        cpu_before = self.process.cpu_percent(interval=0.1)
        
        # Time profiling
        start_time = time.perf_counter()
        
        # Run iterations
        for _ in range(iterations):
            tissue_func(test_data)
        
        # Collect metrics
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000 / iterations  # ms per operation
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        memory_after = self.process.memory_info().rss / 1024 / 1024
        cpu_after = self.process.cpu_percent(interval=0.1)
        
        # Estimate token count (simplified - count function source)
        import inspect
        source = inspect.getsource(tissue_func)
        token_count = len(source.split())  # Rough estimate
        
        return PerformanceMetrics(
            execution_time_ms=execution_time,
            memory_peak_mb=peak / 1024 / 1024,
            memory_allocated_mb=memory_after - memory_before,
            cpu_percent=(cpu_after + cpu_before) / 2,
            token_count=token_count,
            operations_per_second=1000 / execution_time
        )
    
    def estimate_battery_consumption(self,
                                   metrics: PerformanceMetrics,
                                   device: EdgeDevice,
                                   usage_hours: float = 1.0) -> float:
        """
        Estimate battery consumption for edge device.
        
        Args:
            metrics: Performance metrics
            device: Target edge device
            usage_hours: Hours of continuous usage
            
        Returns:
            Estimated battery percentage consumed
        """
        profile = EDGE_PROFILES[device]
        
        if not profile.battery_mah:
            return 0.0
        
        # Simplified power model
        # Power (mW) = CPU_power + Memory_power + Base_power
        cpu_power = (metrics.cpu_percent / 100) * (profile.cpu_cores * 500)  # 500mW per core at 100%
        memory_power = (metrics.memory_allocated_mb / profile.ram_mb) * 200  # 200mW for full RAM
        base_power = 1000  # 1W base consumption
        
        total_power_mw = cpu_power + memory_power + base_power
        
        # Battery consumption
        consumption_mah = (total_power_mw / 1000) * usage_hours * 1000 / 3.7  # 3.7V typical
        consumption_percent = (consumption_mah / profile.battery_mah) * 100
        
        return consumption_percent


class TissueQualityAnalyzer:
    """Analyze tissue quality across multiple dimensions"""
    
    def __init__(self):
        self.profiler = TissueProfiler()
        self.compatibility_cache = {}
    
    def analyze_tissue(self,
                      tissue_id: str,
                      tissue_func: Callable,
                      test_cases: List[Any],
                      tissue_metadata: Dict[str, Any]) -> QualityScore:
        """
        Perform comprehensive quality analysis on a tissue.
        
        Args:
            tissue_id: Unique tissue identifier
            tissue_func: The tissue function
            test_cases: List of test cases
            tissue_metadata: Tissue metadata (tags, dependencies, etc.)
            
        Returns:
            Comprehensive quality score
        """
        dimension_scores = {}
        warnings = []
        recommendations = []
        
        # Performance analysis
        perf_metrics = self._analyze_performance(tissue_func, test_cases)
        dimension_scores[QualityDimension.PERFORMANCE] = self._score_performance(perf_metrics)
        
        # Memory analysis
        memory_score = self._score_memory(perf_metrics)
        dimension_scores[QualityDimension.MEMORY] = memory_score
        
        if memory_score < 70:
            warnings.append("High memory usage detected")
            recommendations.append("Consider optimizing data structures or using generators")
        
        # Battery efficiency
        battery_scores = []
        for device in [EdgeDevice.MOBILE_LOW, EdgeDevice.MOBILE_MID]:
            battery_consumption = self.profiler.estimate_battery_consumption(
                perf_metrics, device, usage_hours=1.0
            )
            battery_scores.append(100 - min(battery_consumption, 100))
        
        dimension_scores[QualityDimension.BATTERY] = np.mean(battery_scores)
        
        # Token efficiency
        token_score = self._score_token_efficiency(perf_metrics, tissue_metadata)
        dimension_scores[QualityDimension.TOKEN_EFFICIENCY] = token_score
        
        # Edge compatibility
        edge_compatibility = self._check_edge_compatibility(perf_metrics)
        compatibility_score = (len([c for c in edge_compatibility.values() if c]) / 
                             len(edge_compatibility)) * 100
        dimension_scores[QualityDimension.EDGE_COMPATIBILITY] = compatibility_score
        
        # Composability (based on metadata)
        composability_score = self._score_composability(tissue_metadata)
        dimension_scores[QualityDimension.COMPOSABILITY] = composability_score
        
        # Reliability (based on test coverage)
        reliability_score = self._score_reliability(tissue_func, test_cases)
        dimension_scores[QualityDimension.RELIABILITY] = reliability_score
        
        # Maintainability (based on code quality)
        maintainability_score = self._score_maintainability(tissue_func, tissue_metadata)
        dimension_scores[QualityDimension.MAINTAINABILITY] = maintainability_score
        
        # Calculate overall score (weighted average)
        weights = {
            QualityDimension.PERFORMANCE: 0.20,
            QualityDimension.MEMORY: 0.20,
            QualityDimension.BATTERY: 0.15,
            QualityDimension.TOKEN_EFFICIENCY: 0.15,
            QualityDimension.EDGE_COMPATIBILITY: 0.10,
            QualityDimension.COMPOSABILITY: 0.10,
            QualityDimension.RELIABILITY: 0.05,
            QualityDimension.MAINTAINABILITY: 0.05
        }
        
        overall_score = sum(dimension_scores[dim] * weights[dim] for dim in dimension_scores)
        
        # Generate recommendations
        if overall_score < 80:
            recommendations.append("Consider optimizing for edge deployment")
        
        return QualityScore(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            edge_compatibility=edge_compatibility,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def _analyze_performance(self, tissue_func: Callable, test_cases: List[Any]) -> PerformanceMetrics:
        """Analyze performance across test cases"""
        metrics_list = []
        
        for test_case in test_cases[:3]:  # Sample first 3 test cases
            metrics = self.profiler.profile_tissue(tissue_func, test_case, iterations=50)
            metrics_list.append(metrics)
        
        # Average metrics
        avg_metrics = PerformanceMetrics(
            execution_time_ms=np.mean([m.execution_time_ms for m in metrics_list]),
            memory_peak_mb=np.max([m.memory_peak_mb for m in metrics_list]),
            memory_allocated_mb=np.mean([m.memory_allocated_mb for m in metrics_list]),
            cpu_percent=np.mean([m.cpu_percent for m in metrics_list]),
            token_count=metrics_list[0].token_count,
            operations_per_second=np.mean([m.operations_per_second for m in metrics_list])
        )
        
        return avg_metrics
    
    def _score_performance(self, metrics: PerformanceMetrics) -> float:
        """Score performance (0-100)"""
        # Scoring based on execution time
        if metrics.execution_time_ms < 1:
            time_score = 100
        elif metrics.execution_time_ms < 10:
            time_score = 90
        elif metrics.execution_time_ms < 100:
            time_score = 70
        elif metrics.execution_time_ms < 1000:
            time_score = 50
        else:
            time_score = 30
        
        # Scoring based on operations per second
        if metrics.operations_per_second > 10000:
            ops_score = 100
        elif metrics.operations_per_second > 1000:
            ops_score = 80
        elif metrics.operations_per_second > 100:
            ops_score = 60
        else:
            ops_score = 40
        
        return (time_score + ops_score) / 2
    
    def _score_memory(self, metrics: PerformanceMetrics) -> float:
        """Score memory usage (0-100)"""
        # Lower memory usage = higher score
        if metrics.memory_peak_mb < 1:
            peak_score = 100
        elif metrics.memory_peak_mb < 10:
            peak_score = 90
        elif metrics.memory_peak_mb < 50:
            peak_score = 70
        elif metrics.memory_peak_mb < 100:
            peak_score = 50
        else:
            peak_score = 30
        
        if metrics.memory_allocated_mb < 0.1:
            alloc_score = 100
        elif metrics.memory_allocated_mb < 1:
            alloc_score = 80
        elif metrics.memory_allocated_mb < 10:
            alloc_score = 60
        else:
            alloc_score = 40
        
        return (peak_score + alloc_score) / 2
    
    def _score_token_efficiency(self, metrics: PerformanceMetrics, metadata: Dict[str, Any]) -> float:
        """Score token efficiency (0-100)"""
        # Ideal token count for edge: 50-500 tokens
        token_count = metrics.token_count
        
        if 50 <= token_count <= 200:
            token_score = 100
        elif 200 < token_count <= 500:
            token_score = 80
        elif token_count < 50:
            token_score = 70  # Too simple
        elif 500 < token_count <= 1000:
            token_score = 60
        else:
            token_score = 40  # Too complex
        
        # Bonus for good documentation
        if metadata.get("description") and len(metadata["description"]) > 100:
            token_score = min(100, token_score + 10)
        
        return token_score
    
    def _check_edge_compatibility(self, metrics: PerformanceMetrics) -> Dict[EdgeDevice, bool]:
        """Check compatibility with edge devices"""
        compatibility = {}
        
        for device, profile in EDGE_PROFILES.items():
            # Check if tissue can run on device
            compatible = True
            
            # Memory check
            if metrics.memory_peak_mb > profile.ram_mb * 0.5:  # Don't use more than 50% RAM
                compatible = False
            
            # Performance check (rough estimate)
            if metrics.execution_time_ms > 1000 and profile.cpu_freq_mhz < 1000:
                compatible = False
            
            compatibility[device] = compatible
        
        return compatibility
    
    def _score_composability(self, metadata: Dict[str, Any]) -> float:
        """Score how well tissue can compose with others"""
        score = 60  # Base score
        
        # Check for standard interfaces
        if metadata.get("tags"):
            if "functional" in metadata["tags"]:
                score += 20
            if "pure" in metadata["tags"]:
                score += 10
            if "stateless" in metadata["tags"]:
                score += 10
        
        # Check dependencies
        deps = metadata.get("dependencies", [])
        if len(deps) <= 2:
            score += 10
        elif len(deps) > 5:
            score -= 20
        
        return min(100, score)
    
    def _score_reliability(self, tissue_func: Callable, test_cases: List[Any]) -> float:
        """Score reliability based on test coverage and error handling"""
        score = 70  # Base score
        
        # Check if function has error handling
        import inspect
        source = inspect.getsource(tissue_func)
        
        if "try:" in source or "except" in source:
            score += 15
        
        if "raise" in source:
            score += 10  # Explicit error signaling
        
        if len(test_cases) >= 5:
            score += 5
        
        return min(100, score)
    
    def _score_maintainability(self, tissue_func: Callable, metadata: Dict[str, Any]) -> float:
        """Score maintainability based on code quality"""
        score = 70  # Base score
        
        # Check documentation
        if tissue_func.__doc__:
            score += 15
        
        # Check metadata completeness
        required_fields = ["version", "author", "last_updated", "description"]
        present_fields = sum(1 for field in required_fields if field in metadata)
        score += (present_fields / len(required_fields)) * 15
        
        return min(100, score)
    
    def generate_quality_report(self, 
                              tissue_id: str,
                              quality_score: QualityScore,
                              output_path: Optional[Path] = None) -> str:
        """
        Generate comprehensive quality report.
        
        Args:
            tissue_id: Tissue identifier
            quality_score: Quality analysis results
            output_path: Optional path to save report
            
        Returns:
            Report as formatted string
        """
        report = f"""
# Tissue Quality Report: {tissue_id}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Overall Quality Score: {quality_score.overall_score:.1f}/100
Status: {'✅ Edge-Ready' if quality_score.is_edge_ready() else '⚠️ Needs Optimization'}

## Dimension Scores
"""
        
        for dim, score in quality_score.dimension_scores.items():
            emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            report += f"- {dim.value.title()}: {emoji} {score:.1f}/100\n"
        
        report += f"\n## Edge Device Compatibility\n"
        compatible_devices = quality_score.get_compatible_devices()
        
        for device in EdgeDevice:
            profile = EDGE_PROFILES[device]
            is_compatible = device in compatible_devices
            status = "✅ Compatible" if is_compatible else "❌ Not Compatible"
            report += f"- {profile.name}: {status}\n"
        
        if quality_score.warnings:
            report += f"\n## ⚠️ Warnings\n"
            for warning in quality_score.warnings:
                report += f"- {warning}\n"
        
        if quality_score.recommendations:
            report += f"\n## 💡 Recommendations\n"
            for rec in quality_score.recommendations:
                report += f"- {rec}\n"
        
        report += f"\n## Optimization Suggestions\n"
        
        # Performance optimization
        perf_score = quality_score.dimension_scores[QualityDimension.PERFORMANCE]
        if perf_score < 80:
            report += "- Consider algorithmic optimizations or caching\n"
        
        # Memory optimization
        mem_score = quality_score.dimension_scores[QualityDimension.MEMORY]
        if mem_score < 80:
            report += "- Use generators or streaming for large datasets\n"
            report += "- Consider in-place operations to reduce memory allocation\n"
        
        # Token optimization
        token_score = quality_score.dimension_scores[QualityDimension.TOKEN_EFFICIENCY]
        if token_score < 80:
            report += "- Simplify implementation or split into smaller tissues\n"
        
        if output_path:
            output_path.write_text(report)
        
        return report


class TissueCompositionAnalyzer:
    """Analyze how tissues work together"""
    
    def __init__(self):
        self.composition_graph = {}
    
    def analyze_composition(self,
                          tissue1_id: str,
                          tissue2_id: str,
                          tissue1_output: type,
                          tissue2_input: type) -> bool:
        """
        Check if two tissues can be composed.
        
        Args:
            tissue1_id: First tissue ID
            tissue2_id: Second tissue ID
            tissue1_output: Output type of first tissue
            tissue2_input: Input type of second tissue
            
        Returns:
            True if tissues can be composed
        """
        # Type compatibility check
        if tissue1_output == tissue2_input:
            return True
        
        # Check if output can be converted to input
        if tissue1_output == np.ndarray and tissue2_input == list:
            return True
        
        if tissue1_output == list and tissue2_input == np.ndarray:
            return True
        
        # String compatibility
        if tissue1_output == str and tissue2_input in [list, dict]:
            return True  # Can parse
        
        return False
    
    def build_composition_graph(self, tissues: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Build a graph of tissue compositions.
        
        Args:
            tissues: List of tissue metadata
            
        Returns:
            Composition graph (tissue_id -> [compatible_tissue_ids])
        """
        graph = {tissue["id"]: [] for tissue in tissues}
        
        for i, tissue1 in enumerate(tissues):
            for j, tissue2 in enumerate(tissues):
                if i != j:
                    # Simplified check based on tags
                    t1_tags = set(tissue1.get("tags", []))
                    t2_tags = set(tissue2.get("tags", []))
                    
                    # Domain compatibility
                    if t1_tags & t2_tags:  # Share at least one tag
                        graph[tissue1["id"]].append(tissue2["id"])
        
        return graph
    
    def suggest_compositions(self, 
                           tissue_id: str,
                           target_task: str,
                           available_tissues: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Suggest tissue composition pipelines for a target task.
        
        Args:
            tissue_id: Starting tissue
            target_task: Target task description
            available_tissues: Available tissues
            
        Returns:
            List of composition pipelines
        """
        # Build composition graph
        graph = self.build_composition_graph(available_tissues)
        
        # Find paths from tissue_id to tissues with target task tag
        target_tissues = [t["id"] for t in available_tissues 
                         if target_task.lower() in " ".join(t.get("tags", [])).lower()]
        
        pipelines = []
        
        # Simple BFS to find paths
        from collections import deque
        
        for target in target_tissues:
            queue = deque([(tissue_id, [tissue_id])])
            visited = {tissue_id}
            
            while queue:
                current, path = queue.popleft()
                
                if current == target:
                    pipelines.append(path)
                    continue
                
                if len(path) > 5:  # Limit pipeline length
                    continue
                
                for next_tissue in graph.get(current, []):
                    if next_tissue not in visited:
                        visited.add(next_tissue)
                        queue.append((next_tissue, path + [next_tissue]))
        
        return pipelines[:5]  # Return top 5 pipelines


# Example usage and quality benchmarking
def create_tissue_quality_benchmark():
    """Create comprehensive quality benchmarks for all tissues"""
    
    analyzer = TissueQualityAnalyzer()
    results = {}
    
    # Define standard test cases for each domain
    cv_test_data = np.random.rand(100, 100, 3).astype(np.uint8)  # Sample image
    nlp_test_data = "This is a sample text for NLP processing." * 10
    ml_test_data = np.random.rand(1000, 20)  # Sample dataset
    
    # Example tissue metadata
    example_metadata = {
        "id": "CV-TISSUE-001",
        "version": "1.0.0",
        "author": "CodeSnippetBank",
        "last_updated": "2024-01-20",
        "description": "Edge detection using Sobel operator",
        "tags": ["cv", "edge-detection", "functional", "pure"],
        "dependencies": ["numpy>=1.24"]
    }
    
    # Placeholder for actual tissue function
    def example_tissue_func(data):
        # Simulate some processing
        return np.sum(data) / len(data)
    
    # Analyze tissue quality
    quality_score = analyzer.analyze_tissue(
        tissue_id="CV-TISSUE-001",
        tissue_func=example_tissue_func,
        test_cases=[cv_test_data],
        tissue_metadata=example_metadata
    )
    
    # Generate report
    report = analyzer.generate_quality_report("CV-TISSUE-001", quality_score)
    print(report)
    
    return quality_score


if __name__ == "__main__":
    # Run quality benchmark
    score = create_tissue_quality_benchmark()
    print(f"\nQuality Analysis Complete!")
    print(f"Overall Score: {score.overall_score:.1f}/100")
    print(f"Edge-Ready: {score.is_edge_ready()}")