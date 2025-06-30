# Tissue Creation Guide

## 🧬 Creating High-Quality Tissues for CodeSnippetBank

This guide will help you create production-ready tissues that meet our quality standards and work seamlessly on edge devices.

## 📋 Tissue Anatomy

Every tissue must follow this structure:

```python
"""
DOMAIN-TISSUE-XXX: Tissue Name
Brief description of what this tissue does
"""

import minimal_dependencies_only
from typing import Dict, Any, Optional

class TissueNameProcessor:  # Optional class wrapper
    def __init__(self, edge_optimized: bool = True):
        """Initialize with edge optimization"""
        pass

def main_tissue_function(input_data: Any, **kwargs) -> Dict[str, Any]:
    """
    Main tissue function - single entry point
    
    Args:
        input_data: Primary input (type varies by tissue)
        **kwargs: Optional parameters with defaults
        
    Returns:
        Dictionary containing:
        - result: Primary output
        - metadata: Performance/quality metrics
        - optional: Additional outputs
        
    Tissue Metadata:
        - Input: Clear input description
        - Output: Clear output description  
        - Edge Performance: Measured performance on edge devices
        - Memory: Peak memory usage
    """
    # Implementation
    result = process(input_data)
    
    return {
        'result': result,
        'performance': {'time_ms': 5.2},
        'metadata': {'version': '1.0.0'}
    }

# Test section
if __name__ == "__main__":
    # Include basic tests
    test_input = create_test_data()
    result = main_tissue_function(test_input)
    assert validate_result(result)
    print(f"Tissue test passed: {result}")
```

## 🎯 Quality Standards

### 1. Single Responsibility
Each tissue should do ONE thing well:
- ❌ `process_image_complete()` - Too broad
- ✅ `detect_edges_sobel()` - Focused

### 2. Edge-First Design
```python
# ❌ Bad: Heavy dependencies
import tensorflow as tf
import torch
import cv2

# ✅ Good: Minimal dependencies  
import numpy as np  # If absolutely necessary
# Better: Pure Python when possible
```

### 3. Clear Input/Output Contract
```python
def detect_faces(image: np.ndarray) -> Dict[str, Any]:
    """
    Detect faces in image
    
    Args:
        image: Grayscale or RGB numpy array (H, W) or (H, W, 3)
        
    Returns:
        {
            'faces': List of face dictionaries with:
                - 'bbox': [x, y, width, height]
                - 'confidence': float (0-1)
                - 'landmarks': optional facial landmarks
            'count': Number of faces detected
            'processing_time': Time in milliseconds
        }
    """
```

### 4. Performance Documentation
Always include measured performance:
```python
"""
Tissue Metadata:
    - Input: Grayscale image (numpy array)
    - Output: Edge map and gradients
    - Edge Performance: 
        - ESP32: 25ms for 320x240
        - RPi Zero: 8ms for 320x240
        - RPi 4: 2ms for 640x480
        - Mobile: 1ms for 1920x1080
    - Memory: ~2MB peak for 640x480
"""
```

### 5. Error Handling
```python
def process_text(text: str) -> Dict[str, Any]:
    # Input validation
    if not isinstance(text, str):
        return {
            'error': 'Input must be string',
            'result': None
        }
    
    if len(text) == 0:
        return {
            'result': [],
            'warning': 'Empty input'
        }
    
    try:
        result = actual_processing(text)
        return {'result': result, 'status': 'success'}
    except Exception as e:
        return {
            'error': str(e),
            'result': None,
            'status': 'failed'
        }
```

## 🔧 Implementation Guidelines

### 1. Memory Efficiency
```python
# ❌ Bad: Loading everything into memory
def process_all(data_list):
    results = []
    for item in data_list:
        results.append(heavy_process(item))
    return results

# ✅ Good: Generator for memory efficiency
def process_stream(data_list):
    for item in data_list:
        yield heavy_process(item)
```

### 2. Edge Device Optimizations
```python
# Adaptive quality based on device
def detect_features(image, device_profile='edge'):
    if device_profile == 'esp32':
        # Ultra-light processing
        scale = 0.25
        max_features = 10
    elif device_profile == 'raspberry_pi':
        scale = 0.5
        max_features = 50
    else:
        scale = 1.0
        max_features = 100
```

### 3. Pure Python When Possible
```python
# ✅ Prefer pure Python for maximum compatibility
def calculate_mean(values):
    return sum(values) / len(values) if values else 0

# Use numpy only when significant performance gain
def matrix_multiply(a, b):
    # For large matrices, numpy is worth it
    if len(a) > 100:
        import numpy as np
        return np.dot(a, b)
    else:
        # Small matrices: pure Python
        return [[sum(a[i][k] * b[k][j] for k in range(len(b))) 
                for j in range(len(b[0]))] for i in range(len(a))]
```

## 📏 Testing Requirements

### 1. Basic Functionality Test
```python
def test_basic_functionality():
    """Test core tissue functionality"""
    # Arrange
    test_input = create_minimal_test_case()
    
    # Act
    result = tissue_function(test_input)
    
    # Assert
    assert 'result' in result
    assert result['result'] is not None
    assert 'error' not in result
```

### 2. Edge Case Testing
```python
def test_edge_cases():
    """Test boundary conditions"""
    # Empty input
    assert tissue_function([])['result'] == []
    
    # Single element
    assert tissue_function([1])['result'] is not None
    
    # Large input
    large_input = list(range(10000))
    result = tissue_function(large_input)
    assert result['status'] == 'success'
```

### 3. Performance Testing
```python
def test_performance():
    """Verify performance claims"""
    import time
    
    test_input = create_standard_test_input()
    
    start = time.time()
    result = tissue_function(test_input)
    duration = (time.time() - start) * 1000
    
    # Should complete within documented time
    assert duration < 50  # ms
    assert 'processing_time' in result
```

## 🏷️ Metadata Standards

### Required Metadata Fields
```python
TISSUE_METADATA = {
    'id': 'CV-TISSUE-001',
    'name': 'Edge Detector Sobel',
    'domain': 'cv',
    'category': 'edge_detection',
    'tags': ['edge', 'detection', 'sobel', 'gradient'],
    'difficulty': 'beginner',
    'dependencies': ['numpy'],  # Minimal!
    'python_version': '>=3.6',
    'tissue_version': '1.0.0'
}
```

### Performance Metadata
```python
PERFORMANCE_METADATA = {
    'time_complexity': 'O(n*m)',  # n=height, m=width
    'space_complexity': 'O(n*m)',
    'measured_performance': {
        'esp32': {'320x240': '25ms', 'memory': '150KB'},
        'rpi_zero': {'320x240': '8ms', 'memory': '2MB'},
        'rpi_4': {'640x480': '2ms', 'memory': '5MB'},
        'mobile': {'1920x1080': '1ms', 'memory': '20MB'}
    }
}
```

## 🚀 Optimization Techniques

### 1. Algorithmic Optimization
```python
# ❌ Naive approach
def find_max_naive(data):
    max_val = data[0]
    for i in range(len(data)):
        for j in range(i+1, len(data)):
            if data[j] > max_val:
                max_val = data[j]
    return max_val  # O(n²)

# ✅ Optimized
def find_max_optimized(data):
    return max(data) if data else None  # O(n)
```

### 2. Memory Optimization
```python
# ❌ Memory hungry
def process_large_data(data):
    processed = []
    for item in data:
        processed.append(transform(item))
    return processed

# ✅ Memory efficient
def process_large_data_efficient(data):
    for i in range(len(data)):
        data[i] = transform(data[i])  # In-place
    return data
```

### 3. Edge-Specific Optimizations
```python
def adaptive_processing(data, available_memory_mb):
    """Adapt algorithm based on available resources"""
    
    if available_memory_mb < 1:  # ESP32
        # Ultra-light processing
        chunk_size = 100
        method = 'simple'
    elif available_memory_mb < 100:  # RPi Zero
        chunk_size = 1000
        method = 'standard'
    else:  # Desktop/Server
        chunk_size = 10000
        method = 'advanced'
    
    return process_in_chunks(data, chunk_size, method)
```

## 📝 Documentation Template

```python
"""
CV-TISSUE-XXX: Your Tissue Name
=================================

Brief description of what this tissue accomplishes.

## Purpose
Explain the specific problem this tissue solves.

## Algorithm
Brief explanation of the approach used.

## Usage Example
```python
result = your_tissue_function(input_data, param1=value1)
print(result['output'])
```

## Performance Characteristics
- Time Complexity: O(n)
- Space Complexity: O(1)
- Edge Device Performance:
  - ESP32: 10ms for typical input
  - RPi: 2ms for typical input

## Limitations
- Maximum input size: 1000 elements
- Requires sorted input
- English language only (for NLP)

## Version History
- 1.0.0: Initial release
- 1.1.0: Added edge optimization
- 1.2.0: Improved memory efficiency
"""
```

## ✅ Quality Checklist

Before submitting your tissue, ensure:

- [ ] Single, clear purpose
- [ ] Minimal dependencies
- [ ] Type hints on all functions
- [ ] Comprehensive docstrings
- [ ] Error handling
- [ ] Performance measurements
- [ ] Memory usage documented
- [ ] Edge device tested
- [ ] Basic tests included
- [ ] Example usage provided
- [ ] Metadata complete
- [ ] Code follows style guide
- [ ] No security vulnerabilities
- [ ] No hardcoded paths/credentials
- [ ] Python 3.6+ compatible

## 🎨 Style Guide

1. **Naming**: Use descriptive names
   - Functions: `verb_noun()` (e.g., `detect_edges()`)
   - Classes: `NounProcessor` (e.g., `EdgeProcessor`)
   - Variables: `descriptive_name` (e.g., `edge_threshold`)

2. **Line Length**: Max 88 characters (Black formatter)

3. **Imports**: Group and sort
   ```python
   # Standard library
   import json
   import time
   
   # Third party (minimal!)
   import numpy as np
   
   # Type hints
   from typing import Dict, List, Optional
   ```

4. **Comments**: Explain why, not what
   ```python
   # ❌ Bad
   x = x + 1  # Increment x
   
   # ✅ Good  
   x = x + 1  # Compensate for 0-based indexing in user display
   ```

## 🚫 Common Pitfalls

1. **Over-engineering**: Keep it simple
2. **Heavy dependencies**: Avoid large libraries
3. **Missing edge cases**: Test thoroughly
4. **Poor error messages**: Be helpful
5. **No performance data**: Measure everything
6. **Unclear I/O**: Document precisely
7. **Memory leaks**: Clean up resources
8. **Blocking operations**: Use async when appropriate

## 🌟 Example: High-Quality Tissue

See `CV-TISSUE-001_edge_detector_sobel.py` for a reference implementation that meets all quality standards.

---

*Remember: Every tissue should be a joy to use and work flawlessly on edge devices!* 🚀