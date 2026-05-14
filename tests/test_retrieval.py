import json

import pytest

from app import database
from app import retrieval


def test_retrieve_relevant_chunks_orders_by_similarity(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "app.db")
    monkeypatch.setattr(retrieval, "embed_texts", lambda texts: [[1.0, 0.0]])
    database.init_db()

    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO documents (id, title, text, char_count, word_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("doc-1", "Evidence", "alpha beta gamma", 16, 3),
        )
        rows = [
            ("chunk-a", 0, "alpha evidence", [1.0, 0.0]),
            ("chunk-b", 1, "unrelated", [0.0, 1.0]),
            ("chunk-c", 2, "partial evidence", [0.5, 0.5]),
        ]
        for chunk_id, chunk_index, text, embedding in rows:
            conn.execute(
                """
                INSERT INTO chunks (id, document_id, chunk_index, text, char_count, word_count)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    "doc-1",
                    chunk_index,
                    text,
                    len(text),
                    len(text.split()),
                ),
            )
            conn.execute(
                """
                INSERT INTO chunk_embeddings (id, chunk_id, embedding, model_name, dimensions)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    f"embedding-{chunk_id}",
                    chunk_id,
                    json.dumps(embedding),
                    "test-model",
                    len(embedding),
                ),
            )

    results = retrieval.retrieve_relevant_chunks("alpha", top_k=2)

    assert [result["chunk_id"] for result in results] == ["chunk-a", "chunk-c"]
    assert results[0]["score"] == pytest.approx(1.0)
    assert results[1]["score"] == pytest.approx(0.70710678)


def test_cosine_similarity_returns_zero_for_zero_vectors():
    assert retrieval.cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0
