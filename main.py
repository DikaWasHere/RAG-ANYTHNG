import os
import asyncio
import warnings
import sys
from dotenv import load_dotenv

from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from sentence_transformers import SentenceTransformer

load_dotenv()

async def main():
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL")  # OpenRouter URL

    # Load embedding model lokal
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Model kecil & cepat

    # 1. Config dasar
    config = RAGAnythingConfig(
        working_dir="./rag_storage",
        parser=os.getenv("PARSER", "mineru"),
        parse_method=os.getenv("PARSE_METHOD", "auto"),
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )

    # 2. Fungsi LLM text
    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return openai_complete_if_cache(
            "openai/gpt-4o-mini",  # GPT-4o-mini via OpenRouter
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )

    # 3. Fungsi vision (gambar)
    def vision_model_func(
        prompt, system_prompt=None, history_messages=[], image_data=None, messages=None, **kwargs
    ):
        if messages:
            # format multimodal direct
            return openai_complete_if_cache(
                "openai/gpt-4o",  # GPT-4o via OpenRouter
                "",
                system_prompt=None,
                history_messages=[],
                messages=messages,
                api_key=api_key,
                base_url=base_url,
                **kwargs,
            )
        elif image_data:
            # single image klasik
            return openai_complete_if_cache(
                "openai/gpt-4o",  # GPT-4o via OpenRouter
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
            # fallback ke LLM text biasa
            return llm_model_func(prompt, system_prompt, history_messages, **kwargs)

    # 4. Fungsi embedding (lokal)
    async def local_embedding(texts):
        # Konversi ke list jika string tunggal
        if isinstance(texts, str):
            texts = [texts]
        # Encode menggunakan model lokal
        embeddings = embedding_model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    
    embedding_func = EmbeddingFunc(
        embedding_dim=384,  # all-MiniLM-L6-v2 dimension
        max_token_size=512,
        func=local_embedding,
    )

    # 5. Inisialisasi RAGAnything
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        vision_model_func=vision_model_func,
        embedding_func=embedding_func,
    )

    # 6. Skip preprocessing jika sudah pernah diproses
    # Uncomment jika perlu preprocessing ulang atau dokumen baru
    await rag.process_document_complete(
        file_path="data/castle.png",
        output_dir=os.getenv("OUTPUT_DIR", "./output"),
        parse_method=os.getenv("PARSE_METHOD", "auto")
    )

    # 7. Query interaktif
    print("\n" + "="*60)
    print("🤖 RAG System siap! Ketik pertanyaan Anda")
    print("   (ketik 'exit' untuk keluar)")
    print("="*60 + "\n")
    
    while True:
        try:
            question = input("\n📝 Pertanyaan: ")
            
            if question.lower() in ['exit', 'quit', 'keluar', 'q']:
                print("\n👋 Terima kasih! Sampai jumpa!")
                return  # Clean exit tanpa warning
                
            if not question.strip():
                continue
            
            print("\n🔍 Mencari jawaban...")
            result = await rag.aquery(question, mode="hybrid")
            print(f"\n💡 Jawaban:\n{result}\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Program dihentikan. Sampai jumpa!")
            return  # Exit cleanly
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)  # Clean exit
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
