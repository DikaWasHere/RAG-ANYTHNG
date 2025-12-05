from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import traceback
from api.services.rag_engine import process_pdf

router = APIRouter()

@router.post("")
@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    # Validasi ekstensi
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Hanya file PDF yang diizinkan.")

    # Validasi ukuran file
    size_limit = int(os.getenv("MAX_PDF_SIZE_MB", 10)) * 1024 * 1024
    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="File kosong.")

    if len(contents) > size_limit:
        raise HTTPException(status_code=400, detail="PDF terlalu besar.")

    # Simpan file
    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    try:
        with open(file_path, "wb") as f:
            f.write(contents)

        # Proses ke RAGAnything
        summary = await process_pdf(file_path)

        return {
            "status": "success",
            "filename": file.filename,
            "summary": summary,
        }

    except Exception as e:
        print(f"\n[Upload Error] Gagal memproses: {file_path}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Gagal memproses PDF.")
