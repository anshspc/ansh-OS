import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_notes_and_vector_search(client: AsyncClient, auth_headers: dict):
    # 1. Create a Note
    note_resp = await client.post(
        "/api/v1/notes",
        headers=auth_headers,
        json={
            "title": "PostgreSQL pgvector Config",
            "content": "To configure pgvector with SQLAlchemy, use the vector data type and cosine distance operator.",
            "tags": ["postgres", "vector"],
        },
    )
    assert note_resp.status_code == 201
    note = note_resp.json()
    assert note["title"] == "PostgreSQL pgvector Config"

    # 2. Create a Text Document (Chunked & Embedded)
    doc_resp = await client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "title": "System Architecture Guide",
            "file_type": "md",
            "content": "Personalix OS features an async FastAPI core, JWT security, and dual database support for SQLite and PostgreSQL.",
        },
    )
    assert doc_resp.status_code == 201
    doc = doc_resp.json()
    assert doc["chunks_count"] >= 1

    # 3. Hybrid Semantic Search
    search_resp = await client.post(
        "/api/v1/documents/search",
        headers=auth_headers,
        json={"query": "FastAPI architecture", "limit": 5},
    )
    assert search_resp.status_code == 200
    results = search_resp.json()["results"]
    assert len(results) >= 1
