"""File cache for parsed AST files."""

import hashlib
import pickle
import time
from pathlib import Path
from typing import Optional, Tuple
import ast


class FileCache:
    """Cache for parsed AST files."""
    
    def __init__(self, cache_dir: str = ".code2llm_cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600
    
    def _get_cache_key(self, file_path: str, content: str) -> str:
        """Generate cache key from file path and content hash."""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:16]
        return f"{Path(file_path).stem}_{content_hash}"
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path."""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def get(self, file_path: str, content: str) -> Optional[Tuple[ast.AST, str]]:
        """Get cached AST if available and not expired."""
        cache_key = self._get_cache_key(file_path, content)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        # Check TTL
        age = time.time() - cache_path.stat().st_mtime
        if age > self.ttl_seconds:
            cache_path.unlink()
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    
    def put(self, file_path: str, content: str, data: Tuple[ast.AST, str]) -> None:
        """Store AST in cache."""
        cache_key = self._get_cache_key(file_path, content)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception:
            pass
    
    def clear(self) -> None:
        """Clear all cached files."""
        for f in self.cache_dir.glob("*.pkl"):
            f.unlink()
