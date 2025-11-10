# =============================================================================
# Makefile for CodeSnippetBank - Modern Python Development
# =============================================================================
# Make commands for linting, formatting, testing, and more
#
# Usage:
#   make install    - Install all dependencies
#   make dev        - Install development dependencies
#   make lint       - Run ruff linter
#   make format     - Format code with ruff
#   make typecheck  - Run mypy type checking
#   make test       - Run pytest tests
#   make coverage   - Run tests with coverage report
#   make all        - Run all checks (format, lint, typecheck, test)
#   make clean      - Clean cache files and build artifacts
#   make help       - Show this help message

.PHONY: help install dev lint format typecheck test coverage all clean pre-commit build upload docs serve

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
MAGENTA := \033[0;35m
CYAN := \033[0;36m
NC := \033[0m # No Color

# Python interpreter
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
RUFF := $(PYTHON) -m ruff
MYPY := $(PYTHON) -m mypy
HATCH := hatch

# Project directories
SRC_DIRS := ai api converters core demos framework marketing research scripts snippets tissues tools
TEST_DIR := tests
DOCS_DIR := docs

# =============================================================================
# Help
# =============================================================================

help: ## Show this help message
	@echo "$(CYAN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║$(NC) $(MAGENTA)CodeSnippetBank - Modern Python Development$(NC)                $(CYAN)║$(NC)"
	@echo "$(CYAN)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Available commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)Examples:$(NC)"
	@echo "  make install      # Install all dependencies"
	@echo "  make format       # Format code"
	@echo "  make test         # Run tests"
	@echo "  make all          # Run all quality checks"
	@echo ""

# =============================================================================
# Installation
# =============================================================================

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e .
	@echo "$(GREEN)✓ Production dependencies installed$(NC)"

dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e ".[dev]"
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

install-all: dev ## Install all dependencies (production + development)
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

# =============================================================================
# Code Quality
# =============================================================================

lint: ## Run ruff linter
	@echo "$(BLUE)Running ruff linter...$(NC)"
	$(RUFF) check . --show-source --show-fixes
	@echo "$(GREEN)✓ Linting complete$(NC)"

lint-fix: ## Run ruff linter with auto-fix
	@echo "$(BLUE)Running ruff linter with auto-fix...$(NC)"
	$(RUFF) check . --fix --show-fixes
	@echo "$(GREEN)✓ Linting with fixes complete$(NC)"

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code with ruff...$(NC)"
	$(RUFF) format .
	@echo "$(GREEN)✓ Code formatting complete$(NC)"

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code format...$(NC)"
	$(RUFF) format . --check
	@echo "$(GREEN)✓ Format check complete$(NC)"

typecheck: ## Run mypy type checking
	@echo "$(BLUE)Running mypy type checking...$(NC)"
	$(MYPY) .
	@echo "$(GREEN)✓ Type checking complete$(NC)"

# =============================================================================
# Testing
# =============================================================================

test: ## Run pytest tests
	@echo "$(BLUE)Running tests...$(NC)"
	$(PYTEST) $(TEST_DIR) -v --tb=short
	@echo "$(GREEN)✓ Tests complete$(NC)"

test-fast: ## Run fast tests only (exclude slow tests)
	@echo "$(BLUE)Running fast tests...$(NC)"
	$(PYTEST) $(TEST_DIR) -v -m "not slow" --tb=short
	@echo "$(GREEN)✓ Fast tests complete$(NC)"

test-slow: ## Run slow tests only
	@echo "$(BLUE)Running slow tests...$(NC)"
	$(PYTEST) $(TEST_DIR) -v -m "slow" --tb=short
	@echo "$(GREEN)✓ Slow tests complete$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(PYTEST) $(TEST_DIR) -v -m "unit" --tb=short
	@echo "$(GREEN)✓ Unit tests complete$(NC)"

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(PYTEST) $(TEST_DIR) -v -m "integration" --tb=short
	@echo "$(GREEN)✓ Integration tests complete$(NC)"

test-parallel: ## Run tests in parallel
	@echo "$(BLUE)Running tests in parallel...$(NC)"
	$(PYTEST) $(TEST_DIR) -v -n auto --tb=short
	@echo "$(GREEN)✓ Parallel tests complete$(NC)"

coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTEST) $(TEST_DIR) --cov=. --cov-report=term-missing --cov-report=html --cov-report=xml
	@echo "$(GREEN)✓ Coverage report generated$(NC)"
	@echo "$(YELLOW)View HTML report: htmlcov/index.html$(NC)"

coverage-html: coverage ## Run coverage and open HTML report
	@echo "$(BLUE)Opening coverage report...$(NC)"
	@$(PYTHON) -c "import webbrowser; webbrowser.open('htmlcov/index.html')"

# =============================================================================
# Pre-commit Hooks
# =============================================================================

pre-commit: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "$(GREEN)✓ Pre-commit hooks installed$(NC)"

pre-commit-run: ## Run pre-commit on all files
	@echo "$(BLUE)Running pre-commit on all files...$(NC)"
	pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit checks complete$(NC)"

pre-commit-update: ## Update pre-commit hooks
	@echo "$(BLUE)Updating pre-commit hooks...$(NC)"
	pre-commit autoupdate
	@echo "$(GREEN)✓ Pre-commit hooks updated$(NC)"

# =============================================================================
# Combined Targets
# =============================================================================

check: format-check lint typecheck ## Run format check, lint, and typecheck (no tests)
	@echo "$(GREEN)✓ All checks passed$(NC)"

all: format lint typecheck test ## Run all checks (format, lint, typecheck, test)
	@echo "$(GREEN)✓ All checks and tests passed$(NC)"

ci: format-check lint typecheck coverage ## Run CI pipeline (no auto-fix)
	@echo "$(GREEN)✓ CI pipeline complete$(NC)"

# =============================================================================
# Build and Distribution
# =============================================================================

build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)✓ Build complete$(NC)"

build-hatch: clean ## Build with hatch
	@echo "$(BLUE)Building with hatch...$(NC)"
	$(HATCH) build
	@echo "$(GREEN)✓ Hatch build complete$(NC)"

upload: build ## Upload to PyPI (requires credentials)
	@echo "$(BLUE)Uploading to PyPI...$(NC)"
	$(PYTHON) -m twine upload dist/*
	@echo "$(GREEN)✓ Upload complete$(NC)"

upload-test: build ## Upload to TestPyPI
	@echo "$(BLUE)Uploading to TestPyPI...$(NC)"
	$(PYTHON) -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)✓ Upload to TestPyPI complete$(NC)"

# =============================================================================
# Documentation
# =============================================================================

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@if [ -d "$(DOCS_DIR)" ]; then \
		cd $(DOCS_DIR) && make html; \
		echo "$(GREEN)✓ Documentation generated$(NC)"; \
	else \
		echo "$(YELLOW)! Documentation directory not found$(NC)"; \
	fi

docs-serve: docs ## Build and serve documentation
	@echo "$(BLUE)Serving documentation...$(NC)"
	@if [ -d "$(DOCS_DIR)" ]; then \
		cd $(DOCS_DIR) && $(PYTHON) -m http.server 8000; \
	else \
		echo "$(YELLOW)! Documentation directory not found$(NC)"; \
	fi

# =============================================================================
# Cleaning
# =============================================================================

clean: ## Clean cache files and build artifacts
	@echo "$(BLUE)Cleaning cache files and build artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build dist htmlcov .coverage coverage.xml
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: clean ## Deep clean including virtual environments
	@echo "$(BLUE)Deep cleaning...$(NC)"
	rm -rf .venv venv env
	@echo "$(GREEN)✓ Deep cleanup complete$(NC)"

# =============================================================================
# Development Helpers
# =============================================================================

shell: ## Open IPython shell
	@echo "$(BLUE)Opening IPython shell...$(NC)"
	ipython

jupyter: ## Start Jupyter Lab
	@echo "$(BLUE)Starting Jupyter Lab...$(NC)"
	jupyter lab

watch: ## Watch files and run tests on changes
	@echo "$(BLUE)Watching for changes...$(NC)"
	$(PYTEST) $(TEST_DIR) -v --tb=short --looponfail

complexity: ## Show code complexity metrics
	@echo "$(BLUE)Analyzing code complexity...$(NC)"
	radon cc . -a -nb
	@echo "$(GREEN)✓ Complexity analysis complete$(NC)"

dead-code: ## Find dead code
	@echo "$(BLUE)Finding dead code...$(NC)"
	vulture . --min-confidence 80
	@echo "$(GREEN)✓ Dead code analysis complete$(NC)"

doc-coverage: ## Check documentation coverage
	@echo "$(BLUE)Checking documentation coverage...$(NC)"
	interrogate -v .
	@echo "$(GREEN)✓ Documentation coverage check complete$(NC)"

# =============================================================================
# Quick Development Workflow
# =============================================================================

fix: format lint-fix ## Quick fix: format and auto-fix linting issues
	@echo "$(GREEN)✓ Quick fix complete$(NC)"

verify: fix typecheck test-fast ## Verify changes: fix, typecheck, fast tests
	@echo "$(GREEN)✓ Verification complete$(NC)"

# =============================================================================
# Information
# =============================================================================

info: ## Show project information
	@echo "$(CYAN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║$(NC) $(MAGENTA)CodeSnippetBank Project Information$(NC)                       $(CYAN)║$(NC)"
	@echo "$(CYAN)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Python:$(NC)      $$($(PYTHON) --version)"
	@echo "$(YELLOW)Pip:$(NC)         $$($(PIP) --version | cut -d' ' -f1,2)"
	@echo "$(YELLOW)Ruff:$(NC)        $$($(RUFF) --version 2>/dev/null || echo 'not installed')"
	@echo "$(YELLOW)Mypy:$(NC)        $$($(MYPY) --version 2>/dev/null || echo 'not installed')"
	@echo "$(YELLOW)Pytest:$(NC)      $$($(PYTEST) --version 2>/dev/null || echo 'not installed')"
	@echo "$(YELLOW)Pre-commit:$(NC)  $$(pre-commit --version 2>/dev/null || echo 'not installed')"
	@echo ""
	@echo "$(YELLOW)Source dirs:$(NC) $(SRC_DIRS)"
	@echo "$(YELLOW)Test dir:$(NC)    $(TEST_DIR)"
	@echo ""
