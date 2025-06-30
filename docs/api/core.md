# Core API Reference

This document provides detailed API documentation for the core components of CodeSnippetBank.

## Table of Contents
- [Models](#models)
  - [CodeSnippet](#codesnippet)
  - [SnippetMetadata](#snippetmetadata)
  - [Category](#category)
  - [Enums](#enums)
- [Storage](#storage)
  - [SnippetStorage](#snippetstorage)
- [Validation](#validation)
  - [SnippetValidator](#snippetvalidator)
  - [ValidationError](#validationerror)

## Models

### CodeSnippet

The main data structure representing a reusable code snippet.

```python
from CodeSnippetBank.core.models import CodeSnippet, SnippetMetadata

class CodeSnippet:
    def __init__(self, 
                 metadata: SnippetMetadata,
                 description: str,
                 code: str,
                 example_usage: str,
                 tests: Optional[str] = None,
                 notes: Optional[str] = None)
```

#### Attributes

- **metadata** (`SnippetMetadata`): Complete metadata for the snippet
- **description** (`str`): Detailed description of what the snippet does
- **code** (`str`): The actual code implementation
- **example_usage** (`str`): Example showing how to use the snippet
- **tests** (`Optional[str]`): Unit tests for the snippet
- **notes** (`Optional[str]`): Additional notes or warnings

#### Methods

##### `to_file_content() -> str`
Convert snippet to the standard file format for storage.

```python
snippet = CodeSnippet(metadata, description, code, example)
content = snippet.to_file_content()
# Returns formatted string ready to save as .py file
```

##### `to_dict() -> Dict[str, Any]`
Convert snippet to dictionary representation.

```python
data = snippet.to_dict()
# Returns: {'metadata': {...}, 'description': '...', 'code': '...', ...}
```

##### `from_dict(data: Dict[str, Any]) -> CodeSnippet`
Create snippet from dictionary (class method).

```python
snippet = CodeSnippet.from_dict(data)
```

##### `get_imports() -> List[str]`
Extract import statements from the code.

```python
imports = snippet.get_imports()
# Returns: ['import numpy as np', 'from typing import List']
```

##### `estimate_lines_of_code() -> int`
Count non-empty, non-comment lines.

```python
loc = snippet.estimate_lines_of_code()
# Returns: 42
```

### SnippetMetadata

Comprehensive metadata for code snippets.

```python
from CodeSnippetBank.core.models import SnippetMetadata, SnippetDifficulty, SnippetType

@dataclass
class SnippetMetadata:
    snippet_id: str
    title: str
    category: str
    subcategory: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    difficulty: SnippetDifficulty = SnippetDifficulty.INTERMEDIATE
    snippet_type: SnippetType = SnippetType.FUNCTION
    dependencies: List[str] = field(default_factory=list)
    python_version: str = "3.8+"
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    performance_notes: Optional[str] = None
    author: str = "CodeSnippetBank"
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    use_cases: List[str] = field(default_factory=list)
    related_snippets: List[str] = field(default_factory=list)
    test_coverage: Optional[float] = None
    community_score: float = 0.0
    usage_count: int = 0
```

#### Key Attributes

- **snippet_id**: Unique identifier (auto-generated if empty)
- **title**: Human-readable title (max 100 chars)
- **category**: Primary category (e.g., "machine_learning/classification")
- **tags**: List of relevant tags for searching
- **difficulty**: Skill level required (BEGINNER, INTERMEDIATE, ADVANCED, EXPERT)
- **dependencies**: External packages required (e.g., ["numpy>=1.20", "pandas"])
- **complexity**: Time/space complexity in Big O notation

### Category

Represents a category in the snippet organization system.

```python
@dataclass
class Category:
    name: str
    path: str
    description: str
    parent: Optional[str] = None
    icon: Optional[str] = None
    snippet_count: int = 0
    subcategories: List[str] = field(default_factory=list)
```

#### Methods

##### `get_full_path() -> str`
Get complete path including parent categories.

```python
category = Category(name="Detection", path="detection", parent="computer_vision")
full_path = category.get_full_path()
# Returns: "computer_vision/detection"
```

### Enums

#### SnippetDifficulty

```python
class SnippetDifficulty(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
```

#### SnippetType

```python
class SnippetType(Enum):
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    SCRIPT = "script"
    CONFIGURATION = "configuration"
    TEMPLATE = "template"
```

## Storage

### SnippetStorage

File-based storage system for managing snippets.

```python
from CodeSnippetBank.core.storage import SnippetStorage

storage = SnippetStorage(base_path="snippets")
```

#### Methods

##### `save_snippet(snippet: CodeSnippet, force: bool = False) -> Tuple[bool, str]`
Save a snippet to storage.

```python
success, message = storage.save_snippet(snippet, force=True)
# Returns: (True, "Snippet CS-ML-a1b2c3d4 saved successfully")
```

**Parameters:**
- `snippet`: The snippet to save
- `force`: Overwrite if exists (default: False)

**Returns:**
- `Tuple[bool, str]`: Success status and message

##### `load_snippet(snippet_id: str) -> Optional[CodeSnippet]`
Load a snippet from storage.

```python
snippet = storage.load_snippet("CS-ML-a1b2c3d4")
if snippet:
    print(snippet.metadata.title)
```

##### `list_snippets(category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]`
List snippets with optional filtering.

```python
# List all snippets
all_snippets = storage.list_snippets()

# Filter by category
ml_snippets = storage.list_snippets(category="machine_learning")

# Filter by tags
async_snippets = storage.list_snippets(tags=["async", "api"])
```

##### `search_snippets(query: str, limit: int = 10) -> List[Dict[str, Any]]`
Search snippets by text query.

```python
results = storage.search_snippets("face detection opencv", limit=5)
for result in results:
    print(f"{result['title']} - Score: {result['score']}")
```

**Search considers:**
- Title (weight: 10)
- Description (weight: 5)
- Tags (weight: 3)
- Category (weight: 2)

##### `delete_snippet(snippet_id: str) -> Tuple[bool, str]`
Delete a snippet (with version backup).

```python
success, message = storage.delete_snippet("CS-ML-a1b2c3d4")
```

##### `get_stats() -> Dict[str, Any]`
Get storage statistics.

```python
stats = storage.get_stats()
print(f"Total snippets: {stats['total_snippets']}")
print(f"Total LOC: {stats['total_lines_of_code']}")
print(f"Categories: {stats['category_distribution']}")
```

**Returns:**
```python
{
    "total_snippets": 150,
    "total_lines_of_code": 5420,
    "average_loc_per_snippet": 36.13,
    "category_distribution": {
        "machine_learning": 45,
        "computer_vision": 38,
        ...
    },
    "difficulty_distribution": {
        "beginner": 30,
        "intermediate": 80,
        ...
    },
    "total_categories": 13,
    "snippets_with_tests": 120
}
```

## Validation

### SnippetValidator

Comprehensive validation for code snippets.

```python
from CodeSnippetBank.core.validator import SnippetValidator

validator = SnippetValidator()
```

#### Configuration

```python
validator.required_metadata_fields = ["snippet_id", "title", "category", ...]
validator.min_description_length = 50
validator.max_title_length = 100
validator.min_tags = 2
validator.max_tags = 10
```

#### Methods

##### `validate(snippet: CodeSnippet) -> Tuple[bool, List[ValidationError]]`
Validate a snippet comprehensively.

```python
is_valid, errors = validator.validate(snippet)
if not is_valid:
    for error in errors:
        print(f"{error.severity}: {error.field} - {error.message}")
```

**Validation checks:**
1. Metadata completeness
2. Code syntax (Python AST)
3. Documentation quality
4. Security patterns
5. Code quality patterns
6. Test validity

##### `validate_batch(snippets: List[CodeSnippet]) -> Dict[str, Any]`
Validate multiple snippets and get summary.

```python
results = validator.validate_batch(snippets)
print(f"Valid: {results['valid']}/{results['total']}")
print(f"Common errors: {results['errors_by_type']}")
```

##### `suggest_improvements(snippet: CodeSnippet) -> List[str]`
Get improvement suggestions for a snippet.

```python
suggestions = validator.suggest_improvements(snippet)
# Returns: ["Add unit tests", "Document time complexity", ...]
```

### ValidationError

Represents a validation error with details.

```python
class ValidationError:
    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # "error", "warning", "info"
```

#### Severity Levels

- **error**: Must be fixed (prevents saving)
- **warning**: Should be fixed (quality issue)
- **info**: Nice to have (suggestion)

## Usage Examples

### Complete Example: Create and Save Snippet

```python
from CodeSnippetBank.core import CodeSnippet, SnippetMetadata, SnippetStorage
from CodeSnippetBank.core.models import SnippetDifficulty, SnippetType

# Create metadata
metadata = SnippetMetadata(
    snippet_id="",  # Auto-generated
    title="Binary Search Implementation",
    category="algorithms/searching",
    tags=["search", "binary-search", "algorithms"],
    difficulty=SnippetDifficulty.INTERMEDIATE,
    snippet_type=SnippetType.FUNCTION,
    dependencies=[],
    time_complexity="O(log n)",
    space_complexity="O(1)",
    use_cases=[
        "Searching in sorted arrays",
        "Finding insertion position",
        "Range queries"
    ]
)

# Create snippet
snippet = CodeSnippet(
    metadata=metadata,
    description="Efficient binary search implementation with proper edge case handling.",
    code='''def binary_search(arr: List[int], target: int) -> int:
    """
    Perform binary search on a sorted array.
    
    Returns:
        Index of target if found, -1 otherwise.
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1''',
    example_usage='''arr = [1, 3, 5, 7, 9, 11, 13]
    index = binary_search(arr, 7)
    print(f"Found at index: {index}")  # Output: 3''',
    tests='''def test_binary_search():
    assert binary_search([1, 3, 5, 7, 9], 5) == 2
    assert binary_search([1, 3, 5, 7, 9], 10) == -1
    assert binary_search([], 5) == -1
    assert binary_search([5], 5) == 0'''
)

# Save to storage
storage = SnippetStorage()
success, message = storage.save_snippet(snippet)
print(message)
```

### Search and Load Example

```python
# Search for snippets
results = storage.search_snippets("binary search")

# Load the first result
if results:
    snippet_id = results[0]['snippet_id']
    snippet = storage.load_snippet(snippet_id)
    
    # Use the snippet
    print(f"Title: {snippet.metadata.title}")
    print(f"Category: {snippet.metadata.category}")
    print(f"Code:\n{snippet.code}")
```

## Best Practices

1. **Always validate** snippets before saving
2. **Use meaningful titles** that describe the solution
3. **Include comprehensive metadata** for better discoverability
4. **Provide clear examples** in the example_usage field
5. **Add tests** whenever possible
6. **Document complexity** for algorithm implementations
7. **Tag appropriately** using consistent naming conventions

---

*For more examples and advanced usage, see the [User Guides](../guides/)*