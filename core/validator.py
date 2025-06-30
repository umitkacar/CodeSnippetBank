"""
Validation system for code snippets.

Ensures snippets meet quality standards, have proper format, 
and contain required information.
"""

import ast
import re
from typing import List, Tuple, Dict, Any, Optional
import subprocess
import tempfile
import os

from .models import CodeSnippet, SnippetMetadata, SnippetDifficulty, SnippetType


class ValidationError:
    """Represents a validation error with severity and details."""
    
    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # "error", "warning", "info"
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.field}: {self.message}"


class SnippetValidator:
    """
    Comprehensive validator for code snippets.
    
    Validates:
    - Metadata completeness and format
    - Code syntax and style
    - Documentation quality
    - Test coverage
    - Security concerns
    """
    
    def __init__(self):
        self.required_metadata_fields = [
            "snippet_id", "title", "category", "tags", 
            "difficulty", "dependencies"
        ]
        
        self.min_description_length = 50
        self.max_title_length = 100
        self.min_tags = 2
        self.max_tags = 10
        
        # Common security patterns to check
        self.security_patterns = [
            (r'eval\s*\(', "Use of eval() is potentially dangerous"),
            (r'exec\s*\(', "Use of exec() is potentially dangerous"),
            (r'__import__\s*\(', "Dynamic imports can be security risks"),
            (r'pickle\.loads?\s*\(', "Pickle can execute arbitrary code"),
            (r'subprocess.*shell\s*=\s*True', "Shell=True in subprocess is dangerous"),
            (r'os\.system\s*\(', "os.system() is less secure than subprocess")
        ]
        
        # Code quality patterns
        self.quality_patterns = [
            (r'except\s*:', "Bare except clauses should be avoided"),
            (r'import\s+\*', "Wildcard imports should be avoided"),
            (r'TODO|FIXME|XXX', "Contains TODO/FIXME comments"),
            (r'print\s*\(', "Contains print statements (use logging instead)")
        ]
    
    def validate(self, snippet: CodeSnippet) -> Tuple[bool, List[ValidationError]]:
        """
        Validate a code snippet comprehensively.
        
        Args:
            snippet: The snippet to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate metadata
        errors.extend(self._validate_metadata(snippet.metadata))
        
        # Validate description
        errors.extend(self._validate_description(snippet.description))
        
        # Validate code
        errors.extend(self._validate_code(snippet.code))
        
        # Validate example usage
        errors.extend(self._validate_example_usage(snippet.example_usage))
        
        # Validate tests if present
        if snippet.tests:
            errors.extend(self._validate_tests(snippet.tests))
        
        # Check security concerns
        errors.extend(self._check_security(snippet.code))
        
        # Check code quality
        errors.extend(self._check_quality(snippet.code))
        
        # Determine if valid (no errors with severity "error")
        is_valid = not any(e.severity == "error" for e in errors)
        
        return is_valid, errors
    
    def _validate_metadata(self, metadata: SnippetMetadata) -> List[ValidationError]:
        """Validate snippet metadata."""
        errors = []
        
        # Check required fields
        for field in self.required_metadata_fields:
            if not getattr(metadata, field, None):
                errors.append(ValidationError(
                    f"metadata.{field}",
                    f"Required field '{field}' is missing or empty"
                ))
        
        # Validate title
        if metadata.title:
            if len(metadata.title) > self.max_title_length:
                errors.append(ValidationError(
                    "metadata.title",
                    f"Title too long (max {self.max_title_length} chars)"
                ))
            
            if not re.match(r'^[A-Z]', metadata.title):
                errors.append(ValidationError(
                    "metadata.title",
                    "Title should start with capital letter",
                    severity="warning"
                ))
        
        # Validate category
        if metadata.category:
            if not re.match(r'^[a-z_]+(/[a-z_]+)*$', metadata.category):
                errors.append(ValidationError(
                    "metadata.category",
                    "Category should be lowercase with underscores (e.g., 'machine_learning/classification')"
                ))
        
        # Validate tags
        if metadata.tags:
            if len(metadata.tags) < self.min_tags:
                errors.append(ValidationError(
                    "metadata.tags",
                    f"At least {self.min_tags} tags required",
                    severity="warning"
                ))
            
            if len(metadata.tags) > self.max_tags:
                errors.append(ValidationError(
                    "metadata.tags",
                    f"Too many tags (max {self.max_tags})",
                    severity="warning"
                ))
            
            for tag in metadata.tags:
                if not re.match(r'^[a-z0-9-]+$', tag):
                    errors.append(ValidationError(
                        "metadata.tags",
                        f"Tag '{tag}' should be lowercase with hyphens only"
                    ))
        
        # Validate dependencies
        if metadata.dependencies:
            for dep in metadata.dependencies:
                if not self._is_valid_dependency(dep):
                    errors.append(ValidationError(
                        "metadata.dependencies",
                        f"Invalid dependency format: '{dep}'"
                    ))
        
        # Validate version
        if metadata.version:
            if not re.match(r'^\d+\.\d+\.\d+$', metadata.version):
                errors.append(ValidationError(
                    "metadata.version",
                    "Version should follow semantic versioning (X.Y.Z)",
                    severity="warning"
                ))
        
        return errors
    
    def _validate_description(self, description: str) -> List[ValidationError]:
        """Validate snippet description."""
        errors = []
        
        if not description:
            errors.append(ValidationError(
                "description",
                "Description is required"
            ))
        elif len(description) < self.min_description_length:
            errors.append(ValidationError(
                "description",
                f"Description too short (min {self.min_description_length} chars)",
                severity="warning"
            ))
        
        return errors
    
    def _validate_code(self, code: str) -> List[ValidationError]:
        """Validate the code syntax and structure."""
        errors = []
        
        if not code or not code.strip():
            errors.append(ValidationError(
                "code",
                "Code is required"
            ))
            return errors
        
        # Check Python syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(ValidationError(
                "code",
                f"Syntax error: {e.msg} at line {e.lineno}"
            ))
            return errors  # Can't do further validation with syntax errors
        
        # Check for docstrings in functions/classes
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    errors.append(ValidationError(
                        "code",
                        f"Function/class '{node.name}' missing docstring",
                        severity="warning"
                    ))
        
        # Check for type hints (warning only)
        has_type_hints = any(
            node.returns is not None or any(arg.annotation is not None for arg in node.args.args)
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        )
        
        if not has_type_hints:
            errors.append(ValidationError(
                "code",
                "Consider adding type hints for better code clarity",
                severity="info"
            ))
        
        # Check line length
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                errors.append(ValidationError(
                    "code",
                    f"Line {i} too long ({len(line)} chars, max 120)",
                    severity="warning"
                ))
        
        return errors
    
    def _validate_example_usage(self, example: str) -> List[ValidationError]:
        """Validate example usage."""
        errors = []
        
        if not example or not example.strip():
            errors.append(ValidationError(
                "example_usage",
                "Example usage is required"
            ))
            return errors
        
        # Check if example is valid Python
        try:
            # Try to parse as Python code
            ast.parse(example)
        except SyntaxError:
            # Maybe it's formatted with text, try to extract code blocks
            code_blocks = re.findall(r'```python\n(.*?)\n```', example, re.DOTALL)
            if not code_blocks:
                code_blocks = re.findall(r'    (.+)$', example, re.MULTILINE)
            
            if not code_blocks:
                errors.append(ValidationError(
                    "example_usage",
                    "Example usage should contain valid Python code",
                    severity="warning"
                ))
        
        return errors
    
    def _validate_tests(self, tests: str) -> List[ValidationError]:
        """Validate test code."""
        errors = []
        
        if not tests or not tests.strip():
            return errors  # Tests are optional
        
        # Check syntax
        try:
            ast.parse(tests)
        except SyntaxError as e:
            errors.append(ValidationError(
                "tests",
                f"Test syntax error: {e.msg} at line {e.lineno}"
            ))
            return errors
        
        # Check for test functions
        tree = ast.parse(tests)
        test_functions = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and 
            (node.name.startswith('test_') or node.name.startswith('Test'))
        ]
        
        if not test_functions:
            errors.append(ValidationError(
                "tests",
                "No test functions found (should start with 'test_' or 'Test')",
                severity="warning"
            ))
        
        return errors
    
    def _check_security(self, code: str) -> List[ValidationError]:
        """Check for security concerns."""
        errors = []
        
        for pattern, message in self.security_patterns:
            if re.search(pattern, code, re.MULTILINE):
                errors.append(ValidationError(
                    "security",
                    message,
                    severity="warning"
                ))
        
        return errors
    
    def _check_quality(self, code: str) -> List[ValidationError]:
        """Check code quality issues."""
        errors = []
        
        for pattern, message in self.quality_patterns:
            matches = re.findall(pattern, code, re.MULTILINE)
            if matches:
                errors.append(ValidationError(
                    "quality",
                    f"{message} ({len(matches)} occurrence(s))",
                    severity="info"
                ))
        
        return errors
    
    def _is_valid_dependency(self, dep: str) -> bool:
        """Check if dependency string is valid."""
        # Simple check for package name and optional version
        pattern = r'^[a-zA-Z0-9_-]+(\[.*\])?([><=!~]+[\d.]+)?$'
        return bool(re.match(pattern, dep))
    
    def validate_batch(self, snippets: List[CodeSnippet]) -> Dict[str, Any]:
        """
        Validate multiple snippets and return summary.
        
        Args:
            snippets: List of snippets to validate
            
        Returns:
            Dictionary with validation summary
        """
        results = {
            "total": len(snippets),
            "valid": 0,
            "invalid": 0,
            "warnings": 0,
            "errors_by_type": {},
            "invalid_snippets": []
        }
        
        for snippet in snippets:
            is_valid, errors = self.validate(snippet)
            
            if is_valid:
                results["valid"] += 1
            else:
                results["invalid"] += 1
                results["invalid_snippets"].append({
                    "snippet_id": snippet.metadata.snippet_id,
                    "title": snippet.metadata.title,
                    "errors": [str(e) for e in errors if e.severity == "error"]
                })
            
            # Count warnings
            warning_count = sum(1 for e in errors if e.severity == "warning")
            if warning_count > 0:
                results["warnings"] += 1
            
            # Count errors by type
            for error in errors:
                error_type = error.field
                if error_type not in results["errors_by_type"]:
                    results["errors_by_type"][error_type] = 0
                results["errors_by_type"][error_type] += 1
        
        return results
    
    def suggest_improvements(self, snippet: CodeSnippet) -> List[str]:
        """
        Suggest improvements for a snippet.
        
        Args:
            snippet: The snippet to analyze
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Check if tests are missing
        if not snippet.tests:
            suggestions.append("Add unit tests to ensure code reliability")
        
        # Check if complexity metrics are missing
        if not snippet.metadata.time_complexity:
            suggestions.append("Document time complexity for performance awareness")
        
        # Check for advanced features
        tree = ast.parse(snippet.code)
        
        # Suggest error handling if not present
        has_try_except = any(isinstance(node, ast.Try) for node in ast.walk(tree))
        if not has_try_except:
            suggestions.append("Consider adding error handling for robustness")
        
        # Suggest logging instead of print
        has_print = any(
            isinstance(node, ast.Call) and 
            isinstance(node.func, ast.Name) and 
            node.func.id == 'print'
            for node in ast.walk(tree)
        )
        if has_print:
            suggestions.append("Replace print statements with proper logging")
        
        # Suggest type hints
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        functions_without_hints = [
            f for f in functions 
            if f.returns is None and not any(arg.annotation for arg in f.args.args)
        ]
        if functions_without_hints:
            suggestions.append(f"Add type hints to {len(functions_without_hints)} function(s)")
        
        # Check docstring quality
        if len(snippet.description) < 100:
            suggestions.append("Expand description for better understanding")
        
        # Suggest related snippets
        if not snippet.metadata.related_snippets:
            suggestions.append("Link related snippets for better discoverability")
        
        return suggestions