"""
Tissue Catalog System - Discovery and Management for Code Tissues

This module provides a comprehensive catalog system for managing,
discovering, and organizing tissue components.
"""

import json
import os
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re

try:
    from .biological import Tissue, TissueType
    from .models import SnippetDifficulty
except ImportError:
    # For standalone testing
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.biological import Tissue, TissueType
    from core.models import SnippetDifficulty


@dataclass
class TissueMetrics:
    """Performance and usage metrics for a tissue"""
    usage_count: int = 0
    avg_execution_time: float = 0.0
    success_rate: float = 1.0
    last_used: Optional[datetime] = None
    user_ratings: List[float] = field(default_factory=list)
    
    @property
    def avg_rating(self) -> float:
        """Calculate average user rating"""
        return sum(self.user_ratings) / len(self.user_ratings) if self.user_ratings else 0.0


@dataclass
class TissueRelationship:
    """Defines relationships between tissues"""
    tissue_id: str
    relationship_type: str  # "requires", "enhances", "replaces", "conflicts"
    strength: float = 1.0  # 0-1, how strong the relationship is
    notes: str = ""


class TissueCatalog:
    """
    Central catalog for all tissue management and discovery.
    Provides search, recommendation, and dependency resolution.
    """
    
    def __init__(self, tissue_root: str = "tissues"):
        self.tissue_root = Path(tissue_root)
        self.tissues: Dict[str, Tissue] = {}
        self.metrics: Dict[str, TissueMetrics] = {}
        self.relationships: Dict[str, List[TissueRelationship]] = {}
        
        # Indexes for fast lookup
        self.category_index: Dict[str, Set[str]] = {}
        self.tag_index: Dict[str, Set[str]] = {}
        self.type_index: Dict[TissueType, Set[str]] = {}
        self.difficulty_index: Dict[SnippetDifficulty, Set[str]] = {}
        
        # Load catalog
        self._load_catalog()
    
    def _load_catalog(self):
        """Load all tissues from the filesystem"""
        if not self.tissue_root.exists():
            self.tissue_root.mkdir(parents=True, exist_ok=True)
            return
        
        # Scan for tissue files
        for tissue_file in self.tissue_root.rglob("*-TISSUE-*.py"):
            try:
                tissue = self._load_tissue_from_file(tissue_file)
                if tissue:
                    self.add_tissue(tissue)
            except Exception as e:
                print(f"Error loading tissue {tissue_file}: {e}")
    
    def _load_tissue_from_file(self, file_path: Path) -> Optional[Tissue]:
        """Load a tissue from a Python file"""
        # Parse tissue metadata from file header
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata using regex
        tissue_id_match = re.search(r'Tissue ID:\s*(\S+)', content)
        title_match = re.search(r'Title:\s*(.+)', content)
        category_match = re.search(r'Category:\s*(.+)', content)
        tags_match = re.search(r'Tags:\s*\[(.*?)\]', content, re.DOTALL)
        difficulty_match = re.search(r'Difficulty:\s*(\w+)', content)
        type_match = re.search(r'Tissue Type:\s*(\w+)', content)
        
        if not (tissue_id_match and title_match):
            return None
        
        # Create tissue object (simplified for catalog)
        # In production, would properly parse and instantiate
        tissue_data = {
            "id": tissue_id_match.group(1),
            "name": title_match.group(1),
            "file_path": str(file_path),
            "category": category_match.group(1) if category_match else "uncategorized",
            "tags": [tag.strip().strip('"') for tag in tags_match.group(1).split(',')] if tags_match else [],
            "difficulty": difficulty_match.group(1) if difficulty_match else "Intermediate",
            "type": type_match.group(1) if type_match else "FUNCTIONAL"
        }
        
        # For now, return tissue data as dict
        # In full implementation, would create proper Tissue object
        return tissue_data
    
    def add_tissue(self, tissue: Any):
        """Add a tissue to the catalog"""
        tissue_id = tissue.get('id') if isinstance(tissue, dict) else tissue.id
        
        # Store tissue
        self.tissues[tissue_id] = tissue
        
        # Initialize metrics
        if tissue_id not in self.metrics:
            self.metrics[tissue_id] = TissueMetrics()
        
        # Update indexes
        self._update_indexes(tissue)
    
    def _update_indexes(self, tissue: Any):
        """Update search indexes"""
        if isinstance(tissue, dict):
            tissue_id = tissue['id']
            category = tissue.get('category', 'uncategorized')
            tags = tissue.get('tags', [])
            difficulty = tissue.get('difficulty', 'Intermediate')
            tissue_type = tissue.get('type', 'FUNCTIONAL')
        else:
            tissue_id = tissue.id
            category = tissue.snippet.metadata.category
            tags = tissue.snippet.metadata.tags
            difficulty = tissue.snippet.metadata.difficulty
            tissue_type = tissue.type
        
        # Category index
        if category not in self.category_index:
            self.category_index[category] = set()
        self.category_index[category].add(tissue_id)
        
        # Tag index
        for tag in tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(tissue_id)
        
        # Type index (simplified for dict)
        if isinstance(tissue_type, str):
            tissue_type = tissue_type.upper()
            if tissue_type not in self.type_index:
                self.type_index[tissue_type] = set()
            self.type_index[tissue_type].add(tissue_id)
        
        # Difficulty index
        if isinstance(difficulty, str):
            if difficulty not in self.difficulty_index:
                self.difficulty_index[difficulty] = set()
            self.difficulty_index[difficulty].add(tissue_id)
    
    def search(self, 
              query: Optional[str] = None,
              category: Optional[str] = None,
              tags: Optional[List[str]] = None,
              tissue_type: Optional[str] = None,
              difficulty: Optional[str] = None,
              limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for tissues based on various criteria.
        
        Returns list of tissue info with relevance scores.
        """
        results = []
        all_tissue_ids = set(self.tissues.keys())
        
        # Filter by category
        if category:
            all_tissue_ids &= self.category_index.get(category, set())
        
        # Filter by tags (ANY match)
        if tags:
            tag_matches = set()
            for tag in tags:
                tag_matches |= self.tag_index.get(tag, set())
            all_tissue_ids &= tag_matches
        
        # Filter by type
        if tissue_type:
            all_tissue_ids &= self.type_index.get(tissue_type.upper(), set())
        
        # Filter by difficulty
        if difficulty:
            all_tissue_ids &= self.difficulty_index.get(difficulty, set())
        
        # Text search in tissue metadata
        if query:
            query_lower = query.lower()
            scored_results = []
            
            for tissue_id in all_tissue_ids:
                tissue = self.tissues[tissue_id]
                score = self._calculate_relevance_score(tissue, query_lower)
                if score > 0:
                    scored_results.append((tissue_id, score))
            
            # Sort by relevance
            scored_results.sort(key=lambda x: x[1], reverse=True)
            all_tissue_ids = [tid for tid, _ in scored_results[:limit]]
        
        # Build results
        for tissue_id in list(all_tissue_ids)[:limit]:
            tissue = self.tissues[tissue_id]
            metrics = self.metrics.get(tissue_id, TissueMetrics())
            
            result = {
                "id": tissue_id,
                "tissue": tissue,
                "metrics": metrics,
                "relevance": 1.0  # Default relevance
            }
            results.append(result)
        
        return results
    
    def _calculate_relevance_score(self, tissue: Any, query: str) -> float:
        """Calculate relevance score for text search"""
        score = 0.0
        
        # Extract searchable fields
        if isinstance(tissue, dict):
            name = tissue.get('name', '').lower()
            tags = ' '.join(tissue.get('tags', [])).lower()
            category = tissue.get('category', '').lower()
            tissue_id = tissue.get('id', '').lower()
        else:
            name = tissue.name.lower()
            tags = ' '.join(tissue.snippet.metadata.tags).lower()
            category = tissue.snippet.metadata.category.lower()
            tissue_id = tissue.id.lower()
        
        # Score based on matches
        if query in tissue_id:
            score += 10.0
        if query in name:
            score += 5.0
        if query in tags:
            score += 3.0
        if query in category:
            score += 2.0
        
        return score
    
    def get_recommendations(self, tissue_id: str, limit: int = 5) -> List[str]:
        """Get recommended tissues based on relationships and usage patterns"""
        recommendations = []
        
        # Get related tissues
        relationships = self.relationships.get(tissue_id, [])
        for rel in relationships:
            if rel.relationship_type in ["enhances", "requires"]:
                recommendations.append(rel.tissue_id)
        
        # Get tissues from same category
        tissue = self.tissues.get(tissue_id)
        if tissue:
            category = tissue.get('category') if isinstance(tissue, dict) else tissue.snippet.metadata.category
            similar = self.category_index.get(category, set())
            recommendations.extend(similar - {tissue_id})
        
        # Remove duplicates and limit
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen and rec in self.tissues:
                seen.add(rec)
                unique_recommendations.append(rec)
                if len(unique_recommendations) >= limit:
                    break
        
        return unique_recommendations
    
    def add_relationship(self, tissue_id: str, relationship: TissueRelationship):
        """Add a relationship between tissues"""
        if tissue_id not in self.relationships:
            self.relationships[tissue_id] = []
        self.relationships[tissue_id].append(relationship)
    
    def update_metrics(self, tissue_id: str, 
                      execution_time: Optional[float] = None,
                      success: Optional[bool] = None,
                      rating: Optional[float] = None):
        """Update tissue metrics after usage"""
        if tissue_id not in self.metrics:
            self.metrics[tissue_id] = TissueMetrics()
        
        metrics = self.metrics[tissue_id]
        metrics.usage_count += 1
        metrics.last_used = datetime.now()
        
        if execution_time is not None:
            # Running average
            metrics.avg_execution_time = (
                (metrics.avg_execution_time * (metrics.usage_count - 1) + execution_time) 
                / metrics.usage_count
            )
        
        if success is not None:
            # Update success rate
            total_attempts = metrics.usage_count
            successful = int(metrics.success_rate * (total_attempts - 1))
            if success:
                successful += 1
            metrics.success_rate = successful / total_attempts
        
        if rating is not None:
            metrics.user_ratings.append(rating)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get catalog statistics"""
        total_tissues = len(self.tissues)
        total_categories = len(self.category_index)
        total_tags = len(self.tag_index)
        
        # Most used tissues
        most_used = sorted(
            [(tid, m.usage_count) for tid, m in self.metrics.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Highest rated tissues
        rated_tissues = [(tid, m.avg_rating) for tid, m in self.metrics.items() if m.user_ratings]
        highest_rated = sorted(rated_tissues, key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_tissues": total_tissues,
            "total_categories": total_categories,
            "total_tags": total_tags,
            "categories": list(self.category_index.keys()),
            "most_used_tissues": most_used,
            "highest_rated_tissues": highest_rated,
            "total_usage": sum(m.usage_count for m in self.metrics.values())
        }
    
    def export_catalog(self, output_path: str):
        """Export catalog metadata to JSON"""
        catalog_data = {
            "tissues": {tid: self._tissue_to_dict(t) for tid, t in self.tissues.items()},
            "metrics": {tid: self._metrics_to_dict(m) for tid, m in self.metrics.items()},
            "relationships": {tid: [self._relationship_to_dict(r) for r in rels] 
                            for tid, rels in self.relationships.items()},
            "statistics": self.get_statistics(),
            "export_date": datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(catalog_data, f, indent=2)
    
    def _tissue_to_dict(self, tissue: Any) -> Dict[str, Any]:
        """Convert tissue to dictionary for export"""
        if isinstance(tissue, dict):
            return tissue
        else:
            return tissue.to_dict()
    
    def _metrics_to_dict(self, metrics: TissueMetrics) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "usage_count": metrics.usage_count,
            "avg_execution_time": metrics.avg_execution_time,
            "success_rate": metrics.success_rate,
            "last_used": metrics.last_used.isoformat() if metrics.last_used else None,
            "avg_rating": metrics.avg_rating,
            "rating_count": len(metrics.user_ratings)
        }
    
    def _relationship_to_dict(self, rel: TissueRelationship) -> Dict[str, Any]:
        """Convert relationship to dictionary"""
        return {
            "tissue_id": rel.tissue_id,
            "type": rel.relationship_type,
            "strength": rel.strength,
            "notes": rel.notes
        }


# Convenience functions
def create_catalog(tissue_root: str = "tissues") -> TissueCatalog:
    """Create and initialize a tissue catalog"""
    return TissueCatalog(tissue_root)


def search_tissues(query: str, catalog: Optional[TissueCatalog] = None) -> List[Dict[str, Any]]:
    """Quick search function"""
    if catalog is None:
        catalog = create_catalog()
    return catalog.search(query=query)


# Example usage
if __name__ == "__main__":
    # Create catalog
    catalog = create_catalog()
    
    # Search examples
    print("Computer Vision tissues:")
    cv_tissues = catalog.search(category="computer_vision")
    for result in cv_tissues[:5]:
        print(f"  - {result['id']}: {result['tissue'].get('name', 'Unknown')}")
    
    # Get statistics
    stats = catalog.get_statistics()
    print(f"\nCatalog Statistics:")
    print(f"  Total tissues: {stats['total_tissues']}")
    print(f"  Categories: {', '.join(stats['categories'][:5])}...")
    
    # Export catalog
    catalog.export_catalog("tissue_catalog.json")
    print("\nCatalog exported to tissue_catalog.json")