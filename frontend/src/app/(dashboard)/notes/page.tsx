"use client";

import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  BookOpen,
  Pin,
  Plus,
  Save,
  Search,
  Tag,
  Trash2,
} from "lucide-react";
import { api } from "@/lib/api";
import { Note } from "@/lib/types";

export default function NotesPage() {
  const queryClient = useQueryClient();
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState("");

  const { data: notes = [], isLoading } = useQuery({
    queryKey: ["notes"],
    queryFn: () => api.getNotes(),
  });

  useEffect(() => {
    if (notes.length > 0 && !selectedNote) {
      const first = notes[0];
      setSelectedNote(first);
      setTitle(first.title);
      setContent(first.content);
      setTags(first.tags || []);
    }
  }, [notes, selectedNote]);

  const createNoteMutation = useMutation({
    mutationFn: (newNote: Partial<Note>) => api.createNote(newNote),
    onSuccess: (saved) => {
      queryClient.invalidateQueries({ queryKey: ["notes"] });
      setSelectedNote(saved);
      setTitle(saved.title);
      setContent(saved.content);
      setTags(saved.tags || []);
    },
  });

  const updateNoteMutation = useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: Partial<Note> }) =>
      api.updateNote(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notes"] });
    },
  });

  const deleteNoteMutation = useMutation({
    mutationFn: (id: string) => api.deleteNote(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notes"] });
      setSelectedNote(null);
    },
  });

  const handleSelectNote = (note: Note) => {
    setSelectedNote(note);
    setTitle(note.title);
    setContent(note.content);
    setTags(note.tags || []);
  };

  const handleSave = () => {
    if (selectedNote) {
      updateNoteMutation.mutate({
        id: selectedNote.id,
        updates: { title, content, tags },
      });
    }
  };

  const handleCreateNew = () => {
    createNoteMutation.mutate({
      title: "Untitled Note",
      content: "# New Note\n\nStart typing thoughts, architecture specs, or code snippets...",
      tags: [],
    });
  };

  const handleAddTag = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && tagInput.trim()) {
      e.preventDefault();
      if (!tags.includes(tagInput.trim())) {
        setTags([...tags, tagInput.trim()]);
      }
      setTagInput("");
    }
  };

  const filteredNotes = notes.filter(
    (n) =>
      n.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      n.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="h-[calc(100vh-140px)] flex gap-5">
      {/* Left Column: Notes List */}
      <div className="w-80 flex flex-col gap-3 bg-[#111726]/80 rounded-2xl border border-slate-800 p-3.5 shadow-sm shrink-0">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-indigo-400" />
            Knowledge Notes
          </h2>
          <button
            onClick={handleCreateNew}
            className="p-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs transition-colors"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>

        {/* Search */}
        <div className="flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 text-xs">
          <Search className="w-3.5 h-3.5 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search notes..."
            className="bg-transparent border-none outline-none text-white placeholder-slate-500 w-full text-xs"
          />
        </div>

        {/* Notes Items */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {filteredNotes.map((note) => (
            <div
              key={note.id}
              onClick={() => handleSelectNote(note)}
              className={`p-3 rounded-xl border cursor-pointer transition-all ${
                selectedNote?.id === note.id
                  ? "bg-indigo-600/20 border-indigo-500/40 text-white shadow-sm"
                  : "bg-slate-900/60 border-slate-800/80 text-slate-300 hover:bg-slate-800/60"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold truncate">{note.title}</span>
                {note.is_pinned && <Pin className="w-3 h-3 text-amber-400 shrink-0" />}
              </div>
              <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                {note.content.replace(/^#+\s+/gm, "")}
              </p>
              {note.tags && note.tags.length > 0 && (
                <div className="flex items-center gap-1 mt-2 overflow-hidden">
                  {note.tags.slice(0, 3).map((t, idx) => (
                    <span
                      key={idx}
                      className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 font-mono"
                    >
                      #{t}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Right Column: Markdown Editor */}
      {selectedNote ? (
        <div className="flex-1 bg-[#111726]/80 rounded-2xl border border-slate-800 p-6 flex flex-col justify-between shadow-sm">
          <div className="space-y-4 flex-1 flex flex-col">
            {/* Top Toolbar */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Note Title..."
                className="text-lg font-bold text-white bg-transparent border-none outline-none w-full"
              />

              <div className="flex items-center gap-2">
                <button
                  onClick={() =>
                    updateNoteMutation.mutate({
                      id: selectedNote.id,
                      updates: { is_pinned: !selectedNote.is_pinned },
                    })
                  }
                  className={`p-2 rounded-lg border transition-colors ${
                    selectedNote.is_pinned
                      ? "bg-amber-500/20 border-amber-500/40 text-amber-300"
                      : "border-slate-800 text-slate-400 hover:text-white"
                  }`}
                >
                  <Pin className="w-3.5 h-3.5" />
                </button>

                <button
                  onClick={() => deleteNoteMutation.mutate(selectedNote.id)}
                  className="p-2 rounded-lg border border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-500/30 transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>

                <button
                  onClick={handleSave}
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all"
                >
                  <Save className="w-3.5 h-3.5" />
                  Save
                </button>
              </div>
            </div>

            {/* Tags Bar */}
            <div className="flex items-center gap-2 flex-wrap text-xs">
              <Tag className="w-3.5 h-3.5 text-slate-500" />
              {tags.map((t, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-indigo-300 flex items-center gap-1"
                >
                  #{t}
                  <button
                    onClick={() => setTags(tags.filter((_, i) => i !== idx))}
                    className="hover:text-rose-400"
                  >
                    &times;
                  </button>
                </span>
              ))}
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={handleAddTag}
                placeholder="Add tag (Press Enter)..."
                className="bg-transparent border-none outline-none text-slate-400 text-xs w-44"
              />
            </div>

            {/* Markdown Textarea */}
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Write markdown here..."
              className="flex-1 w-full bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 text-slate-200 text-xs font-mono leading-relaxed outline-none focus:border-indigo-500/50 resize-none"
            />
          </div>
        </div>
      ) : (
        <div className="flex-1 bg-[#111726]/40 rounded-2xl border border-slate-800 flex items-center justify-center text-slate-500 text-xs">
          Select or create a note to begin editing
        </div>
      )}
    </div>
  );
}
