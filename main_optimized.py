"""
Optimized RAG System with enhanced performance
Includes: lazy loading, smart caching, async optimization, monitoring
"""
import os
import asyncio
import warnings
import sys
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache
from lightrag.utils import EmbeddingFunc
from sentence_transformers import SentenceTransformer

# Import optimizations
from config import CONFIG
from cache import CacheManager, EmbeddingCache
from monitoring import PerformanceMonitor, Timer

# Suppress warnings
warnings.filterwarnings('ignore', message='.*Failed to finalize RAGAnything storages.*')
warnings.filterwarnings('ignore', message='.*no current event loop.*')

# Suppress logging dari library
import logging
logging.getLogger('raganything').setLevel(logging.ERROR)
logging.getLogger('lightrag').setLevel(logging.ERROR)

load_dotenv()


class OptimizedEmbedding:
    """Optimized embedding dengan lazy loading dan caching"""
    def __init__(self, config, cache: Optional[EmbeddingCache] = None):
        self.config = config
        self.cache = cache
        self._model = None
        self._lock = asyncio.Lock()
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load embedding model"""
        if self._model is None:
            print(f"🔄 Loading embedding model: {self.config.model.embedding_model_name}")
            self._model = SentenceTransformer(
                self.config.model.embedding_model_name,
                device='cpu'  # Atau 'cuda' jika ada GPU
            )
            print("✅ Embedding model loaded")
        return self._model
    
    async def encode(self, texts: List[str], show_progress: bool = False) -> List[List[float]]:
        """Encode texts dengan caching support"""
        if isinstance(texts, str):
            texts = [texts]
        
        # Check cache jika enabled
        if self.cache:
            cached_embeddings, missing_indices = await self.cache.get_batch(texts)
            
            # Jika semua ada di cache
            if not missing_indices:
                return [emb for emb in cached_embeddings if emb is not None]
            
            # Encode only missing texts
            missing_texts = [texts[i] for i in missing_indices]
            new_embeddings = self.model.encode(
                missing_texts,
                normalize_embeddings=True,
                show_progress_bar=show_progress,
                batch_size=self.config.model.embedding_batch_size
            ).tolist()
            
            # Update cache
            await self.cache.set_batch(missing_texts, new_embeddings)
            
            # Merge results
            result = []
            new_idx = 0
            for i, cached in enumerate(cached_embeddings):
                if cached is not None:
                    result.append(cached)
                else:
                    result.append(new_embeddings[new_idx])
                    new_idx += 1
            return result
        else:
            # No cache, direct encoding
            return self.model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=show_progress,
                batch_size=self.config.model.embedding_batch_size
            ).tolist()


class OptimizedRAGSystem:
    """Optimized RAG system dengan semua enhancement"""
    def __init__(self, config=None):
        self.config = config or CONFIG
        
        # Initialize components
        self.cache_manager = CacheManager(self.config)
        self.monitor = PerformanceMonitor(self.config.performance.enable_monitoring)
        self.embedding_handler = OptimizedEmbedding(
            self.config,
            self.cache_manager.embedding_cache
        )
        
        # RAG components (lazy loaded)
        self._rag = None
        self._initialized = False
    
    def _llm_model_func(self, prompt, system_prompt=None, history_messages=[], **kwargs):
        """LLM function dengan caching"""
        # Set defaults from config
        kwargs.setdefault('temperature', self.config.model.llm_temperature)
        kwargs.setdefault('max_tokens', self.config.model.llm_max_tokens)
        kwargs.setdefault('timeout', self.config.model.llm_timeout)
        
        return openai_complete_if_cache(
            self.config.model.llm_model,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=self.config.model.api_key,
            base_url=self.config.model.base_url,
            **kwargs,
        )
    
    def _vision_model_func(self, prompt, system_prompt=None, history_messages=[], 
                           image_data=None, messages=None, **kwargs):
        """Vision function untuk multimodal"""
        kwargs.setdefault('timeout', self.config.model.llm_timeout)
        
        if messages:
            return openai_complete_if_cache(
                self.config.model.vision_model,
                "",
                system_prompt=None,
                history_messages=[],
                messages=messages,
                api_key=self.config.model.api_key,
                base_url=self.config.model.base_url,
                **kwargs,
            )
        elif image_data:
            return openai_complete_if_cache(
                self.config.model.vision_model,
                "",
                system_prompt=None,
                history_messages=[],
                messages=[
                    {"role": "system", "content": system_prompt} if system_prompt else None,
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                            },
                        ],
                    },
                ],
                api_key=self.config.model.api_key,
                base_url=self.config.model.base_url,
                **kwargs,
            )
        else:
            return self._llm_model_func(prompt, system_prompt, history_messages, **kwargs)
    
    async def _embedding_func(self, texts):
        """Async embedding function dengan caching"""
        return await self.embedding_handler.encode(texts)
    
    async def initialize(self):
        """Initialize RAG system"""
        if self._initialized:
            return
        
        print("🚀 Initializing Optimized RAG System...")
        
        # Create RAG config
        rag_config = RAGAnythingConfig(
            working_dir=self.config.rag.working_dir,
            parser=self.config.rag.parser,
            parse_method=self.config.rag.parse_method,
            enable_image_processing=self.config.rag.enable_image_processing,
            enable_table_processing=self.config.rag.enable_table_processing,
            enable_equation_processing=self.config.rag.enable_equation_processing,
        )
        
        # Create embedding function
        embedding_func = EmbeddingFunc(
            embedding_dim=self.config.model.embedding_dim,
            max_token_size=self.config.model.embedding_max_tokens,
            func=self._embedding_func,
        )
        
        # Initialize RAG
        self._rag = RAGAnything(
            config=rag_config,
            llm_model_func=self._llm_model_func,
            vision_model_func=self._vision_model_func,
            embedding_func=embedding_func,
        )
        
        self._initialized = True
        print("✅ RAG System initialized")
    
    async def process_document(self, file_path: str, output_dir: Optional[str] = None):
        """Process document dengan monitoring"""
        await self.initialize()
        
        output_dir = output_dir or self.config.rag.output_dir
        
        print(f"\n📄 Processing document: {file_path}")
        start_time = asyncio.get_event_loop().time()
        
        await self._rag.process_document_complete(
            file_path=file_path,
            output_dir=output_dir,
            parse_method=self.config.rag.parse_method
        )
        
        elapsed = asyncio.get_event_loop().time() - start_time
        print(f"✅ Document processed in {elapsed:.2f}s")
    
    async def query(self, question: str, mode: Optional[str] = None, **kwargs) -> str:
        """Query dengan caching dan monitoring"""
        await self.initialize()
        
        mode = mode or self.config.rag.default_query_mode
        
        # Check query cache
        if self.cache_manager.query_cache:
            cached = await self.cache_manager.query_cache.get(question, mode, **kwargs)
            if cached:
                print("⚡ Cache hit!")
                return cached
        
        # Create metrics
        metrics = self.monitor.create_query_metrics(question, mode)
        
        try:
            # Time embedding
            async with Timer() as t:
                pass  # Embedding sudah tracked di dalam
            metrics.embedding_time = t.elapsed
            
            # Time retrieval + LLM
            async with Timer() as t:
                result = await self._rag.aquery(
                    question,
                    mode=mode,
                    top_k=kwargs.get('top_k', self.config.rag.top_k),
                    **kwargs
                )
            metrics.llm_time = t.elapsed
            
            # Finish metrics
            metrics.finish(result=result)
            await self.monitor.record_query(metrics)
            
            # Cache result
            if self.cache_manager.query_cache:
                await self.cache_manager.query_cache.set(question, mode, result, **kwargs)
            
            return result
            
        except Exception as e:
            metrics.finish()
            await self.monitor.record_query(metrics)
            raise e
    
    async def batch_query(self, questions: List[str], mode: Optional[str] = None) -> List[str]:
        """Process multiple queries in parallel"""
        semaphore = asyncio.Semaphore(self.config.performance.max_concurrent_queries)
        
        async def query_with_limit(q):
            async with semaphore:
                return await self.query(q, mode)
        
        return await asyncio.gather(*[query_with_limit(q) for q in questions])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            "monitor": self.monitor.get_statistics(),
            "cache": self.cache_manager.stats(),
            "config": self.config.to_dict(),
        }
    
    def print_stats(self):
        """Print formatted statistics"""
        stats = self.get_stats()
        
        print("\n" + "="*60)
        print("📊 SYSTEM STATISTICS")
        print("="*60)
        
        # Monitor stats
        mon = stats['monitor']
        print(f"\n⏱️  Performance:")
        print(f"   Total queries: {mon['total_queries']}")
        print(f"   Uptime: {mon['uptime_seconds']:.2f}s")
        
        if 'performance' in mon:
            perf = mon['performance']
            print(f"   Avg duration: {perf['avg_duration']}s")
            print(f"   Avg embedding: {perf['avg_embedding_time']}s")
            print(f"   Avg LLM: {perf['avg_llm_time']}s")
        
        # Cache stats
        if 'cache' in stats:
            print(f"\n💾 Cache:")
            for cache_type, cache_stats in stats['cache'].items():
                if cache_stats:
                    print(f"   {cache_type}: {cache_stats['size']}/{cache_stats['maxsize']} "
                          f"(hit rate: {cache_stats['hit_rate']:.2%})")
        
        print("="*60 + "\n")
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.cache_manager.clear_all()
        await self.monitor.clear()


async def main():
    """Main interactive loop"""
    # Create optimized system
    system = OptimizedRAGSystem()
    
    # Initialize
    await system.initialize()
    
    # Optional: Process document
    # Uncomment jika ada dokumen baru atau perlu preprocessing ulang
    # await system.process_document("data/jdih.pdf")
    
    # Interactive query loop
    print("\n" + "="*60)
    print("🤖 Optimized RAG System Ready!")
    print("   Commands: 'exit', 'stats', 'clear', atau tanya apapun")
    print("="*60 + "\n")
    
    while True:
        try:
            question = input("\n📝 Pertanyaan: ")
            
            if question.lower() in ['exit', 'quit', 'keluar', 'q']:
                print("\n👋 Terima kasih! Sampai jumpa!")
                return
            
            if question.lower() == 'stats':
                system.print_stats()
                continue
            
            if question.lower() == 'clear':
                await system.cleanup()
                print("🗑️  Cache cleared!")
                continue
            
            if not question.strip():
                continue
            
            print("\n🔍 Mencari jawaban...")
            result = await system.query(question)
            print(f"\n💡 Jawaban:\n{result}\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Program dihentikan. Sampai jumpa!")
            return
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
