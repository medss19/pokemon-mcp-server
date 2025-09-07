# src/pokemon_mcp/data/cache.py
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Optional, Any
import aiofiles

class PokemonCache:
    def __init__(self, cache_dir: str = "cache", cache_duration: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_duration = cache_duration
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache = {}
    
    def _get_cache_key(self, identifier: str) -> str:
        """Generate a cache key from identifier"""
        return hashlib.md5(identifier.lower().encode()).hexdigest()
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{cache_key}.json"
    
    async def get(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Get cached data"""
        cache_key = self._get_cache_key(identifier)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if time.time() - entry['timestamp'] < self.cache_duration:
                return entry['data']
            else:
                del self.memory_cache[cache_key]
        
        # Check file cache
        cache_file = self._get_cache_file(cache_key)
        if cache_file.exists():
            try:
                async with aiofiles.open(cache_file, 'r') as f:
                    content = await f.read()
                    entry = json.loads(content)
                
                if time.time() - entry['timestamp'] < self.cache_duration:
                    # Load into memory cache
                    self.memory_cache[cache_key] = entry
                    return entry['data']
                else:
                    # Remove expired cache
                    cache_file.unlink()
            except Exception:
                # Remove corrupted cache
                if cache_file.exists():
                    cache_file.unlink()
        
        return None
    
    async def set(self, identifier: str, data: Dict[str, Any]) -> None:
        """Set cached data"""
        cache_key = self._get_cache_key(identifier)
        entry = {
            'data': data,
            'timestamp': time.time()
        }
        
        # Set in memory cache
        self.memory_cache[cache_key] = entry
        
        # Set in file cache
        try:
            cache_file = self._get_cache_file(cache_key)
            async with aiofiles.open(cache_file, 'w') as f:
                await f.write(json.dumps(entry))
        except Exception as e:
            print(f"Failed to write cache file: {e}")
    
    async def clear_expired(self) -> None:
        """Clear expired cache entries"""
        current_time = time.time()
        
        # Clear memory cache
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if current_time - entry['timestamp'] >= self.cache_duration
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Clear file cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                async with aiofiles.open(cache_file, 'r') as f:
                    content = await f.read()
                    entry = json.loads(content)
                
                if current_time - entry['timestamp'] >= self.cache_duration:
                    cache_file.unlink()
            except Exception:
                # Remove corrupted files
                cache_file.unlink()