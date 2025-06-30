# Contributing to CodeSnippetBank

Thank you for your interest in contributing to CodeSnippetBank! This guide will help you get started with contributing to the project.

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## 🚀 Getting Started

### Development Setup

1. **Fork the repository**
   ```bash
   # Click the 'Fork' button on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/CodeSnippetBank.git
   cd CodeSnippetBank
   ```

3. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   
   # Install in editable mode
   pip install -e .
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📋 Development Workflow

### 1. Make Your Changes

Follow these guidelines:
- Write clean, readable code
- Follow PEP 8 style guidelines
- Add type hints where appropriate
- Include docstrings for all public functions/classes
- Keep commits focused and atomic

### 2. Write Tests

All new features should include tests:

```python
# tests/test_your_feature.py
import pytest
from CodeSnippetBank.your_module import your_function

def test_your_function():
    result = your_function(input_data)
    assert result == expected_output

def test_edge_case():
    with pytest.raises(ValueError):
        your_function(invalid_input)
```

Run tests:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_your_feature.py

# Run with coverage
pytest --cov=CodeSnippetBank
```

### 3. Update Documentation

- Update relevant documentation in `docs/`
- Add docstrings to your code
- Update README.md if needed
- Add examples if introducing new features

### 4. Code Quality Checks

Before submitting:

```bash
# Format code with black
black CodeSnippetBank/

# Check style with flake8
flake8 CodeSnippetBank/

# Type checking with mypy
mypy CodeSnippetBank/

# Run all checks
make lint  # If Makefile is available
```

### 5. Submit Pull Request

1. Push your changes:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a Pull Request on GitHub

3. Fill out the PR template:
   - Describe what changes you made
   - Link any related issues
   - Include screenshots if relevant
   - List any breaking changes

## 🏗️ Project Structure

```
CodeSnippetBank/
├── core/                 # Core functionality
│   ├── models.py        # Data models
│   ├── storage.py       # Storage system
│   └── validator.py     # Validation logic
├── converters/          # Conversion modules
│   ├── text2snippet/    # Text to snippet conversion
│   └── code2snippet/    # Code to snippet conversion
├── tests/               # Test suite
│   ├── test_core/       # Core module tests
│   └── test_converters/ # Converter tests
├── docs/                # Documentation
└── examples/            # Example usage
```

## 📝 Contribution Types

### 🐛 Bug Reports

Create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)
- Minimal code example

### ✨ Feature Requests

Create an issue with:
- Clear description of the feature
- Use cases and benefits
- Potential implementation approach
- Any mockups or examples

### 📚 Documentation

Help improve docs by:
- Fixing typos and grammar
- Adding examples
- Clarifying confusing sections
- Translating documentation

### 🔧 Code Contributions

Areas where we need help:
- **Parsers**: Add support for new documentation formats
- **Analyzers**: Improve code analysis capabilities
- **Validators**: Add new validation rules
- **Categories**: Expand snippet categories
- **Tests**: Increase test coverage
- **Performance**: Optimize search and storage

## 🎯 Coding Standards

### Python Style

```python
# Good: Clear, documented function
def extract_code_blocks(text: str, language: str = "python") -> List[Dict[str, Any]]:
    """
    Extract code blocks from text.
    
    Args:
        text: The input text to parse
        language: Programming language to filter by
        
    Returns:
        List of dictionaries containing code blocks and metadata
    """
    blocks = []
    # Implementation...
    return blocks

# Bad: Unclear, undocumented
def get_blocks(t, l="python"):
    b = []
    # ...
    return b
```

### Commit Messages

Follow conventional commits:
```
feat: add RST parser for documentation
fix: handle empty code blocks in markdown parser
docs: update installation guide
test: add tests for snippet validation
refactor: simplify storage indexing logic
```

### Branch Naming

Use descriptive branch names:
- `feature/add-html-parser`
- `fix/validation-error-handling`
- `docs/improve-api-reference`
- `refactor/storage-optimization`

## 🧪 Testing Guidelines

### Test Structure

```python
class TestSnippetValidator:
    """Test suite for SnippetValidator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SnippetValidator()
        self.valid_snippet = create_test_snippet()
    
    def test_valid_snippet_passes(self):
        """Test that valid snippets pass validation."""
        is_valid, errors = self.validator.validate(self.valid_snippet)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_title_fails(self):
        """Test that snippets without title fail validation."""
        snippet = create_test_snippet(title="")
        is_valid, errors = self.validator.validate(snippet)
        assert not is_valid
        assert any(e.field == "metadata.title" for e in errors)
```

### Test Coverage

Aim for:
- Minimum 80% code coverage
- 100% coverage for critical paths
- Edge cases and error conditions
- Integration tests for converters

## 📦 Adding Dependencies

If you need to add a new dependency:

1. Ensure it's necessary and well-maintained
2. Add to `requirements.txt` or `requirements-dev.txt`
3. Document why it's needed in the PR
4. Consider optional dependencies for heavy packages

## 🚀 Release Process

Maintainers handle releases:

1. Update version in `__version__.py`
2. Update CHANGELOG.md
3. Create release PR
4. Tag release after merge
5. Deploy to PyPI

## 💡 Tips for Contributors

### First Time Contributors

- Start with "good first issue" labeled issues
- Read existing code to understand patterns
- Ask questions in issues or discussions
- Don't be afraid to submit small PRs

### Performance Considerations

- Profile code for performance bottlenecks
- Use generators for large datasets
- Cache expensive computations
- Consider async operations where beneficial

### Security

- Never commit secrets or API keys
- Validate all user inputs
- Use safe parsing methods
- Report security issues privately

## 🙏 Recognition

Contributors are recognized in:
- AUTHORS.md file
- Release notes
- Project documentation
- GitHub contributors page

## 📞 Getting Help

- 💬 [GitHub Discussions](https://github.com/yourusername/CodeSnippetBank/discussions)
- 🐛 [Issue Tracker](https://github.com/yourusername/CodeSnippetBank/issues)
- 📧 Email: codesnippetbank@example.com

---

**Thank you for contributing to CodeSnippetBank! Together we're building something amazing 🚀**