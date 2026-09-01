from typing import Any, List
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentResponse, SearchQuery, SearchResponse
from app.services.vector_service import VectorService

router = APIRouter()


@router.get("", response_model=List[DocumentResponse])
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    docs = await VectorService.get_documents(db=db, user_id=current_user.id)
    return [
        DocumentResponse(
            id=d.id,
            user_id=d.user_id,
            title=d.title,
            file_type=d.file_type,
            file_path=d.file_path,
            file_size=d.file_size,
            content_summary=d.content_summary,
            metadata_json=d.metadata_json,
            chunks_count=len(d.chunks) if "chunks" in d.__dict__ else 0,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )
        for d in docs
    ]


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_text_document(
    payload: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    doc = await VectorService.ingest_document(
        db=db,
        user_id=current_user.id,
        title=payload.title,
        content=payload.content or "",
        file_type=payload.file_type,
        metadata=payload.metadata,
    )
    return DocumentResponse(
        id=doc.id,
        user_id=doc.user_id,
        title=doc.title,
        file_type=doc.file_type,
        file_path=doc.file_path,
        file_size=doc.file_size,
        content_summary=doc.content_summary,
        metadata_json=doc.metadata_json,
        chunks_count=1,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document_file(
    file: UploadFile = File(...),
    title: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    content_bytes = await file.read()
    try:
        content_str = content_bytes.decode('utf-8', errors='ignore')
    except Exception:
        content_str = f"Binary file upload: {file.filename}"

    file_title = title or file.filename or "Uploaded Document"
    file_type = file.filename.split(".")[-1] if file.filename and "." in file.filename else "txt"

    doc = await VectorService.ingest_document(
        db=db,
        user_id=current_user.id,
        title=file_title,
        content=content_str,
        file_type=file_type,
        metadata={"original_filename": file.filename, "content_type": file.content_type},
    )
    return DocumentResponse(
        id=doc.id,
        user_id=doc.user_id,
        title=doc.title,
        file_type=doc.file_type,
        file_path=doc.file_path,
        file_size=doc.file_size,
        content_summary=doc.content_summary,
        metadata_json=doc.metadata_json,
        chunks_count=1,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    payload: SearchQuery,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    results = await VectorService.search_knowledge(
        db=db,
        user_id=current_user.id,
        query=payload.query,
        limit=payload.limit,
        category=payload.category,
    )
    return SearchResponse(
        query=payload.query,
        results=results,
        total=len(results),
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await VectorService.delete_document(db=db, user_id=current_user.id, doc_id=document_id)
