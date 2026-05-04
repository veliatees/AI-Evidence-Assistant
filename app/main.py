from fastapi import FastAPI
from uuid import uuid4
from app.schemas import DocumentCreate, DocumentResponse


app= FastAPI(
    title= "AI Evidence Assistant",
    version= "0.1.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/login")
def login_check():
    return {"status": "logged in"}

@app.post("/documents", response_model=DocumentResponse)
def create_document(document: DocumentCreate):
    return DocumentResponse(
        id = str (uuid4()), 
        title= document.title,
        char_count= len(document.text),
        word_count= len(document.text.split()),
    )