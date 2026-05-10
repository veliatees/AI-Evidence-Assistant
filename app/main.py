from fastapi import FastAPI, HTTPException
from uuid import uuid4
from app.database import get_connection, init_db
from app.schemas import DocumentCreate, DocumentDetailResponse, DocumentResponse, ChunkDetailResponse
from app.chunking import chunk_text

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
    chunks = chunk_text(document.text)

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO documents (id, title, text, char_count, word_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (document_id, document.title, document.text, char_count, word_count),
        )

        for index, chunk in enumerate(chunks):
            conn.execute(
                """
                INSERT INTO chunks (id, document_id, chunk_index, text, char_count, word_count)
                VALUES (?, ?, ?, ?, ?, ?) 
                """,
                (
                    str(uuid4()),
                    document_id,
                    index,
                    chunk,
                    len(chunk),
                    len(chunk.split()),
                ),
            )

    return DocumentResponse(
        id=document_id,
        title=document.title,
        char_count=char_count,
        word_count=word_count,
    )

@app.get("/documents", response_model= list[DocumentDetailResponse])
def list_documents():
        with get_connection() as conn:
            row= conn.execute(
                """
                Select id, title, text, char_count, word_count
                FROM documents
                ORDER BY rowid DESC
                """
                          ).fetchall()
            
            if row is None:
                 raise HTTPException(status_code= 404, detail= "Document not found")
            
        return [
            DocumentDetailResponse(
                id=single_row[0],
                title=single_row[1],
                text=single_row[2],
                char_count=single_row[3],
                word_count=single_row[4],
            )
            for single_row in row
        ]
@app.get("/documents/{document_id}/chunks", response_model= list[ChunkDetailResponse])
def list_documents(document_id: str):
        with get_connection() as conn:
            rows= conn.execute(
                """
                Select id, document_id, chunk_index, text, char_count, word_count
                FROM chunks
                WHERE document_id= ?
                ORDER BY chunk_index
                """, (document_id, ), 
                          ).fetchall()
            
        return [
            ChunkDetailResponse
                (
                id=single_row[0],
                document_id =single_row[1],
                chunk_index= row[2],
                text=single_row[3],
                char_count=single_row[4],
                word_count=single_row[5],
                )
            for single_row in rows
        ]