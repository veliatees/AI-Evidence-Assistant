from fastapi import FastAPI
from uuid import uuid4
from app.schemas import DocumentCreate, DocumentResponse
from app.database import get_connection, init_db

app= FastAPI(
    title= "AI Evidence Assistant",
    version= "0.1.0",
)

init_db()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/login")
def login_check():
    return {"status": "logged in"}

@app.post("/documents", response_model=DocumentResponse)
def create_document(document: DocumentCreate):
    document_id = str(uuid4())
    char_count = len(document.text)
    word_count = len(document.text.split())
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO documents (id, title, text, char_count, word_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (document_id, document.title, document.text, char_count, word_count))
    return DocumentResponse(
        id = str (uuid4()), 
        title= document.title,
        char_count= len(document.text),
        word_count= len(document.text.split()),
    )

#sdasd