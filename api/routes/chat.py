from fastapi import APIRouter, Query
from api.services.rag_engine import rag
from api.services.memory import get_chat_history, save_message_redis, save_message_postgres

import uuid

router = APIRouter()

@router.get("/history")
async def get_history(chat_id: str):
    return {"messages": get_chat_history(chat_id)}

@router.post("/send")
async def send_message(
    question: str = Query(...),
    doc_id: str = Query(...),
    user_id: str = Query(...),
    chat_id: str = Query(None),
):
    # Buat chat_id baru jika belum ada
    if not chat_id:
        chat_id = str(uuid.uuid4())

    # Simpan pertanyaan ke Redis + Postgres
    save_message_redis(chat_id, "user", question)
    save_message_postgres(chat_id, doc_id, user_id, "user", question)

    # Ambil history terakhir (untuk memory)
    history = get_chat_history(chat_id)

    # Kirim ke LLM
    result = await rag.aquery(
        question,
        mode="hybrid",
        top_k=3
    )
    answer = result if isinstance(result, str) else result.get("text", "Tidak ada jawaban.")

    # Simpan jawaban juga
    save_message_redis(chat_id, "bot", answer)
    save_message_postgres(chat_id, doc_id, user_id, "bot", answer)

    return {"chat_id": chat_id, "answer": answer}
