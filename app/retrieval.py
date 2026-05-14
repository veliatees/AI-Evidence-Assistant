import math, json
from app.embedding import embed_texts
from app.database import get_connection

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a==0 or norm_b==0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def retrieve_relevant_chunks(query: str, top_k: int = 3) -> list[dict]:
    query_embedding = embed_texts([query])[0]

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.id, c.document_id, c.chunk_index, c.text, e.embedding
            FROM chunks c
            JOIN chunk_embeddings e ON e.chunk_id = c.id
            """
        ).fetchall()

    results = []

    for row in rows:
        stored_embedding = json.loads(row[4])
        score = cosine_similarity(query_embedding, stored_embedding)

        results.append(
            {
                "chunk_id": row[0],
                "document_id": row[1],
                "chunk_index": row[2],
                "text": row[3],
                "score": score,
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)

    return results[:top_k]
