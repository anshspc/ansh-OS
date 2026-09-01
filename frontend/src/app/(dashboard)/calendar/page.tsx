"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Calendar as CalendarIcon,
  Clock,
  Plus,
  Trash2,
  X,
} from "lucide-react";
import { api } from "@/lib/api";
import { CalendarEvent } from "@/lib/types";

export default function CalendarPage() {
  const queryClient = useQueryClient();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [eventType, setEventType] = useState<CalendarEvent["event_type"]>("focus");
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("10:30");
  const [color, setColor] = useState("#6366f1");

  const { data: events = [], isLoading } = useQuery({
    queryKey: ["calendar-events"],
    queryFn: () => api.getCalendarEvents(),
  });

  const createEventMutation = useMutation({
    mutationFn: (newEvent: Partial<CalendarEvent>) => api.createCalendarEvent(newEvent),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendar-events"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      setIsCreateOpen(false);
      setTitle("");
    },
  });

  const deleteEventMutation = useMutation({
    mutationFn: (id: string) => api.deleteCalendarEvent(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendar-events"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  const hours = [
    "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Calendar & Focus Schedule</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Structure your day into dedicated deep work, strategic reviews, and meetings
          </p>
        </div>

        <button
          onClick={() => setIsCreateOpen(true)}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition-all"
        >
          <Plus className="w-4 h-4" />
          Add Schedule Block
        </button>
      </div>

      {/* Daily Timeline Schedule */}
      <div className="p-6 rounded-2xl bg-[#111726]/80 border border-slate-800 shadow-sm space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <CalendarIcon className="w-4 h-4 text-indigo-400" />
          Today&apos;s Focus Blocks & Timeline
        </h2>

        <div className="divide-y divide-slate-800/80 border-t border-slate-800/80 mt-4">
          {hours.map((hour) => {
            const hourEvents = events.filter((e) => {
              const startH = new Date(e.start_time).toLocaleTimeString([], { hour: "2-digit", hour12: false });
              return startH.startsWith(hour.split(":")[0]);
            });

            return (
              <div key={hour} className="py-3 flex items-start gap-4 group">
                <span className="text-xs font-mono text-slate-500 w-14 shrink-0 pt-1">
                  {hour}
                </span>

                <div className="flex-1 min-h-[44px] flex items-center gap-3 flex-wrap">
                  {hourEvents.map((evt) => (
                    <div
                      key={evt.id}
                      className="px-3.5 py-2 rounded-xl border flex items-center justify-between gap-3 text-xs shadow-sm"
                      style={{
                        backgroundColor: `${evt.color || "#6366f1"}20`,
                        borderColor: `${evt.color || "#6366f1"}50`,
                      }}
                    >
                      <div>
                        <span className="font-bold text-white">{evt.title}</span>
                        <span className="text-[10px] text-slate-400 ml-2 font-mono uppercase">
                          ({evt.event_type})
                        </span>
                      </div>
                      <button
                        onClick={() => deleteEventMutation.mutate(evt.id)}
                        className="text-slate-400 hover:text-rose-400"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  ))}

                  {hourEvents.length === 0 && (
                    <span className="text-[11px] text-slate-700 italic opacity-0 group-hover:opacity-100 transition-opacity">
                      Open slot
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Create Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111726] border border-slate-800 rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-white">Add Calendar Event</h2>
              <button onClick={() => setIsCreateOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Event Title *</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Deep Work: Refactor Auth Engine"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Start Time</label>
                  <input
                    type="time"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">End Time</label>
                  <input
                    type="time"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Type</label>
                  <select
                    value={eventType}
                    onChange={(e) => setEventType(e.target.value as any)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white outline-none"
                  >
                    <option value="focus">Focus Block</option>
                    <option value="meeting">Meeting</option>
                    <option value="deadline">Deadline</option>
                    <option value="personal">Personal</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Color</label>
                  <input
                    type="color"
                    value={color}
                    onChange={(e) => setColor(e.target.value)}
                    className="w-full h-9 bg-slate-900 border border-slate-700 rounded-lg p-1 outline-none"
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
                    const today = new Date();
                    const [sH, sM] = startTime.split(":").map(Number);
                    const [eH, eM] = endTime.split(":").map(Number);
                    const startDt = new Date(today.getFullYear(), today.getMonth(), today.getDate(), sH, sM);
                    const endDt = new Date(today.getFullYear(), today.getMonth(), today.getDate(), eH, eM);

                    createEventMutation.mutate({
                      title,
                      start_time: startDt.toISOString(),
                      end_time: endDt.toISOString(),
                      event_type: eventType,
                      color,
                    });
                  }
                }}
                disabled={!title.trim()}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold"
              >
                Save Event
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
