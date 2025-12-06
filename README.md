# Chatbot PDF dengan Retrieval-Augmented Generation (RAG)

Proyek ini adalah **Chatbot PDF** yang menggunakan mesin Retrieval-Augmented Generation (RAG). Chatbot ini memungkinkan pengguna untuk mengunggah dokumen PDF, berinteraksi dengan konten melalui antarmuka chat, dan beralih antara beberapa sesi chat dengan mudah. Sistem ini dirancang untuk menyimpan riwayat chat dan mempertahankan status aplikasi meskipun halaman di-refresh.



### Prasyarat
- Python 3.11+
- Html, css, dan js
- Docker
- Postgre

### Setup proyek

1. Clone repositori:
   ```bash
   git clone https://github.com/ArifRahmanHakima/pdf-rag-engine.git
   cd pdf-rag-engine
   ```

2. Buat virtual environment dan instal dependensi:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Konfigurasi variabel lingkungan:
   Buat file `.env` di direktori
   ```bash
    # === OPENROUTER ===
    OPENROUTER_API_KEY= Masukan API Openroute
    OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
    LLM_MODEL=openai/gpt-4o-mini
    VISION_MODEL=openai/gpt-4o-mini

    # === EMBEDDING ===
    EMBEDDING_MODEL=intfloat/e5-small-v2

    # === DIR ===
    WORKING_DIR=./rag_storage
    UPLOAD_DIR=./uploads
    MAX_PDF_SIZE_MB=10

    # === REDIS ===
    REDIS_HOST=localhost
    REDIS_PORT=6379

    # === POSTGRES ===
    POSTGRES_DB=chatbot
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=Isi password postgre
    POSTGRES_HOST=localhost
    POSTGRES_PORT=Masukan port sesuai port postgre

    # === TOKEN LIMITS ===
    MAX_INPUT_TOKENS=800
    MAX_OUTPUT_TOKENS=512
   ```
   Buat file `docker-compose.yml`
   ```bash
    version: '3.8'

    services:
    qdrant:
        image: qdrant/qdrant
        ports:
        - "6333:6333"
        volumes:
        - qdrant_data:/qdrant/storage

    redis:
        image: redis:alpine
        ports:
        - "6379:6379"

    postgres:
        image: postgres:14
        environment:
        POSTGRES_DB: chatbot
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: postgres
        ports:
        - "5432:5432"
        volumes:
        - pgdata:/var/lib/postgresql/data

    volumes:
    qdrant_data:
    pgdata:
   ```

4. Jalankan backend:
    jalankan perintah berikut ke terminal untuk membaut tabel data:
   ```bash
   pyhton -m api.services.init_db
   ```
    jalan perintah berikut untuk menjalankan docker compose:
    ```bash
    docker-compose up -d
    ```
    Jalan perintah berikut untuk membuka ui
    ```bash
    uvicorn api.main:app --reload	
    ```

5. Uji coba chatbot
