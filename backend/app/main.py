from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import RequestLoggingMiddleware, logger
from app.db.seed import seed_demo_data
from app.db.session import AsyncSessionLocal, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Personalix OS Backend Engine...")

    await init_db()

    # Auto-seed demo dataset on startup.
    async with AsyncSessionLocal() as session:
        try:
            await seed_demo_data(session)
            logger.info("Demo user and starter dataset verified/seeded.")
        except Exception as e:
            logger.warning(f"Demo seed notice: {e}")

    logger.info(
        f"Personalix OS running on http://{settings.HOST}:{settings.PORT}"
    )

    yield

    logger.info("Shutting down Personalix OS Backend...")


# ==========================================
# API Documentation
# ==========================================
# Swagger/ReDoc remain available during development
# but are disabled in production.
is_production = settings.ENVIRONMENT.strip().lower() == "production"

app = FastAPI(
    title="Personalix OS API",
    description="Production-Grade AI-Powered Personal Operating System & Command Center",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
)


# ==========================================
# Request Logging Middleware
# ==========================================
app.add_middleware(RequestLoggingMiddleware)


# ==========================================
# CORS Configuration
# ==========================================
# Never fall back to "*" because credentials are enabled.
allowed_origins = (
    settings.CORS_ORIGINS
    if isinstance(settings.CORS_ORIGINS, list)
    else []
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
)


# ==========================================
# Custom Exception Handler
# ==========================================
@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.detail,
                "request_id": getattr(
                    request.state,
                    "request_id",
                    None,
                ),
            }
        },
        headers=exc.headers,
    )


# ==========================================
# Root Endpoint
# ==========================================
@app.get("/")
async def root():
    return {
        "app": "Personalix OS",
        "tagline": "One intelligent operating system for managing your personal life and work.",
        "version": "1.0.0",
        "docs": "/docs" if not is_production else None,
        "health": "/api/v1/health",
    }


# ==========================================
# API v1 Router
# ==========================================
app.include_router(
    api_router,
    prefix="/api/v1",
)
