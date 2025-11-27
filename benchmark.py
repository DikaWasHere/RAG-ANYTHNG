"""
Performance comparison antara original dan optimized version
Run this untuk lihat improvement secara real-time
"""
import asyncio
import time
from typing import List, Tuple

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')
import logging
logging.getLogger('raganything').setLevel(logging.ERROR)
logging.getLogger('lightrag').setLevel(logging.ERROR)


async def benchmark_original():
    """Benchmark original main.py"""
    print("\n🔵 Testing ORIGINAL version...")
    
    from main import main as original_main
    # Note: Ini akan run full main() - untuk benchmark sebenarnya
    # perlu modifikasi main.py untuk bisa di-import sebagai function
    
    return "Skipped - modify main.py untuk benchmarking"


async def benchmark_optimized():
    """Benchmark optimized version"""
    print("\n🟢 Testing OPTIMIZED version...")
    
    from main_optimized import OptimizedRAGSystem
    
    system = OptimizedRAGSystem()
    
    # Test queries
    test_queries = [
        "Apa sanksi perdagangan manusia?",
        "Siapa yang bertanggung jawab?",
        "Apa sanksi perdagangan manusia?",  # Repeat untuk test cache
    ]
    
    results = {}
    
    # Initialize
    start = time.time()
    await system.initialize()
    results['init_time'] = time.time() - start
    
    # First query (cold)
    start = time.time()
    await system.query(test_queries[0])
    results['first_query_cold'] = time.time() - start
    
    # Second query (warm)
    start = time.time()
    await system.query(test_queries[1])
    results['second_query_warm'] = time.time() - start
    
    # Repeat first query (cached)
    start = time.time()
    await system.query(test_queries[2])
    results['cached_query'] = time.time() - start
    
    # Batch queries
    start = time.time()
    await system.batch_query(test_queries[:2])
    results['batch_query_2'] = time.time() - start
    
    # Get stats
    stats = system.get_stats()
    
    return results, stats


async def run_comparison():
    """Run full comparison"""
    print("="*70)
    print("🏁 RAG SYSTEM PERFORMANCE COMPARISON")
    print("="*70)
    
    # Benchmark optimized
    try:
        results, stats = await benchmark_optimized()
        
        print("\n📊 RESULTS:")
        print("-"*70)
        print(f"⚡ Initialization time: {results['init_time']:.3f}s")
        print(f"🔵 First query (cold):  {results['first_query_cold']:.3f}s")
        print(f"🟡 Second query (warm): {results['second_query_warm']:.3f}s")
        print(f"🟢 Cached query:        {results['cached_query']:.3f}s")
        print(f"🚀 Batch 2 queries:     {results['batch_query_2']:.3f}s")
        
        # Calculate improvements
        cache_speedup = results['first_query_cold'] / results['cached_query']
        
        print(f"\n💡 INSIGHTS:")
        print(f"   Cache speedup: {cache_speedup:.1f}x faster!")
        
        # Monitor stats
        print(f"\n📈 STATISTICS:")
        mon = stats['monitor']
        print(f"   Total queries: {mon['total_queries']}")
        
        if 'cache' in stats:
            print(f"\n💾 CACHE STATUS:")
            for cache_type, cache_stats in stats['cache'].items():
                if cache_stats:
                    print(f"   {cache_type}: {cache_stats['size']}/{cache_stats['maxsize']}")
        
        print("\n" + "="*70)
        print("✅ Benchmark completed!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error during benchmark: {e}")
        import traceback
        traceback.print_exc()


async def quick_demo():
    """Quick demo untuk showcase features"""
    print("\n" + "="*70)
    print("🎯 QUICK FEATURE DEMO")
    print("="*70)
    
    from main_optimized import OptimizedRAGSystem
    
    system = OptimizedRAGSystem()
    await system.initialize()
    
    # Demo 1: Cache effect
    print("\n1️⃣  CACHE DEMO")
    print("-"*70)
    question = "Apa sanksi perdagangan manusia?"
    
    print(f"Query: {question}")
    print("\n   First call (computing)...")
    start = time.time()
    result1 = await system.query(question)
    time1 = time.time() - start
    print(f"   ⏱️  Time: {time1:.3f}s")
    print(f"   📝 Result: {result1[:100]}...")
    
    print("\n   Second call (from cache)...")
    start = time.time()
    result2 = await system.query(question)
    time2 = time.time() - start
    print(f"   ⚡ Time: {time2:.3f}s ({time1/time2:.1f}x faster!)")
    
    # Demo 2: Batch processing
    print("\n\n2️⃣  BATCH PROCESSING DEMO")
    print("-"*70)
    questions = [
        "Apa itu perdagangan manusia?",
        "Siapa yang bertanggung jawab?",
        "Bagaimana cara melaporkan?",
    ]
    
    print(f"Processing {len(questions)} queries in parallel...")
    start = time.time()
    results = await system.batch_query(questions)
    batch_time = time.time() - start
    print(f"   ⏱️  Total time: {batch_time:.3f}s")
    print(f"   📊 Avg per query: {batch_time/len(questions):.3f}s")
    
    # Demo 3: Statistics
    print("\n\n3️⃣  STATISTICS DEMO")
    print("-"*70)
    system.print_stats()
    
    print("\n" + "="*70)
    print("✅ Demo completed!")
    print("="*70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Quick demo
        asyncio.run(quick_demo())
    else:
        # Full comparison
        asyncio.run(run_comparison())
