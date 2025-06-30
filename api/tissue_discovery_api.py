"""
Tissue Discovery API
Revolutionary API for discovering and accessing code tissues for Edge LLMs
"""

import json
import os
import sqlite3
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
import hashlib
from pathlib import Path
import re
from collections import defaultdict
import numpy as np

class TissueDiscoveryAPI:
    def __init__(self, 
                 tissue_root: str = "../tissues",
                 db_path: str = "tissue_index.db",
                 cache_size: int = 100):
        """
        Initialize Tissue Discovery API
        
        Args:
            tissue_root: Root directory containing tissues
            db_path: Path to SQLite database for indexing
            cache_size: Number of tissues to cache in memory
        """
        self.tissue_root = Path(tissue_root)
        self.db_path = db_path
        self.cache_size = cache_size
        
        # Memory cache for frequently accessed tissues
        self._tissue_cache = {}
        self._cache_access_count = defaultdict(int)
        
        # Initialize database
        self._init_database()
        
        # Build index if needed
        if self._needs_reindex():
            self.rebuild_index()
    
    def _init_database(self):
        """Initialize SQLite database for tissue indexing"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tissues (
                id TEXT PRIMARY KEY,
                domain TEXT NOT NULL,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                main_function TEXT NOT NULL,
                description TEXT,
                input_type TEXT,
                output_type TEXT,
                edge_performance TEXT,
                memory_usage TEXT,
                tags TEXT,
                dependencies TEXT,
                created_at TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                quality_score REAL DEFAULT 0.0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tissue_tags (
                tissue_id TEXT,
                tag TEXT,
                FOREIGN KEY (tissue_id) REFERENCES tissues(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tissue_embeddings (
                tissue_id TEXT PRIMARY KEY,
                embedding BLOB,
                FOREIGN KEY (tissue_id) REFERENCES tissues(id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_domain ON tissues(domain)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON tissue_tags(tag)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality ON tissues(quality_score DESC)")
        
        self.conn.commit()
    
    def _needs_reindex(self) -> bool:
        """Check if tissue index needs rebuilding"""
        cursor = self.conn.cursor()
        
        # Check if index is empty
        cursor.execute("SELECT COUNT(*) FROM tissues")
        count = cursor.fetchone()[0]
        
        if count == 0:
            return True
        
        # Check if tissue files have been modified
        cursor.execute("SELECT file_path, created_at FROM tissues")
        for row in cursor:
            file_path = Path(row['file_path'])
            if file_path.exists():
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                db_time = datetime.fromisoformat(row['created_at'])
                if file_mtime > db_time:
                    return True
            else:
                return True  # File missing
                
        return False
    
    def rebuild_index(self):
        """Rebuild the tissue index from files"""
        print("Rebuilding tissue index...")
        
        # Clear existing index
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tissues")
        cursor.execute("DELETE FROM tissue_tags")
        cursor.execute("DELETE FROM tissue_embeddings")
        
        # Scan tissue directories
        tissue_count = 0
        for domain_dir in self.tissue_root.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                
                for tissue_file in domain_dir.glob("*-TISSUE-*.py"):
                    tissue_data = self._parse_tissue_file(tissue_file, domain)
                    
                    if tissue_data:
                        self._index_tissue(tissue_data)
                        tissue_count += 1
        
        self.conn.commit()
        print(f"Indexed {tissue_count} tissues")
    
    def _parse_tissue_file(self, file_path: Path, domain: str) -> Optional[Dict[str, Any]]:
        """Parse tissue file and extract metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract tissue ID from filename
            match = re.search(r'(\w+-TISSUE-\d+)', file_path.stem)
            if not match:
                return None
                
            tissue_id = match.group(1)
            
            # Extract metadata from docstring and comments
            metadata = {
                'id': tissue_id,
                'domain': domain,
                'name': file_path.stem.replace('_', ' ').title(),
                'file_path': str(file_path.absolute()),
                'created_at': datetime.fromtimestamp(file_path.stat().st_mtime)
            }
            
            # Extract main function
            func_match = re.search(r'def\s+(\w+)\s*\([^)]*\)\s*->\s*([^:]+):', content)
            if func_match:
                metadata['main_function'] = func_match.group(1)
                metadata['output_type'] = func_match.group(2).strip()
            
            # Extract description from docstring
            doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if doc_match:
                description = doc_match.group(1).strip()
                metadata['description'] = description.split('\n')[0]
            
            # Extract tissue metadata from comments
            meta_match = re.search(r'Tissue Metadata:(.*?)"""', content, re.DOTALL)
            if meta_match:
                meta_text = meta_match.group(1)
                
                # Parse metadata fields
                for line in meta_text.split('\n'):
                    if 'Input:' in line:
                        metadata['input_type'] = line.split('Input:')[1].strip()
                    elif 'Output:' in line:
                        metadata['output_type'] = line.split('Output:')[1].strip()
                    elif 'Edge Performance:' in line:
                        metadata['edge_performance'] = line.split('Edge Performance:')[1].strip()
                    elif 'Memory:' in line:
                        metadata['memory_usage'] = line.split('Memory:')[1].strip()
            
            # Extract tags from content
            tags = self._extract_tags(content, domain)
            metadata['tags'] = json.dumps(tags)
            
            # Extract dependencies
            dependencies = self._extract_dependencies(content)
            metadata['dependencies'] = json.dumps(dependencies)
            
            # Compute quality score
            metadata['quality_score'] = self._compute_quality_score(metadata, content)
            
            return metadata
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _extract_tags(self, content: str, domain: str) -> List[str]:
        """Extract relevant tags from tissue content"""
        tags = [domain]
        
        # Common CV tags
        cv_keywords = ['edge', 'detection', 'segmentation', 'tracking', 'feature',
                      'transform', 'filter', 'histogram', 'morphology', 'optical']
        
        # Common NLP tags
        nlp_keywords = ['tokenize', 'embed', 'classify', 'sentiment', 'entity',
                       'summarize', 'translate', 'language', 'text', 'nlp']
        
        # Common ML tags
        ml_keywords = ['regression', 'classification', 'cluster', 'neural',
                      'ensemble', 'svm', 'decision', 'gaussian', 'pca']
        
        # Check for keywords
        content_lower = content.lower()
        for keyword in cv_keywords + nlp_keywords + ml_keywords:
            if keyword in content_lower:
                tags.append(keyword)
        
        return list(set(tags))
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract tissue dependencies"""
        dependencies = []
        
        # Look for numpy/scipy imports
        if 'import numpy' in content:
            dependencies.append('numpy')
        if 'import scipy' in content:
            dependencies.append('scipy')
        if 'from sklearn' in content:
            dependencies.append('sklearn')
            
        return dependencies
    
    def _compute_quality_score(self, metadata: Dict[str, Any], content: str) -> float:
        """Compute tissue quality score"""
        score = 0.0
        
        # Has documentation
        if metadata.get('description'):
            score += 0.2
            
        # Has metadata
        if metadata.get('edge_performance'):
            score += 0.2
        if metadata.get('memory_usage'):
            score += 0.2
            
        # Has type hints
        if '->' in content:
            score += 0.1
            
        # Has error handling
        if 'try:' in content or 'except' in content:
            score += 0.1
            
        # Has tests
        if '__main__' in content:
            score += 0.1
            
        # Code complexity (reasonable length)
        lines = content.split('\n')
        if 100 < len(lines) < 500:
            score += 0.1
            
        return min(score, 1.0)
    
    def _index_tissue(self, tissue_data: Dict[str, Any]):
        """Index tissue in database"""
        cursor = self.conn.cursor()
        
        # Insert tissue
        cursor.execute("""
            INSERT OR REPLACE INTO tissues (
                id, domain, name, file_path, main_function, description,
                input_type, output_type, edge_performance, memory_usage,
                tags, dependencies, created_at, quality_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tissue_data['id'],
            tissue_data['domain'],
            tissue_data['name'],
            tissue_data['file_path'],
            tissue_data.get('main_function', ''),
            tissue_data.get('description', ''),
            tissue_data.get('input_type', ''),
            tissue_data.get('output_type', ''),
            tissue_data.get('edge_performance', ''),
            tissue_data.get('memory_usage', ''),
            tissue_data.get('tags', '[]'),
            tissue_data.get('dependencies', '[]'),
            tissue_data['created_at'],
            tissue_data.get('quality_score', 0.0)
        ))
        
        # Insert tags
        tags = json.loads(tissue_data.get('tags', '[]'))
        for tag in tags:
            cursor.execute("""
                INSERT INTO tissue_tags (tissue_id, tag) VALUES (?, ?)
            """, (tissue_data['id'], tag))
        
        # Generate and store embedding (simplified)
        embedding = self._generate_embedding(tissue_data)
        cursor.execute("""
            INSERT OR REPLACE INTO tissue_embeddings (tissue_id, embedding)
            VALUES (?, ?)
        """, (tissue_data['id'], embedding.tobytes()))
    
    def _generate_embedding(self, tissue_data: Dict[str, Any]) -> np.ndarray:
        """Generate simple embedding for tissue (for semantic search)"""
        # Simplified embedding - in practice use proper text embeddings
        text = f"{tissue_data.get('name', '')} {tissue_data.get('description', '')} {tissue_data.get('tags', '')}"
        
        # Simple hash-based embedding
        hash_val = hashlib.md5(text.encode()).hexdigest()
        embedding = np.array([int(hash_val[i:i+2], 16) / 255.0 for i in range(0, 32, 2)])
        
        return embedding
    
    def search(self,
              query: str,
              domain: Optional[str] = None,
              tags: Optional[List[str]] = None,
              limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for tissues
        
        Args:
            query: Search query
            domain: Filter by domain
            tags: Filter by tags
            limit: Maximum results
            
        Returns:
            List of matching tissues
        """
        cursor = self.conn.cursor()
        
        # Build query
        sql = """
            SELECT DISTINCT t.* FROM tissues t
            LEFT JOIN tissue_tags tt ON t.id = tt.tissue_id
            WHERE 1=1
        """
        params = []
        
        # Add filters
        if domain:
            sql += " AND t.domain = ?"
            params.append(domain)
            
        if tags:
            placeholders = ','.join(['?' for _ in tags])
            sql += f" AND tt.tag IN ({placeholders})"
            params.extend(tags)
            
        if query:
            sql += """ AND (
                t.name LIKE ? OR 
                t.description LIKE ? OR
                t.main_function LIKE ?
            )"""
            query_pattern = f"%{query}%"
            params.extend([query_pattern, query_pattern, query_pattern])
        
        # Order by relevance and quality
        sql += " ORDER BY t.quality_score DESC, t.access_count DESC"
        sql += f" LIMIT {limit}"
        
        cursor.execute(sql, params)
        
        results = []
        for row in cursor:
            tissue_dict = dict(row)
            tissue_dict['tags'] = json.loads(tissue_dict.get('tags', '[]'))
            tissue_dict['dependencies'] = json.loads(tissue_dict.get('dependencies', '[]'))
            results.append(tissue_dict)
            
        return results
    
    def semantic_search(self,
                       query: str,
                       domain: Optional[str] = None,
                       threshold: float = 0.7,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Semantic search using embeddings
        
        Args:
            query: Search query
            domain: Filter by domain
            threshold: Similarity threshold
            limit: Maximum results
            
        Returns:
            List of matching tissues with similarity scores
        """
        # Generate query embedding
        query_data = {'name': query, 'description': query, 'tags': ''}
        query_embedding = self._generate_embedding(query_data)
        
        cursor = self.conn.cursor()
        
        # Get all embeddings
        sql = """
            SELECT t.*, e.embedding FROM tissues t
            JOIN tissue_embeddings e ON t.id = e.tissue_id
        """
        params = []
        
        if domain:
            sql += " WHERE t.domain = ?"
            params.append(domain)
            
        cursor.execute(sql, params)
        
        # Compute similarities
        results = []
        for row in cursor:
            tissue_dict = dict(row)
            
            # Decode embedding
            tissue_embedding = np.frombuffer(tissue_dict['embedding'], dtype=np.float64)
            
            # Compute cosine similarity
            similarity = np.dot(query_embedding, tissue_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(tissue_embedding) + 1e-6
            )
            
            if similarity >= threshold:
                tissue_dict['similarity'] = float(similarity)
                tissue_dict['tags'] = json.loads(tissue_dict.get('tags', '[]'))
                tissue_dict['dependencies'] = json.loads(tissue_dict.get('dependencies', '[]'))
                del tissue_dict['embedding']  # Remove binary data
                results.append(tissue_dict)
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results[:limit]
    
    def get_tissue(self, tissue_id: str) -> Optional[Dict[str, Any]]:
        """Get tissue by ID"""
        # Check cache first
        if tissue_id in self._tissue_cache:
            self._cache_access_count[tissue_id] += 1
            return self._tissue_cache[tissue_id]
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tissues WHERE id = ?", (tissue_id,))
        row = cursor.fetchone()
        
        if row:
            tissue_dict = dict(row)
            tissue_dict['tags'] = json.loads(tissue_dict.get('tags', '[]'))
            tissue_dict['dependencies'] = json.loads(tissue_dict.get('dependencies', '[]'))
            
            # Update access count
            cursor.execute("""
                UPDATE tissues 
                SET access_count = access_count + 1,
                    last_accessed = ?
                WHERE id = ?
            """, (datetime.now(), tissue_id))
            self.conn.commit()
            
            # Cache tissue
            self._cache_tissue(tissue_dict)
            
            return tissue_dict
            
        return None
    
    def get_tissue_code(self, tissue_id: str) -> Optional[str]:
        """Get tissue source code"""
        tissue = self.get_tissue(tissue_id)
        
        if tissue and tissue.get('file_path'):
            try:
                with open(tissue['file_path'], 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                pass
                
        return None
    
    def _cache_tissue(self, tissue: Dict[str, Any]):
        """Cache tissue in memory"""
        tissue_id = tissue['id']
        
        # Add to cache
        self._tissue_cache[tissue_id] = tissue
        self._cache_access_count[tissue_id] += 1
        
        # Evict least used if cache full
        if len(self._tissue_cache) > self.cache_size:
            # Find least accessed tissue
            least_used = min(self._tissue_cache.keys(),
                           key=lambda k: self._cache_access_count[k])
            
            del self._tissue_cache[least_used]
            del self._cache_access_count[least_used]
    
    def recommend_tissues(self,
                         context: Dict[str, Any],
                         limit: int = 5) -> List[Dict[str, Any]]:
        """
        Recommend tissues based on context
        
        Args:
            context: Context dictionary with task info
            limit: Maximum recommendations
            
        Returns:
            List of recommended tissues
        """
        recommendations = []
        
        # Extract context features
        task_type = context.get('task_type', '')
        input_data = context.get('input_type', '')
        required_output = context.get('output_type', '')
        device_profile = context.get('device', 'edge')
        
        # Build recommendation query
        cursor = self.conn.cursor()
        
        # Start with high quality tissues
        sql = """
            SELECT * FROM tissues
            WHERE quality_score >= 0.7
        """
        params = []
        
        # Filter by task type
        if task_type:
            sql += " AND (description LIKE ? OR tags LIKE ?)"
            params.extend([f"%{task_type}%", f"%{task_type}%"])
        
        # Filter by input/output compatibility
        if input_data:
            sql += " AND input_type LIKE ?"
            params.append(f"%{input_data}%")
            
        if required_output:
            sql += " AND output_type LIKE ?"
            params.append(f"%{required_output}%")
        
        # Order by relevance
        sql += " ORDER BY quality_score DESC, access_count DESC"
        sql += f" LIMIT {limit}"
        
        cursor.execute(sql, params)
        
        for row in cursor:
            tissue_dict = dict(row)
            tissue_dict['tags'] = json.loads(tissue_dict.get('tags', '[]'))
            tissue_dict['dependencies'] = json.loads(tissue_dict.get('dependencies', '[]'))
            
            # Compute relevance score
            relevance = self._compute_relevance(tissue_dict, context)
            tissue_dict['relevance_score'] = relevance
            
            recommendations.append(tissue_dict)
        
        # Sort by relevance
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return recommendations
    
    def _compute_relevance(self,
                          tissue: Dict[str, Any],
                          context: Dict[str, Any]) -> float:
        """Compute tissue relevance to context"""
        score = tissue.get('quality_score', 0.0)
        
        # Boost score based on context matches
        if context.get('task_type'):
            task_lower = context['task_type'].lower()
            if task_lower in tissue.get('description', '').lower():
                score += 0.3
            if task_lower in str(tissue.get('tags', [])).lower():
                score += 0.2
                
        # Device compatibility
        if context.get('device') == 'edge' and tissue.get('edge_performance'):
            score += 0.2
            
        return min(score, 1.0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total tissues
        cursor.execute("SELECT COUNT(*) FROM tissues")
        stats['total_tissues'] = cursor.fetchone()[0]
        
        # By domain
        cursor.execute("""
            SELECT domain, COUNT(*) as count 
            FROM tissues 
            GROUP BY domain
        """)
        stats['by_domain'] = {row['domain']: row['count'] for row in cursor}
        
        # Most accessed
        cursor.execute("""
            SELECT id, name, access_count 
            FROM tissues 
            ORDER BY access_count DESC 
            LIMIT 10
        """)
        stats['most_accessed'] = [dict(row) for row in cursor]
        
        # Quality distribution
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN quality_score >= 0.8 THEN 'excellent'
                    WHEN quality_score >= 0.6 THEN 'good'
                    WHEN quality_score >= 0.4 THEN 'fair'
                    ELSE 'poor'
                END as quality_level,
                COUNT(*) as count
            FROM tissues
            GROUP BY quality_level
        """)
        stats['quality_distribution'] = {row['quality_level']: row['count'] for row in cursor}
        
        # Cache stats
        stats['cache_size'] = len(self._tissue_cache)
        stats['cache_hits'] = sum(self._cache_access_count.values())
        
        return stats


# REST API wrapper using Flask
def create_tissue_api_app(tissue_root: str = "../tissues"):
    """Create Flask app for Tissue Discovery API"""
    from flask import Flask, jsonify, request
    
    app = Flask(__name__)
    api = TissueDiscoveryAPI(tissue_root)
    
    @app.route('/api/v1/tissues/search', methods=['GET'])
    def search_tissues():
        """Search for tissues"""
        query = request.args.get('q', '')
        domain = request.args.get('domain')
        tags = request.args.getlist('tags')
        limit = int(request.args.get('limit', 10))
        
        results = api.search(query, domain, tags, limit)
        return jsonify({
            'success': True,
            'count': len(results),
            'tissues': results
        })
    
    @app.route('/api/v1/tissues/semantic-search', methods=['POST'])
    def semantic_search_tissues():
        """Semantic search for tissues"""
        data = request.get_json()
        query = data.get('query', '')
        domain = data.get('domain')
        threshold = data.get('threshold', 0.7)
        limit = data.get('limit', 10)
        
        results = api.semantic_search(query, domain, threshold, limit)
        return jsonify({
            'success': True,
            'count': len(results),
            'tissues': results
        })
    
    @app.route('/api/v1/tissues/<tissue_id>', methods=['GET'])
    def get_tissue(tissue_id):
        """Get tissue by ID"""
        tissue = api.get_tissue(tissue_id)
        
        if tissue:
            return jsonify({
                'success': True,
                'tissue': tissue
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Tissue not found'
            }), 404
    
    @app.route('/api/v1/tissues/<tissue_id>/code', methods=['GET'])
    def get_tissue_code(tissue_id):
        """Get tissue source code"""
        code = api.get_tissue_code(tissue_id)
        
        if code:
            return jsonify({
                'success': True,
                'tissue_id': tissue_id,
                'code': code
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Tissue code not found'
            }), 404
    
    @app.route('/api/v1/tissues/recommend', methods=['POST'])
    def recommend_tissues():
        """Get tissue recommendations"""
        context = request.get_json()
        limit = context.get('limit', 5)
        
        recommendations = api.recommend_tissues(context, limit)
        return jsonify({
            'success': True,
            'count': len(recommendations),
            'recommendations': recommendations
        })
    
    @app.route('/api/v1/statistics', methods=['GET'])
    def get_statistics():
        """Get API statistics"""
        stats = api.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    
    @app.route('/api/v1/tissues/rebuild-index', methods=['POST'])
    def rebuild_index():
        """Rebuild tissue index"""
        api.rebuild_index()
        return jsonify({
            'success': True,
            'message': 'Index rebuilt successfully'
        })
    
    return app


# CLI interface
def create_tissue_cli():
    """Create command-line interface for Tissue Discovery"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Tissue Discovery CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for tissues')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--domain', help='Filter by domain')
    search_parser.add_argument('--tags', nargs='+', help='Filter by tags')
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum results')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get tissue by ID')
    get_parser.add_argument('tissue_id', help='Tissue ID')
    get_parser.add_argument('--code', action='store_true', help='Show source code')
    
    # Recommend command
    recommend_parser = subparsers.add_parser('recommend', help='Get recommendations')
    recommend_parser.add_argument('--task', help='Task type')
    recommend_parser.add_argument('--input', help='Input type')
    recommend_parser.add_argument('--output', help='Output type')
    recommend_parser.add_argument('--device', default='edge', help='Device profile')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # Rebuild command
    rebuild_parser = subparsers.add_parser('rebuild', help='Rebuild index')
    
    args = parser.parse_args()
    
    # Initialize API
    api = TissueDiscoveryAPI()
    
    if args.command == 'search':
        results = api.search(args.query, args.domain, args.tags, args.limit)
        for tissue in results:
            print(f"\n{tissue['id']}: {tissue['name']}")
            print(f"  Domain: {tissue['domain']}")
            print(f"  Description: {tissue.get('description', 'N/A')}")
            print(f"  Quality: {tissue.get('quality_score', 0):.2f}")
            
    elif args.command == 'get':
        if args.code:
            code = api.get_tissue_code(args.tissue_id)
            if code:
                print(code)
            else:
                print(f"Tissue {args.tissue_id} not found")
        else:
            tissue = api.get_tissue(args.tissue_id)
            if tissue:
                print(f"\nTissue: {tissue['id']}")
                print(f"Name: {tissue['name']}")
                print(f"Domain: {tissue['domain']}")
                print(f"Description: {tissue.get('description', 'N/A')}")
                print(f"Main Function: {tissue.get('main_function', 'N/A')}")
                print(f"Input: {tissue.get('input_type', 'N/A')}")
                print(f"Output: {tissue.get('output_type', 'N/A')}")
                print(f"Performance: {tissue.get('edge_performance', 'N/A')}")
                print(f"Memory: {tissue.get('memory_usage', 'N/A')}")
                print(f"Tags: {', '.join(tissue.get('tags', []))}")
            else:
                print(f"Tissue {args.tissue_id} not found")
                
    elif args.command == 'recommend':
        context = {
            'task_type': args.task,
            'input_type': args.input,
            'output_type': args.output,
            'device': args.device
        }
        recommendations = api.recommend_tissues(context)
        
        print("\nRecommended Tissues:")
        for tissue in recommendations:
            print(f"\n{tissue['id']}: {tissue['name']}")
            print(f"  Relevance: {tissue['relevance_score']:.2f}")
            print(f"  Description: {tissue.get('description', 'N/A')}")
            
    elif args.command == 'stats':
        stats = api.get_statistics()
        print("\nTissue Discovery Statistics:")
        print(f"Total Tissues: {stats['total_tissues']}")
        print(f"\nBy Domain:")
        for domain, count in stats['by_domain'].items():
            print(f"  {domain}: {count}")
        print(f"\nMost Accessed:")
        for tissue in stats['most_accessed'][:5]:
            print(f"  {tissue['id']}: {tissue['access_count']} accesses")
            
    elif args.command == 'rebuild':
        api.rebuild_index()
        print("Index rebuilt successfully")


if __name__ == "__main__":
    # Run CLI if executed directly
    create_tissue_cli()