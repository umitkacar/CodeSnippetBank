# Quick Start Guide - Modern Python Development Environment

## 🚀 Get Started in 3 Steps

```bash
# 1️⃣ Install development dependencies
make dev

# 2️⃣ Install pre-commit hooks
make pre-commit

# 3️⃣ Verify everything works
make all
```

## 📋 Essential Commands

### Daily Development Workflow

```bash
# Before starting work
make dev              # Ensure dependencies are installed

# During development
make format           # Format your code
make lint             # Check for issues
make test-fast        # Run quick tests

# Before committing
make verify           # Quick check (format, lint, typecheck, fast tests)

# Before pushing
make all              # Full check (format, lint, typecheck, all tests)
```

### One-Command Shortcuts

| Command | What it does |
|---------|--------------|
| `make fix` | Format + auto-fix linting |
| `make verify` | Quick validation (fast tests) |
| `make all` | Complete validation (all tests) |
| `make ci` | Simulate CI pipeline |

## 🛠️ Tools Installed

- **Ruff** - Ultra-fast linter + formatter (replaces black, flake8, isort)
- **Mypy** - Strict static type checking
- **Pytest** - Modern testing with coverage
- **Pre-commit** - Automated git hooks
- **Hatch** - Modern Python project manager

## 📁 Configuration Files

```
CodeSnippetBank/
├── pyproject.toml              # Main project configuration
├── .pre-commit-config.yaml     # Git hooks configuration
├── pytest.ini                  # Pytest settings
├── .coveragerc                 # Coverage settings
├── requirements-dev.txt        # Development dependencies
├── Makefile                    # Common commands
├── DEVELOPMENT.md              # Detailed setup guide
└── QUICK_START.md             # This file
```

## 🎯 Common Tasks

### Linting and Formatting

```bash
make format          # Auto-format all code
make lint            # Check for issues
make lint-fix        # Auto-fix issues
```

### Type Checking

```bash
make typecheck       # Run mypy
```

### Testing

```bash
make test            # Run all tests
make test-fast       # Skip slow tests
make test-unit       # Unit tests only
make coverage        # Generate coverage report
```

### Code Quality

```bash
make complexity      # Check complexity metrics
make dead-code       # Find unused code
make doc-coverage    # Check documentation
```

### Cleaning

```bash
make clean           # Remove cache files
make clean-all       # Deep clean
```

## 🔧 Pre-commit Hooks

After running `make pre-commit`, these checks run automatically:

- ✅ Ruff formatting
- ✅ Ruff linting
- ✅ Mypy type checking (main code only)
- ✅ Pytest tests (fast tests only)
- ✅ File checks (trailing whitespace, EOF, etc.)
- ✅ Syntax validation (YAML, JSON, TOML)
- ✅ Security scanning (Bandit)

Skip hooks temporarily (not recommended):
```bash
git commit --no-verify
```

## 📊 Quality Standards

- **Coverage:** Minimum 80% code coverage required
- **Type Hints:** All functions must have type annotations
- **Complexity:** Maximum cyclomatic complexity of 10
- **Style:** PEP 8 compliance enforced by Ruff
- **Docstrings:** Google style docstrings required

## 🐛 Troubleshooting

### Installation Issues

```bash
# Upgrade pip first
python3 -m pip install --upgrade pip

# Then install dependencies
make dev
```

### Pre-commit Failing

```bash
# Run manually to see errors
pre-commit run --all-files

# Update hooks
make pre-commit-update
```

### Tests Failing

```bash
# Verbose output
pytest -vv --tb=long

# Debug with pdb
pytest --pdb
```

## 📚 Learn More

- Full guide: See `DEVELOPMENT.md`
- All commands: Run `make help`
- Project info: Run `make info`

## 🎓 Best Practices

1. **Always format before committing:** `make format`
2. **Run tests frequently:** `make test-fast`
3. **Check types regularly:** `make typecheck`
4. **Keep coverage high:** `make coverage`
5. **Use pre-commit hooks:** They catch issues early!

## 🔗 Quick Links

- Ruff: https://docs.astral.sh/ruff/
- Mypy: https://mypy.readthedocs.io/
- Pytest: https://docs.pytest.org/
- Pre-commit: https://pre-commit.com/

---

**Need help?** Run `make help` or check `DEVELOPMENT.md`
