import os
import asyncio
from dotenv import load_dotenv
from raganything import RAGAnything, RAGAnythingConfig
from sentence_transformers import SentenceTransformer
from lightrag.utils import EmbeddingFunc
from api.services.llm_wrapper import llm_model_func, vision_model_func

load_dotenv()

# === Load Embedding Model ===
embed_model = SentenceTransformer(os.getenv("EMBEDDING_MODEL"))

embedding_func = EmbeddingFunc(
    embedding_dim=384,
    max_token_size=512,
    func=lambda texts: asyncio.to_thread(
        embed_model.encode,
        texts,
        normalize_embeddings=True
    )
)

# === Load RAG Config dari ENV ===
config = RAGAnythingConfig(
    working_dir="./rag_storage",
    parser="mineru",
    parse_method="auto",
    enable_image_processing=True,
    enable_table_processing=True,
    enable_equation_processing=True,
)

# === RAG INSTANCE ===
rag = RAGAnything(
    config=config,
    llm_model_func=llm_model_func,
    vision_model_func=vision_model_func,
    embedding_func=embedding_func,
)

# === WRAPPER PROCESS PDF ===
async def process_pdf(file_path: str):
    await rag.process_document_complete(
        file_path=file_path,
        output_dir=config.working_dir
    )
    return f"File {os.path.basename(file_path)} berhasil diproses"
