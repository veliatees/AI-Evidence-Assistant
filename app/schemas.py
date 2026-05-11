from pydantic import BaseModel, Field

class DocumentCreate(BaseModel):
    title: str = Field (..., min_length= 1, max_length= 200)
    text: str = Field (..., min_length= 20)

class DocumentResponse(BaseModel):
      id : str
      title: str
      char_count: int
      word_count: int

class DocumentDetailResponse(BaseModel):
        id: str
        title: str
        text: str
        char_count: int
        word_count: int

class ChunkDetailResponse(BaseModel):
        id: str
        document_id: str
        chunk_index: int
        text: str
        char_count: int
        word_count: int

class EmbeddingDetailResponse(BaseModel):
        chunk_id: str
        model_name: str
        dimensions: int
        embedding_preview: list[float]
