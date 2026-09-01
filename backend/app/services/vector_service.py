import hashlib
import json
import math
import re
from typing import Any, Dict, List, Optional
import httpx
import numpy as np
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.core.logging import logger
from app.models.document import Document, DocumentChunk
from app.models.note import Note
from app.models.project import Project
from app.models.task import Task
from app.schemas.document import DocumentCreate, SearchResultItem
from app.services.activity_service import ActivityService


class VectorService:
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        """Split text into overlapping character chunks cleanly on paragraph or sentence boundaries."""
        if not text:
            return []
        
        # Clean text
        text = re.sub(r'\r\n', '\n', text)
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            if len(current_chunk) + len(p) <= chunk_size:
                current_chunk = (current_chunk + "\n\n" + p).strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                if len(p) > chunk_size:
                    # Break long paragraph on sentence boundaries
                    sentences = re.split(r'(?<=[.!?])\s+', p)
                    curr_sent_chunk = ""
                    for s in sentences:
                        if len(curr_sent_chunk) + len(s) <= chunk_size:
                            curr_sent_chunk = (curr_sent_chunk + " " + s).strip()
                        else:
                            if curr_sent_chunk:
                                chunks.append(curr_sent_chunk)
                            curr_sent_chunk = s
                    if curr_sent_chunk:
                        current_chunk = curr_sent_chunk
                    else:
                        current_chunk = ""
                else:
                    current_chunk = p

        if current_chunk:
            chunks.append(current_chunk)

        return chunks if chunks else [text[:chunk_size]]

    @staticmethod
    async def get_embedding(text: str) -> List[float]:
        """Get 1536-dimensional embedding vector via OpenAI if configured, or deterministic vector fallback."""
        if settings.OPENAI_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        "https://api.openai.com/v1/embeddings",
                        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                        json={
                            "input": text[:8000],
                            "model": settings.EMBEDDING_MODEL,
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["data"][0]["embedding"]
            except Exception as e:
                logger.warning(f"OpenAI embedding API failed, falling back to local vector encoder: {e}")

        # Deterministic offline vector encoder (1536 dimensions) using normalized hashed frequency
        dim = 1536
        vec = np.zeros(dim, dtype=np.float32)
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return vec.tolist()

        for w in words:
            # Deterministic hash to dimension index
            h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if ((h >> 8) % 2 == 0) else -1.0
            vec[idx] += sign

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return vec.tolist()

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """Compute cosine similarity between two vector lists."""
        a = np.array(v1, dtype=np.float32)
        b = np.array(v2, dtype=np.float32)
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    @staticmethod
    async def ingest_document(
        db: AsyncSession,
        user_id: str,
        title: str,
        content: str,
        file_type: str = "txt",
        file_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """Ingest document, split into chunks, compute embeddings, and store in DB."""
        summary = content[:200] + ("..." if len(content) > 200 else "")
        doc = Document(
            user_id=user_id,
            title=title,
            file_type=file_type,
            file_path=file_path,
            file_size=len(content.encode('utf-8')),
            content_summary=summary,
            metadata_json=metadata or {},
        )
        db.add(doc)
        await db.flush()

        chunks = VectorService.chunk_text(content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        for idx, chunk_str in enumerate(chunks):
            embedding = await VectorService.get_embedding(chunk_str)
            chunk_record = DocumentChunk(
                document_id=doc.id,
                user_id=user_id,
                chunk_index=idx,
                content=chunk_str,
                embedding_json=embedding,
                metadata_json={"title": title, "file_type": file_type},
            )
            db.add(chunk_record)

        await db.commit()
        await db.refresh(doc)

        await ActivityService.log_activity(
            db=db,
            user_id=user_id,
            action="document_uploaded",
            entity_type="document",
            entity_id=doc.id,
            details={"title": doc.title, "chunks": len(chunks)},
        )

        return doc

    @staticmethod
    async def search_knowledge(
        db: AsyncSession,
        user_id: str,
        query: str,
        limit: int = 6,
        category: Optional[str] = None,
    ) -> List[SearchResultItem]:
        """Perform hybrid semantic + lexical search across Documents, Notes, Tasks, and Projects."""
        results: List[SearchResultItem] = []
        query_embedding = await VectorService.get_embedding(query)
        q_lower = query.lower()

        # 1. Search Document Chunks via Vector Cosine Similarity
        if category in (None, "all", "documents"):
            stmt_chunks = select(DocumentChunk).where(DocumentChunk.user_id == user_id)
            res_chunks = await db.execute(stmt_chunks)
            chunks = list(res_chunks.scalars().all())

            for chunk in chunks:
                if chunk.embedding_json:
                    sim = VectorService.cosine_similarity(query_embedding, chunk.embedding_json)
                    # Keyword bonus
                    if q_lower in chunk.content.lower():
                        sim += 0.2
                    if sim > 0.15:
                        doc_title = chunk.metadata_json.get("title", "Document")
                        results.append(
                            SearchResultItem(
                                id=chunk.document_id,
                                type="document",
                                title=doc_title,
                                snippet=chunk.content[:240] + ("..." if len(chunk.content) > 240 else ""),
                                score=round(float(sim), 3),
                                metadata=chunk.metadata_json or {},
                            )
                        )

        # 2. Search Notes
        if category in (None, "all", "notes"):
            stmt_notes = select(Note).where(
                Note.user_id == user_id,
                or_(
                    Note.title.ilike(f"%{query}%"),
                    Note.content.ilike(f"%{query}%"),
                ),
            )
            res_notes = await db.execute(stmt_notes)
            notes = list(res_notes.scalars().all())
            for n in notes:
                results.append(
                    SearchResultItem(
                        id=n.id,
                        type="note",
                        title=n.title,
                        snippet=n.content[:240] + ("..." if len(n.content) > 240 else ""),
                        score=0.85 if query.lower() in n.title.lower() else 0.65,
                        metadata={"tags": n.tags, "is_pinned": n.is_pinned},
                    )
                )

        # 3. Search Tasks
        if category in (None, "all", "tasks"):
            stmt_tasks = select(Task).where(
                Task.user_id == user_id,
                or_(
                    Task.title.ilike(f"%{query}%"),
                    Task.description.ilike(f"%{query}%"),
                ),
            )
            res_tasks = await db.execute(stmt_tasks)
            tasks = list(res_tasks.scalars().all())
            for t in tasks:
                results.append(
                    SearchResultItem(
                        id=t.id,
                        type="task",
                        title=t.title,
                        snippet=t.description or f"Status: {t.status} | Priority: {t.priority}",
                        score=0.80 if query.lower() in t.title.lower() else 0.60,
                        metadata={"status": t.status, "priority": t.priority, "due_date": str(t.due_date)},
                    )
                )

        # 4. Search Projects
        if category in (None, "all", "projects"):
            stmt_proj = select(Project).where(
                Project.user_id == user_id,
                or_(
                    Project.title.ilike(f"%{query}%"),
                    Project.description.ilike(f"%{query}%"),
                ),
            )
            res_proj = await db.execute(stmt_proj)
            proj_list = list(res_proj.scalars().all())
            for p in proj_list:
                results.append(
                    SearchResultItem(
                        id=p.id,
                        type="project",
                        title=p.title,
                        snippet=p.description or f"Status: {p.status} | Progress: {p.progress}%",
                        score=0.82 if query.lower() in p.title.lower() else 0.60,
                        metadata={"status": p.status, "progress": p.progress},
                    )
                )

        # Sort by score descending and take top limit
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    @staticmethod
    async def get_documents(db: AsyncSession, user_id: str) -> List[Document]:
        stmt = (
            select(Document)
            .options(selectinload(Document.chunks))
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete_document(db: AsyncSession, user_id: str, doc_id: str) -> None:
        stmt = select(Document).where(Document.id == doc_id, Document.user_id == user_id)
        result = await db.execute(stmt)
        doc = result.scalar_one_or_none()
        if not doc:
            raise NotFoundException(resource="Document", identifier=doc_id)
        await db.delete(doc)
        await db.commit()
