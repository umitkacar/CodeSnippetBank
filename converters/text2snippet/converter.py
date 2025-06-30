"""
Text2CodeSnippet Converter - Extracts and transforms code snippets from documentation.

This converter intelligently extracts code from various text formats (Markdown, RST, HTML)
and transforms them into standardized, reusable CodeSnippet objects.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import hashlib
from datetime import datetime

from ...core.models import CodeSnippet, SnippetMetadata, SnippetDifficulty, SnippetType
from ...core.validator import SnippetValidator
from .parsers import MarkdownParser, RSTParser, HTMLParser
from .analyzers import CodeAnalyzer, ContextAnalyzer
from .generators import SnippetGenerator, TestGenerator


class Text2CodeSnippet:
    """
    Main converter class that orchestrates the extraction and transformation
    of code snippets from text documentation.
    """
    
    def __init__(self, validate: bool = True, auto_improve: bool = True):
        """
        Initialize the converter.
        
        Args:
            validate: Whether to validate generated snippets
            auto_improve: Whether to automatically improve snippets
        """
        self.validate = validate
        self.auto_improve = auto_improve
        
        # Initialize components
        self.parsers = {
            'markdown': MarkdownParser(),
            'md': MarkdownParser(),
            'rst': RSTParser(),
            'html': HTMLParser(),
            'htm': HTMLParser()
        }
        
        self.code_analyzer = CodeAnalyzer()
        self.context_analyzer = ContextAnalyzer()
        self.snippet_generator = SnippetGenerator()
        self.test_generator = TestGenerator()
        self.validator = SnippetValidator() if validate else None
        
        # Statistics
        self.stats = {
            'files_processed': 0,
            'snippets_extracted': 0,
            'snippets_improved': 0,
            'validation_failures': 0
        }
    
    def convert_file(self, file_path: str) -> List[CodeSnippet]:
        """
        Convert a single documentation file to code snippets.
        
        Args:
            file_path: Path to the documentation file
            
        Returns:
            List of extracted and processed CodeSnippet objects
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine file type
        file_type = path.suffix.lower().lstrip('.')
        if file_type not in self.parsers:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Read file content
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata from file
        file_metadata = self._extract_file_metadata(path, content)
        
        # Convert content
        snippets = self.convert_text(content, file_type, file_metadata)
        
        self.stats['files_processed'] += 1
        
        return snippets
    
    def convert_text(self, text: str, format_type: str = 'markdown', 
                    context: Optional[Dict[str, Any]] = None) -> List[CodeSnippet]:
        """
        Convert text content to code snippets.
        
        Args:
            text: The text content to process
            format_type: Format of the text (markdown, rst, html)
            context: Additional context information
            
        Returns:
            List of extracted CodeSnippet objects
        """
        if format_type not in self.parsers:
            raise ValueError(f"Unsupported format: {format_type}")
        
        parser = self.parsers[format_type]
        context = context or {}
        
        # Parse text to extract code blocks and surrounding context
        parsed_blocks = parser.parse(text)
        
        snippets = []
        for block in parsed_blocks:
            # Analyze the code and context
            code_info = self.code_analyzer.analyze(block['code'], block.get('language', 'python'))
            context_info = self.context_analyzer.analyze(
                block.get('before_text', ''),
                block.get('after_text', ''),
                block.get('section_title', '')
            )
            
            # Determine snippet metadata
            metadata = self._create_metadata(code_info, context_info, context)
            
            # Generate improved code if needed
            if self.auto_improve:
                improved_code = self.snippet_generator.improve_code(
                    block['code'],
                    code_info,
                    context_info
                )
            else:
                improved_code = block['code']
            
            # Generate description
            description = self._generate_description(code_info, context_info, block)
            
            # Generate example usage
            example_usage = self._generate_example_usage(improved_code, code_info)
            
            # Generate tests if possible
            tests = None
            if self.auto_improve and code_info.get('testable', False):
                tests = self.test_generator.generate_tests(improved_code, code_info)
            
            # Create snippet
            snippet = CodeSnippet(
                metadata=metadata,
                description=description,
                code=improved_code,
                example_usage=example_usage,
                tests=tests
            )
            
            # Validate if enabled
            if self.validate:
                is_valid, errors = self.validator.validate(snippet)
                if not is_valid:
                    # Try to fix common issues
                    snippet = self._fix_validation_errors(snippet, errors)
                    
                    # Re-validate
                    is_valid, errors = self.validator.validate(snippet)
                    if not is_valid:
                        print(f"Warning: Snippet validation failed: {errors}")
                        self.stats['validation_failures'] += 1
                        continue
            
            snippets.append(snippet)
            self.stats['snippets_extracted'] += 1
            
            if self.auto_improve:
                self.stats['snippets_improved'] += 1
        
        return snippets
    
    def _extract_file_metadata(self, path: Path, content: str) -> Dict[str, Any]:
        """Extract metadata from file path and content."""
        metadata = {
            'source_file': str(path),
            'file_name': path.stem,
            'file_type': path.suffix.lstrip('.')
        }
        
        # Try to extract title from content
        title_patterns = [
            r'^#\s+(.+)$',  # Markdown h1
            r'^(.+)\n=+$',  # Markdown/RST underline style
            r'<h1[^>]*>(.+?)</h1>',  # HTML
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                metadata['document_title'] = match.group(1).strip()
                break
        
        # Extract potential category from file path
        parts = path.parts
        if len(parts) > 2:
            # Assume structure like: .../category/subcategory/file.md
            potential_category = '/'.join(parts[-3:-1]).lower().replace('-', '_')
            metadata['suggested_category'] = potential_category
        
        return metadata
    
    def _create_metadata(self, code_info: Dict[str, Any], 
                        context_info: Dict[str, Any],
                        file_context: Dict[str, Any]) -> SnippetMetadata:
        """Create snippet metadata from analyzed information."""
        # Generate title
        title = self._generate_title(code_info, context_info, file_context)
        
        # Determine category
        category = self._determine_category(code_info, context_info, file_context)
        
        # Generate tags
        tags = self._generate_tags(code_info, context_info)
        
        # Determine difficulty
        difficulty = self._determine_difficulty(code_info)
        
        # Determine snippet type
        snippet_type = self._determine_snippet_type(code_info)
        
        # Extract dependencies
        dependencies = code_info.get('imports', {}).get('external_packages', [])
        
        # Create metadata
        metadata = SnippetMetadata(
            snippet_id="",  # Will be auto-generated
            title=title,
            category=category,
            tags=tags,
            difficulty=difficulty,
            snippet_type=snippet_type,
            dependencies=dependencies,
            python_version=code_info.get('min_python_version', '3.8+'),
            time_complexity=code_info.get('complexity', {}).get('time'),
            space_complexity=code_info.get('complexity', {}).get('space'),
            author="Text2CodeSnippet",
            version="1.0.0",
            use_cases=context_info.get('use_cases', [])
        )
        
        return metadata
    
    def _generate_title(self, code_info: Dict, context_info: Dict, 
                       file_context: Dict) -> str:
        """Generate a descriptive title for the snippet."""
        # Try to use context title first
        if context_info.get('title'):
            return context_info['title']
        
        # Generate from main functionality
        main_function = code_info.get('main_function')
        main_class = code_info.get('main_class')
        
        if main_function:
            # Convert function name to title case
            title = main_function.replace('_', ' ').title()
        elif main_class:
            title = f"{main_class} Implementation"
        else:
            # Generic title based on category
            category = file_context.get('suggested_category', 'code')
            title = f"{category.replace('/', ' - ').title()} Snippet"
        
        return title[:100]  # Limit length
    
    def _determine_category(self, code_info: Dict, context_info: Dict,
                           file_context: Dict) -> str:
        """Determine the most appropriate category."""
        # Check for explicit category in context
        if context_info.get('category'):
            return context_info['category']
        
        # Use suggested category from file path
        if file_context.get('suggested_category'):
            return file_context['suggested_category']
        
        # Analyze imports and functionality to guess category
        imports = code_info.get('imports', {}).get('external_packages', [])
        
        category_hints = {
            'computer_vision': ['cv2', 'PIL', 'skimage', 'opencv'],
            'nlp': ['nltk', 'spacy', 'transformers', 'textblob'],
            'machine_learning': ['sklearn', 'scikit-learn', 'xgboost', 'lightgbm'],
            'deep_learning': ['torch', 'tensorflow', 'keras', 'jax'],
            'data_processing': ['pandas', 'numpy', 'scipy', 'polars'],
            'web_scraping': ['requests', 'beautifulsoup4', 'scrapy', 'selenium'],
            'api_integration': ['requests', 'httpx', 'aiohttp', 'fastapi'],
            'database': ['sqlalchemy', 'pymongo', 'redis', 'psycopg2']
        }
        
        for category, hints in category_hints.items():
            if any(pkg in imports for pkg in hints):
                return category
        
        return 'utilities'  # Default category
    
    def _generate_tags(self, code_info: Dict, context_info: Dict) -> List[str]:
        """Generate relevant tags for the snippet."""
        tags = set()
        
        # Add tags from imports
        important_packages = code_info.get('imports', {}).get('external_packages', [])
        for pkg in important_packages[:5]:  # Limit to 5 package tags
            tags.add(pkg.lower().replace('_', '-'))
        
        # Add functionality tags
        if code_info.get('uses_async'):
            tags.add('async')
        if code_info.get('uses_classes'):
            tags.add('oop')
        if code_info.get('uses_decorators'):
            tags.add('decorators')
        if code_info.get('uses_generators'):
            tags.add('generators')
        
        # Add context tags
        keywords = context_info.get('keywords', [])
        for keyword in keywords[:5]:
            tags.add(keyword.lower().replace(' ', '-'))
        
        return sorted(list(tags))[:10]  # Max 10 tags
    
    def _determine_difficulty(self, code_info: Dict) -> SnippetDifficulty:
        """Determine snippet difficulty based on code analysis."""
        score = 0
        
        # Complexity factors
        if code_info.get('lines_of_code', 0) > 50:
            score += 1
        if code_info.get('lines_of_code', 0) > 100:
            score += 1
        
        if code_info.get('uses_advanced_features', False):
            score += 2
        
        if code_info.get('complexity', {}).get('cyclomatic', 0) > 10:
            score += 1
        
        if len(code_info.get('imports', {}).get('external_packages', [])) > 5:
            score += 1
        
        # Map score to difficulty
        if score <= 1:
            return SnippetDifficulty.BEGINNER
        elif score <= 3:
            return SnippetDifficulty.INTERMEDIATE
        elif score <= 5:
            return SnippetDifficulty.ADVANCED
        else:
            return SnippetDifficulty.EXPERT
    
    def _determine_snippet_type(self, code_info: Dict) -> SnippetType:
        """Determine the type of snippet."""
        if code_info.get('is_complete_script'):
            return SnippetType.SCRIPT
        elif code_info.get('main_class'):
            return SnippetType.CLASS
        elif code_info.get('main_function'):
            return SnippetType.FUNCTION
        elif code_info.get('is_configuration'):
            return SnippetType.CONFIGURATION
        else:
            return SnippetType.MODULE
    
    def _generate_description(self, code_info: Dict, context_info: Dict,
                            block: Dict) -> str:
        """Generate a comprehensive description."""
        parts = []
        
        # Use context description if available
        if context_info.get('description'):
            parts.append(context_info['description'])
        
        # Add functionality summary
        if code_info.get('summary'):
            parts.append(code_info['summary'])
        
        # Add what it does
        main_purpose = self._extract_main_purpose(code_info, context_info)
        if main_purpose:
            parts.append(main_purpose)
        
        # Combine and clean
        description = ' '.join(parts)
        description = re.sub(r'\s+', ' ', description).strip()
        
        # Ensure minimum length
        if len(description) < 50:
            description += " This snippet provides a reusable implementation that can be easily integrated into your projects."
        
        return description[:500]  # Limit length
    
    def _extract_main_purpose(self, code_info: Dict, context_info: Dict) -> str:
        """Extract the main purpose of the code."""
        # Try to extract from docstrings
        if code_info.get('docstrings'):
            first_docstring = list(code_info['docstrings'].values())[0]
            if first_docstring:
                return first_docstring.split('\n')[0]
        
        # Generate from function/class names
        if code_info.get('main_function'):
            func_name = code_info['main_function']
            return f"Implements {func_name.replace('_', ' ')} functionality"
        
        if code_info.get('main_class'):
            class_name = code_info['main_class']
            return f"Provides a {class_name} implementation"
        
        return ""
    
    def _generate_example_usage(self, code: str, code_info: Dict) -> str:
        """Generate example usage for the snippet."""
        examples = []
        
        # If there's a main function, show how to call it
        if code_info.get('main_function'):
            func_name = code_info['main_function']
            func_params = code_info.get('functions', {}).get(func_name, {}).get('parameters', [])
            
            # Generate parameter examples
            param_examples = []
            for param in func_params:
                param_name = param.get('name', 'arg')
                param_type = param.get('type', 'Any')
                
                # Generate example values based on type
                if 'str' in str(param_type).lower():
                    param_examples.append(f'{param_name}="example"')
                elif 'int' in str(param_type).lower():
                    param_examples.append(f'{param_name}=42')
                elif 'float' in str(param_type).lower():
                    param_examples.append(f'{param_name}=3.14')
                elif 'list' in str(param_type).lower():
                    param_examples.append(f'{param_name}=[1, 2, 3]')
                elif 'dict' in str(param_type).lower():
                    param_examples.append(f'{param_name}={{"key": "value"}}')
                else:
                    param_examples.append(f'{param_name}=None')
            
            examples.append(f"result = {func_name}({', '.join(param_examples[:3])})")
            examples.append("print(result)")
        
        # If there's a main class, show instantiation
        elif code_info.get('main_class'):
            class_name = code_info['main_class']
            examples.append(f"instance = {class_name}()")
            
            # Show method calls if any
            methods = code_info.get('classes', {}).get(class_name, {}).get('methods', [])
            for method in methods[:2]:  # Show first 2 methods
                if not method.startswith('_'):  # Skip private methods
                    examples.append(f"instance.{method}()")
        
        # If no specific structure, show generic import
        else:
            examples.append("# Import and use the code")
            examples.append("from snippet import *")
        
        return '    ' + '\n    '.join(examples)
    
    def _fix_validation_errors(self, snippet: CodeSnippet, 
                              errors: List[Any]) -> CodeSnippet:
        """Attempt to fix common validation errors."""
        for error in errors:
            if error.severity != "error":
                continue
            
            # Fix missing tags
            if "tags" in error.field and "required" in error.message:
                snippet.metadata.tags = ["python", "snippet"]
            
            # Fix missing description
            elif "description" in error.field and len(snippet.description) < 50:
                snippet.description = (
                    f"{snippet.description} "
                    f"This {snippet.metadata.snippet_type.value} provides "
                    f"functionality for {snippet.metadata.category.replace('_', ' ')}."
                )
            
            # Fix category format
            elif "category" in error.field and "lowercase" in error.message:
                snippet.metadata.category = snippet.metadata.category.lower().replace(' ', '_')
        
        return snippet
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversion statistics."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset conversion statistics."""
        self.stats = {
            'files_processed': 0,
            'snippets_extracted': 0,
            'snippets_improved': 0,
            'validation_failures': 0
        }