"""
Performance monitoring untuk RAG system
Track query performance, memory usage, dan statistics
"""
import time
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class QueryMetrics:
    """Metrics untuk single query"""
    query: str
    mode: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    
    # Performance metrics
    embedding_time: float = 0.0
    retrieval_time: float = 0.0
    llm_time: float = 0.0
    
    # Cache hits
    embedding_cache_hit: bool = False
    query_cache_hit: bool = False
    llm_cache_hit: bool = False
    
    # Result info
    result_length: int = 0
    chunks_retrieved: int = 0
    
    def finish(self, result: str = "", chunks: int = 0):
        """Mark query as finished"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.result_length = len(result)
        self.chunks_retrieved = chunks
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "query": self.query[:100],  # Truncate
            "mode": self.mode,
            "duration": round(self.duration, 3) if self.duration else None,
            "embedding_time": round(self.embedding_time, 3),
            "retrieval_time": round(self.retrieval_time, 3),
            "llm_time": round(self.llm_time, 3),
            "cache_hits": {
                "embedding": self.embedding_cache_hit,
                "query": self.query_cache_hit,
                "llm": self.llm_cache_hit,
            },
            "chunks_retrieved": self.chunks_retrieved,
            "timestamp": datetime.fromtimestamp(self.start_time).isoformat(),
        }

class PerformanceMonitor:
    """Monitor performance metrics"""
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.queries: List[QueryMetrics] = []
        self.start_time = time.time()
        self._lock = asyncio.Lock()
    
    def create_query_metrics(self, query: str, mode: str) -> QueryMetrics:
        """Create new query metrics"""
        return QueryMetrics(
            query=query,
            mode=mode,
            start_time=time.time()
        )
    
    async def record_query(self, metrics: QueryMetrics):
        """Record completed query metrics"""
        if not self.enabled:
            return
        
        async with self._lock:
            self.queries.append(metrics)
            # Keep only last 1000 queries
            if len(self.queries) > 1000:
                self.queries = self.queries[-1000:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        if not self.queries:
            return {
                "total_queries": 0,
                "uptime_seconds": time.time() - self.start_time,
            }
        
        total = len(self.queries)
        durations = [q.duration for q in self.queries if q.duration]
        
        # Cache hit rates
        embedding_hits = sum(1 for q in self.queries if q.embedding_cache_hit)
        query_hits = sum(1 for q in self.queries if q.query_cache_hit)
        llm_hits = sum(1 for q in self.queries if q.llm_cache_hit)
        
        return {
            "total_queries": total,
            "uptime_seconds": round(time.time() - self.start_time, 2),
            "performance": {
                "avg_duration": round(sum(durations) / len(durations), 3) if durations else 0,
                "min_duration": round(min(durations), 3) if durations else 0,
                "max_duration": round(max(durations), 3) if durations else 0,
                "avg_embedding_time": round(sum(q.embedding_time for q in self.queries) / total, 3),
                "avg_retrieval_time": round(sum(q.retrieval_time for q in self.queries) / total, 3),
                "avg_llm_time": round(sum(q.llm_time for q in self.queries) / total, 3),
            },
            "cache_hit_rates": {
                "embedding": round(embedding_hits / total, 3) if total > 0 else 0,
                "query": round(query_hits / total, 3) if total > 0 else 0,
                "llm": round(llm_hits / total, 3) if total > 0 else 0,
            },
            "query_modes": self._count_modes(),
        }
    
    def _count_modes(self) -> Dict[str, int]:
        """Count queries by mode"""
        modes = {}
        for q in self.queries:
            modes[q.mode] = modes.get(q.mode, 0) + 1
        return modes
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent queries"""
        return [q.to_dict() for q in self.queries[-limit:]]
    
    def export_stats(self, filepath: str):
        """Export statistics to JSON file"""
        stats = {
            "statistics": self.get_statistics(),
            "recent_queries": self.get_recent_queries(50),
            "exported_at": datetime.now().isoformat(),
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    
    async def clear(self):
        """Clear all metrics"""
        async with self._lock:
            self.queries.clear()
            self.start_time = time.time()

class Timer:
    """Context manager untuk timing operations"""
    def __init__(self, name: str = ""):
        self.name = name
        self.start_time = None
        self.elapsed = 0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.elapsed = time.time() - self.start_time
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, *args):
        self.elapsed = time.time() - self.start_time
