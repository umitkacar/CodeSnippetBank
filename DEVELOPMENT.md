# Development Environment Setup Guide

This guide will help you set up the modern Python development environment for CodeSnippetBank.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Development Tools](#development-tools)
- [Common Tasks](#common-tasks)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## Quick Start

```bash
# 1. Install development dependencies
make dev

# 2. Install pre-commit hooks
make pre-commit

# 3. Run all checks
make all
```

## Prerequisites

- Python 3.9 or higher
- pip (latest version recommended)
- git (for pre-commit hooks)

## Installation

### Option 1: Using Make (Recommended)

```bash
# Install all dependencies
make dev

# Or just production dependencies
make install
```

### Option 2: Using pip directly

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or install from requirements-dev.txt
pip install -r requirements-dev.txt
```

### Option 3: Using Hatch

```bash
# Install hatch
pip install hatch

# Create and use development environment
hatch shell
```

## Development Tools

### 1. Ruff - Modern Linter and Formatter

Ruff is a blazingly fast Python linter and formatter that replaces black, flake8, and isort.

```bash
# Lint code
make lint

# Auto-fix linting issues
make lint-fix

# Format code
make format

# Check formatting without changes
make format-check
```

**Configuration:** See `[tool.ruff]` section in `pyproject.toml`

### 2. Mypy - Static Type Checking

Mypy ensures type safety across the codebase with strict settings.

```bash
# Run type checking
make typecheck
```

**Configuration:** See `[tool.mypy]` section in `pyproject.toml`

### 3. Pytest - Testing Framework

Modern testing with coverage, async support, and parallel execution.

```bash
# Run all tests
make test

# Run fast tests only (exclude slow tests)
make test-fast

# Run specific test categories
make test-unit
make test-integration

# Run tests in parallel
make test-parallel

# Generate coverage report
make coverage

# Open HTML coverage report
make coverage-html
```

**Configuration:** See `pytest.ini` and `[tool.pytest.ini_options]` in `pyproject.toml`

### 4. Pre-commit Hooks

Automatically run checks before each commit.

```bash
# Install hooks
make pre-commit

# Run on all files manually
make pre-commit-run

# Update hooks to latest versions
make pre-commit-update
```

**Configuration:** See `.pre-commit-config.yaml`

## Common Tasks

### Before Committing

```bash
# Quick fix and verify
make verify
# This runs: format, lint-fix, typecheck, test-fast
```

### Full Quality Check

```bash
# Run all checks
make all
# This runs: format, lint, typecheck, test
```

### CI Pipeline Simulation

```bash
# Run CI checks (no auto-fix)
make ci
# This runs: format-check, lint, typecheck, coverage
```

### Code Quality Metrics

```bash
# Show code complexity
make complexity

# Find dead code
make dead-code

# Check documentation coverage
make doc-coverage
```

### Cleaning

```bash
# Clean cache files
make clean

# Deep clean (including virtual environments)
make clean-all
```

### Building and Distribution

```bash
# Build distribution packages
make build

# Build with hatch
make build-hatch

# Upload to TestPyPI
make upload-test

# Upload to PyPI
make upload
```

## Makefile Commands Reference

Run `make help` to see all available commands:

```bash
make help
```

### Essential Commands

| Command | Description |
|---------|-------------|
| `make install` | Install production dependencies |
| `make dev` | Install development dependencies |
| `make lint` | Run ruff linter |
| `make format` | Format code with ruff |
| `make typecheck` | Run mypy type checking |
| `make test` | Run pytest tests |
| `make coverage` | Run tests with coverage |
| `make all` | Run all checks |
| `make clean` | Clean cache files |
| `make help` | Show help message |

## Configuration Files

### pyproject.toml
Modern Python project configuration with:
- Project metadata and dependencies
- Hatch build system configuration
- Ruff linter and formatter settings
- Mypy strict type checking configuration
- Pytest and coverage settings
- Development dependencies

### .pre-commit-config.yaml
Git hooks configuration with:
- Ruff formatting and linting
- Mypy type checking
- Pytest test execution
- File and syntax checks
- Security scanning with Bandit
- Documentation checks with Pydocstyle

### pytest.ini
Pytest configuration with:
- Test discovery patterns
- Coverage settings
- Test markers (unit, integration, slow, etc.)
- Warning filters
- Async support

### .coveragerc
Coverage.py configuration with:
- Source paths and omit patterns
- Branch coverage
- Coverage thresholds (80% minimum)
- HTML/XML/JSON report settings

### requirements-dev.txt
Comprehensive development dependencies including:
- Code quality tools (ruff, mypy, bandit)
- Testing tools (pytest and plugins)
- Build tools (hatch, build, twine)
- Documentation tools (sphinx, mkdocs)
- Development utilities (ipython, jupyter, rich)

### Makefile
Common development commands for:
- Installing dependencies
- Running quality checks
- Testing and coverage
- Building and distribution
- Cleaning and utilities

## CI/CD Integration

### GitHub Actions Example

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: make dev
    - name: Run CI checks
      run: make ci
```

### GitLab CI Example

```yaml
test:
  image: python:3.9
  script:
    - make dev
    - make ci
  coverage: '/(?i)total.*? (100(?:\.0+)?\%|[1-9]?\d(?:\.\d+)?\%)$/'
```

## Best Practices

### Code Style
- Follow PEP 8 guidelines (enforced by Ruff)
- Use type hints for all functions (enforced by Mypy)
- Write docstrings in Google style
- Keep functions focused and under 50 lines
- Maximum cyclomatic complexity: 10

### Testing
- Write tests for all new features
- Maintain minimum 80% code coverage
- Use appropriate test markers (unit, integration, slow)
- Mock external dependencies
- Use parametrize for similar test cases

### Type Hints
- Add type hints to all function signatures
- Use `typing` module for complex types
- Avoid using `Any` type
- Enable strict mode in Mypy

### Documentation
- Write clear docstrings for all public functions
- Keep README.md up to date
- Document complex algorithms
- Add inline comments for non-obvious code

## Troubleshooting

### Pre-commit hooks failing

```bash
# Run hooks manually to see detailed errors
pre-commit run --all-files

# Skip hooks temporarily (not recommended)
git commit --no-verify
```

### Type checking errors

```bash
# Run mypy with verbose output
mypy . --show-error-codes --pretty

# Ignore specific errors (add to code)
# type: ignore[error-code]
```

### Tests failing

```bash
# Run tests with verbose output
pytest -vv --tb=long

# Run specific test
pytest tests/test_file.py::test_function -v

# Debug test with pdb
pytest --pdb
```

### Import errors

```bash
# Install package in editable mode
pip install -e .

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

## Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Hatch Documentation](https://hatch.pypa.io/)
- [Python Packaging User Guide](https://packaging.python.org/)

## Getting Help

- Check `make help` for available commands
- Review configuration files for detailed settings
- Run `make info` to see project information
- Consult tool-specific documentation for advanced usage

---

**Last Updated:** 2025-11-08
**Python Version:** 3.9+
**Tools:** Ruff, Mypy, Pytest, Pre-commit, Hatch
