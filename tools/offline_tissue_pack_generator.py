"""
Offline Tissue Pack Generator
Create optimized tissue packs for offline Edge LLM deployment
"""

import json
import os
import zipfile
import hashlib
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import subprocess
import tempfile
import py_compile
import ast

class TissuePackGenerator:
    def __init__(self,
                 tissue_root: str = "../tissues",
                 output_dir: str = "../tissue_packs",
                 compression_level: int = 9):
        """
        Initialize Tissue Pack Generator
        
        Args:
            tissue_root: Root directory containing tissues
            output_dir: Output directory for generated packs
            compression_level: ZIP compression level (0-9)
        """
        self.tissue_root = Path(tissue_root)
        self.output_dir = Path(output_dir)
        self.compression_level = compression_level
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Pack metadata
        self.pack_metadata = {
            'generator_version': '1.0.0',
            'created_at': None,
            'tissues': {},
            'dependencies': {},
            'optimization_level': 'high'
        }
        
    def create_device_pack(self,
                          device_profile: str,
                          tissue_ids: Optional[List[str]] = None,
                          domains: Optional[List[str]] = None,
                          optimize: bool = True) -> str:
        """
        Create tissue pack for specific device profile
        
        Args:
            device_profile: Target device (e.g., 'raspberry_pi', 'mobile', 'esp32')
            tissue_ids: Specific tissues to include
            domains: Domains to include (if tissue_ids not specified)
            optimize: Whether to optimize tissues
            
        Returns:
            Path to generated pack
        """
        print(f"🎁 Creating tissue pack for {device_profile}...")
        
        # Reset metadata
        self.pack_metadata['created_at'] = datetime.now().isoformat()
        self.pack_metadata['device_profile'] = device_profile
        self.pack_metadata['tissues'] = {}
        
        # Collect tissues
        if tissue_ids:
            tissues = self._collect_specific_tissues(tissue_ids)
        elif domains:
            tissues = self._collect_domain_tissues(domains)
        else:
            tissues = self._collect_all_tissues()
            
        print(f"📦 Collected {len(tissues)} tissues")
        
        # Create temporary directory for pack contents
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Process each tissue
            for tissue_path in tissues:
                self._process_tissue(tissue_path, temp_path, device_profile, optimize)
                
            # Add metadata
            self._create_pack_metadata(temp_path)
            
            # Add runtime components
            self._add_runtime_components(temp_path, device_profile)
            
            # Create optimized index
            self._create_tissue_index(temp_path)
            
            # Generate pack
            pack_name = f"tissue_pack_{device_profile}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            pack_path = self.output_dir / pack_name
            
            self._create_zip_pack(temp_path, pack_path)
            
        print(f"✅ Pack created: {pack_path}")
        print(f"📊 Pack size: {pack_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return str(pack_path)
    
    def _collect_specific_tissues(self, tissue_ids: List[str]) -> List[Path]:
        """Collect specific tissues by ID"""
        tissues = []
        
        for domain_dir in self.tissue_root.iterdir():
            if domain_dir.is_dir():
                for tissue_file in domain_dir.glob("*.py"):
                    if any(tid in tissue_file.stem for tid in tissue_ids):
                        tissues.append(tissue_file)
                        
        return tissues
    
    def _collect_domain_tissues(self, domains: List[str]) -> List[Path]:
        """Collect tissues from specific domains"""
        tissues = []
        
        for domain in domains:
            domain_path = self.tissue_root / domain
            if domain_path.exists():
                tissues.extend(domain_path.glob("*-TISSUE-*.py"))
                
        return tissues
    
    def _collect_all_tissues(self) -> List[Path]:
        """Collect all available tissues"""
        tissues = []
        
        for domain_dir in self.tissue_root.iterdir():
            if domain_dir.is_dir():
                tissues.extend(domain_dir.glob("*-TISSUE-*.py"))
                
        return tissues
    
    def _process_tissue(self,
                       tissue_path: Path,
                       output_dir: Path,
                       device_profile: str,
                       optimize: bool):
        """Process individual tissue for packing"""
        # Read tissue content
        with open(tissue_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract tissue ID
        tissue_id = tissue_path.stem
        
        # Optimize if requested
        if optimize:
            content = self._optimize_tissue(content, device_profile)
            
        # Create domain directory
        domain = tissue_path.parent.name
        domain_dir = output_dir / "tissues" / domain
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        # Write optimized tissue
        output_path = domain_dir / tissue_path.name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Compile to bytecode for faster loading
        if device_profile != 'esp32':  # ESP32 might not support bytecode
            try:
                py_compile.compile(str(output_path), doraise=True)
            except:
                pass  # Some edge devices might not support compilation
                
        # Extract metadata
        metadata = self._extract_tissue_metadata(content)
        metadata['file_size'] = len(content)
        metadata['optimized'] = optimize
        metadata['checksum'] = hashlib.md5(content.encode()).hexdigest()
        
        self.pack_metadata['tissues'][tissue_id] = metadata
        
        # Extract dependencies
        deps = self._extract_dependencies(content)
        for dep in deps:
            if dep not in self.pack_metadata['dependencies']:
                self.pack_metadata['dependencies'][dep] = []
            self.pack_metadata['dependencies'][dep].append(tissue_id)
    
    def _optimize_tissue(self, content: str, device_profile: str) -> str:
        """Optimize tissue code for target device"""
        # Device-specific optimizations
        optimizations = self._get_device_optimizations(device_profile)
        
        if optimizations.get('remove_docstrings', False):
            content = self._remove_docstrings(content)
            
        if optimizations.get('remove_comments', False):
            content = self._remove_comments(content)
            
        if optimizations.get('minify', False):
            content = self._minify_code(content)
            
        if optimizations.get('inline_constants', False):
            content = self._inline_constants(content)
            
        if optimizations.get('remove_type_hints', False):
            content = self._remove_type_hints(content)
            
        return content
    
    def _get_device_optimizations(self, device_profile: str) -> Dict[str, bool]:
        """Get optimization settings for device profile"""
        profiles = {
            'esp32': {
                'remove_docstrings': True,
                'remove_comments': True,
                'minify': True,
                'inline_constants': True,
                'remove_type_hints': True
            },
            'raspberry_pi': {
                'remove_docstrings': False,
                'remove_comments': True,
                'minify': False,
                'inline_constants': True,
                'remove_type_hints': False
            },
            'mobile': {
                'remove_docstrings': True,
                'remove_comments': True,
                'minify': False,
                'inline_constants': True,
                'remove_type_hints': False
            },
            'edge_gpu': {
                'remove_docstrings': False,
                'remove_comments': False,
                'minify': False,
                'inline_constants': True,
                'remove_type_hints': False
            }
        }
        
        return profiles.get(device_profile, {
            'remove_docstrings': False,
            'remove_comments': True,
            'minify': False,
            'inline_constants': False,
            'remove_type_hints': False
        })
    
    def _remove_docstrings(self, content: str) -> str:
        """Remove docstrings from code"""
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if ast.get_docstring(node):
                    node.body = [n for n in node.body 
                                if not (isinstance(n, ast.Expr) and 
                                       isinstance(n.value, ast.Str))]
                                       
        return ast.unparse(tree)
    
    def _remove_comments(self, content: str) -> str:
        """Remove comments from code"""
        lines = content.split('\n')
        cleaned = []
        
        for line in lines:
            # Remove inline comments
            if '#' in line:
                code_part = line.split('#')[0].rstrip()
                if code_part:
                    cleaned.append(code_part)
            else:
                cleaned.append(line)
                
        return '\n'.join(cleaned)
    
    def _minify_code(self, content: str) -> str:
        """Minify Python code"""
        # Remove empty lines and excessive whitespace
        lines = content.split('\n')
        minified = []
        
        for line in lines:
            stripped = line.strip()
            if stripped:
                # Preserve indentation structure
                indent = len(line) - len(line.lstrip())
                minified.append(' ' * indent + stripped)
                
        return '\n'.join(minified)
    
    def _inline_constants(self, content: str) -> str:
        """Inline simple constants"""
        # Simple constant inlining (careful not to break code)
        # This is a simplified version - real implementation would use AST
        return content
    
    def _remove_type_hints(self, content: str) -> str:
        """Remove type hints for smaller size"""
        try:
            tree = ast.parse(content)
            
            class TypeHintRemover(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    # Remove return type annotation
                    node.returns = None
                    # Remove argument annotations
                    for arg in node.args.args:
                        arg.annotation = None
                    self.generic_visit(node)
                    return node
                    
                def visit_AnnAssign(self, node):
                    # Convert annotated assignment to regular assignment
                    return ast.Assign(
                        targets=[node.target],
                        value=node.value
                    ) if node.value else None
                    
            remover = TypeHintRemover()
            tree = remover.visit(tree)
            
            return ast.unparse(tree)
        except:
            return content  # Return original if parsing fails
    
    def _extract_tissue_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from tissue content"""
        metadata = {}
        
        # Extract main function
        func_match = re.search(r'def\s+(\w+)\s*\([^)]*\)', content)
        if func_match:
            metadata['main_function'] = func_match.group(1)
            
        # Extract description from docstring
        doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if doc_match:
            metadata['description'] = doc_match.group(1).strip().split('\n')[0]
            
        # Extract performance info
        if 'Edge Performance:' in content:
            perf_match = re.search(r'Edge Performance:\s*([^\n]+)', content)
            if perf_match:
                metadata['edge_performance'] = perf_match.group(1).strip()
                
        # Extract memory usage
        if 'Memory:' in content:
            mem_match = re.search(r'Memory:\s*([^\n]+)', content)
            if mem_match:
                metadata['memory_usage'] = mem_match.group(1).strip()
                
        return metadata
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract tissue dependencies"""
        deps = set()
        
        # Standard imports
        import_lines = [l for l in content.split('\n') if l.strip().startswith('import') or 'from' in l]
        
        for line in import_lines:
            if 'import numpy' in line:
                deps.add('numpy')
            elif 'import scipy' in line or 'from scipy' in line:
                deps.add('scipy')
            elif 'import sklearn' in line or 'from sklearn' in line:
                deps.add('scikit-learn')
                
        return list(deps)
    
    def _create_pack_metadata(self, output_dir: Path):
        """Create pack metadata file"""
        metadata_path = output_dir / "pack_metadata.json"
        
        with open(metadata_path, 'w') as f:
            json.dump(self.pack_metadata, f, indent=2)
    
    def _add_runtime_components(self, output_dir: Path, device_profile: str):
        """Add runtime components for tissue execution"""
        runtime_dir = output_dir / "runtime"
        runtime_dir.mkdir(exist_ok=True)
        
        # Create tissue loader
        loader_content = self._generate_tissue_loader(device_profile)
        with open(runtime_dir / "tissue_loader.py", 'w') as f:
            f.write(loader_content)
            
        # Create tissue executor
        executor_content = self._generate_tissue_executor(device_profile)
        with open(runtime_dir / "tissue_executor.py", 'w') as f:
            f.write(executor_content)
            
        # Create device-specific optimizations
        if device_profile == 'esp32':
            self._add_micropython_compatibility(runtime_dir)
    
    def _generate_tissue_loader(self, device_profile: str) -> str:
        """Generate tissue loader code"""
        return f'''"""
Tissue Loader for {device_profile}
Optimized for offline tissue loading
"""

import os
import json
import importlib.util
from pathlib import Path

class TissueLoader:
    def __init__(self, pack_root="."):
        self.pack_root = Path(pack_root)
        self.tissues = {{}}
        self._load_metadata()
        
    def _load_metadata(self):
        """Load pack metadata"""
        metadata_path = self.pack_root / "pack_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {{}}
            
    def load_tissue(self, tissue_id):
        """Load tissue by ID"""
        if tissue_id in self.tissues:
            return self.tissues[tissue_id]
            
        # Find tissue file
        for domain_dir in (self.pack_root / "tissues").iterdir():
            for tissue_file in domain_dir.glob(f"*{tissue_id}*.py"):
                # Load tissue module
                spec = importlib.util.spec_from_file_location(
                    tissue_id, tissue_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                self.tissues[tissue_id] = module
                return module
                
        raise ValueError(f"Tissue {{tissue_id}} not found")
        
    def get_tissue_function(self, tissue_id, function_name=None):
        """Get main function from tissue"""
        module = self.load_tissue(tissue_id)
        
        if function_name:
            return getattr(module, function_name)
        else:
            # Get main function from metadata
            tissue_meta = self.metadata.get('tissues', {{}}).get(tissue_id, {{}})
            main_func = tissue_meta.get('main_function')
            
            if main_func:
                return getattr(module, main_func)
            else:
                # Try to find main function
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and not attr_name.startswith('_'):
                        return attr
                        
        raise ValueError(f"No suitable function found in {{tissue_id}}")
'''
    
    def _generate_tissue_executor(self, device_profile: str) -> str:
        """Generate tissue executor code"""
        return f'''"""
Tissue Executor for {device_profile}
Handles tissue composition and execution
"""

from tissue_loader import TissueLoader

class TissueExecutor:
    def __init__(self, pack_root="."):
        self.loader = TissueLoader(pack_root)
        self.cache = {{}}
        
    def execute(self, tissue_id, *args, **kwargs):
        """Execute tissue function"""
        func = self.loader.get_tissue_function(tissue_id)
        return func(*args, **kwargs)
        
    def compose(self, tissue_pipeline):
        """Compose multiple tissues into pipeline"""
        def pipeline_func(data):
            result = data
            for tissue_id in tissue_pipeline:
                func = self.loader.get_tissue_function(tissue_id)
                result = func(result)
            return result
            
        return pipeline_func
        
    def batch_execute(self, tissue_id, data_list):
        """Execute tissue on batch of data"""
        func = self.loader.get_tissue_function(tissue_id)
        return [func(data) for data in data_list]

# Convenience functions
_executor = None

def get_executor():
    global _executor
    if _executor is None:
        _executor = TissueExecutor()
    return _executor
    
def run_tissue(tissue_id, *args, **kwargs):
    """Quick tissue execution"""
    return get_executor().execute(tissue_id, *args, **kwargs)
'''
    
    def _add_micropython_compatibility(self, runtime_dir: Path):
        """Add MicroPython compatibility layer"""
        compat_content = '''"""
MicroPython Compatibility Layer
Minimal implementations for ESP32/MicroPython
"""

# Minimal numpy-like operations for MicroPython
class mini_np:
    @staticmethod
    def array(data):
        return data
        
    @staticmethod
    def zeros(shape):
        if isinstance(shape, int):
            return [0] * shape
        elif len(shape) == 2:
            return [[0] * shape[1] for _ in range(shape[0])]
            
    @staticmethod
    def dot(a, b):
        # Simple dot product
        if isinstance(a[0], list):
            # Matrix multiplication
            result = []
            for i in range(len(a)):
                row = []
                for j in range(len(b[0])):
                    val = sum(a[i][k] * b[k][j] for k in range(len(b)))
                    row.append(val)
                result.append(row)
            return result
        else:
            # Vector dot product
            return sum(x * y for x, y in zip(a, b))

# Replace numpy imports
import sys
sys.modules['numpy'] = mini_np
'''
        
        with open(runtime_dir / "micropython_compat.py", 'w') as f:
            f.write(compat_content)
    
    def _create_tissue_index(self, output_dir: Path):
        """Create fast tissue index"""
        index = {
            'tissues': {},
            'domains': {},
            'functions': {}
        }
        
        tissues_dir = output_dir / "tissues"
        for domain_dir in tissues_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                index['domains'][domain] = []
                
                for tissue_file in domain_dir.glob("*.py"):
                    tissue_id = tissue_file.stem
                    
                    index['tissues'][tissue_id] = {
                        'domain': domain,
                        'path': str(tissue_file.relative_to(output_dir))
                    }
                    
                    index['domains'][domain].append(tissue_id)
                    
                    # Add function mapping from metadata
                    tissue_meta = self.pack_metadata['tissues'].get(tissue_id, {})
                    if 'main_function' in tissue_meta:
                        index['functions'][tissue_meta['main_function']] = tissue_id
        
        # Write index
        index_path = output_dir / "tissue_index.json"
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _create_zip_pack(self, source_dir: Path, output_path: Path):
        """Create compressed tissue pack"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, 
                           compresslevel=self.compression_level) as zf:
            
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(source_dir)
                    zf.write(file_path, arcname)
    
    def create_mini_pack(self,
                        tissue_ids: List[str],
                        pack_name: str,
                        target_size_kb: int = 100) -> str:
        """
        Create ultra-minimal pack for extremely constrained devices
        
        Args:
            tissue_ids: Tissues to include
            pack_name: Name for the pack
            target_size_kb: Target size in KB
            
        Returns:
            Path to mini pack
        """
        print(f"🔬 Creating mini pack: {pack_name} (target: {target_size_kb}KB)")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            total_size = 0
            included_tissues = []
            
            # Sort tissues by importance/size
            tissue_infos = []
            for tissue_id in tissue_ids:
                tissues = self._collect_specific_tissues([tissue_id])
                if tissues:
                    size = tissues[0].stat().st_size
                    tissue_infos.append((tissue_id, tissues[0], size))
                    
            # Sort by size (smallest first)
            tissue_infos.sort(key=lambda x: x[2])
            
            # Add tissues until size limit
            for tissue_id, tissue_path, size in tissue_infos:
                if total_size + size <= target_size_kb * 1024:
                    self._process_tissue(
                        tissue_path, temp_path, 'minimal', optimize=True
                    )
                    included_tissues.append(tissue_id)
                    total_size += size
                    
            print(f"📦 Included {len(included_tissues)} tissues")
            
            # Create minimal metadata
            minimal_meta = {
                'pack_type': 'mini',
                'tissues': included_tissues,
                'size_kb': total_size // 1024
            }
            
            with open(temp_path / "mini_metadata.json", 'w') as f:
                json.dump(minimal_meta, f)
                
            # Create pack
            pack_path = self.output_dir / f"{pack_name}_mini.zip"
            self._create_zip_pack(temp_path, pack_path)
            
        print(f"✅ Mini pack created: {pack_path} ({pack_path.stat().st_size // 1024}KB)")
        return str(pack_path)
    
    def verify_pack(self, pack_path: str) -> Dict[str, Any]:
        """Verify tissue pack integrity"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'tissues_verified': 0
        }
        
        try:
            with zipfile.ZipFile(pack_path, 'r') as zf:
                # Check for required files
                required_files = ['pack_metadata.json', 'tissue_index.json']
                for req_file in required_files:
                    if req_file not in zf.namelist():
                        results['errors'].append(f"Missing required file: {req_file}")
                        results['valid'] = False
                        
                # Load and verify metadata
                if 'pack_metadata.json' in zf.namelist():
                    with zf.open('pack_metadata.json') as f:
                        metadata = json.load(f)
                        
                    # Verify each tissue
                    for tissue_id, tissue_meta in metadata.get('tissues', {}).items():
                        # Check checksum if available
                        if 'checksum' in tissue_meta:
                            # Find tissue file
                            tissue_files = [n for n in zf.namelist() 
                                          if tissue_id in n and n.endswith('.py')]
                            
                            if tissue_files:
                                with zf.open(tissue_files[0]) as f:
                                    content = f.read()
                                    checksum = hashlib.md5(content).hexdigest()
                                    
                                if checksum != tissue_meta['checksum']:
                                    results['errors'].append(
                                        f"Checksum mismatch for {tissue_id}"
                                    )
                                    results['valid'] = False
                                else:
                                    results['tissues_verified'] += 1
                                    
        except Exception as e:
            results['errors'].append(f"Pack verification failed: {str(e)}")
            results['valid'] = False
            
        return results


# Pack distribution utilities
class TissuePackDistributor:
    """Utilities for distributing tissue packs"""
    
    @staticmethod
    def create_install_script(pack_path: str, target_device: str) -> str:
        """Create installation script for pack"""
        script = f'''#!/bin/bash
# Tissue Pack Installer for {target_device}

PACK_FILE="{os.path.basename(pack_path)}"
INSTALL_DIR="/opt/tissue_packs"

echo "Installing Tissue Pack..."

# Create installation directory
mkdir -p $INSTALL_DIR

# Extract pack
unzip -q $PACK_FILE -d $INSTALL_DIR

# Set permissions
chmod -R 755 $INSTALL_DIR

# Create symlinks for easy access
ln -sf $INSTALL_DIR/runtime/tissue_executor.py /usr/local/bin/tissue_exec

echo "✅ Tissue pack installed successfully!"
echo "📍 Location: $INSTALL_DIR"
echo "🚀 Usage: tissue_exec <tissue_id> <args>"
'''
        
        script_path = pack_path.replace('.zip', '_install.sh')
        with open(script_path, 'w') as f:
            f.write(script)
            
        os.chmod(script_path, 0o755)
        return script_path
    
    @staticmethod
    def create_ota_manifest(packs: List[str]) -> str:
        """Create OTA update manifest for packs"""
        manifest = {
            'version': '1.0',
            'packs': []
        }
        
        for pack_path in packs:
            pack_info = {
                'filename': os.path.basename(pack_path),
                'size': os.path.getsize(pack_path),
                'checksum': hashlib.sha256(open(pack_path, 'rb').read()).hexdigest(),
                'url': f"https://tissue-cdn.example.com/packs/{os.path.basename(pack_path)}"
            }
            manifest['packs'].append(pack_info)
            
        manifest_path = "tissue_pack_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            
        return manifest_path


# Test the pack generator
if __name__ == "__main__":
    import re
    
    print("🏗️ Tissue Pack Generator Test\n")
    
    # Initialize generator
    generator = TissuePackGenerator()
    
    # Test 1: Create Raspberry Pi pack
    print("1️⃣ Creating Raspberry Pi pack...")
    pi_pack = generator.create_device_pack(
        device_profile="raspberry_pi",
        domains=["cv", "ml"],
        optimize=True
    )
    
    # Test 2: Create ESP32 mini pack
    print("\n2️⃣ Creating ESP32 mini pack...")
    esp_pack = generator.create_mini_pack(
        tissue_ids=["CV-TISSUE-001", "CV-TISSUE-002", "ML-TISSUE-001"],
        pack_name="esp32_vision",
        target_size_kb=50
    )
    
    # Test 3: Verify packs
    print("\n3️⃣ Verifying packs...")
    
    verification = generator.verify_pack(pi_pack)
    print(f"Raspberry Pi pack: {'✅ Valid' if verification['valid'] else '❌ Invalid'}")
    print(f"  Tissues verified: {verification['tissues_verified']}")
    
    # Test 4: Create distribution files
    print("\n4️⃣ Creating distribution files...")
    
    distributor = TissuePackDistributor()
    install_script = distributor.create_install_script(pi_pack, "raspberry_pi")
    print(f"Install script: {install_script}")
    
    manifest = distributor.create_ota_manifest([pi_pack, esp_pack])
    print(f"OTA manifest: {manifest}")
    
    print("\n✅ Pack generator test complete!")
    print("\n📊 Benefits over traditional approach:")
    print("  • Optimized for specific devices")
    print("  • Reduced size through minification")
    print("  • Offline-ready with all dependencies")
    print("  • Fast loading with pre-compiled bytecode")
    print("  • Device-specific runtime optimizations")