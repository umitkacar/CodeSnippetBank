"""
Tissue Versioning System
Advanced version control and evolution tracking for code tissues
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Set
from pathlib import Path
import difflib
import sqlite3
from dataclasses import dataclass, asdict
import semver
import shutil

@dataclass
class TissueVersion:
    """Represents a tissue version"""
    tissue_id: str
    version: str
    created_at: datetime
    author: str
    changes: List[str]
    performance_delta: Dict[str, float]
    quality_score: float
    breaking_changes: bool
    migration_notes: Optional[str] = None
    dependencies_changed: bool = False
    file_hash: Optional[str] = None

@dataclass
class VersionDiff:
    """Represents differences between versions"""
    from_version: str
    to_version: str
    additions: int
    deletions: int
    modifications: int
    performance_impact: Dict[str, float]
    api_changes: List[str]
    risk_level: str  # 'low', 'medium', 'high'

class TissueVersioningSystem:
    def __init__(self,
                 tissue_root: str = "../tissues",
                 version_db: str = "tissue_versions.db",
                 archive_dir: str = "../tissue_archive"):
        """
        Initialize Tissue Versioning System
        
        Args:
            tissue_root: Root directory for current tissues
            version_db: SQLite database for version tracking
            archive_dir: Directory for archived versions
        """
        self.tissue_root = Path(tissue_root)
        self.version_db = version_db
        self.archive_dir = Path(archive_dir)
        
        # Create directories
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Version comparison cache
        self._diff_cache = {}
        
    def _init_database(self):
        """Initialize version tracking database"""
        self.conn = sqlite3.connect(self.version_db)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Version history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tissue_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tissue_id TEXT NOT NULL,
                version TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                author TEXT NOT NULL,
                changes TEXT NOT NULL,
                performance_delta TEXT,
                quality_score REAL,
                breaking_changes BOOLEAN,
                migration_notes TEXT,
                dependencies_changed BOOLEAN,
                file_hash TEXT,
                file_content TEXT,
                UNIQUE(tissue_id, version)
            )
        """)
        
        # Version dependencies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS version_dependencies (
                version_id INTEGER,
                dependency_tissue_id TEXT,
                dependency_version TEXT,
                FOREIGN KEY (version_id) REFERENCES tissue_versions(id)
            )
        """)
        
        # Deployment history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deployment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tissue_id TEXT NOT NULL,
                version TEXT NOT NULL,
                device_profile TEXT,
                deployed_at TIMESTAMP,
                deployment_status TEXT,
                performance_metrics TEXT,
                rollback_version TEXT
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tissue_version ON tissue_versions(tissue_id, version)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deployment ON deployment_history(tissue_id, deployed_at)")
        
        self.conn.commit()
    
    def create_version(self,
                      tissue_id: str,
                      file_path: str,
                      author: str = "system",
                      changes: List[str] = None,
                      breaking_changes: bool = False,
                      migration_notes: Optional[str] = None) -> TissueVersion:
        """
        Create a new version of a tissue
        
        Args:
            tissue_id: Tissue identifier
            file_path: Path to tissue file
            author: Version author
            changes: List of changes
            breaking_changes: Whether version has breaking changes
            migration_notes: Notes for migration
            
        Returns:
            Created tissue version
        """
        # Read current tissue content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compute file hash
        file_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Get current version or start from 1.0.0
        current_version = self.get_latest_version(tissue_id)
        
        if current_version:
            # Determine version bump
            old_ver = semver.VersionInfo.parse(current_version.version)
            
            if breaking_changes:
                new_version = str(old_ver.bump_major())
            elif self._has_new_features(content, tissue_id):
                new_version = str(old_ver.bump_minor())
            else:
                new_version = str(old_ver.bump_patch())
                
            # Compute performance delta
            performance_delta = self._compute_performance_delta(
                tissue_id, current_version.version, content
            )
        else:
            new_version = "1.0.0"
            performance_delta = {}
        
        # Analyze quality
        quality_score = self._analyze_quality(content)
        
        # Check dependency changes
        dependencies_changed = self._check_dependency_changes(
            tissue_id, content, current_version
        )
        
        # Create version object
        version = TissueVersion(
            tissue_id=tissue_id,
            version=new_version,
            created_at=datetime.now(),
            author=author,
            changes=changes or ["Auto-generated version"],
            performance_delta=performance_delta,
            quality_score=quality_score,
            breaking_changes=breaking_changes,
            migration_notes=migration_notes,
            dependencies_changed=dependencies_changed,
            file_hash=file_hash
        )
        
        # Store version
        self._store_version(version, content)
        
        # Archive current version
        self._archive_tissue(tissue_id, new_version, file_path)
        
        return version
    
    def _has_new_features(self, content: str, tissue_id: str) -> bool:
        """Check if content has new features"""
        current = self.get_latest_version(tissue_id)
        if not current:
            return True
            
        # Get previous content
        old_content = self._get_version_content(tissue_id, current.version)
        
        # Simple heuristic: new functions or classes
        old_funcs = set(self._extract_functions(old_content))
        new_funcs = set(self._extract_functions(content))
        
        return len(new_funcs - old_funcs) > 0
    
    def _extract_functions(self, content: str) -> List[str]:
        """Extract function names from content"""
        import re
        pattern = r'def\s+(\w+)\s*\('
        return re.findall(pattern, content)
    
    def _compute_performance_delta(self,
                                  tissue_id: str,
                                  old_version: str,
                                  new_content: str) -> Dict[str, float]:
        """Compute performance changes between versions"""
        # Simplified - in practice would run benchmarks
        delta = {}
        
        # Check for optimization keywords
        if 'optimize' in new_content.lower() or 'fast' in new_content.lower():
            delta['speed_improvement'] = 0.15  # 15% faster
            
        # Check for memory improvements
        if 'memory' in new_content.lower() and 'efficient' in new_content.lower():
            delta['memory_reduction'] = 0.10  # 10% less memory
            
        return delta
    
    def _analyze_quality(self, content: str) -> float:
        """Analyze code quality"""
        score = 0.0
        
        # Documentation
        if '"""' in content:
            score += 0.2
            
        # Type hints
        if '->' in content and ':' in content:
            score += 0.2
            
        # Error handling
        if 'try:' in content:
            score += 0.1
            
        # Tests
        if '__main__' in content:
            score += 0.1
            
        # Comments
        comment_lines = len([l for l in content.split('\n') if l.strip().startswith('#')])
        if comment_lines > 5:
            score += 0.1
            
        # Code organization
        if 'class' in content:
            score += 0.1
            
        # Performance optimizations
        if any(keyword in content.lower() for keyword in ['cache', 'optimize', 'efficient']):
            score += 0.2
            
        return min(score, 1.0)
    
    def _check_dependency_changes(self,
                                 tissue_id: str,
                                 content: str,
                                 current_version: Optional[TissueVersion]) -> bool:
        """Check if dependencies have changed"""
        if not current_version:
            return False
            
        old_content = self._get_version_content(tissue_id, current_version.version)
        
        # Extract imports
        old_imports = set(self._extract_imports(old_content))
        new_imports = set(self._extract_imports(content))
        
        return old_imports != new_imports
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        import re
        imports = []
        
        # Standard imports
        imports.extend(re.findall(r'import\s+(\w+)', content))
        
        # From imports
        from_imports = re.findall(r'from\s+(\w+)\s+import', content)
        imports.extend(from_imports)
        
        return imports
    
    def _store_version(self, version: TissueVersion, content: str):
        """Store version in database"""
        cursor = self.conn.cursor()
        
        # Insert version
        cursor.execute("""
            INSERT INTO tissue_versions (
                tissue_id, version, created_at, author, changes,
                performance_delta, quality_score, breaking_changes,
                migration_notes, dependencies_changed, file_hash, file_content
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            version.tissue_id,
            version.version,
            version.created_at,
            version.author,
            json.dumps(version.changes),
            json.dumps(version.performance_delta),
            version.quality_score,
            version.breaking_changes,
            version.migration_notes,
            version.dependencies_changed,
            version.file_hash,
            content
        ))
        
        self.conn.commit()
    
    def _archive_tissue(self, tissue_id: str, version: str, file_path: str):
        """Archive tissue version"""
        # Create archive directory
        archive_path = self.archive_dir / tissue_id / version
        archive_path.mkdir(parents=True, exist_ok=True)
        
        # Copy tissue file
        shutil.copy2(file_path, archive_path / Path(file_path).name)
        
        # Create metadata file
        metadata = {
            'tissue_id': tissue_id,
            'version': version,
            'archived_at': datetime.now().isoformat(),
            'original_path': str(file_path)
        }
        
        with open(archive_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_latest_version(self, tissue_id: str) -> Optional[TissueVersion]:
        """Get latest version of a tissue"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM tissue_versions
            WHERE tissue_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (tissue_id,))
        
        row = cursor.fetchone()
        if row:
            return self._row_to_version(row)
        return None
    
    def get_version(self, tissue_id: str, version: str) -> Optional[TissueVersion]:
        """Get specific version of a tissue"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM tissue_versions
            WHERE tissue_id = ? AND version = ?
        """, (tissue_id, version))
        
        row = cursor.fetchone()
        if row:
            return self._row_to_version(row)
        return None
    
    def _row_to_version(self, row: sqlite3.Row) -> TissueVersion:
        """Convert database row to TissueVersion"""
        return TissueVersion(
            tissue_id=row['tissue_id'],
            version=row['version'],
            created_at=datetime.fromisoformat(row['created_at']),
            author=row['author'],
            changes=json.loads(row['changes']),
            performance_delta=json.loads(row['performance_delta'] or '{}'),
            quality_score=row['quality_score'],
            breaking_changes=bool(row['breaking_changes']),
            migration_notes=row['migration_notes'],
            dependencies_changed=bool(row['dependencies_changed']),
            file_hash=row['file_hash']
        )
    
    def get_version_history(self,
                           tissue_id: str,
                           limit: int = 10) -> List[TissueVersion]:
        """Get version history for a tissue"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM tissue_versions
            WHERE tissue_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (tissue_id, limit))
        
        return [self._row_to_version(row) for row in cursor]
    
    def _get_version_content(self, tissue_id: str, version: str) -> Optional[str]:
        """Get content of specific version"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT file_content FROM tissue_versions
            WHERE tissue_id = ? AND version = ?
        """, (tissue_id, version))
        
        row = cursor.fetchone()
        return row['file_content'] if row else None
    
    def compare_versions(self,
                        tissue_id: str,
                        version1: str,
                        version2: str) -> VersionDiff:
        """Compare two versions of a tissue"""
        # Check cache
        cache_key = f"{tissue_id}:{version1}:{version2}"
        if cache_key in self._diff_cache:
            return self._diff_cache[cache_key]
        
        # Get version contents
        content1 = self._get_version_content(tissue_id, version1)
        content2 = self._get_version_content(tissue_id, version2)
        
        if not content1 or not content2:
            raise ValueError(f"Version not found for {tissue_id}")
        
        # Compute diff
        lines1 = content1.splitlines()
        lines2 = content2.splitlines()
        
        differ = difflib.unified_diff(lines1, lines2)
        
        additions = 0
        deletions = 0
        modifications = 0
        
        for line in differ:
            if line.startswith('+') and not line.startswith('+++'):
                additions += 1
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1
                
        # Estimate modifications
        modifications = min(additions, deletions)
        additions -= modifications
        deletions -= modifications
        
        # Analyze API changes
        api_changes = self._analyze_api_changes(content1, content2)
        
        # Get performance impact
        v1_data = self.get_version(tissue_id, version1)
        v2_data = self.get_version(tissue_id, version2)
        
        performance_impact = v2_data.performance_delta if v2_data else {}
        
        # Assess risk level
        risk_level = self._assess_risk_level(
            api_changes, v2_data.breaking_changes if v2_data else False
        )
        
        diff = VersionDiff(
            from_version=version1,
            to_version=version2,
            additions=additions,
            deletions=deletions,
            modifications=modifications,
            performance_impact=performance_impact,
            api_changes=api_changes,
            risk_level=risk_level
        )
        
        # Cache result
        self._diff_cache[cache_key] = diff
        
        return diff
    
    def _analyze_api_changes(self, content1: str, content2: str) -> List[str]:
        """Analyze API changes between versions"""
        changes = []
        
        # Extract function signatures
        funcs1 = set(self._extract_function_signatures(content1))
        funcs2 = set(self._extract_function_signatures(content2))
        
        # Removed functions
        for func in funcs1 - funcs2:
            changes.append(f"Removed: {func}")
            
        # Added functions
        for func in funcs2 - funcs1:
            changes.append(f"Added: {func}")
            
        # TODO: Check for parameter changes in common functions
        
        return changes
    
    def _extract_function_signatures(self, content: str) -> List[str]:
        """Extract function signatures"""
        import re
        pattern = r'def\s+(\w+\s*\([^)]*\))'
        return re.findall(pattern, content)
    
    def _assess_risk_level(self,
                          api_changes: List[str],
                          breaking_changes: bool) -> str:
        """Assess risk level of version change"""
        if breaking_changes or any('Removed:' in change for change in api_changes):
            return 'high'
        elif len(api_changes) > 3:
            return 'medium'
        else:
            return 'low'
    
    def rollback(self,
                tissue_id: str,
                target_version: str,
                current_file_path: str) -> bool:
        """
        Rollback tissue to previous version
        
        Args:
            tissue_id: Tissue identifier
            target_version: Version to rollback to
            current_file_path: Current tissue file path
            
        Returns:
            Success status
        """
        # Get target version content
        content = self._get_version_content(tissue_id, target_version)
        
        if not content:
            return False
        
        # Backup current version
        backup_path = str(current_file_path) + '.backup'
        shutil.copy2(current_file_path, backup_path)
        
        try:
            # Write target version content
            with open(current_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Record rollback
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO deployment_history (
                    tissue_id, version, device_profile, deployed_at,
                    deployment_status, rollback_version
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tissue_id,
                target_version,
                'rollback',
                datetime.now(),
                'rolled_back',
                self.get_latest_version(tissue_id).version
            ))
            self.conn.commit()
            
            return True
            
        except Exception as e:
            # Restore from backup
            shutil.copy2(backup_path, current_file_path)
            raise e
        finally:
            # Clean up backup
            if os.path.exists(backup_path):
                os.remove(backup_path)
    
    def generate_migration_guide(self,
                                tissue_id: str,
                                from_version: str,
                                to_version: str) -> str:
        """Generate migration guide between versions"""
        # Get version diff
        diff = self.compare_versions(tissue_id, from_version, to_version)
        
        # Get version metadata
        to_version_data = self.get_version(tissue_id, to_version)
        
        guide = f"# Migration Guide: {tissue_id} v{from_version} → v{to_version}\n\n"
        
        # Risk assessment
        guide += f"## Risk Level: {diff.risk_level.upper()}\n\n"
        
        # Summary
        guide += "## Summary\n"
        guide += f"- Additions: {diff.additions} lines\n"
        guide += f"- Deletions: {diff.deletions} lines\n"
        guide += f"- Modifications: {diff.modifications} lines\n\n"
        
        # Performance impact
        if diff.performance_impact:
            guide += "## Performance Impact\n"
            for metric, delta in diff.performance_impact.items():
                sign = '+' if delta > 0 else ''
                guide += f"- {metric}: {sign}{delta*100:.1f}%\n"
            guide += "\n"
        
        # API changes
        if diff.api_changes:
            guide += "## API Changes\n"
            for change in diff.api_changes:
                guide += f"- {change}\n"
            guide += "\n"
        
        # Migration notes
        if to_version_data and to_version_data.migration_notes:
            guide += "## Migration Notes\n"
            guide += to_version_data.migration_notes + "\n\n"
        
        # Step-by-step guide
        guide += "## Migration Steps\n"
        
        if diff.risk_level == 'low':
            guide += "1. Update tissue reference to new version\n"
            guide += "2. Run tests to verify compatibility\n"
        elif diff.risk_level == 'medium':
            guide += "1. Review API changes above\n"
            guide += "2. Update code to accommodate changes\n"
            guide += "3. Test thoroughly before deployment\n"
        else:  # high risk
            guide += "1. **BREAKING CHANGES DETECTED**\n"
            guide += "2. Carefully review all API changes\n"
            guide += "3. Update all tissue usages\n"
            guide += "4. Consider gradual rollout\n"
            guide += "5. Have rollback plan ready\n"
        
        return guide
    
    def auto_upgrade(self,
                    tissue_id: str,
                    current_file_path: str,
                    max_risk: str = 'medium') -> Optional[TissueVersion]:
        """
        Automatically upgrade tissue to latest compatible version
        
        Args:
            tissue_id: Tissue identifier
            current_file_path: Current tissue file path
            max_risk: Maximum acceptable risk level
            
        Returns:
            Upgraded version or None if no safe upgrade
        """
        # Get current version
        with open(current_file_path, 'r') as f:
            current_content = f.read()
        current_hash = hashlib.sha256(current_content.encode()).hexdigest()
        
        # Find current version by hash
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT version FROM tissue_versions
            WHERE tissue_id = ? AND file_hash = ?
        """, (tissue_id, current_hash))
        
        row = cursor.fetchone()
        if not row:
            return None
            
        current_version = row['version']
        
        # Get all newer versions
        history = self.get_version_history(tissue_id)
        newer_versions = [v for v in history if semver.compare(v.version, current_version) > 0]
        
        # Find best upgrade candidate
        risk_levels = {'low': 0, 'medium': 1, 'high': 2}
        max_risk_level = risk_levels[max_risk]
        
        for version in newer_versions:
            diff = self.compare_versions(tissue_id, current_version, version.version)
            
            if risk_levels[diff.risk_level] <= max_risk_level:
                # Safe to upgrade
                content = self._get_version_content(tissue_id, version.version)
                
                with open(current_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                return version
                
        return None


# Version management utilities
class TissueVersionManager:
    """High-level version management interface"""
    
    def __init__(self, versioning_system: TissueVersioningSystem):
        self.vs = versioning_system
        
    def check_updates(self, tissue_manifest: Dict[str, str]) -> Dict[str, Any]:
        """
        Check for available updates
        
        Args:
            tissue_manifest: Dict of tissue_id -> current_version
            
        Returns:
            Update information
        """
        updates = {}
        
        for tissue_id, current_version in tissue_manifest.items():
            latest = self.vs.get_latest_version(tissue_id)
            
            if latest and semver.compare(latest.version, current_version) > 0:
                # Get upgrade path
                diff = self.vs.compare_versions(tissue_id, current_version, latest.version)
                
                updates[tissue_id] = {
                    'current': current_version,
                    'latest': latest.version,
                    'risk': diff.risk_level,
                    'performance_gain': diff.performance_impact,
                    'changes': latest.changes
                }
                
        return updates
    
    def bulk_upgrade(self,
                    tissue_paths: Dict[str, str],
                    max_risk: str = 'medium',
                    dry_run: bool = False) -> Dict[str, Any]:
        """
        Upgrade multiple tissues
        
        Args:
            tissue_paths: Dict of tissue_id -> file_path
            max_risk: Maximum acceptable risk
            dry_run: Preview changes without applying
            
        Returns:
            Upgrade results
        """
        results = {}
        
        for tissue_id, file_path in tissue_paths.items():
            if dry_run:
                # Just check what would happen
                current = self._get_file_version(tissue_id, file_path)
                latest = self.vs.get_latest_version(tissue_id)
                
                if latest and current:
                    diff = self.vs.compare_versions(tissue_id, current, latest.version)
                    
                    results[tissue_id] = {
                        'would_upgrade': diff.risk_level <= max_risk,
                        'from': current,
                        'to': latest.version,
                        'risk': diff.risk_level
                    }
            else:
                # Perform upgrade
                upgraded = self.vs.auto_upgrade(tissue_id, file_path, max_risk)
                
                results[tissue_id] = {
                    'upgraded': upgraded is not None,
                    'new_version': upgraded.version if upgraded else None
                }
                
        return results
    
    def _get_file_version(self, tissue_id: str, file_path: str) -> Optional[str]:
        """Get version of file by content hash"""
        with open(file_path, 'r') as f:
            content = f.read()
        file_hash = hashlib.sha256(content.encode()).hexdigest()
        
        cursor = self.vs.conn.cursor()
        cursor.execute("""
            SELECT version FROM tissue_versions
            WHERE tissue_id = ? AND file_hash = ?
        """, (tissue_id, file_hash))
        
        row = cursor.fetchone()
        return row['version'] if row else None


# Test the versioning system
if __name__ == "__main__":
    # Initialize system
    vs = TissueVersioningSystem()
    vm = TissueVersionManager(vs)
    
    print("🔄 Tissue Versioning System Test\n")
    
    # Test 1: Create initial version
    print("1. Creating initial version...")
    
    # Simulate tissue file
    test_tissue_path = "test_tissue.py"
    with open(test_tissue_path, 'w') as f:
        f.write("""
def process_data(data):
    '''Process data v1'''
    return data * 2
""")
    
    v1 = vs.create_version(
        tissue_id="TEST-TISSUE-001",
        file_path=test_tissue_path,
        author="developer",
        changes=["Initial version"]
    )
    
    print(f"Created version: {v1.version}")
    
    # Test 2: Create update with improvements
    print("\n2. Creating improved version...")
    
    with open(test_tissue_path, 'w') as f:
        f.write("""
def process_data(data, optimize=True):
    '''Process data v2 - now with optimization!'''
    if optimize:
        # Fast path
        return data * 2
    return data * 2

def process_batch(data_list):
    '''New feature: batch processing'''
    return [process_data(d) for d in data_list]
""")
    
    v2 = vs.create_version(
        tissue_id="TEST-TISSUE-001",
        file_path=test_tissue_path,
        author="developer",
        changes=["Added optimization option", "Added batch processing"]
    )
    
    print(f"Created version: {v2.version}")
    print(f"Quality score: {v2.quality_score:.2f}")
    
    # Test 3: Compare versions
    print("\n3. Comparing versions...")
    
    diff = vs.compare_versions("TEST-TISSUE-001", v1.version, v2.version)
    print(f"Changes: +{diff.additions} -{diff.deletions} ~{diff.modifications}")
    print(f"Risk level: {diff.risk_level}")
    print(f"API changes: {diff.api_changes}")
    
    # Test 4: Generate migration guide
    print("\n4. Generating migration guide...")
    
    guide = vs.generate_migration_guide("TEST-TISSUE-001", v1.version, v2.version)
    print(guide)
    
    # Clean up
    os.remove(test_tissue_path)
    os.remove(vs.version_db)
    shutil.rmtree(vs.archive_dir, ignore_errors=True)
    
    print("\n✅ Versioning system test complete!")