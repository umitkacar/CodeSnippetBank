"""
Biological Code Organization - Tissue Model

This module implements the biological tissue model for code organization:
Cell (Function) → Tissue (Snippet) → System (LLM combines tissues)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import hashlib
import json
from enum import Enum

from .models import CodeSnippet, SnippetMetadata


class TissueType(Enum):
    """Types of code tissues based on biological element model"""
    STRUCTURAL = "structural"    # Like Carbon - forms backbone
    FUNCTIONAL = "functional"    # Like Nitrogen - specific operations  
    CONNECTIVE = "connective"    # Like Hydrogen - connects components
    ENERGETIC = "energetic"      # Like Oxygen - provides performance


@dataclass
class TissueDNA:
    """
    Genetic information for a tissue - defines its characteristics
    and hereditary traits that persist across translations/mutations
    """
    lineage: str  # Origin tracking (e.g., "opencv_v4.5")
    mutations: List[str] = field(default_factory=list)  # Evolution history
    fitness_score: float = 1.0  # Performance in ecosystem (0-1)
    
    # Hereditary traits
    complexity: Dict[str, str] = field(default_factory=dict)  # {"time": "O(n)", "space": "O(1)"}
    error_handling: str = "basic"  # basic, robust, comprehensive
    thread_safety: bool = False
    memory_safety: bool = True
    
    # Environmental adaptation
    tested_environments: List[str] = field(default_factory=list)  # ["edge", "cloud", "mobile"]
    compatible_tissues: List[str] = field(default_factory=list)  # Can combine with these tissues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DNA to dictionary for serialization"""
        return {
            "lineage": self.lineage,
            "mutations": self.mutations,
            "fitness_score": self.fitness_score,
            "complexity": self.complexity,
            "error_handling": self.error_handling,
            "thread_safety": self.thread_safety,
            "memory_safety": self.memory_safety,
            "tested_environments": self.tested_environments,
            "compatible_tissues": self.compatible_tissues
        }


@dataclass
class Tissue:
    """
    A Tissue is a specialized CodeSnippet with biological properties.
    It represents a cohesive unit of functionality that can bond with other tissues.
    """
    id: str
    name: str
    type: TissueType
    snippet: CodeSnippet
    dna: TissueDNA
    
    # Bonding properties
    bonds_available: int = 1  # How many connections it can make
    bond_types: List[str] = field(default_factory=list)  # ["input", "output", "bidirectional"]
    compatible_tissues: List[str] = field(default_factory=list)
    
    # Translation support
    base_language: str = "python"
    translatable: bool = True
    translations: Dict[str, str] = field(default_factory=dict)  # {"cpp": "code...", "rust": "code..."}
    
    # Health metrics
    usage_count: int = 0
    error_rate: float = 0.0
    last_evolved: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Initialize tissue-specific properties"""
        # Set bonds based on tissue type
        if self.type == TissueType.STRUCTURAL:
            self.bonds_available = 4  # Like Carbon
        elif self.type == TissueType.FUNCTIONAL:
            self.bonds_available = 3  # Like Nitrogen
        elif self.type == TissueType.CONNECTIVE:
            self.bonds_available = 1  # Like Hydrogen
        elif self.type == TissueType.ENERGETIC:
            self.bonds_available = 2  # Like Oxygen
    
    def can_bond_with(self, other: 'Tissue') -> bool:
        """Check if this tissue can bond with another"""
        # Check if we have available bonds
        if self.bonds_available <= 0 or other.bonds_available <= 0:
            return False
        
        # Check compatibility
        if other.id in self.compatible_tissues:
            return True
        
        # Check type compatibility rules
        compatibility_rules = {
            TissueType.STRUCTURAL: [TissueType.FUNCTIONAL, TissueType.CONNECTIVE, TissueType.ENERGETIC],
            TissueType.FUNCTIONAL: [TissueType.STRUCTURAL, TissueType.CONNECTIVE, TissueType.ENERGETIC],
            TissueType.CONNECTIVE: [TissueType.STRUCTURAL, TissueType.FUNCTIONAL],  # Bonds with all
            TissueType.ENERGETIC: [TissueType.STRUCTURAL, TissueType.FUNCTIONAL]
        }
        
        return other.type in compatibility_rules.get(self.type, [])
    
    def translate_to(self, target_language: str, translator: Optional[Callable] = None) -> str:
        """Translate this tissue to another programming language"""
        # Check if translation already exists
        if target_language in self.translations:
            return self.translations[target_language]
        
        if not self.translatable:
            raise ValueError(f"Tissue {self.id} is not translatable")
        
        if translator:
            # Use provided translator (e.g., LLM)
            translated_code = translator(self.snippet.code, self.base_language, target_language)
            self.translations[target_language] = translated_code
            return translated_code
        
        raise ValueError(f"No translator provided for {target_language}")
    
    def evolve(self, improvement: str, reason: str) -> 'Tissue':
        """Create an evolved version of this tissue"""
        # Create new DNA with mutation record
        new_dna = TissueDNA(
            lineage=self.dna.lineage,
            mutations=self.dna.mutations + [f"{datetime.now().isoformat()}: {reason}"],
            fitness_score=self.dna.fitness_score * 1.1,  # Assume improvement
            complexity=self.dna.complexity,
            error_handling=self.dna.error_handling,
            thread_safety=self.dna.thread_safety,
            memory_safety=self.dna.memory_safety,
            tested_environments=self.dna.tested_environments,
            compatible_tissues=self.dna.compatible_tissues
        )
        
        # Create evolved snippet
        evolved_snippet = CodeSnippet(
            metadata=self.snippet.metadata,
            description=self.snippet.description,
            code=improvement,
            example_usage=self.snippet.example_usage,
            tests=self.snippet.tests
        )
        
        # Create new tissue
        return Tissue(
            id=f"{self.id}_v{len(self.dna.mutations)+2}",
            name=self.name,
            type=self.type,
            snippet=evolved_snippet,
            dna=new_dna,
            compatible_tissues=self.compatible_tissues,
            base_language=self.base_language,
            translatable=self.translatable
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tissue to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "snippet": self.snippet.to_dict(),
            "dna": self.dna.to_dict(),
            "bonds_available": self.bonds_available,
            "bond_types": self.bond_types,
            "compatible_tissues": self.compatible_tissues,
            "base_language": self.base_language,
            "translatable": self.translatable,
            "translations": self.translations,
            "usage_count": self.usage_count,
            "error_rate": self.error_rate,
            "last_evolved": self.last_evolved.isoformat()
        }


class TissueFactory:
    """Factory for creating tissues from code snippets"""
    
    @staticmethod
    def create_tissue(
        snippet: CodeSnippet,
        tissue_type: TissueType,
        lineage: str,
        compatible_with: List[str] = None
    ) -> Tissue:
        """Create a tissue from a code snippet"""
        
        # Extract complexity from snippet metadata
        complexity = {}
        if snippet.metadata.time_complexity:
            complexity["time"] = snippet.metadata.time_complexity
        if snippet.metadata.space_complexity:
            complexity["space"] = snippet.metadata.space_complexity
        
        # Create DNA
        dna = TissueDNA(
            lineage=lineage,
            complexity=complexity,
            error_handling="robust" if "error" in snippet.code.lower() else "basic",
            thread_safety="thread" in snippet.code.lower() or "lock" in snippet.code.lower(),
            memory_safety=True,  # Assume Python is memory safe
            tested_environments=["python", "edge"]
        )
        
        # Create tissue
        tissue = Tissue(
            id=f"TISSUE-{snippet.metadata.snippet_id}",
            name=snippet.metadata.title.lower().replace(" ", "_"),
            type=tissue_type,
            snippet=snippet,
            dna=dna,
            compatible_tissues=compatible_with or []
        )
        
        return tissue
    
    @staticmethod
    def determine_tissue_type(snippet: CodeSnippet) -> TissueType:
        """Automatically determine tissue type from snippet characteristics"""
        
        code_lower = snippet.code.lower()
        category_lower = snippet.metadata.category.lower()
        
        # Structural: Classes, frameworks, configuration
        if any(keyword in code_lower for keyword in ["class ", "framework", "config", "setup"]):
            return TissueType.STRUCTURAL
        
        # Energetic: Async, parallel, performance
        elif any(keyword in code_lower for keyword in ["async", "thread", "parallel", "cache", "optimize"]):
            return TissueType.ENERGETIC
        
        # Connective: Adapters, bridges, converters
        elif any(keyword in category_lower for keyword in ["adapter", "bridge", "converter", "wrapper"]):
            return TissueType.CONNECTIVE
        
        # Functional: Default for most operations
        else:
            return TissueType.FUNCTIONAL


class TissueCatalog:
    """Catalog for managing and discovering tissues"""
    
    def __init__(self):
        self.tissues: Dict[str, Tissue] = {}
        self.categories: Dict[str, List[str]] = {}  # category -> tissue_ids
        self.type_index: Dict[TissueType, List[str]] = {t: [] for t in TissueType}
    
    def add_tissue(self, tissue: Tissue) -> None:
        """Add a tissue to the catalog"""
        self.tissues[tissue.id] = tissue
        
        # Update category index
        category = tissue.snippet.metadata.category
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(tissue.id)
        
        # Update type index
        self.type_index[tissue.type].append(tissue.id)
    
    def find_by_category(self, category: str) -> List[Tissue]:
        """Find all tissues in a category"""
        tissue_ids = self.categories.get(category, [])
        return [self.tissues[tid] for tid in tissue_ids if tid in self.tissues]
    
    def find_by_type(self, tissue_type: TissueType) -> List[Tissue]:
        """Find all tissues of a specific type"""
        tissue_ids = self.type_index.get(tissue_type, [])
        return [self.tissues[tid] for tid in tissue_ids if tid in self.tissues]
    
    def find_compatible(self, tissue: Tissue) -> List[Tissue]:
        """Find tissues compatible with the given tissue"""
        compatible = []
        for tid in tissue.compatible_tissues:
            if tid in self.tissues:
                compatible.append(self.tissues[tid])
        return compatible
    
    def search(self, query: str) -> List[Tissue]:
        """Search tissues by name, description, or tags"""
        results = []
        query_lower = query.lower()
        
        for tissue in self.tissues.values():
            if (query_lower in tissue.name.lower() or
                query_lower in tissue.snippet.description.lower() or
                any(query_lower in tag for tag in tissue.snippet.metadata.tags)):
                results.append(tissue)
        
        return results