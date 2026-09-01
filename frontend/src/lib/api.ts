import {
  AIMemory,
  AIChatResponse,
  AIMessage,
  CalendarEvent,
  DailyPlan,
  DashboardSummary,
  Document,
  Goal,
  Habit,
  Note,
  ProductivityScore,
  Project,
  SearchResultItem,
  Task,
  User,
  WeeklyReview,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("personalix_token");
  }

  setToken(token: string) {
    if (typeof window !== "undefined") {
      localStorage.setItem("personalix_token", token);
    }
  }

  clearToken() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("personalix_token");
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const url = `${API_BASE}/api/v1${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 204) {
      return {} as T;
    }

    if (!response.ok) {
      let errDetail = "An unexpected error occurred";
      try {
        const errJson = await response.json();
        errDetail = errJson.detail || errJson.error?.message || errDetail;
      } catch {}
      throw new Error(errDetail);
    }

    return response.json();
  }

  // Auth
  async login(email: string, password: string) {
    const data = await this.request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async demoLogin() {
    const data = await this.request<{ access_token: string }>("/auth/demo-login", {
      method: "POST",
    });
    this.setToken(data.access_token);
    return data;
  }

  async register(email: string, password: string, full_name: string) {
    const data = await this.request<{ access_token: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async getMe(): Promise<User> {
    return this.request<User>("/auth/me");
  }

  async updateMe(payload: Partial<User>): Promise<User> {
    return this.request<User>("/auth/me", {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  // Dashboard & Analytics
  async getDashboardSummary(): Promise<DashboardSummary> {
    return this.request<DashboardSummary>("/analytics/dashboard-summary");
  }

  async getProductivityScore(): Promise<ProductivityScore> {
    return this.request<ProductivityScore>("/analytics/productivity-score");
  }

  async getRecentActivities(): Promise<any[]> {
    return this.request<any[]>("/analytics/activities");
  }

  // Tasks
  async getTasks(params?: { status?: string; priority?: string; project_id?: string; tag?: string; search?: string }): Promise<Task[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<Task[]>(`/tasks${query ? `?${query}` : ""}`);
  }

  async createTask(task: Partial<Task>): Promise<Task> {
    return this.request<Task>("/tasks", {
      method: "POST",
      body: JSON.stringify(task),
    });
  }

  async updateTask(id: string, task: Partial<Task>): Promise<Task> {
    return this.request<Task>(`/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(task),
    });
  }

  async deleteTask(id: string): Promise<void> {
    return this.request<void>(`/tasks/${id}`, { method: "DELETE" });
  }

  async addSubtask(taskId: string, subtask: { title: string; position?: number }): Promise<any> {
    return this.request(`/tasks/${taskId}/subtasks`, {
      method: "POST",
      body: JSON.stringify(subtask),
    });
  }

  async updateSubtask(taskId: string, subtaskId: string, payload: { is_completed?: boolean; title?: string }): Promise<any> {
    return this.request(`/tasks/${taskId}/subtasks/${subtaskId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  // Projects
  async getProjects(status?: string): Promise<Project[]> {
    return this.request<Project[]>(`/projects${status ? `?status=${status}` : ""}`);
  }

  async createProject(project: Partial<Project>): Promise<Project> {
    return this.request<Project>("/projects", {
      method: "POST",
      body: JSON.stringify(project),
    });
  }

  async updateProject(id: string, project: Partial<Project>): Promise<Project> {
    return this.request<Project>(`/projects/${id}`, {
      method: "PUT",
      body: JSON.stringify(project),
    });
  }

  async deleteProject(id: string): Promise<void> {
    return this.request<void>(`/projects/${id}`, { method: "DELETE" });
  }

  // Goals
  async getGoals(category?: string): Promise<Goal[]> {
    return this.request<Goal[]>(`/goals${category ? `?category=${category}` : ""}`);
  }

  async createGoal(goal: Partial<Goal>): Promise<Goal> {
    return this.request<Goal>("/goals", {
      method: "POST",
      body: JSON.stringify(goal),
    });
  }

  async updateGoal(id: string, goal: Partial<Goal>): Promise<Goal> {
    return this.request<Goal>(`/goals/${id}`, {
      method: "PUT",
      body: JSON.stringify(goal),
    });
  }

  async deleteGoal(id: string): Promise<void> {
    return this.request<void>(`/goals/${id}`, { method: "DELETE" });
  }

  // Habits
  async getHabits(): Promise<Habit[]> {
    return this.request<Habit[]>("/habits");
  }

  async createHabit(habit: Partial<Habit>): Promise<Habit> {
    return this.request<Habit>("/habits", {
      method: "POST",
      body: JSON.stringify(habit),
    });
  }

  async updateHabit(id: string, habit: Partial<Habit>): Promise<Habit> {
    return this.request<Habit>(`/habits/${id}`, {
      method: "PUT",
      body: JSON.stringify(habit),
    });
  }

  async logHabit(id: string, logged_date: string, completed: boolean = true): Promise<Habit> {
    return this.request<Habit>(`/habits/${id}/log`, {
      method: "POST",
      body: JSON.stringify({ logged_date, completed }),
    });
  }

  async getHabitHeatmap(days: number = 365): Promise<Record<string, number>> {
    return this.request<Record<string, number>>(`/habits/heatmap?days=${days}`);
  }

  async deleteHabit(id: string): Promise<void> {
    return this.request<void>(`/habits/${id}`, { method: "DELETE" });
  }

  // Notes
  async getNotes(params?: { project_id?: string; tag?: string; search?: string }): Promise<Note[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<Note[]>(`/notes${query ? `?${query}` : ""}`);
  }

  async createNote(note: Partial<Note>): Promise<Note> {
    return this.request<Note>("/notes", {
      method: "POST",
      body: JSON.stringify(note),
    });
  }

  async updateNote(id: string, note: Partial<Note>): Promise<Note> {
    return this.request<Note>(`/notes/${id}`, {
      method: "PUT",
      body: JSON.stringify(note),
    });
  }

  async deleteNote(id: string): Promise<void> {
    return this.request<void>(`/notes/${id}`, { method: "DELETE" });
  }

  // Documents & RAG
  async getDocuments(): Promise<Document[]> {
    return this.request<Document[]>("/documents");
  }

  async createDocument(doc: { title: string; file_type?: string; content: string }): Promise<Document> {
    return this.request<Document>("/documents", {
      method: "POST",
      body: JSON.stringify(doc),
    });
  }

  async searchKnowledge(query: string, limit: number = 5): Promise<{ results: SearchResultItem[]; total: number }> {
    return this.request("/documents/search", {
      method: "POST",
      body: JSON.stringify({ query, limit }),
    });
  }

  async deleteDocument(id: string): Promise<void> {
    return this.request<void>(`/documents/${id}`, { method: "DELETE" });
  }

  // Calendar
  async getCalendarEvents(start_date?: string, end_date?: string): Promise<CalendarEvent[]> {
    const params = new URLSearchParams();
    if (start_date) params.append("start_date", start_date);
    if (end_date) params.append("end_date", end_date);
    const q = params.toString();
    return this.request<CalendarEvent[]>(`/calendar/events${q ? `?${q}` : ""}`);
  }

  async createCalendarEvent(event: Partial<CalendarEvent>): Promise<CalendarEvent> {
    return this.request<CalendarEvent>("/calendar/events", {
      method: "POST",
      body: JSON.stringify(event),
    });
  }

  async deleteCalendarEvent(id: string): Promise<void> {
    return this.request<void>(`/calendar/events/${id}`, { method: "DELETE" });
  }

  // Daily Plans
  async getDailyPlan(dateStr: string): Promise<DailyPlan> {
    return this.request<DailyPlan>(`/daily-plans/${dateStr}`);
  }

  async generateDailyPlan(dateStr?: string): Promise<DailyPlan> {
    return this.request<DailyPlan>("/daily-plans/generate", {
      method: "POST",
      body: JSON.stringify({ date: dateStr }),
    });
  }

  async updateDailyPlan(id: string, payload: Partial<DailyPlan>): Promise<DailyPlan> {
    return this.request<DailyPlan>(`/daily-plans/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  // Weekly Reviews
  async getWeeklyReviews(): Promise<WeeklyReview[]> {
    return this.request<WeeklyReview[]>("/weekly-reviews");
  }

  async generateWeeklyReview(): Promise<WeeklyReview> {
    return this.request<WeeklyReview>("/weekly-reviews/generate", {
      method: "POST",
      body: JSON.stringify({}),
    });
  }

  // AI & Chat
  async sendChatMessage(message: string, conversation_id?: string, provider?: string): Promise<AIChatResponse> {
    return this.request<AIChatResponse>("/ai/chat", {
      method: "POST",
      body: JSON.stringify({ message, conversation_id, provider }),
    });
  }

  async getConversations(): Promise<any[]> {
    return this.request<any[]>("/ai/conversations");
  }

  async getConversationMessages(id: string): Promise<AIMessage[]> {
    return this.request<AIMessage[]>(`/ai/conversations/${id}/messages`);
  }

  async getMemories(): Promise<AIMemory[]> {
    return this.request<AIMemory[]>("/ai/memories");
  }

  async createMemory(memory: Partial<AIMemory>): Promise<AIMemory> {
    return this.request<AIMemory>("/ai/memories", {
      method: "POST",
      body: JSON.stringify(memory),
    });
  }

  async deleteMemory(id: string): Promise<void> {
    return this.request<void>(`/ai/memories/${id}`, { method: "DELETE" });
  }

  // ── Voice ────────────────────────────────────────────────────────────────

  async getVoiceSettings(): Promise<any> {
    return this.request<any>("/voice/settings");
  }

  async updateVoiceSettings(settings: any): Promise<any> {
    return this.request<any>("/voice/settings", {
      method: "PUT",
      body: JSON.stringify(settings),
    });
  }

  async getVoiceHistory(limit = 50): Promise<any[]> {
    return this.request<any[]>(`/voice/history?limit=${limit}`);
  }

  async getVoiceCapabilities(): Promise<any> {
    return this.request<any>("/voice/capabilities");
  }
}

export const api = new ApiClient();
