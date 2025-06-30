"""
Markdown parser for extracting code blocks and their context.
"""

import re
from typing import List, Dict, Any, Optional, Tuple


class MarkdownParser:
    """
    Parser for Markdown documents to extract code blocks with context.
    
    Extracts:
    - Code blocks (fenced with ``` or indented)
    - Language specifications
    - Surrounding text context
    - Section titles and hierarchy
    """
    
    def __init__(self):
        # Regex patterns for different Markdown elements
        self.patterns = {
            'fenced_code': re.compile(r'```(\w+)?\n(.*?)\n```', re.DOTALL),
            'indented_code': re.compile(r'(?:(?:^|\n)(?:    |\t).*)+'),
            'heading': re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE),
            'alt_heading1': re.compile(r'^(.+)\n=+$', re.MULTILINE),
            'alt_heading2': re.compile(r'^(.+)\n-+$', re.MULTILINE),
            'list_item': re.compile(r'^\s*[-*+]\s+(.+)$', re.MULTILINE),
            'numbered_list': re.compile(r'^\s*\d+\.\s+(.+)$', re.MULTILINE),
            'link': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
            'bold': re.compile(r'\*\*(.+?)\*\*|__(.+?)__'),
            'italic': re.compile(r'\*(.+?)\*|_(.+?)_'),
            'inline_code': re.compile(r'`([^`]+)`')
        }
    
    def parse(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse Markdown content and extract code blocks with context.
        
        Args:
            content: Markdown content as string
            
        Returns:
            List of dictionaries containing code blocks and metadata
        """
        blocks = []
        
        # First, extract the document structure
        sections = self._extract_sections(content)
        
        # Extract fenced code blocks
        fenced_blocks = self._extract_fenced_blocks(content, sections)
        blocks.extend(fenced_blocks)
        
        # Extract indented code blocks
        indented_blocks = self._extract_indented_blocks(content, sections)
        blocks.extend(indented_blocks)
        
        # Sort blocks by position in document
        blocks.sort(key=lambda x: x['position'])
        
        return blocks
    
    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extract document sections based on headings."""
        sections = []
        lines = content.split('\n')
        
        current_section = {
            'title': 'Introduction',
            'level': 0,
            'start': 0,
            'content_start': 0
        }
        
        for i, line in enumerate(lines):
            # Check for ATX style headings (# Title)
            heading_match = self.patterns['heading'].match(line)
            if heading_match:
                # Save previous section
                if i > current_section['start']:
                    current_section['end'] = i - 1
                    sections.append(current_section.copy())
                
                # Start new section
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                current_section = {
                    'title': title,
                    'level': level,
                    'start': i,
                    'content_start': i + 1
                }
                continue
            
            # Check for Setext style headings (Title\n====)
            if i < len(lines) - 1:
                next_line = lines[i + 1]
                if re.match(r'^=+$', next_line):
                    # Level 1 heading
                    if i > current_section['start']:
                        current_section['end'] = i - 1
                        sections.append(current_section.copy())
                    
                    current_section = {
                        'title': line.strip(),
                        'level': 1,
                        'start': i,
                        'content_start': i + 2
                    }
                elif re.match(r'^-+$', next_line):
                    # Level 2 heading
                    if i > current_section['start']:
                        current_section['end'] = i - 1
                        sections.append(current_section.copy())
                    
                    current_section = {
                        'title': line.strip(),
                        'level': 2,
                        'start': i,
                        'content_start': i + 2
                    }
        
        # Add the last section
        current_section['end'] = len(lines) - 1
        sections.append(current_section)
        
        return sections
    
    def _extract_fenced_blocks(self, content: str, 
                              sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract fenced code blocks with triple backticks."""
        blocks = []
        
        for match in self.patterns['fenced_code'].finditer(content):
            language = match.group(1) or 'python'  # Default to Python
            code = match.group(2).strip()
            
            # Skip empty blocks
            if not code:
                continue
            
            # Find position in original content
            start_pos = match.start()
            end_pos = match.end()
            
            # Extract context
            context = self._extract_context(content, start_pos, end_pos, sections)
            
            blocks.append({
                'code': code,
                'language': language.lower(),
                'type': 'fenced',
                'position': start_pos,
                **context
            })
        
        return blocks
    
    def _extract_indented_blocks(self, content: str,
                                sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract indented code blocks (4 spaces or tab)."""
        blocks = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            # Check if line is indented
            if self._is_code_line(lines[i]):
                # Collect all consecutive indented lines
                code_lines = []
                start_line = i
                
                while i < len(lines) and (self._is_code_line(lines[i]) or not lines[i].strip()):
                    if lines[i].strip():  # Non-empty line
                        # Remove indentation
                        code_lines.append(self._remove_indent(lines[i]))
                    else:
                        code_lines.append('')
                    i += 1
                
                # Create code block if we have content
                code = '\n'.join(code_lines).strip()
                if code:
                    # Calculate position
                    position = sum(len(line) + 1 for line in lines[:start_line])
                    
                    # Extract context
                    context = self._extract_context_by_line(
                        lines, start_line, i - 1, sections
                    )
                    
                    blocks.append({
                        'code': code,
                        'language': 'python',  # Default for indented blocks
                        'type': 'indented',
                        'position': position,
                        **context
                    })
            else:
                i += 1
        
        return blocks
    
    def _is_code_line(self, line: str) -> bool:
        """Check if a line is indented (code block)."""
        return line.startswith('    ') or line.startswith('\t')
    
    def _remove_indent(self, line: str) -> str:
        """Remove code block indentation."""
        if line.startswith('    '):
            return line[4:]
        elif line.startswith('\t'):
            return line[1:]
        return line
    
    def _extract_context(self, content: str, start_pos: int, end_pos: int,
                        sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract context information around a code block."""
        # Find line numbers
        lines_before = content[:start_pos].count('\n')
        
        # Find section
        section_title = 'Unknown'
        section_level = 0
        
        for section in sections:
            if section['content_start'] <= lines_before <= section.get('end', float('inf')):
                section_title = section['title']
                section_level = section['level']
                break
        
        # Extract text before and after
        before_start = max(0, start_pos - 500)
        before_text = content[before_start:start_pos].strip()
        
        after_end = min(len(content), end_pos + 500)
        after_text = content[end_pos:after_end].strip()
        
        # Extract description from text before
        description = self._extract_description(before_text)
        
        # Extract keywords
        keywords = self._extract_keywords(before_text + ' ' + after_text)
        
        return {
            'section_title': section_title,
            'section_level': section_level,
            'before_text': before_text[-200:],  # Last 200 chars
            'after_text': after_text[:200],     # First 200 chars
            'description': description,
            'keywords': keywords
        }
    
    def _extract_context_by_line(self, lines: List[str], start_line: int,
                                end_line: int, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract context using line numbers."""
        # Find section
        section_title = 'Unknown'
        section_level = 0
        
        for section in sections:
            if section['content_start'] <= start_line <= section.get('end', float('inf')):
                section_title = section['title']
                section_level = section['level']
                break
        
        # Extract surrounding text
        before_start = max(0, start_line - 10)
        before_lines = lines[before_start:start_line]
        before_text = '\n'.join(before_lines).strip()
        
        after_end = min(len(lines), end_line + 10)
        after_lines = lines[end_line + 1:after_end]
        after_text = '\n'.join(after_lines).strip()
        
        # Extract description
        description = self._extract_description(before_text)
        
        # Extract keywords
        keywords = self._extract_keywords(before_text + ' ' + after_text)
        
        return {
            'section_title': section_title,
            'section_level': section_level,
            'before_text': before_text[-200:],
            'after_text': after_text[:200],
            'description': description,
            'keywords': keywords
        }
    
    def _extract_description(self, text: str) -> str:
        """Extract a description from the text before code."""
        if not text:
            return ""
        
        # Split into sentences
        sentences = re.split(r'[.!?]\s+', text)
        
        # Look for sentences that might describe code
        description_patterns = [
            r'(?:following|below|this|example|demonstrates|shows|implements)',
            r'(?:function|method|class|code|snippet|algorithm)',
            r'(?:to|for|that|which)\s+\w+'
        ]
        
        for sentence in reversed(sentences):  # Start from closest to code
            sentence = sentence.strip()
            if any(re.search(pattern, sentence, re.IGNORECASE) for pattern in description_patterns):
                return sentence
        
        # If no descriptive sentence found, use the last sentence
        if sentences:
            return sentences[-1].strip()
        
        return ""
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        # Remove Markdown formatting
        clean_text = text
        for pattern in [self.patterns['link'], self.patterns['bold'], 
                       self.patterns['italic'], self.patterns['inline_code']]:
            clean_text = pattern.sub(r'\1', clean_text)
        
        # Common words to exclude
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'this', 'that', 'these', 'those', 'it', 'its', 'their', 'our'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_text.lower())
        
        # Count frequency
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in keywords[:10]]