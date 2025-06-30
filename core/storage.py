"""
Storage system for CodeSnippetBank.

Handles saving, loading, and organizing snippets in the file system.
Supports both individual snippet files and JSON-based index for fast searching.
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import hashlib

from .models import CodeSnippet, SnippetMetadata, Category, SnippetVersion


class SnippetStorage:
    """
    File-based storage system for code snippets.
    
    Organizes snippets in a hierarchical directory structure based on categories
    and maintains a JSON index for fast searching and retrieval.
    """
    
    def __init__(self, base_path: str = "snippets"):
        """
        Initialize storage system.
        
        Args:
            base_path: Root directory for storing snippets
        """
        self.base_path = Path(base_path)
        self.index_file = self.base_path / "_index.json"
        self.categories_file = self.base_path / "_categories.json"
        self.versions_dir = self.base_path / "_versions"
        
        # Create base directories
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.versions_dir.mkdir(exist_ok=True)
        
        # Load or create index
        self.index = self._load_index()
        self.categories = self._load_categories()
    
    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load snippet index from file."""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        """Save snippet index to file."""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def _load_categories(self) -> Dict[str, Category]:
        """Load categories from file."""
        if self.categories_file.exists():
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: Category(**v) for k, v in data.items()}
        return self._initialize_default_categories()
    
    def _save_categories(self):
        """Save categories to file."""
        data = {k: v.to_dict() for k, v in self.categories.items()}
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _initialize_default_categories(self) -> Dict[str, Category]:
        """Create default category structure."""
        categories = {
            "computer_vision": Category(
                name="Computer Vision",
                path="computer_vision",
                description="Image and video processing, object detection, segmentation"
            ),
            "nlp": Category(
                name="Natural Language Processing",
                path="nlp",
                description="Text processing, tokenization, embeddings, generation"
            ),
            "machine_learning": Category(
                name="Machine Learning",
                path="machine_learning",
                description="Classical ML algorithms, preprocessing, evaluation"
            ),
            "deep_learning": Category(
                name="Deep Learning",
                path="deep_learning",
                description="Neural networks, training loops, architectures"
            ),
            "data_processing": Category(
                name="Data Processing",
                path="data_processing",
                description="Data cleaning, transformation, analysis"
            ),
            "web_scraping": Category(
                name="Web Scraping",
                path="web_scraping",
                description="Web data extraction, parsing, automation"
            ),
            "api_integration": Category(
                name="API Integration",
                path="api_integration",
                description="REST APIs, GraphQL, webhooks, authentication"
            ),
            "database": Category(
                name="Database",
                path="database",
                description="SQL, NoSQL, ORMs, query optimization"
            ),
            "authentication": Category(
                name="Authentication & Security",
                path="authentication",
                description="Auth flows, encryption, security best practices"
            ),
            "deployment": Category(
                name="Deployment",
                path="deployment",
                description="Docker, Kubernetes, CI/CD, cloud deployment"
            ),
            "testing": Category(
                name="Testing",
                path="testing",
                description="Unit tests, integration tests, mocking"
            ),
            "optimization": Category(
                name="Performance Optimization",
                path="optimization",
                description="Code optimization, profiling, caching"
            ),
            "utilities": Category(
                name="Utilities",
                path="utilities",
                description="Helper functions, common patterns, tools"
            )
        }
        
        # Create subdirectories
        subcategories = {
            "computer_vision": ["detection", "segmentation", "tracking", "3d_vision", "image_processing"],
            "nlp": ["tokenization", "embeddings", "generation", "classification", "ner"],
            "machine_learning": ["classification", "regression", "clustering", "preprocessing"],
            "deep_learning": ["layers", "optimizers", "losses", "models", "training"],
            "data_processing": ["cleaning", "transformation", "visualization", "statistics"],
            "web_scraping": ["parsers", "browsers", "extractors", "patterns"],
            "api_integration": ["rest", "graphql", "authentication", "rate_limiting"],
            "database": ["queries", "connections", "migrations", "optimization"]
        }
        
        for parent, subs in subcategories.items():
            if parent in categories:
                categories[parent].subcategories = subs
                for sub in subs:
                    sub_path = f"{parent}/{sub}"
                    categories[sub_path] = Category(
                        name=sub.replace('_', ' ').title(),
                        path=sub,
                        parent=parent,
                        description=f"Subcategory of {categories[parent].name}"
                    )
        
        self._save_categories()
        return categories
    
    def save_snippet(self, snippet: CodeSnippet, force: bool = False) -> Tuple[bool, str]:
        """
        Save a snippet to storage.
        
        Args:
            snippet: The snippet to save
            force: Overwrite if exists
            
        Returns:
            Tuple of (success, message)
        """
        snippet_id = snippet.metadata.snippet_id
        
        # Check if snippet already exists
        if snippet_id in self.index and not force:
            return False, f"Snippet {snippet_id} already exists. Use force=True to overwrite."
        
        # Determine file path
        category_path = self.base_path / snippet.metadata.category.replace('/', os.sep)
        category_path.mkdir(parents=True, exist_ok=True)
        
        file_name = f"{snippet_id}_{snippet.metadata.title.lower().replace(' ', '_')}.py"
        file_path = category_path / file_name
        
        # Save previous version if updating
        if snippet_id in self.index:
            self._save_version(snippet_id)
        
        # Write snippet file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(snippet.to_file_content())
            
            # Update index
            self.index[snippet_id] = {
                "metadata": snippet.metadata.to_dict(),
                "file_path": str(file_path.relative_to(self.base_path)),
                "description": snippet.description,
                "example_usage": snippet.example_usage,
                "has_tests": snippet.tests is not None,
                "lines_of_code": snippet.estimate_lines_of_code(),
                "imports": snippet.get_imports()
            }
            
            # Update category counts
            self._update_category_counts()
            
            # Save index
            self._save_index()
            
            return True, f"Snippet {snippet_id} saved successfully to {file_path}"
            
        except Exception as e:
            return False, f"Error saving snippet: {str(e)}"
    
    def load_snippet(self, snippet_id: str) -> Optional[CodeSnippet]:
        """
        Load a snippet from storage.
        
        Args:
            snippet_id: ID of the snippet to load
            
        Returns:
            CodeSnippet object or None if not found
        """
        if snippet_id not in self.index:
            return None
        
        snippet_info = self.index[snippet_id]
        file_path = self.base_path / snippet_info["file_path"]
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the file content back to CodeSnippet
            # This is a simplified parser - in production, use proper parsing
            return self._parse_snippet_file(content, snippet_info)
            
        except Exception as e:
            print(f"Error loading snippet {snippet_id}: {e}")
            return None
    
    def _parse_snippet_file(self, content: str, index_info: Dict[str, Any]) -> CodeSnippet:
        """
        Parse a snippet file back into a CodeSnippet object.
        
        This is a simplified implementation. In production, use a proper parser.
        """
        # Extract metadata from index (more reliable than parsing)
        metadata = SnippetMetadata.from_dict(index_info["metadata"])
        
        # Extract code section (everything after the docstring)
        lines = content.split('\n')
        code_start = 0
        in_docstring = False
        
        for i, line in enumerate(lines):
            if line.strip() == '"""':
                if not in_docstring:
                    in_docstring = True
                else:
                    code_start = i + 2  # Skip the closing """ and empty line
                    break
        
        code_lines = []
        test_lines = []
        in_tests = False
        
        for line in lines[code_start:]:
            if line.strip() == "# Auto-generated tests":
                in_tests = True
                continue
            
            if in_tests:
                test_lines.append(line)
            else:
                code_lines.append(line)
        
        code = '\n'.join(code_lines).strip()
        tests = '\n'.join(test_lines).strip() if test_lines else None
        
        return CodeSnippet(
            metadata=metadata,
            description=index_info["description"],
            code=code,
            example_usage=index_info["example_usage"],
            tests=tests
        )
    
    def list_snippets(self, category: Optional[str] = None, 
                     tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List snippets with optional filtering.
        
        Args:
            category: Filter by category
            tags: Filter by tags
            
        Returns:
            List of snippet metadata
        """
        results = []
        
        for snippet_id, info in self.index.items():
            metadata = info["metadata"]
            
            # Apply filters
            if category and not metadata["category"].startswith(category):
                continue
            
            if tags:
                snippet_tags = set(metadata.get("tags", []))
                if not any(tag in snippet_tags for tag in tags):
                    continue
            
            results.append({
                "snippet_id": snippet_id,
                "title": metadata["title"],
                "category": metadata["category"],
                "tags": metadata.get("tags", []),
                "difficulty": metadata.get("difficulty", "intermediate"),
                "description": info["description"][:100] + "...",
                "lines_of_code": info.get("lines_of_code", 0)
            })
        
        return sorted(results, key=lambda x: x["title"])
    
    def search_snippets(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Simple text search across snippets.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching snippets with scores
        """
        query_lower = query.lower()
        results = []
        
        for snippet_id, info in self.index.items():
            score = 0.0
            matched_fields = []
            
            # Search in title (highest weight)
            if query_lower in info["metadata"]["title"].lower():
                score += 10.0
                matched_fields.append("title")
            
            # Search in description
            if query_lower in info["description"].lower():
                score += 5.0
                matched_fields.append("description")
            
            # Search in tags
            tags = info["metadata"].get("tags", [])
            if any(query_lower in tag.lower() for tag in tags):
                score += 3.0
                matched_fields.append("tags")
            
            # Search in category
            if query_lower in info["metadata"]["category"].lower():
                score += 2.0
                matched_fields.append("category")
            
            if score > 0:
                results.append({
                    "snippet_id": snippet_id,
                    "title": info["metadata"]["title"],
                    "category": info["metadata"]["category"],
                    "description": info["description"][:150] + "...",
                    "score": score,
                    "matched_fields": matched_fields
                })
        
        # Sort by score and limit
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def delete_snippet(self, snippet_id: str) -> Tuple[bool, str]:
        """
        Delete a snippet from storage.
        
        Args:
            snippet_id: ID of snippet to delete
            
        Returns:
            Tuple of (success, message)
        """
        if snippet_id not in self.index:
            return False, f"Snippet {snippet_id} not found"
        
        try:
            # Save to versions before deleting
            self._save_version(snippet_id, is_deletion=True)
            
            # Delete file
            file_path = self.base_path / self.index[snippet_id]["file_path"]
            if file_path.exists():
                file_path.unlink()
            
            # Remove from index
            del self.index[snippet_id]
            self._save_index()
            
            # Update category counts
            self._update_category_counts()
            
            return True, f"Snippet {snippet_id} deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting snippet: {str(e)}"
    
    def _save_version(self, snippet_id: str, is_deletion: bool = False):
        """Save a version of the snippet before modification."""
        if snippet_id not in self.index:
            return
        
        snippet = self.load_snippet(snippet_id)
        if not snippet:
            return
        
        # Create version entry
        version_data = {
            "snippet_id": snippet_id,
            "version": snippet.metadata.version,
            "timestamp": datetime.now().isoformat(),
            "is_deletion": is_deletion,
            "snippet_data": snippet.to_dict()
        }
        
        # Save to versions directory
        version_file = self.versions_dir / f"{snippet_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2, ensure_ascii=False)
    
    def _update_category_counts(self):
        """Update snippet counts for all categories."""
        # Reset counts
        for category in self.categories.values():
            category.snippet_count = 0
        
        # Count snippets per category
        for info in self.index.values():
            category_path = info["metadata"]["category"]
            if category_path in self.categories:
                self.categories[category_path].snippet_count += 1
            
            # Also update parent category counts
            if '/' in category_path:
                parent = category_path.split('/')[0]
                if parent in self.categories:
                    self.categories[parent].snippet_count += 1
        
        self._save_categories()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        total_snippets = len(self.index)
        total_loc = sum(info.get("lines_of_code", 0) for info in self.index.values())
        
        # Category distribution
        category_dist = {}
        for info in self.index.values():
            cat = info["metadata"]["category"].split('/')[0]
            category_dist[cat] = category_dist.get(cat, 0) + 1
        
        # Difficulty distribution
        difficulty_dist = {}
        for info in self.index.values():
            diff = info["metadata"].get("difficulty", "intermediate")
            difficulty_dist[diff] = difficulty_dist.get(diff, 0) + 1
        
        return {
            "total_snippets": total_snippets,
            "total_lines_of_code": total_loc,
            "average_loc_per_snippet": total_loc / total_snippets if total_snippets > 0 else 0,
            "category_distribution": category_dist,
            "difficulty_distribution": difficulty_dist,
            "total_categories": len(self.categories),
            "snippets_with_tests": sum(1 for info in self.index.values() if info.get("has_tests", False))
        }