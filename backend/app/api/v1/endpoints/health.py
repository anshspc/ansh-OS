from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "Personalix OS API", "version": "1.0.0"}


@router.get("/health/db")
async def health_db_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "connected", "database": "healthy"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
