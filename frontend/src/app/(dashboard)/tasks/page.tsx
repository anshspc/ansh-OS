"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle2,
  Clock,
  Filter,
  Kanban,
  List as ListIcon,
  Plus,
  Search,
  Tag,
  Trash2,
  X,
} from "lucide-react";
import { api } from "@/lib/api";
import { Task } from "@/lib/types";

export default function TasksPage() {
  const queryClient = useQueryClient();
  const [viewMode, setViewMode] = useState<"kanban" | "list">("kanban");
  const [searchQuery, setSearchQuery] = useState("");
  const [priorityFilter, setPriorityFilter] = useState<string>("all");
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // New task form state
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<"critical" | "high" | "medium" | "low">("medium");
  const [status, setStatus] = useState<"inbox" | "todo" | "in_progress" | "completed">("todo");
  const [estimatedDuration, setEstimatedDuration] = useState(30);

  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => api.getTasks(),
  });

  const createTaskMutation = useMutation({
    mutationFn: (newTask: Partial<Task>) => api.createTask(newTask),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      setIsCreateOpen(false);
      setTitle("");
      setDescription("");
    },
  });

  const updateTaskMutation = useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: Partial<Task> }) =>
      api.updateTask(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  const deleteTaskMutation = useMutation({
    mutationFn: (id: string) => api.deleteTask(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  const filteredTasks = tasks.filter((t) => {
    const matchesSearch =
      t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (t.description && t.description.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesPriority = priorityFilter === "all" || t.priority === priorityFilter;
    return matchesSearch && matchesPriority;
  });

  const columns = [
    { id: "inbox", label: "Inbox", color: "border-slate-700" },
    { id: "todo", label: "To Do", color: "border-blue-500/30" },
    { id: "in_progress", label: "In Progress", color: "border-amber-500/30" },
    { id: "completed", label: "Completed", color: "border-emerald-500/30" },
  ];

  const handleStatusChange = (task: Task, newStatus: Task["status"]) => {
    updateTaskMutation.mutate({ id: task.id, updates: { status: newStatus } });
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Task Command Center</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Organize, prioritize, and clear your active workloads
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* View Toggle */}
          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-1">
            <button
              onClick={() => setViewMode("kanban")}
              className={`p-1.5 rounded text-xs transition-colors flex items-center gap-1.5 ${
                viewMode === "kanban"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Kanban className="w-3.5 h-3.5" />
              <span>Kanban</span>
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`p-1.5 rounded text-xs transition-colors flex items-center gap-1.5 ${
                viewMode === "list"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <ListIcon className="w-3.5 h-3.5" />
              <span>List</span>
            </button>
          </div>

          <button
            onClick={() => setIsCreateOpen(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            Add Task
          </button>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3 rounded-xl bg-[#111726]/60 border border-slate-800">
        <div className="flex items-center gap-2 w-full sm:w-72 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800">
          <Search className="w-3.5 h-3.5 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter tasks..."
            className="bg-transparent border-none outline-none text-xs text-white placeholder-slate-500 w-full"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto">
          <span className="text-xs text-slate-500 flex items-center gap-1">
            <Filter className="w-3 h-3" /> Priority:
          </span>
          {["all", "critical", "high", "medium", "low"].map((p) => (
            <button
              key={p}
              onClick={() => setPriorityFilter(p)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium uppercase transition-all ${
                priorityFilter === p
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Kanban Board View */}
      {viewMode === "kanban" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 items-start">
          {columns.map((col) => {
            const colTasks = filteredTasks.filter((t) => t.status === col.id);
            return (
              <div
                key={col.id}
                className={`p-3.5 rounded-2xl bg-[#0e1320]/90 border ${col.color} flex flex-col gap-3 min-h-[500px] shadow-sm`}
              >
                {/* Column Header */}
                <div className="flex items-center justify-between px-1">
                  <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                    {col.label}
                  </span>
                  <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
                    {colTasks.length}
                  </span>
                </div>

                {/* Task Cards */}
                <div className="space-y-2.5 flex-1">
                  {colTasks.map((task) => (
                    <div
                      key={task.id}
                      className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-indigo-500/40 transition-all shadow-sm group relative"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span
                          className={`text-[9px] px-1.5 py-0.5 rounded uppercase font-mono font-bold ${
                            task.priority === "critical"
                              ? "bg-rose-500/20 text-rose-300"
                              : task.priority === "high"
                              ? "bg-amber-500/20 text-amber-300"
                              : "bg-blue-500/20 text-blue-300"
                          }`}
                        >
                          {task.priority}
                        </span>

                        {/* Move status dropdown */}
                        <select
                          value={task.status}
                          onChange={(e) => handleStatusChange(task, e.target.value as any)}
                          className="bg-slate-950 border border-slate-800 text-[10px] text-slate-400 rounded px-1.5 py-0.5 outline-none"
                        >
                          <option value="inbox">Inbox</option>
                          <option value="todo">To Do</option>
                          <option value="in_progress">In Progress</option>
                          <option value="completed">Completed</option>
                        </select>
                      </div>

                      <h3
                        className={`text-xs font-semibold mt-2 ${
                          task.status === "completed"
                            ? "line-through text-slate-500"
                            : "text-slate-200"
                        }`}
                      >
                        {task.title}
                      </h3>

                      {task.description && (
                        <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                          {task.description}
                        </p>
                      )}

                      {/* Subtasks summary */}
                      {task.subtasks && task.subtasks.length > 0 && (
                        <div className="mt-2 text-[10px] text-slate-400 flex items-center gap-1 font-mono">
                          <CheckCircle2 className="w-3 h-3 text-indigo-400" />
                          {task.subtasks.filter((s) => s.is_completed).length} / {task.subtasks.length} subtasks
                        </div>
                      )}

                      {/* Footer info */}
                      <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-800/60 text-[10px] text-slate-500">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" /> {task.estimated_duration}m
                        </span>
                        <button
                          onClick={() => deleteTaskMutation.mutate(task.id)}
                          className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 transition-opacity p-1"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  ))}

                  {colTasks.length === 0 && (
                    <div className="h-32 border border-dashed border-slate-800/80 rounded-xl flex items-center justify-center text-slate-600 text-xs">
                      No tasks
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* List View */
        <div className="rounded-2xl bg-[#111726]/80 border border-slate-800 divide-y divide-slate-800/80 overflow-hidden shadow-sm">
          {filteredTasks.map((task) => (
            <div
              key={task.id}
              className="p-4 hover:bg-slate-900/60 transition-colors flex items-center justify-between gap-4"
            >
              <div className="flex items-center gap-3">
                <button
                  onClick={() =>
                    handleStatusChange(task, task.status === "completed" ? "todo" : "completed")
                  }
                  className={`w-5 h-5 rounded-md border flex items-center justify-center transition-colors ${
                    task.status === "completed"
                      ? "bg-emerald-500 border-emerald-500 text-white"
                      : "border-slate-700 hover:border-indigo-500"
                  }`}
                >
                  {task.status === "completed" && <CheckCircle2 className="w-3.5 h-3.5" />}
                </button>
                <div>
                  <p
                    className={`text-xs font-semibold ${
                      task.status === "completed" ? "line-through text-slate-500" : "text-slate-200"
                    }`}
                  >
                    {task.title}
                  </p>
                  <p className="text-[11px] text-slate-400 mt-0.5">{task.description}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span
                  className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold uppercase ${
                    task.priority === "critical"
                      ? "bg-rose-500/20 text-rose-300"
                      : task.priority === "high"
                      ? "bg-amber-500/20 text-amber-300"
                      : "bg-blue-500/20 text-blue-300"
                  }`}
                >
                  {task.priority}
                </span>
                <span className="text-[11px] text-slate-400 uppercase font-mono">{task.status}</span>
                <button
                  onClick={() => deleteTaskMutation.mutate(task.id)}
                  className="p-1.5 text-slate-500 hover:text-rose-400 rounded transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Task Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111726] border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-white">Create New Task</h2>
              <button onClick={() => setIsCreateOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Task Title *</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Implement Vector RAG Chunking"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  placeholder="Details, sub-items, or context..."
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Priority</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as any)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white outline-none"
                  >
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Status</label>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value as any)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white outline-none"
                  >
                    <option value="inbox">Inbox</option>
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Est. Minutes</label>
                  <input
                    type="number"
                    value={estimatedDuration}
                    onChange={(e) => setEstimatedDuration(Number(e.target.value))}
                    min={5}
                    step={5}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white outline-none"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => setIsCreateOpen(false)}
                className="px-4 py-2 rounded-xl text-slate-400 hover:text-white text-xs"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (title.trim()) {
                    createTaskMutation.mutate({
                      title,
                      description,
                      priority,
                      status,
                      estimated_duration: estimatedDuration,
                    });
                  }
                }}
                disabled={!title.trim()}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold shadow-md shadow-indigo-600/20"
              >
                Create Task
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
