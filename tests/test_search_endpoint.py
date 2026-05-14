from fastapi.testclient import TestClient

import app.main as main


client = TestClient(main.app)


def test_search_endpoint_returns_relevant_chunks(monkeypatch):
    def fake_retrieve_relevant_chunks(query: str, top_k: int = 3):
        assert query == "privacy policy"
        assert top_k == 2
        return [
            {
                "chunk_id": "chunk-1",
                "document_id": "doc-1",
                "chunk_index": 0,
                "text": "The privacy policy explains data retention.",
                "score": 0.91,
            }
        ]

    monkeypatch.setattr(
        main,
        "retrieve_relevant_chunks",
        fake_retrieve_relevant_chunks,
    )

    response = client.post(
        "/search",
        json={"query": "privacy policy", "top_k": 2},
    )

    assert response.status_code == 200
    assert response.json() == {
        "query": "privacy policy",
        "results": [
            {
                "chunk_id": "chunk-1",
                "document_id": "doc-1",
                "chunk_index": 0,
                "text": "The privacy policy explains data retention.",
                "score": 0.91,
            }
        ],
    }


def test_search_endpoint_rejects_invalid_top_k():
    response = client.post(
        "/search",
        json={"query": "privacy policy", "top_k": 0},
    )

    assert response.status_code == 422
