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
            id=document_id,
            title=document.title,
            char_count=char_count,
            word_count=word_count,
        )

@app.get("/documents", response_model= list[DocumentResponse])
def list_documents():
        with get_connection() as conn:
            rows= conn.execute(
                """
                Select id, title, char_count, word_count
                FROM documents
                ORDER BY rowid DESC
                """
                          ).fetchall()
        return [
            DocumentResponse(
                id= row[0],
                title= row[1],
                char_count=row[2],
                word_count= row[3],
            )
            for row in rows
        ]