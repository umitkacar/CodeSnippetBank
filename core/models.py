"""
Core data models for CodeSnippetBank.

This module defines the fundamental data structures used throughout the system
for representing, storing, and managing code snippets.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import hashlib
import json


class SnippetDifficulty(Enum):
    """Difficulty levels for code snippets."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SnippetType(Enum):
    """Type classification for snippets."""
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    SCRIPT = "script"
    CONFIGURATION = "configuration"
    TEMPLATE = "template"


@dataclass
class SnippetMetadata:
    """
    Metadata information for a code snippet.
    
    Contains all non-code information about a snippet including
    categorization, dependencies, performance metrics, etc.
    """
    snippet_id: str
    title: str
    category: str
    subcategory: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    difficulty: SnippetDifficulty = SnippetDifficulty.INTERMEDIATE
    snippet_type: SnippetType = SnippetType.FUNCTION
    
    # Dependencies and requirements
    dependencies: List[str] = field(default_factory=list)
    python_version: str = "3.8+"
    
    # Performance and complexity
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    performance_notes: Optional[str] = None
    
    # Authorship and versioning
    author: str = "CodeSnippetBank"
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Usage and examples
    use_cases: List[str] = field(default_factory=list)
    related_snippets: List[str] = field(default_factory=list)
    
    # Quality metrics
    test_coverage: Optional[float] = None
    community_score: float = 0.0
    usage_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary format."""
        return {
            "snippet_id": self.snippet_id,
            "title": self.title,
            "category": self.category,
            "subcategory": self.subcategory,
            "tags": self.tags,
            "difficulty": self.difficulty.value,
            "snippet_type": self.snippet_type.value,
            "dependencies": self.dependencies,
            "python_version": self.python_version,
            "time_complexity": self.time_complexity,
            "space_complexity": self.space_complexity,
            "performance_notes": self.performance_notes,
            "author": self.author,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "use_cases": self.use_cases,
            "related_snippets": self.related_snippets,
            "test_coverage": self.test_coverage,
            "community_score": self.community_score,
            "usage_count": self.usage_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SnippetMetadata':
        """Create metadata from dictionary."""
        data = data.copy()
        
        # Convert enums
        if 'difficulty' in data:
            data['difficulty'] = SnippetDifficulty(data['difficulty'])
        if 'snippet_type' in data:
            data['snippet_type'] = SnippetType(data['snippet_type'])
        
        # Convert dates
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)


@dataclass
class CodeSnippet:
    """
    Complete code snippet with metadata, code, documentation, and tests.
    
    This is the core data structure that represents a single reusable
    code snippet in the system.
    """
    metadata: SnippetMetadata
    description: str
    code: str
    example_usage: str
    tests: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Generate snippet ID if not provided."""
        if not self.metadata.snippet_id:
            self.metadata.snippet_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID based on content hash."""
        content = f"{self.metadata.title}{self.metadata.category}{self.code}"
        hash_obj = hashlib.sha256(content.encode())
        short_hash = hash_obj.hexdigest()[:8]
        
        category_prefix = self.metadata.category.split('/')[0].upper()[:2]
        return f"CS-{category_prefix}-{short_hash}"
    
    def to_file_content(self) -> str:
        """
        Convert snippet to the standard file format.
        
        Returns formatted string ready to be saved as a .py file.
        """
        # Create header comment with metadata
        header_lines = [
            '"""',
            f"Snippet ID: {self.metadata.snippet_id}",
            f"Title: {self.metadata.title}",
            f"Category: {self.metadata.category}"
        ]
        
        if self.metadata.subcategory:
            header_lines.append(f"Subcategory: {self.metadata.subcategory}")
        
        header_lines.extend([
            f"Tags: {self.metadata.tags}",
            f"Difficulty: {self.metadata.difficulty.value.capitalize()}",
            f"Dependencies: {self.metadata.dependencies}",
            f"Performance: {self.metadata.time_complexity or 'N/A'}",
            f"Tested: Python {self.metadata.python_version}",
            f"Author: {self.metadata.author}",
            f"Version: {self.metadata.version}",
            f"Last Updated: {self.metadata.updated_at.strftime('%Y-%m-%d')}",
            "",
            "Description:",
            self.description,
            ""
        ])
        
        if self.metadata.use_cases:
            header_lines.append("Use Cases:")
            for use_case in self.metadata.use_cases:
                header_lines.append(f"- {use_case}")
            header_lines.append("")
        
        header_lines.extend([
            "Example Usage:",
            self.example_usage,
            '"""',
            "",
            self.code
        ])
        
        if self.tests:
            header_lines.extend([
                "",
                "",
                "# Auto-generated tests",
                self.tests
            ])
        
        return "\n".join(header_lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert snippet to dictionary format."""
        return {
            "metadata": self.metadata.to_dict(),
            "description": self.description,
            "code": self.code,
            "example_usage": self.example_usage,
            "tests": self.tests,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeSnippet':
        """Create snippet from dictionary."""
        data = data.copy()
        data['metadata'] = SnippetMetadata.from_dict(data['metadata'])
        return cls(**data)
    
    def get_imports(self) -> List[str]:
        """Extract import statements from the code."""
        imports = []
        for line in self.code.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        return imports
    
    def estimate_lines_of_code(self) -> int:
        """Count non-empty, non-comment lines."""
        count = 0
        in_docstring = False
        
        for line in self.code.split('\n'):
            line = line.strip()
            
            # Handle docstrings
            if line.startswith('"""') or line.startswith("'''"):
                in_docstring = not in_docstring
                continue
            
            if in_docstring:
                continue
            
            # Count non-empty, non-comment lines
            if line and not line.startswith('#'):
                count += 1
        
        return count


@dataclass
class Category:
    """
    Represents a category in the snippet organization system.
    
    Categories can be hierarchical (e.g., "computer_vision/detection").
    """
    name: str
    path: str
    description: str
    parent: Optional[str] = None
    icon: Optional[str] = None
    snippet_count: int = 0
    subcategories: List[str] = field(default_factory=list)
    
    def get_full_path(self) -> str:
        """Get the complete path including parent categories."""
        if self.parent:
            return f"{self.parent}/{self.path}"
        return self.path
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "parent": self.parent,
            "icon": self.icon,
            "snippet_count": self.snippet_count,
            "subcategories": self.subcategories
        }


@dataclass
class SnippetVersion:
    """
    Represents a specific version of a snippet.
    
    Used for tracking changes and maintaining version history.
    """
    snippet_id: str
    version: str
    changes: str
    code: str
    metadata_changes: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "snippet_id": self.snippet_id,
            "version": self.version,
            "changes": self.changes,
            "code": self.code,
            "metadata_changes": self.metadata_changes,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by
        }


@dataclass
class SnippetSearchResult:
    """
    Represents a search result when querying snippets.
    """
    snippet: CodeSnippet
    score: float
    matched_fields: List[str] = field(default_factory=list)
    highlights: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "snippet": self.snippet.to_dict(),
            "score": self.score,
            "matched_fields": self.matched_fields,
            "highlights": self.highlights
        }