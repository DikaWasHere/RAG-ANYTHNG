"""
Efficient caching layer untuk RAG system
Implements LRU cache untuk embeddings, queries, dan LLM responses
"""
import hashlib
import json
import time
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple
from collections import OrderedDict
import asyncio

class TTLCache:
    """Time-To-Live cache with LRU eviction"""
    def __init__(self, maxsize: int = 128, ttl: int = 3600):
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, float] = {}
        self._lock = asyncio.Lock()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.timestamps:
            return True
        return time.time() - self.timestamps[key] > self.ttl
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key in self.cache and not self._is_expired(key):
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
            elif key in self.cache:
                # Expired, remove it
                del self.cache[key]
                del self.timestamps[key]
        return None
    
    async def set(self, key: str, value: Any):
        """Set value in cache"""
        async with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.maxsize:
                    # Remove oldest
                    oldest = next(iter(self.cache))
                    del self.cache[oldest]
                    del self.timestamps[oldest]
            
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    async def clear(self):
        """Clear all cache"""
        async with self._lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "maxsize": self.maxsize,
            "ttl": self.ttl,
            "hit_rate": getattr(self, '_hits', 0) / max(getattr(self, '_requests', 1), 1)
        }

class EmbeddingCache:
    """Cache untuk embedding results"""
    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        self.cache = TTLCache(maxsize, ttl)
    
    def _hash_text(self, text: str) -> str:
        """Create hash from text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    async def get(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache"""
        key = self._hash_text(text)
        return await self.cache.get(key)
    
    async def set(self, text: str, embedding: List[float]):
        """Store embedding in cache"""
        key = self._hash_text(text)
        await self.cache.set(key, embedding)
    
    async def get_batch(self, texts: List[str]) -> Tuple[List[Optional[List[float]]], List[int]]:
        """Get multiple embeddings, return (embeddings, missing_indices)"""
        embeddings = []
        missing_indices = []
        
        for i, text in enumerate(texts):
            emb = await self.get(text)
            embeddings.append(emb)
            if emb is None:
                missing_indices.append(i)
        
        return embeddings, missing_indices
    
    async def set_batch(self, texts: List[str], embeddings: List[List[float]]):
        """Store multiple embeddings"""
        for text, emb in zip(texts, embeddings):
            await self.set(text, emb)

class QueryCache:
    """Cache untuk query results"""
    def __init__(self, maxsize: int = 100, ttl: int = 3600):
        self.cache = TTLCache(maxsize, ttl)
    
    def _create_key(self, query: str, mode: str, **kwargs) -> str:
        """Create cache key from query parameters"""
        key_data = {
            "query": query.lower().strip(),
            "mode": mode,
            **{k: v for k, v in kwargs.items() if k in ['top_k', 'enable_rerank']}
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, query: str, mode: str, **kwargs) -> Optional[str]:
        """Get query result from cache"""
        key = self._create_key(query, mode, **kwargs)
        return await self.cache.get(key)
    
    async def set(self, query: str, mode: str, result: str, **kwargs):
        """Store query result in cache"""
        key = self._create_key(query, mode, **kwargs)
        await self.cache.set(key, result)

class LLMCache:
    """Cache untuk LLM responses"""
    def __init__(self, maxsize: int = 500, ttl: int = 3600):
        self.cache = TTLCache(maxsize, ttl)
    
    def _create_key(self, prompt: str, model: str, **kwargs) -> str:
        """Create cache key from LLM parameters"""
        key_data = {
            "prompt": prompt[:500],  # Truncate untuk efficiency
            "model": model,
            "temperature": kwargs.get("temperature", 0.7),
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, prompt: str, model: str, **kwargs) -> Optional[str]:
        """Get LLM response from cache"""
        key = self._create_key(prompt, model, **kwargs)
        return await self.cache.get(key)
    
    async def set(self, prompt: str, model: str, response: str, **kwargs):
        """Store LLM response in cache"""
        key = self._create_key(prompt, model, **kwargs)
        await self.cache.set(key, response)

class CacheManager:
    """Centralized cache management"""
    def __init__(self, config):
        self.config = config
        self.embedding_cache = EmbeddingCache(
            config.cache.embedding_cache_size,
            config.cache.cache_ttl
        ) if config.cache.enable_embedding_cache else None
        
        self.query_cache = QueryCache(
            config.cache.query_cache_size,
            config.cache.cache_ttl
        ) if config.cache.enable_query_cache else None
        
        self.llm_cache = LLMCache(
            config.cache.llm_cache_size,
            config.cache.cache_ttl
        ) if config.cache.enable_llm_cache else None
    
    async def clear_all(self):
        """Clear all caches"""
        if self.embedding_cache:
            await self.embedding_cache.cache.clear()
        if self.query_cache:
            await self.query_cache.cache.clear()
        if self.llm_cache:
            await self.llm_cache.cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics for all caches"""
        return {
            "embedding": self.embedding_cache.cache.stats() if self.embedding_cache else None,
            "query": self.query_cache.cache.stats() if self.query_cache else None,
            "llm": self.llm_cache.cache.stats() if self.llm_cache else None,
        }
