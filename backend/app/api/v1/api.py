from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai,
    analytics,
    auth,
    calendar,
    daily_plans,
    documents,
    goals,
    habits,
    health,
    notes,
    projects,
    tasks,
    voice,
    weekly_reviews,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(goals.router, prefix="/goals", tags=["Goals"])
api_router.include_router(habits.router, prefix="/habits", tags=["Habits"])
api_router.include_router(notes.router, prefix="/notes", tags=["Notes"])
api_router.include_router(documents.router, prefix="/documents", tags=["Knowledge & Documents"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
api_router.include_router(daily_plans.router, prefix="/daily-plans", tags=["Daily Plans"])
api_router.include_router(weekly_reviews.router, prefix="/weekly-reviews", tags=["Weekly Reviews"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Assistant & Memory"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Dashboard"])
api_router.include_router(voice.router, prefix="/voice", tags=["Personalix Voice"])
