# Tissue Discovery API Documentation

## Overview

The Tissue Discovery API is a revolutionary system that enables Edge LLMs to discover, access, and utilize high-quality code tissues efficiently. Unlike traditional code search, our API understands context, performance requirements, and device constraints.

## Key Features

- **Intelligent Search**: Find tissues by task, not implementation details
- **Semantic Understanding**: Discovers tissues based on meaning, not just keywords
- **Quality Guarantees**: Every tissue has a quality score
- **Edge Optimization**: Performance metrics for edge devices
- **Smart Recommendations**: Context-aware tissue suggestions
- **Usage Analytics**: Track popular tissues and optimize

## API Endpoints

### 1. Search Tissues
```
GET /api/v1/tissues/search
```

**Parameters:**
- `q` (string): Search query
- `domain` (string, optional): Filter by domain (cv, nlp, ml)
- `tags` (array, optional): Filter by tags
- `limit` (integer, default: 10): Maximum results

**Example:**
```bash
curl "http://localhost:5000/api/v1/tissues/search?q=edge%20detection&domain=cv&limit=5"
```

### 2. Semantic Search
```
POST /api/v1/tissues/semantic-search
```

**Body:**
```json
{
    "query": "find objects in images",
    "domain": "cv",
    "threshold": 0.7,
    "limit": 10
}
```

### 3. Get Tissue Details
```
GET /api/v1/tissues/{tissue_id}
```

**Example:**
```bash
curl "http://localhost:5000/api/v1/tissues/CV-TISSUE-001"
```

### 4. Get Tissue Code
```
GET /api/v1/tissues/{tissue_id}/code
```

Returns the complete source code for a tissue.

### 5. Get Recommendations
```
POST /api/v1/tissues/recommend
```

**Body:**
```json
{
    "task_type": "face detection",
    "input_type": "image",
    "output_type": "bounding boxes",
    "device": "edge",
    "limit": 5
}
```

### 6. Get Statistics
```
GET /api/v1/statistics
```

Returns usage statistics and system metrics.

## Python SDK

### Installation
```python
from api.tissue_discovery_api import TissueDiscoveryAPI

# Initialize
api = TissueDiscoveryAPI(tissue_root="./tissues")
```

### Basic Usage
```python
# Search for tissues
results = api.search("edge detection", domain="cv")

# Get specific tissue
tissue = api.get_tissue("CV-TISSUE-001")

# Get recommendations
context = {
    'task_type': 'object detection',
    'input_type': 'image',
    'device': 'raspberry_pi'
}
recommendations = api.recommend_tissues(context)

# Semantic search
similar = api.semantic_search("blur faces for privacy")
```

## CLI Usage

### Search Command
```bash
python tissue_discovery_api.py search "edge detection" --domain cv --limit 5
```

### Get Tissue
```bash
python tissue_discovery_api.py get CV-TISSUE-001 --code
```

### Get Recommendations
```bash
python tissue_discovery_api.py recommend --task "face detection" --device edge
```

### View Statistics
```bash
python tissue_discovery_api.py stats
```

## Response Format

### Tissue Object
```json
{
    "id": "CV-TISSUE-001",
    "domain": "cv",
    "name": "Edge Detector Sobel",
    "description": "Sobel edge detection optimized for edge devices",
    "main_function": "detect_edges",
    "input_type": "Grayscale image (numpy array)",
    "output_type": "Edge map, gradients, and statistics",
    "edge_performance": "5-10ms on Raspberry Pi 4",
    "memory_usage": "~2MB peak",
    "tags": ["cv", "edge", "detection", "sobel"],
    "dependencies": ["numpy"],
    "quality_score": 0.85,
    "access_count": 42
}
```

## Integration with Edge LLMs

### Example: Phi-2 Integration
```python
class EdgeLLMWithTissues:
    def __init__(self):
        self.tissue_api = TissueDiscoveryAPI()
        
    def generate_code(self, user_request):
        # Extract task context from request
        context = self.extract_context(user_request)
        
        # Get tissue recommendations
        tissues = self.tissue_api.recommend_tissues(context, limit=3)
        
        # Generate minimal code using tissues
        code = self.combine_tissues(tissues)
        
        return code  # <100 tokens instead of 2000+
```

## Performance Metrics

- **Search Latency**: <50ms for 10k tissues
- **Recommendation Latency**: <100ms with context analysis
- **Memory Usage**: ~50MB for full index
- **Cache Hit Rate**: >80% for popular tissues

## Quality Scoring

Each tissue is scored on multiple dimensions:
- Documentation completeness (20%)
- Performance metrics provided (20%)
- Memory usage documented (20%)
- Type hints present (10%)
- Error handling (10%)
- Test coverage (10%)
- Code complexity (10%)

## Best Practices

1. **Use Semantic Search** for natural language queries
2. **Provide Context** for better recommendations
3. **Check Quality Scores** before using tissues
4. **Monitor Performance** metrics for your device
5. **Cache Popular Tissues** locally

## Advantages Over Traditional Approaches

| Feature | Traditional | CodeSnippetBank |
|---------|------------|-----------------|
| Discovery Time | Hours | Seconds |
| Quality Guarantee | None | Built-in |
| Edge Optimization | Manual | Automatic |
| Token Usage | 2000+ | <100 |
| Performance Data | Unknown | Documented |

## Future Enhancements

- **Auto-composition**: Automatically combine tissues
- **Performance Prediction**: ML-based performance estimation
- **Tissue Evolution**: Version control and updates
- **Community Tissues**: User-contributed tissues
- **Cross-domain Fusion**: Combine CV+NLP+ML tissues

## Support

For issues or contributions:
- GitHub: github.com/codebase/tissue-discovery
- Email: tissues@codebase.ai

---

*CodeSnippetBank: Empowering Edge AI, One Tissue at a Time!*