#!/usr/bin/env python3
"""
CodeSnippetBank CLI Tool
Command-line interface for discovering, testing, and deploying tissues
"""

import argparse
import json
import os
import sys
import time
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import shutil
import zipfile
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.tissue_discovery_api import TissueDiscoveryAPI
from tools.offline_tissue_pack_generator import TissuePackGenerator
from framework.quality.tissue_quality_framework import TissueQualityAnalyzer, EdgeDevice
from framework.versioning.tissue_versioning_system import TissueVersioningSystem


class TissueCLI:
    """Command-line interface for CodeSnippetBank"""
    
    def __init__(self):
        self.api = TissueDiscoveryAPI()
        self.pack_generator = TissuePackGenerator()
        self.quality_analyzer = TissueQualityAnalyzer()
        self.versioning = TissueVersioningSystem()
        
        # CLI configuration
        self.config_file = Path.home() / '.codebank' / 'config.json'
        self.cache_dir = Path.home() / '.codebank' / 'cache'
        self.load_config()
    
    def load_config(self):
        """Load CLI configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'default_device': 'raspberry_pi_4',
                'output_dir': str(Path.cwd()),
                'auto_update': True,
                'quality_threshold': 0.8
            }
            self.save_config()
    
    def save_config(self):
        """Save CLI configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def search_tissues(self, query: str, domain: Optional[str] = None, 
                      tags: Optional[List[str]] = None, limit: int = 10):
        """Search for tissues"""
        print(f"🔍 Searching for: '{query}'")
        if domain:
            print(f"   Domain: {domain}")
        if tags:
            print(f"   Tags: {', '.join(tags)}")
        print()
        
        results = self.api.search(query, domain=domain, tags=tags)[:limit]
        
        if not results:
            print("❌ No tissues found matching your criteria")
            return
        
        print(f"📋 Found {len(results)} tissue(s):\n")
        
        for i, tissue in enumerate(results, 1):
            print(f"{i}. {tissue['id']} - {tissue['name']}")
            print(f"   📁 Domain: {tissue['domain']}")
            print(f"   🏷️  Tags: {', '.join(tissue.get('tags', []))}")
            print(f"   ⭐ Quality: {tissue.get('quality_score', 0):.2f}")
            print(f"   📊 Performance: {tissue.get('performance', 'N/A')}")
            print()
    
    def show_tissue_details(self, tissue_id: str):
        """Show detailed information about a tissue"""
        print(f"📄 Tissue Details: {tissue_id}")
        print("="*60)
        
        # Get tissue metadata
        try:
            tissue = self.api.get_tissue_metadata(tissue_id)
        except Exception as e:
            print(f"❌ Error: Could not find tissue {tissue_id}")
            return
        
        # Basic information
        print(f"\n📋 Basic Information:")
        print(f"   Name: {tissue['name']}")
        print(f"   Domain: {tissue['domain']}")
        print(f"   Category: {tissue.get('category', 'general')}")
        print(f"   Version: {tissue.get('version', '1.0.0')}")
        print(f"   Tags: {', '.join(tissue.get('tags', []))}")
        
        # Quality metrics
        quality = tissue.get('quality_metrics', {})
        print(f"\n⭐ Quality Metrics:")
        print(f"   Overall Score: {quality.get('overall', 0):.2f}")
        print(f"   Performance: {quality.get('performance', 0):.2f}")
        print(f"   Memory: {quality.get('memory', 0):.2f}")
        print(f"   Edge Compatibility: {quality.get('edge_compatibility', 0):.2f}")
        
        # Performance data
        perf = tissue.get('performance_data', {})
        if perf:
            print(f"\n📊 Performance Benchmarks:")
            for device, metrics in perf.items():
                print(f"   {device}:")
                print(f"     • Time: {metrics.get('time', 'N/A')}")
                print(f"     • Memory: {metrics.get('memory', 'N/A')}")
        
        # Dependencies
        deps = tissue.get('dependencies', [])
        print(f"\n📦 Dependencies: {', '.join(deps) if deps else 'None (Pure Python)'}")
        
        # Usage example
        if tissue.get('example'):
            print(f"\n💡 Usage Example:")
            print("   ```python")
            for line in tissue['example'].split('\n'):
                print(f"   {line}")
            print("   ```")
        
        # Recent updates
        print(f"\n🔄 Recent Updates:")
        versions = self.versioning.get_version_history(tissue_id)[:3]
        for v in versions:
            print(f"   v{v['version']} - {v['date']} - {v.get('description', 'Update')}")
    
    def test_tissue(self, tissue_id: str, device: Optional[str] = None):
        """Test a tissue on specified device profile"""
        device = device or self.config['default_device']
        print(f"🧪 Testing tissue: {tissue_id}")
        print(f"📱 Device profile: {device}")
        print()
        
        # Get tissue code
        try:
            code = self.api.get_tissue_code(tissue_id)
        except Exception as e:
            print(f"❌ Error: Could not load tissue {tissue_id}")
            return
        
        # Create test environment
        test_file = self.cache_dir / f"test_{tissue_id}.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write test harness
        test_code = f"""
# Test harness for {tissue_id}
import time
import tracemalloc
import json

# Tissue code
{code}

# Test execution
def run_test():
    # Start monitoring
    tracemalloc.start()
    start_time = time.time()
    
    try:
        # Create test input
        test_input = create_test_input()
        
        # Run tissue function
        result = {tissue_id.lower().replace('-', '_')}(test_input)
        
        # Get metrics
        duration = (time.time() - start_time) * 1000
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {{
            'success': True,
            'result': result,
            'duration_ms': duration,
            'memory_mb': peak / 1024 / 1024
        }}
    except Exception as e:
        return {{
            'success': False,
            'error': str(e),
            'duration_ms': 0,
            'memory_mb': 0
        }}

def create_test_input():
    # Create appropriate test input based on tissue type
    import numpy as np
    if 'CV' in '{tissue_id}':
        return np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    elif 'NLP' in '{tissue_id}':
        return "This is a test sentence for natural language processing."
    else:
        return [1, 2, 3, 4, 5]

# Run test
if __name__ == "__main__":
    result = run_test()
    print(json.dumps(result))
"""
        
        with open(test_file, 'w') as f:
            f.write(test_code)
        
        # Run test
        print("🏃 Running test...")
        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                test_result = json.loads(result.stdout)
                
                if test_result['success']:
                    print(f"✅ Test passed!")
                    print(f"   ⏱️  Duration: {test_result['duration_ms']:.2f}ms")
                    print(f"   💾 Memory: {test_result['memory_mb']:.2f}MB")
                    
                    # Device-specific analysis
                    device_profile = getattr(EdgeDevice, device.upper(), None)
                    if device_profile:
                        if test_result['memory_mb'] * 1024 > device_profile.ram_mb:
                            print(f"   ⚠️  Warning: Memory usage exceeds {device} capacity")
                else:
                    print(f"❌ Test failed: {test_result['error']}")
            else:
                print(f"❌ Test error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ Test timeout (30s)")
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()
    
    def create_pack(self, tissue_ids: List[str], device: str, 
                   output: Optional[str] = None, optimize: bool = True):
        """Create tissue pack for deployment"""
        output = output or f"{device}_pack_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        print(f"📦 Creating tissue pack")
        print(f"   Tissues: {', '.join(tissue_ids)}")
        print(f"   Device: {device}")
        print(f"   Output: {output}")
        print(f"   Optimize: {'Yes' if optimize else 'No'}")
        print()
        
        # Validate tissues exist
        valid_tissues = []
        for tissue_id in tissue_ids:
            try:
                self.api.get_tissue_metadata(tissue_id)
                valid_tissues.append(tissue_id)
                print(f"   ✅ {tissue_id} - Found")
            except:
                print(f"   ❌ {tissue_id} - Not found")
        
        if not valid_tissues:
            print("\n❌ No valid tissues to pack")
            return
        
        print(f"\n🔨 Building pack with {len(valid_tissues)} tissues...")
        
        # Create pack
        pack_data = self.pack_generator.create_pack(
            valid_tissues,
            device_profile=device,
            optimize=optimize
        )
        
        # Save pack
        output_path = Path(self.config['output_dir']) / output
        self.pack_generator.save_pack(pack_data, str(output_path))
        
        # Show pack info
        pack_size = output_path.stat().st_size
        print(f"\n✅ Pack created successfully!")
        print(f"   📦 File: {output_path}")
        print(f"   📏 Size: {pack_size / 1024:.1f}KB")
        print(f"   🧬 Tissues: {len(valid_tissues)}")
        
        # Show deployment instructions
        self._show_deployment_instructions(device, output_path)
    
    def recommend_tissues(self, task: str, device: Optional[str] = None,
                         limit: int = 5):
        """Get tissue recommendations for a task"""
        device = device or self.config['default_device']
        
        print(f"🤖 Getting recommendations")
        print(f"   Task: {task}")
        print(f"   Device: {device}")
        print()
        
        context = {
            'task_type': task,
            'device': device,
            'optimize_for': 'edge'
        }
        
        recommendations = self.api.recommend_tissues(context)[:limit]
        
        if not recommendations:
            print("❌ No recommendations available")
            return
        
        print(f"💡 Recommended tissues:\n")
        
        for i, rec in enumerate(recommendations, 1):
            tissue = rec['tissue']
            print(f"{i}. {tissue['id']} - {tissue['name']}")
            print(f"   📊 Score: {rec['score']:.2f}")
            print(f"   💭 Reason: {rec['reason']}")
            
            # Check device compatibility
            perf = tissue.get('performance_data', {}).get(device, {})
            if perf:
                print(f"   ⚡ {device} performance: {perf.get('time', 'N/A')}")
            print()
    
    def update_tissues(self, tissue_ids: Optional[List[str]] = None,
                      risk_level: str = 'medium'):
        """Update tissues to latest versions"""
        print(f"🔄 Checking for tissue updates...")
        
        if tissue_ids:
            tissues_to_check = tissue_ids
        else:
            # Check all cached tissues
            tissues_to_check = self._get_cached_tissues()
        
        updates_available = []
        
        for tissue_id in tissues_to_check:
            try:
                current = self.versioning.get_current_version(tissue_id)
                latest = self.versioning.get_latest_version(tissue_id)
                
                if current != latest:
                    updates_available.append({
                        'tissue_id': tissue_id,
                        'current': current,
                        'latest': latest,
                        'risk': self.versioning.assess_upgrade_risk(
                            tissue_id, current, latest
                        )
                    })
            except:
                pass
        
        if not updates_available:
            print("✅ All tissues are up to date!")
            return
        
        print(f"\n📋 Updates available for {len(updates_available)} tissue(s):\n")
        
        for update in updates_available:
            print(f"• {update['tissue_id']}")
            print(f"  Current: v{update['current']} → Latest: v{update['latest']}")
            print(f"  Risk: {update['risk']['level']} - {update['risk']['reason']}")
            print()
        
        # Apply updates based on risk level
        if self.config['auto_update']:
            print(f"🚀 Auto-updating tissues with {risk_level} risk or lower...")
            
            for update in updates_available:
                if update['risk']['level'] in ['low', 'medium']:
                    if risk_level == 'low' and update['risk']['level'] != 'low':
                        continue
                    
                    print(f"\n📦 Updating {update['tissue_id']}...")
                    try:
                        self.versioning.upgrade_tissue(
                            update['tissue_id'],
                            update['latest']
                        )
                        print(f"✅ Updated to v{update['latest']}")
                    except Exception as e:
                        print(f"❌ Update failed: {str(e)}")
    
    def show_stats(self):
        """Show usage statistics"""
        print("📊 CodeSnippetBank Statistics")
        print("="*60)
        
        stats = self.api.get_statistics()
        
        print(f"\n🧬 Tissue Library:")
        print(f"   Total tissues: {stats['total_tissues']}")
        print(f"   By domain:")
        for domain, count in stats['by_domain'].items():
            print(f"     • {domain}: {count}")
        
        print(f"\n📈 Usage Stats:")
        print(f"   Total accesses: {stats['total_accesses']}")
        print(f"   Average quality: {stats['average_quality']:.2f}")
        
        print(f"\n🔥 Most Popular:")
        for i, tissue in enumerate(stats['most_popular'][:5], 1):
            print(f"   {i}. {tissue['id']} ({tissue['access_count']} uses)")
        
        print(f"\n⭐ Highest Quality:")
        for i, tissue in enumerate(stats['highest_quality'][:5], 1):
            print(f"   {i}. {tissue['id']} (score: {tissue['quality_score']:.2f})")
    
    def _show_deployment_instructions(self, device: str, pack_file: Path):
        """Show device-specific deployment instructions"""
        print(f"\n📚 Deployment Instructions for {device}:")
        print("-"*40)
        
        instructions = {
            'esp32': """
1. Convert pack to MicroPython format:
   python tools/esp32_converter.py {pack}
   
2. Flash to ESP32:
   esptool.py write_flash 0x200000 {pack}.bin
   
3. Use in your code:
   from tissue_loader import load_tissue
   tissue = load_tissue('TISSUE-ID')
""",
            'raspberry_pi': """
1. Copy pack to device:
   scp {pack} pi@raspberrypi:/opt/tissues/
   
2. Extract on device:
   ssh pi@raspberrypi
   cd /opt/tissues && unzip {pack}
   
3. Use in your code:
   from tissue_runtime import TissueRuntime
   runtime = TissueRuntime('/opt/tissues')
""",
            'mobile': """
1. Add to your app assets:
   cp {pack} app/src/main/assets/
   
2. Load in React Native:
   import {{ TissueLoader }} from 'tissue-runtime';
   const loader = new TissueLoader();
   await loader.loadPack('assets/{pack}');
   
3. Use tissues:
   const result = await loader.runTissue('TISSUE-ID', input);
"""
        }
        
        device_key = device.replace('_', '').lower()
        for key, template in instructions.items():
            if key in device_key:
                print(template.format(pack=pack_file.name))
                return
        
        # Generic instructions
        print(f"""
1. Copy pack to device:
   scp {pack_file.name} user@device:/path/to/tissues/
   
2. Extract pack:
   unzip {pack_file.name}
   
3. Load tissues as needed
""")
    
    def _get_cached_tissues(self) -> List[str]:
        """Get list of cached tissue IDs"""
        # In real implementation, would check local cache
        return ['CV-TISSUE-001', 'NLP-TISSUE-001', 'ML-TISSUE-001']


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='CodeSnippetBank CLI - Manage and deploy code tissues',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for tissues
  tissue search "edge detection"
  tissue search "face" --domain cv --limit 5
  
  # Get tissue details
  tissue info CV-TISSUE-001
  
  # Test tissue
  tissue test CV-TISSUE-005 --device esp32
  
  # Create deployment pack
  tissue pack CV-TISSUE-001 CV-TISSUE-005 --device raspberry_pi
  
  # Get recommendations
  tissue recommend "privacy camera" --device rpi4
  
  # Update tissues
  tissue update --risk low
  
  # Show statistics
  tissue stats
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for tissues')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--domain', help='Filter by domain (cv, nlp, ml)')
    search_parser.add_argument('--tags', nargs='+', help='Filter by tags')
    search_parser.add_argument('--limit', type=int, default=10, help='Number of results')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show tissue details')
    info_parser.add_argument('tissue_id', help='Tissue ID')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test a tissue')
    test_parser.add_argument('tissue_id', help='Tissue ID')
    test_parser.add_argument('--device', help='Device profile')
    
    # Pack command
    pack_parser = subparsers.add_parser('pack', help='Create deployment pack')
    pack_parser.add_argument('tissues', nargs='+', help='Tissue IDs')
    pack_parser.add_argument('--device', required=True, help='Target device')
    pack_parser.add_argument('--output', help='Output filename')
    pack_parser.add_argument('--no-optimize', action='store_true', help='Skip optimization')
    
    # Recommend command
    rec_parser = subparsers.add_parser('recommend', help='Get recommendations')
    rec_parser.add_argument('task', help='Task description')
    rec_parser.add_argument('--device', help='Target device')
    rec_parser.add_argument('--limit', type=int, default=5, help='Number of recommendations')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update tissues')
    update_parser.add_argument('tissues', nargs='*', help='Specific tissues to update')
    update_parser.add_argument('--risk', choices=['low', 'medium', 'high'], 
                              default='medium', help='Maximum risk level')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configure CLI')
    config_parser.add_argument('key', nargs='?', help='Config key')
    config_parser.add_argument('value', nargs='?', help='Config value')
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = TissueCLI()
    
    # Execute command
    if args.command == 'search':
        cli.search_tissues(args.query, domain=args.domain, 
                          tags=args.tags, limit=args.limit)
    
    elif args.command == 'info':
        cli.show_tissue_details(args.tissue_id)
    
    elif args.command == 'test':
        cli.test_tissue(args.tissue_id, device=args.device)
    
    elif args.command == 'pack':
        cli.create_pack(args.tissues, args.device, 
                       output=args.output, optimize=not args.no_optimize)
    
    elif args.command == 'recommend':
        cli.recommend_tissues(args.task, device=args.device, limit=args.limit)
    
    elif args.command == 'update':
        cli.update_tissues(args.tissues or None, risk_level=args.risk)
    
    elif args.command == 'stats':
        cli.show_stats()
    
    elif args.command == 'config':
        if args.key and args.value:
            cli.config[args.key] = args.value
            cli.save_config()
            print(f"✅ Set {args.key} = {args.value}")
        elif args.key:
            print(f"{args.key} = {cli.config.get(args.key, 'Not set')}")
        else:
            print("Current configuration:")
            for key, value in cli.config.items():
                print(f"  {key}: {value}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()