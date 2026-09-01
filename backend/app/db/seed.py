from datetime import date, datetime, time, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.ai_memory import AIMemory
from app.models.calendar_event import CalendarEvent
from app.models.goal import Goal, GoalMilestone
from app.models.habit import Habit, HabitLog
from app.models.note import Note
from app.models.project import Milestone, Project
from app.models.task import Subtask, Task
from app.models.user import User
from app.services.vector_service import VectorService


async def seed_demo_data(db: AsyncSession) -> User:
    """Seed comprehensive, realistic demo data for Personalix OS."""
    # Check if demo user already exists
    stmt = select(User).where(User.email == "demo@personalix.os")
    res = await db.execute(stmt)
    existing_user = res.scalar_one_or_none()
    if existing_user:
        return existing_user

    # 1. Create Demo User
    user = User(
        email="demo@personalix.os",
        hashed_password=get_password_hash("Password123!"),
        full_name="Alex Mercer",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&h=200&fit=crop&crop=faces",
        role="user",
        is_active=True,
        has_onboarded=True,
        preferences={
            "theme": "dark",
            "working_hours_start": "09:00",
            "working_hours_end": "18:00",
            "productivity_style": "deep_work",
            "ai_creativity": "balanced",
            "daily_reminder": True,
        },
    )
    db.add(user)
    await db.flush()

    # 2. Create Goals
    g1 = Goal(
        user_id=user.id,
        title="Launch Personalix OS v1.0",
        description="Ship a production-grade AI-native operating system with 100% test coverage and full documentation.",
        category="career",
        target_date=datetime.now(timezone.utc) + timedelta(days=30),
        progress=75.0,
        status="in_progress",
        color="#3b82f6",
        icon="rocket",
        metrics={"target": 100, "current": 75, "unit": "% shipped"},
    )
    g2 = Goal(
        user_id=user.id,
        title="Master Distributed Systems & High Performance Python",
        description="Complete 4 distributed computing deep-dives and implement an event-driven architecture.",
        category="learning",
        target_date=datetime.now(timezone.utc) + timedelta(days=60),
        progress=50.0,
        status="in_progress",
        color="#10b981",
        icon="book-open",
        metrics={"target": 4, "current": 2, "unit": "modules"},
    )
    g3 = Goal(
        user_id=user.id,
        title="Reach Peak Physical Endurance",
        description="Log 100km of running and maintain 5x weekly strength training sessions.",
        category="health",
        target_date=datetime.now(timezone.utc) + timedelta(days=45),
        progress=65.0,
        status="in_progress",
        color="#f59e0b",
        icon="heart",
        metrics={"target": 100, "current": 65, "unit": "km"},
    )
    db.add_all([g1, g2, g3])
    await db.flush()

    # Goal Milestones
    gm1 = GoalMilestone(goal_id=g1.id, title="Complete Backend API & Schema Architecture", is_completed=True, position=0)
    gm2 = GoalMilestone(goal_id=g1.id, title="Implement Vector RAG & Tool Calling Loop", is_completed=True, position=1)
    gm3 = GoalMilestone(goal_id=g1.id, title="Build Next.js Command Center Frontend", is_completed=False, position=2)
    db.add_all([gm1, gm2, gm3])

    # 3. Create Projects
    p1 = Project(
        user_id=user.id,
        goal_id=g1.id,
        title="Personalix OS Core Engine",
        description="FastAPI async backend, PostgreSQL pgvector integration, and unified AI orchestration services.",
        status="active",
        color="#6366f1",
        icon="cpu",
        start_date=datetime.now(timezone.utc) - timedelta(days=14),
        target_date=datetime.now(timezone.utc) + timedelta(days=14),
        progress=80.0,
        tags=["fastapi", "ai", "fullstack", "docker"],
    )
    p2 = Project(
        user_id=user.id,
        goal_id=g2.id,
        title="Distributed Queue & Cache Architecture",
        description="Redis cluster caching layer, idempotency keys, and real-time SSE streaming dispatcher.",
        status="active",
        color="#06b6d4",
        icon="server",
        start_date=datetime.now(timezone.utc) - timedelta(days=7),
        target_date=datetime.now(timezone.utc) + timedelta(days=21),
        progress=45.0,
        tags=["redis", "performance", "architecture"],
    )
    db.add_all([p1, p2])
    await db.flush()

    # Milestones
    m1 = Milestone(project_id=p1.id, title="Data Models & JWT Auth", due_date=datetime.now(timezone.utc) - timedelta(days=5), is_completed=True, position=0)
    m2 = Milestone(project_id=p1.id, title="Vector Search & Hybrid RAG Engine", due_date=datetime.now(timezone.utc) + timedelta(days=3), is_completed=True, position=1)
    m3 = Milestone(project_id=p1.id, title="End-to-End Test Suite Execution", due_date=datetime.now(timezone.utc) + timedelta(days=10), is_completed=False, position=2)
    db.add_all([m1, m2, m3])

    # 4. Create Tasks
    t1 = Task(
        user_id=user.id,
        project_id=p1.id,
        goal_id=g1.id,
        title="Refactor AI Orchestrator with Multi-Turn Tool Loop",
        description="Ensure OpenAI, Anthropic, and Offline Heuristic engines support function calling with confirmation guards.",
        status="completed",
        priority="critical",
        due_date=datetime.now(timezone.utc) - timedelta(days=1),
        estimated_duration=60,
        actual_duration=55,
        tags=["ai", "architecture"],
        completed_at=datetime.now(timezone.utc) - timedelta(days=1),
        position=0,
    )
    t2 = Task(
        user_id=user.id,
        project_id=p1.id,
        goal_id=g1.id,
        title="Build Interactive Habits Heatmap Component",
        description="365-day SVG/CSS grid showing completion density and streak progression with tooltip stats.",
        status="in_progress",
        priority="high",
        due_date=datetime.now(timezone.utc) + timedelta(hours=6),
        estimated_duration=45,
        tags=["frontend", "habits"],
        position=1,
    )
    t3 = Task(
        user_id=user.id,
        project_id=p1.id,
        goal_id=g1.id,
        title="Implement Global Command Palette (Ctrl+K)",
        description="Fuzzy keyboard search across tasks, notes, goals, and AI actions with instant keyboard navigation.",
        status="todo",
        priority="high",
        due_date=datetime.now(timezone.utc) + timedelta(days=1),
        estimated_duration=50,
        tags=["frontend", "ux"],
        position=2,
    )
    t4 = Task(
        user_id=user.id,
        project_id=p2.id,
        goal_id=g2.id,
        title="Benchmark Async Database Connection Poolers",
        description="Run load tests on SQLite async vs PostgreSQL asyncpg under 500 concurrent queries.",
        status="todo",
        priority="medium",
        due_date=datetime.now(timezone.utc) + timedelta(days=3),
        estimated_duration=40,
        tags=["database", "performance"],
        position=3,
    )
    t5 = Task(
        user_id=user.id,
        project_id=None,
        goal_id=None,
        title="Weekly Review & Workspace Cleanup",
        description="Archive stale tasks, review habit streaks, and generate next week's deep work schedule.",
        status="inbox",
        priority="low",
        due_date=datetime.now(timezone.utc) + timedelta(days=2),
        estimated_duration=25,
        tags=["productivity"],
        position=4,
    )
    db.add_all([t1, t2, t3, t4, t5])
    await db.flush()

    # Subtasks
    st1 = Subtask(task_id=t2.id, title="Implement date normalization algorithm", is_completed=True, position=0)
    st2 = Subtask(task_id=t2.id, title="Render CSS grid with 5 color intensity levels", is_completed=True, position=1)
    st3 = Subtask(task_id=t2.id, title="Add hover tooltip showing date and logs count", is_completed=False, position=2)
    db.add_all([st1, st2, st3])

    # 5. Create Habits with 30-Day Historical Check-ins
    h1 = Habit(
        user_id=user.id,
        goal_id=g1.id,
        title="Morning Deep Work Session (90 mins)",
        description="Zero notifications, focused engineering block on hardest problem.",
        frequency="daily",
        target_days=[0, 1, 2, 3, 4, 5, 6],
        reminder_time="09:00",
        streak_count=14,
        best_streak=21,
        color="#6366f1",
        icon="zap",
    )
    h2 = Habit(
        user_id=user.id,
        goal_id=g2.id,
        title="Read 1 Research Paper or RFC",
        description="Focus on distributed systems, AI alignment, or database internals.",
        frequency="daily",
        target_days=[0, 1, 2, 3, 4, 5, 6],
        reminder_time="17:00",
        streak_count=8,
        best_streak=12,
        color="#10b981",
        icon="book",
    )
    h3 = Habit(
        user_id=user.id,
        goal_id=g3.id,
        title="5km Run or Strength Workout",
        description="Maintain cardiovascular stamina and peak energy levels.",
        frequency="daily",
        target_days=[1, 2, 3, 4, 5, 6],
        reminder_time="07:00",
        streak_count=6,
        best_streak=15,
        color="#f59e0b",
        icon="activity",
    )
    db.add_all([h1, h2, h3])
    await db.flush()

    # Populate 30 days of habit logs
    today = date.today()
    for days_back in range(30):
        log_date = (today - timedelta(days=days_back)).isoformat()
        
        # Habit 1: completed 26 out of 30 days
        if days_back < 14 or days_back % 7 != 3:
            db.add(HabitLog(habit_id=h1.id, user_id=user.id, logged_date=log_date, completed=True))
        
        # Habit 2: completed 22 out of 30 days
        if days_back < 8 or days_back % 5 != 2:
            db.add(HabitLog(habit_id=h2.id, user_id=user.id, logged_date=log_date, completed=True))

        # Habit 3: completed 20 out of 30 days
        if days_back < 6 or days_back % 4 != 1:
            db.add(HabitLog(habit_id=h3.id, user_id=user.id, logged_date=log_date, completed=True))

    # 6. Create Notes
    n1 = Note(
        user_id=user.id,
        project_id=p1.id,
        goal_id=g1.id,
        title="Personalix OS Architecture Overview",
        content="""# Personalix OS Architecture

The system is constructed with a high-cohesion, decoupled full-stack paradigm:

- **Frontend**: Next.js 15 App Router, TypeScript, Tailwind CSS, Lucide icons.
- **Backend**: FastAPI with async SQLAlchemy 2.0 and Pydantic v2 validation.
- **AI Orchestration**: Multi-provider LLM abstraction with native tool calling and RAG context injection.
- **Data Layer**: Dual database support: instant SQLite for local dev & PostgreSQL + pgvector for Docker production.

Key performance criteria:
1. Sub-100ms response time on cached dashboard queries.
2. Safe confirmation execution for destructive entity deletions.
3. Offline heuristic intelligence when third-party API keys are unset.
""",
        tags=["architecture", "system-design", "fastapi"],
        is_pinned=True,
    )
    n2 = Note(
        user_id=user.id,
        project_id=p2.id,
        goal_id=g2.id,
        title="Async Event Loop Best Practices in Python 3.13",
        content="""# Python 3.13 Async Best Practices

1. Never run synchronous blocking I/O inside async route handlers.
2. Use `asyncio.to_thread` for CPU-intensive hashing algorithms if payload is large.
3. Always utilize `async_sessionmaker` and context managers for DB connection pooling.
4. Keep connection pools bounded (e.g. pool_size=10, max_overflow=20).
""",
        tags=["python", "async", "performance"],
        is_pinned=False,
    )
    db.add_all([n1, n2])

    # 7. Create Calendar Events for Today & Tomorrow
    now = datetime.now(timezone.utc)
    c1 = CalendarEvent(
        user_id=user.id,
        title="Deep Work: Personalix OS UI Implementation",
        description="Focused sprint on Kanban drag-and-drop and AI Assistant slide-over.",
        start_time=now.replace(hour=9, minute=0, second=0),
        end_time=now.replace(hour=11, minute=0, second=0),
        event_type="focus",
        color="#6366f1",
    )
    c2 = CalendarEvent(
        user_id=user.id,
        title="Architecture Review & PR Discussion",
        description="Review database schemas, vector embedding pipeline, and security endpoints.",
        start_time=now.replace(hour=14, minute=0, second=0),
        end_time=now.replace(hour=15, minute=0, second=0),
        event_type="meeting",
        color="#06b6d4",
    )
    c3 = CalendarEvent(
        user_id=user.id,
        title="Evening Endurance Run (5km)",
        description="Outdoor tempo run.",
        start_time=now.replace(hour=18, minute=30, second=0),
        end_time=now.replace(hour=19, minute=15, second=0),
        event_type="personal",
        color="#10b981",
    )
    db.add_all([c1, c2, c3])

    # 8. Create AI Memories
    mem1 = AIMemory(
        user_id=user.id,
        category="preference",
        content="Prefers working in uninterrupted deep work blocks between 09:00 and 11:30 in the morning.",
        confidence=1.0,
        source="onboarding",
    )
    mem2 = AIMemory(
        user_id=user.id,
        category="goal",
        content="Primary quarterly focus is shipping Personalix OS v1.0 and polishing technical architecture docs.",
        confidence=0.95,
        source="onboarding",
    )
    mem3 = AIMemory(
        user_id=user.id,
        category="behavioral_pattern",
        content="Most productive on Tuesdays and Thursdays; prefers batching meetings to late afternoon.",
        confidence=0.9,
        source="analytics",
    )
    db.add_all([mem1, mem2, mem3])

    # 9. Ingest Sample Document with Vectors
    doc_content = """# Personalix OS Technical Specification

Personalix OS represents an AI-native personal command center designed to unify fragmented productivity workflows.

## Core Capabilities
1. Unified Dashboard: Real-time aggregated productivity metrics, focus tasks, and calendar events.
2. Dynamic Task Engine: Multi-view Kanban, subtask decomposition, priority sorting, and auto-completion tracking.
3. Goal & Project Alignment: Two-way linkage between overarching objectives, milestones, and daily tasks.
4. Intelligent Habit Tracker: Consecutive streak calculations, 365-day interactive heatmap, and consistency scoring.
5. Semantic Knowledge Base: Hybrid lexical and vector cosine similarity search across all personal documents.
6. AI Agent System: Safe tool execution, time-blocked daily scheduling, and weekly retrospective synthesis.
"""
    await VectorService.ingest_document(
        db=db,
        user_id=user.id,
        title="Personalix OS Technical Specification",
        content=doc_content,
        file_type="md",
    )

    await db.commit()
    return user
