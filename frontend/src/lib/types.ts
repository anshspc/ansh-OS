export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  role: string;
  is_active: boolean;
  has_onboarded: boolean;
  preferences: {
    theme?: string;
    working_hours_start?: string;
    working_hours_end?: string;
    productivity_style?: string;
    ai_creativity?: string;
    daily_reminder?: boolean;
  };
  created_at: string;
  updated_at: string;
}

export interface Subtask {
  id: string;
  task_id: string;
  title: string;
  is_completed: boolean;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  user_id: string;
  project_id?: string | null;
  goal_id?: string | null;
  title: string;
  description?: string | null;
  status: "inbox" | "todo" | "in_progress" | "completed" | "archived";
  priority: "critical" | "high" | "medium" | "low";
  due_date?: string | null;
  estimated_duration: number;
  actual_duration: number;
  tags: string[];
  recurring: boolean;
  recurrence_rule?: string | null;
  position: number;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
  subtasks: Subtask[];
}

export interface Milestone {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  due_date?: string;
  is_completed: boolean;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  user_id: string;
  goal_id?: string | null;
  title: string;
  description?: string | null;
  status: "active" | "completed" | "on_hold" | "archived";
  color: string;
  icon: string;
  start_date?: string | null;
  target_date?: string | null;
  progress: number;
  tags: string[];
  created_at: string;
  updated_at: string;
  milestones: Milestone[];
  tasks_count?: number;
  completed_tasks_count?: number;
}

export interface GoalMilestone {
  id: string;
  goal_id: string;
  title: string;
  is_completed: boolean;
  due_date?: string;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description?: string | null;
  category: "career" | "learning" | "health" | "finance" | "personal";
  target_date?: string | null;
  progress: number;
  status: "in_progress" | "achieved" | "paused" | "cancelled";
  color: string;
  icon: string;
  metrics: {
    current?: number;
    target?: number;
    unit?: string;
  };
  created_at: string;
  updated_at: string;
  milestones: GoalMilestone[];
  linked_projects_count?: number;
  linked_tasks_count?: number;
}

export interface HabitLog {
  id: string;
  habit_id: string;
  user_id: string;
  logged_date: string;
  completed: boolean;
  value: number;
  notes?: string | null;
  created_at: string;
}

export interface Habit {
  id: string;
  user_id: string;
  goal_id?: string | null;
  title: string;
  description?: string | null;
  frequency: "daily" | "weekly";
  target_days: number[];
  reminder_time?: string | null;
  streak_count: number;
  best_streak: number;
  color: string;
  icon: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  today_completed?: boolean;
  completion_rate_30d?: number;
  recent_logs: HabitLog[];
}

export interface Note {
  id: string;
  user_id: string;
  project_id?: string | null;
  goal_id?: string | null;
  title: string;
  content: string;
  tags: string[];
  is_pinned: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  user_id: string;
  title: string;
  file_type: string;
  file_path?: string | null;
  file_size: number;
  content_summary?: string | null;
  metadata_json: Record<string, any>;
  chunks_count?: number;
  created_at: string;
  updated_at: string;
}

export interface CalendarEvent {
  id: string;
  user_id: string;
  title: string;
  description?: string | null;
  start_time: string;
  end_time: string;
  is_all_day: boolean;
  event_type: "focus" | "meeting" | "deadline" | "reminder" | "personal";
  color: string;
  location?: string | null;
  recurrence?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TimeBlock {
  id: string;
  start_time: string;
  end_time: string;
  title: string;
  type: "task" | "habit" | "event" | "break" | "deep_work";
  task_id?: string | null;
  completed: boolean;
}

export interface DailyPlan {
  id: string;
  user_id: string;
  plan_date: string;
  summary?: string | null;
  time_blocks_json: TimeBlock[];
  focus_areas_json: string[];
  status: "generated" | "accepted" | "modified" | "completed";
  created_at: string;
  updated_at: string;
}

export interface WeeklyReview {
  id: string;
  user_id: string;
  start_date: string;
  end_date: string;
  summary: string;
  wins_json: string[];
  bottlenecks_json: string[];
  recommendations_json: string[];
  productivity_score: number;
  stats_json: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface AIMemory {
  id: string;
  user_id: string;
  category: "preference" | "goal" | "project" | "fact" | "behavioral_pattern";
  key?: string | null;
  content: string;
  confidence: number;
  is_active: boolean;
  source: string;
  last_accessed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ToolCallItem {
  id: string;
  name: string;
  arguments: Record<string, any>;
  result?: Record<string, any>;
  status: string;
}

export interface AIChatResponse {
  conversation_id: string;
  message_id: string;
  reply: string;
  role: string;
  provider: string;
  model: string;
  tool_calls?: ToolCallItem[];
  tokens_used: number;
}

export interface AIMessage {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  tool_calls?: any;
  tool_results?: any;
  model?: string;
  created_at: string;
}

export interface ProductivityScore {
  total_score: number;
  grade: "S" | "A" | "B" | "C" | "D";
  breakdown: {
    task_completion: number;
    goal_progress: number;
    focus_consistency: number;
    habit_consistency: number;
    deadline_management: number;
  };
  explanation: string;
  insights: string[];
  trend_compared_to_last_week: number;
}

export interface DashboardSummary {
  greeting: string;
  today_date: string;
  productivity_score: number;
  productivity_grade: string;
  tasks_summary: {
    total: number;
    completed: number;
    pending: number;
    overdue: number;
    high_priority: number;
  };
  habits_summary: {
    total: number;
    completed_today: number;
    current_streak_best: number;
  };
  active_projects_count: number;
  active_goals_count: number;
  today_focus_tasks: Array<{
    id: string;
    title: string;
    status: string;
    priority: string;
    due_date?: string;
    estimated_duration: number;
    tags: string[];
  }>;
  today_events: Array<{
    id: string;
    title: string;
    start_time: string;
    end_time: string;
    event_type: string;
    color: string;
    location?: string;
  }>;
  ai_daily_insight: string;
  recent_activities: Array<{
    id: string;
    action: string;
    entity_type: string;
    entity_id?: string;
    details: Record<string, any>;
    created_at: string;
  }>;
}

export interface SearchResultItem {
  id: string;
  type: "document" | "note" | "task" | "project";
  title: string;
  snippet: string;
  score: number;
  metadata: Record<string, any>;
}
