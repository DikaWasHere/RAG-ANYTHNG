import os
import asyncio
from dotenv import load_dotenv

from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache
from lightrag.utils import EmbeddingFunc
from sentence_transformers import SentenceTransformer

load_dotenv()

async def main():
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL")

    # Load embedding model lokal
    print("🔄 Loading embedding model...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    # Config dasar
    config = RAGAnythingConfig(
        working_dir="./rag_storage",
        parser=os.getenv("PARSER", "mineru"),
        parse_method=os.getenv("PARSE_METHOD", "auto"),
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )

    # Fungsi LLM text
    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return openai_complete_if_cache(
            "openai/gpt-4o-mini",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )

    # Fungsi vision
    def vision_model_func(
        prompt, system_prompt=None, history_messages=[], image_data=None, messages=None, **kwargs
    ):
        if messages:
            return openai_complete_if_cache(
                "openai/gpt-4o",
                "",
                system_prompt=None,
                history_messages=[],
                messages=messages,
                api_key=api_key,
                base_url=base_url,
                **kwargs,
            )
        elif image_data:
            return openai_complete_if_cache(
                "openai/gpt-4o",
                "",
                system_prompt=None,
                history_messages=[],
                messages=[
                    {"role": "system", "content": system_prompt}
                    if system_prompt
                    else None,
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                },
                            },
                        ],
                    }
                    if image_data
                    else {"role": "user", "content": prompt},
                ],
                api_key=api_key,
                base_url=base_url,
                **kwargs,
            )
        else:
            return llm_model_func(prompt, system_prompt, history_messages, **kwargs)

    # Fungsi embedding lokal
    async def local_embedding(texts):
        if isinstance(texts, str):
            texts = [texts]
        embeddings = embedding_model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    
    embedding_func = EmbeddingFunc(
        embedding_dim=384,
        max_token_size=512,
        func=local_embedding,
    )

    # Inisialisasi RAGAnything
    print("🔄 Initializing RAG system...")
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        vision_model_func=vision_model_func,
        embedding_func=embedding_func,
    )
    
    # Cek apakah ada data yang sudah diproses
    import os.path
    if not os.path.exists("./rag_storage/kv_store_full_docs.json"):
        print("\n" + "="*60)
        print("❌ BELUM ADA DATA DOKUMEN!")
        print("="*60)
        print("\n📚 Silakan jalankan preprocessing terlebih dahulu:")
        print("   1. Buka main.py")
        print("   2. Uncomment baris 116-120 (hapus tanda #)")
        print("   3. Jalankan: python main.py")
        print("\n   Atau langsung jalankan preprocessing sekarang? (y/n)")
        
        choice = input("\n   Pilihan: ")
        if choice.lower() == 'y':
            print("\n🔄 Memproses dokumen...")
            await rag.process_document_complete(
                file_path="data/jdih.pdf",
                output_dir=os.getenv("OUTPUT_DIR", "./output"),
                parse_method=os.getenv("PARSE_METHOD", "auto")
            )
            print("\n✅ Preprocessing selesai!\n")
        else:
            print("\n👋 Silakan preprocessing dulu, lalu jalankan lagi chat.py")
            return

    # Mode interaktif
    print("\n" + "="*60)
    print("🤖 RAG Chat System - Siap menjawab pertanyaan Anda!")
    print("   Dokumen: data/jdih.pdf")
    print("   Ketik 'exit', 'quit', atau 'q' untuk keluar")
    print("="*60 + "\n")
    
    while True:
        try:
            question = input("📝 Pertanyaan: ")
            
            if question.lower() in ['exit', 'quit', 'keluar', 'q']:
                print("\n👋 Terima kasih! Sampai jumpa!")
                break
                
            if not question.strip():
                continue
            
            print("\n🔍 Mencari jawaban...")
            result = await rag.aquery(question, mode="hybrid")
            print(f"\n💡 Jawaban:\n{result}\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Program dihentikan. Sampai jumpa!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
