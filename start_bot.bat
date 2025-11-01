@echo off
IF NOT EXIST docs_index.faiss (
    echo Building index...
    python index_docs.py
)
uvicorn app:app --reload --port 8000
pause
