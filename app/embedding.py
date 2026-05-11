from sentence_transformers import SentenceTransformer

MODEL_NAME= "sentence-transformers/all-MiniLM-L6-v2"
_model= SentenceTransformer(MODEL_NAME)

def embed_texts(texts: list[str])-> list[list[float]]:
    embeddings= _model.encode(texts)

    return embeddings.tolist()