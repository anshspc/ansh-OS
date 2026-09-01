from app.schemas.user import (
    UserRegister, UserLogin, Token, TokenRefresh, UserUpdate, UserResponse, UserPreferences
)
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskBatchUpdate, SubtaskCreate, SubtaskUpdate, SubtaskResponse
)
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, MilestoneCreate, MilestoneUpdate, MilestoneResponse
)
from app.schemas.goal import (
    GoalCreate, GoalUpdate, GoalResponse, GoalMilestoneCreate, GoalMilestoneUpdate, GoalMilestoneResponse
)
from app.schemas.habit import (
    HabitCreate, HabitUpdate, HabitResponse, HabitLogCreate, HabitLogResponse
)
from app.schemas.note import (
    NoteCreate, NoteUpdate, NoteResponse
)
from app.schemas.document import (
    DocumentCreate, DocumentResponse, DocumentChunkResponse, SearchQuery, SearchResultItem, SearchResponse
)
from app.schemas.calendar_event import (
    CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse
)
from app.schemas.daily_plan import (
    DailyPlanCreate, DailyPlanUpdate, DailyPlanResponse, TimeBlockSchema, GenerateDailyPlanRequest
)
from app.schemas.weekly_review import (
    WeeklyReviewCreate, WeeklyReviewResponse, GenerateWeeklyReviewRequest
)
from app.schemas.ai import (
    AIChatMessageRequest, AIChatResponse, AIConversationResponse, AIMessageResponse,
    AIMemoryCreate, AIMemoryUpdate, AIMemoryResponse, ToolCallItem, ToolExecutionConfirmationRequest
)
from app.schemas.analytics import (
    ProductivityScoreResponse, ProductivityBreakdown, DashboardSummaryResponse, ActivityLogResponse
)

__all__ = [
    "UserRegister", "UserLogin", "Token", "TokenRefresh", "UserUpdate", "UserResponse", "UserPreferences",
    "TaskCreate", "TaskUpdate", "TaskResponse", "TaskBatchUpdate", "SubtaskCreate", "SubtaskUpdate", "SubtaskResponse",
    "ProjectCreate", "ProjectUpdate", "ProjectResponse", "MilestoneCreate", "MilestoneUpdate", "MilestoneResponse",
    "GoalCreate", "GoalUpdate", "GoalResponse", "GoalMilestoneCreate", "GoalMilestoneUpdate", "GoalMilestoneResponse",
    "HabitCreate", "HabitUpdate", "HabitResponse", "HabitLogCreate", "HabitLogResponse",
    "NoteCreate", "NoteUpdate", "NoteResponse",
    "DocumentCreate", "DocumentResponse", "DocumentChunkResponse", "SearchQuery", "SearchResultItem", "SearchResponse",
    "CalendarEventCreate", "CalendarEventUpdate", "CalendarEventResponse",
    "DailyPlanCreate", "DailyPlanUpdate", "DailyPlanResponse", "TimeBlockSchema", "GenerateDailyPlanRequest",
    "WeeklyReviewCreate", "WeeklyReviewResponse", "GenerateWeeklyReviewRequest",
    "AIChatMessageRequest", "AIChatResponse", "AIConversationResponse", "AIMessageResponse",
    "AIMemoryCreate", "AIMemoryUpdate", "AIMemoryResponse", "ToolCallItem", "ToolExecutionConfirmationRequest",
    "ProductivityScoreResponse", "ProductivityBreakdown", "DashboardSummaryResponse", "ActivityLogResponse",
]
