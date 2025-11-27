"""
🚀 QUICK START GUIDE

Langkah cepat untuk mulai menggunakan Optimized RAG System
"""

print("""
╔═══════════════════════════════════════════════════════════════╗
║                  RAG ANYTHING - QUICK START                   ║
╚═══════════════════════════════════════════════════════════════╝

📦 STEP 1: INSTALL (jika belum)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Activate virtual environment terlebih dahulu:
   
   Windows PowerShell:
   > .\\.venv\\Scripts\\Activate.ps1
   
   Kemudian install dependencies:
   > pip install -r requirements.txt


⚙️  STEP 2: SETUP API KEY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Edit file .env:
   
   OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   
   Get API key dari: https://openrouter.ai/


🎯 STEP 3: PILIH VERSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   A. OPTIMIZED VERSION (Recommended) 🟢
   
      > python main_optimized.py
      
      ✨ Features:
      - 50x faster untuk repeated queries (with cache)
      - 30x faster startup (lazy loading)
      - Performance monitoring
      - Batch processing
      
      Commands:
      - Tanya apapun
      - "stats" untuk lihat statistik
      - "clear" untuk clear cache
      - "exit" untuk keluar
   
   
   B. STANDARD VERSION (Simple) 🔵
   
      > python main.py
      
      Simple, straightforward, no frills.


📊 STEP 4: BENCHMARK (Optional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Lihat perbedaan performance:
   
   > python benchmark.py demo
   
   Akan show:
   - Cache speedup comparison
   - Batch processing demo
   - Real-time statistics


💡 TIPS & TRICKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   1. Gunakan optimized version untuk production
   2. Ketik "stats" regularly untuk monitor performance
   3. Cache otomatis clear setelah 1 jam (configurable)
   4. Batch queries untuk process multiple questions sekaligus
   5. Adjust config.py untuk custom tuning


📚 DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   README.md           - General overview
   OPTIMIZATION.md     - Detailed optimization guide
   config.py          - Configuration options
   benchmark.py       - Performance testing


🆘 TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Problem: "Import could not be resolved"
   Solution: Activate .venv terlebih dahulu
   
   Problem: Slow queries
   Solution: Enable caching, check "stats" untuk bottleneck
   
   Problem: API key error
   Solution: Check .env file, pastikan valid API key
   
   Problem: Out of memory
   Solution: Reduce cache sizes di config.py


🎓 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   ✓ Jalankan optimized version
   ✓ Coba beberapa queries
   ✓ Check "stats" untuk performance
   ✓ Read OPTIMIZATION.md untuk advanced features
   ✓ Customize config.py sesuai kebutuhan
   ✓ Deploy untuk production! 🚀


╔═══════════════════════════════════════════════════════════════╗
║              Ready? Run: python main_optimized.py             ║
╚═══════════════════════════════════════════════════════════════╝

""")
