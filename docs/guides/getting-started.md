# Getting Started with CodeSnippetBank

Welcome to CodeSnippetBank! This guide will help you get up and running quickly.

## 📋 Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)
- Basic knowledge of Python programming

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/CodeSnippetBank.git
cd CodeSnippetBank
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "from CodeSnippetBank.core import CodeSnippet; print('✅ Installation successful!')"
```

## 🎯 Quick Start

### Your First Snippet Extraction

Let's extract code snippets from a markdown file:

```python
from CodeSnippetBank.converters import Text2CodeSnippet
from CodeSnippetBank.core import SnippetStorage

# Initialize converter
converter = Text2CodeSnippet(validate=True, auto_improve=True)

# Create sample markdown content
markdown_content = """
# Array Utilities

Here's a useful function to find duplicates in an array:

```python
def find_duplicates(arr):
    seen = set()
    duplicates = set()
    
    for item in arr:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    
    return list(duplicates)
```

This function efficiently finds all duplicate elements using sets.
"""

# Convert to snippets
snippets = converter.convert_text(markdown_content, format_type='markdown')

# Save snippets
storage = SnippetStorage()
for snippet in snippets:
    success, message = storage.save_snippet(snippet)
    print(f"✅ Saved: {snippet.metadata.title}")
```

### Search and Use Snippets

```python
# Search for array-related snippets
results = storage.search_snippets("array duplicates")

# Load and use the first result
if results:
    snippet = storage.load_snippet(results[0]['snippet_id'])
    
    # Display snippet information
    print(f"Title: {snippet.metadata.title}")
    print(f"Category: {snippet.metadata.category}")
    print(f"Tags: {', '.join(snippet.metadata.tags)}")
    print(f"\nCode:")
    print(snippet.code)
    print(f"\nExample:")
    print(snippet.example_usage)
```

## 📚 Basic Operations

### 1. Extract from Documentation Files

```python
# Extract from a markdown file
snippets = converter.convert_file("docs/tutorial.md")

# Extract from multiple files
import glob
for file_path in glob.glob("docs/*.md"):
    snippets = converter.convert_file(file_path)
    for snippet in snippets:
        storage.save_snippet(snippet)
```

### 2. Browse Available Snippets

```python
# List all snippets
all_snippets = storage.list_snippets()
for snippet_info in all_snippets:
    print(f"- {snippet_info['title']} ({snippet_info['category']})")

# List by category
ml_snippets = storage.list_snippets(category="machine_learning")

# List by tags
async_snippets = storage.list_snippets(tags=["async", "concurrent"])
```

### 3. Create Snippets Manually

```python
from CodeSnippetBank.core import CodeSnippet, SnippetMetadata
from CodeSnippetBank.core.models import SnippetDifficulty

# Create metadata
metadata = SnippetMetadata(
    snippet_id="",  # Auto-generated
    title="URL Validator",
    category="utilities/validation",
    tags=["url", "validation", "regex"],
    difficulty=SnippetDifficulty.BEGINNER,
    dependencies=[]
)

# Create snippet
snippet = CodeSnippet(
    metadata=metadata,
    description="Validate URLs using regular expressions.",
    code='''import re

def is_valid_url(url):
    """Check if a string is a valid URL."""
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return pattern.match(url) is not None''',
    example_usage='''print(is_valid_url("https://example.com"))  # True
print(is_valid_url("not a url"))  # False'''
)

# Save it
storage.save_snippet(snippet)
```

## 🔍 Understanding the Output

### Snippet Structure

Each snippet contains:
- **Metadata**: ID, title, category, tags, difficulty
- **Code**: The actual implementation
- **Description**: What the snippet does
- **Example**: How to use it
- **Tests**: Optional unit tests

### File Organization

Snippets are stored in:
```
snippets/
├── _index.json              # Search index
├── _categories.json         # Category definitions
├── computer_vision/
│   ├── detection/
│   │   └── CS-CV-12345_face_detection.py
│   └── segmentation/
├── machine_learning/
│   ├── classification/
│   └── preprocessing/
└── utilities/
```

## 🛠️ Configuration

### Converter Settings

```python
# Create converter with custom settings
converter = Text2CodeSnippet(
    validate=True,      # Enable validation
    auto_improve=True   # Automatically improve code
)

# Access converter statistics
stats = converter.get_stats()
print(f"Files processed: {stats['files_processed']}")
print(f"Snippets extracted: {stats['snippets_extracted']}")
```

### Storage Settings

```python
# Use custom storage location
storage = SnippetStorage(base_path="my_snippets")

# Get storage statistics
stats = storage.get_stats()
print(f"Total snippets: {stats['total_snippets']}")
print(f"Total lines of code: {stats['total_lines_of_code']}")
```

## 📝 Next Steps

Now that you have the basics down, explore:

1. **[Using Converters](converters.md)** - Advanced extraction techniques
2. **[Storage System](storage.md)** - Managing your snippet library
3. **[Search Guide](search.md)** - Finding snippets effectively
4. **[API Reference](../api/core.md)** - Detailed API documentation

## 🤔 Common Issues

### Import Errors

If you see import errors:
```bash
# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Permission Errors

If you can't save snippets:
```bash
# Ensure write permissions
chmod -R u+w snippets/
```

### Validation Failures

If snippets fail validation:
```python
# Check validation errors
is_valid, errors = validator.validate(snippet)
for error in errors:
    print(f"{error.severity}: {error.message}")
```

## 🆘 Getting Help

- Check the [FAQ](faq.md)
- Browse [Examples](../examples/)
- Open an [issue](https://github.com/yourusername/CodeSnippetBank/issues)
- Join [discussions](https://github.com/yourusername/CodeSnippetBank/discussions)

---

**Ready to transform your code into reusable snippets? Let's go! 🚀**