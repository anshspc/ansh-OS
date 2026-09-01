from typing import Any, Callable, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.calendar_event import CalendarEventCreate
from app.schemas.daily_plan import GenerateDailyPlanRequest
from app.schemas.goal import GoalCreate
from app.schemas.habit import HabitCreate, HabitLogCreate
from app.schemas.note import NoteCreate
from app.schemas.project import ProjectCreate
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.weekly_review import GenerateWeeklyReviewRequest
from app.services.analytics_service import AnalyticsService
from app.services.calendar_service import CalendarService
from app.services.daily_plan_service import DailyPlanService
from app.services.goal_service import GoalService
from app.services.habit_service import HabitService
from app.services.note_service import NoteService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.vector_service import VectorService
from app.services.weekly_review_service import WeeklyReviewService

# Standard OpenAI-compatible Tool Definitions
AVAILABLE_AI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task in the user's task management system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the task."},
                    "description": {"type": "string", "description": "Optional details about the task."},
                    "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"], "default": "medium"},
                    "estimated_duration": {"type": "integer", "description": "Estimated time in minutes.", "default": 30},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional list of tags."},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task's status, priority, or title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The unique ID of the task to update."},
                    "status": {"type": "string", "enum": ["inbox", "todo", "in_progress", "completed", "archived"]},
                    "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                    "title": {"type": "string"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task. Requires confirmation for safety.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The unique ID of the task to delete."},
                    "confirmed": {"type": "boolean", "description": "Set to true only if explicitly confirmed by user."},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List existing tasks filtered by status or priority.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["inbox", "todo", "in_progress", "completed", "archived"]},
                    "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                    "limit": {"type": "integer", "default": 20},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_note",
            "description": "Create a new note or save information to knowledge base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the note."},
                    "content": {"type": "string", "description": "Full markdown content of the note."},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_goal",
            "description": "Create a new high-level goal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the goal."},
                    "category": {"type": "string", "enum": ["career", "learning", "health", "finance", "personal"], "default": "career"},
                    "description": {"type": "string"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_habit",
            "description": "Create a recurring habit to track.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Habit title."},
                    "frequency": {"type": "string", "enum": ["daily", "weekly"], "default": "daily"},
                    "reminder_time": {"type": "string", "description": "Optional reminder time e.g. 08:00."},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "Semantic search across documents, notes, projects, and tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query or concept."},
                    "limit": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_daily_plan",
            "description": "Generate an automated time-blocked daily schedule based on tasks and habits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Target date YYYY-MM-DD."},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_weekly_review",
            "description": "Generate an AI summary of weekly wins, bottlenecks, and productivity score.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date YYYY-MM-DD."},
                    "end_date": {"type": "string", "description": "End date YYYY-MM-DD."},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_productivity_stats",
            "description": "Retrieve the user's transparent 0-100 productivity score and metrics breakdown.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]


class ToolDispatcher:
    @staticmethod
    async def dispatch(
        db: AsyncSession,
        user_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a recognized tool securely and return structured results."""
        try:
            if tool_name == "create_task":
                payload = TaskCreate(
                    title=arguments.get("title", "New Task"),
                    description=arguments.get("description"),
                    priority=arguments.get("priority", "medium"),
                    estimated_duration=arguments.get("estimated_duration", 30),
                    tags=arguments.get("tags", []),
                )
                task = await TaskService.create_task(db, user_id, payload)
                return {"status": "success", "message": f"Created task '{task.title}'", "data": {"id": task.id, "title": task.title}}

            elif tool_name == "update_task":
                task_id = arguments["task_id"]
                payload = TaskUpdate(
                    status=arguments.get("status"),
                    priority=arguments.get("priority"),
                    title=arguments.get("title"),
                )
                updated = await TaskService.update_task(db, user_id, task_id, payload)
                return {"status": "success", "message": f"Updated task '{updated.title}'", "data": {"id": updated.id}}

            elif tool_name == "delete_task":
                task_id = arguments["task_id"]
                confirmed = arguments.get("confirmed", False)
                if not confirmed:
                    return {
                        "status": "requires_confirmation",
                        "message": f"Deleting task {task_id} requires confirmation.",
                        "data": {"action": "delete_task", "task_id": task_id},
                    }
                await TaskService.delete_task(db, user_id, task_id)
                return {"status": "success", "message": f"Deleted task {task_id}"}

            elif tool_name == "list_tasks":
                tasks = await TaskService.get_tasks(
                    db,
                    user_id,
                    status=arguments.get("status"),
                    priority=arguments.get("priority"),
                    limit=arguments.get("limit", 20),
                )
                return {
                    "status": "success",
                    "data": [{"id": t.id, "title": t.title, "status": t.status, "priority": t.priority} for t in tasks],
                }

            elif tool_name == "create_note":
                payload = NoteCreate(
                    title=arguments.get("title", "Note"),
                    content=arguments.get("content", ""),
                    tags=arguments.get("tags", []),
                )
                note = await NoteService.create_note(db, user_id, payload)
                return {"status": "success", "message": f"Created note '{note.title}'", "data": {"id": note.id, "title": note.title}}

            elif tool_name == "create_goal":
                payload = GoalCreate(
                    title=arguments.get("title", "Goal"),
                    category=arguments.get("category", "career"),
                    description=arguments.get("description"),
                )
                goal = await GoalService.create_goal(db, user_id, payload)
                return {"status": "success", "message": f"Created goal '{goal['title']}'", "data": goal}

            elif tool_name == "create_habit":
                payload = HabitCreate(
                    title=arguments.get("title", "Habit"),
                    frequency=arguments.get("frequency", "daily"),
                    reminder_time=arguments.get("reminder_time"),
                )
                habit = await HabitService.create_habit(db, user_id, payload)
                return {"status": "success", "message": f"Created habit '{habit['title']}'", "data": habit}

            elif tool_name == "search_knowledge":
                query = arguments.get("query", "")
                limit = arguments.get("limit", 5)
                results = await VectorService.search_knowledge(db, user_id, query, limit=limit)
                return {
                    "status": "success",
                    "data": [r.model_dump() for r in results],
                }

            elif tool_name == "generate_daily_plan":
                plan = await DailyPlanService.generate_daily_plan(
                    db, user_id, GenerateDailyPlanRequest(date=arguments.get("date"))
                )
                return {
                    "status": "success",
                    "message": f"Generated plan for {plan.plan_date}",
                    "data": {"plan_date": plan.plan_date, "blocks_count": len(plan.time_blocks_json)},
                }

            elif tool_name == "generate_weekly_review":
                review = await WeeklyReviewService.generate_weekly_review(
                    db, user_id, GenerateWeeklyReviewRequest(
                        start_date=arguments.get("start_date"),
                        end_date=arguments.get("end_date"),
                    )
                )
                return {
                    "status": "success",
                    "message": f"Generated weekly review for {review.start_date} - {review.end_date}",
                    "data": {"score": review.productivity_score, "summary": review.summary},
                }

            elif tool_name == "get_productivity_stats":
                stats = await AnalyticsService.compute_productivity_score(db, user_id)
                return {
                    "status": "success",
                    "data": stats.model_dump(),
                }

            else:
                return {"status": "failed", "error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"status": "failed", "error": str(e)}
