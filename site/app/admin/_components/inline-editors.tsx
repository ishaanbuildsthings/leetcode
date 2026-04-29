"use client";

import { useState, useEffect } from "react";
import { trpc } from "../../providers";
import { programming_language, tag_role } from "@/src/generated/prisma/enums";

export function InlineEditText({
  label,
  value,
  valueClassName = "text-gray-600",
  onSave,
}: {
  label: string;
  value: string;
  valueClassName?: string;
  onSave: (value: string) => Promise<unknown>;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value);
  const [saving, setSaving] = useState(false);

  const startEdit = () => {
    setDraft(value);
    setEditing(true);
  };

  const save = async () => {
    if (draft === value) {
      setEditing(false);
      return;
    }
    setSaving(true);
    try {
      await onSave(draft);
      setEditing(false);
    } catch (e: any) {
      alert(`Failed to save: ${e?.message ?? e}`);
    } finally {
      setSaving(false);
    }
  };

  if (editing) {
    return (
      <div className="mt-2">
        <div className="text-xs font-semibold text-gray-700 mb-1">{label}:</div>
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          autoFocus
          rows={Math.max(2, Math.min(8, draft.split("\n").length + 1))}
          className="w-full text-sm text-gray-800 border border-blue-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-400"
          onKeyDown={(e) => {
            if (e.key === "Escape") {
              setEditing(false);
            } else if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
              e.preventDefault();
              save();
            }
          }}
        />
        <div className="flex gap-2 mt-1">
          <button
            onClick={save}
            disabled={saving}
            className="px-2 py-0.5 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save"}
          </button>
          <button
            onClick={() => setEditing(false)}
            disabled={saving}
            className="px-2 py-0.5 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          >
            Cancel
          </button>
          <span className="text-xs text-gray-400 self-center">⌘+Enter to save · Esc to cancel</span>
        </div>
      </div>
    );
  }

  if (!value) {
    return (
      <div className="mt-2">
        <button
          onClick={startEdit}
          className="text-xs text-gray-400 hover:text-blue-600 inline-flex items-center gap-1"
        >
          ✎ Add {label.toLowerCase()}
        </button>
      </div>
    );
  }

  return (
    <div className="mt-2">
      <span className="text-xs font-semibold text-gray-700">{label}: </span>
      <span className={`text-sm ${valueClassName}`}>{value}</span>
      <button
        onClick={startEdit}
        className="ml-1 text-xs text-gray-400 hover:text-blue-600"
        title={`Edit ${label.toLowerCase()}`}
      >
        ✎
      </button>
    </div>
  );
}

export type ProblemTagRow = {
  tag: { id: string; name: string };
  role: tag_role | null;
  tagDifficulty: number | null;
  isInstructive: boolean | null;
};

export type TagMutationInput = { tagId: string; role?: tag_role; tagDifficulty?: number; isInstructive?: boolean };

export function tagsToMutation(tags: ProblemTagRow[]): TagMutationInput[] {
  return tags.map((pt) => ({
    tagId: pt.tag.id,
    role: pt.role ?? undefined,
    tagDifficulty: pt.tagDifficulty ?? undefined,
    isInstructive: pt.isInstructive ?? undefined,
  }));
}

export function InlineTagEditor({
  pt,
  allTags,
  onChange,
  onRemove,
}: {
  pt: ProblemTagRow;
  allTags: ProblemTagRow[];
  onChange: (updated: TagMutationInput[]) => Promise<unknown>;
  onRemove: (updated: TagMutationInput[]) => Promise<unknown>;
}) {
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const classes = pt.isInstructive === true
    ? "bg-purple-100 text-purple-800 border border-purple-300"
    : pt.role === "core"
    ? "bg-blue-100 text-blue-800"
    : pt.role === "secondary"
    ? "bg-green-100 text-green-800"
    : pt.role === "mention"
    ? "bg-yellow-100 text-yellow-800"
    : "bg-gray-100 text-gray-800";

  const applyPatch = async (patch: Partial<TagMutationInput>) => {
    setSaving(true);
    try {
      const updated = tagsToMutation(allTags).map((t) =>
        t.tagId === pt.tag.id ? { ...t, ...patch } : t
      );
      await onChange(updated);
    } catch (e: any) {
      alert(`Failed to save: ${e?.message ?? e}`);
    } finally {
      setSaving(false);
    }
  };

  const removeTag = async () => {
    setSaving(true);
    setOpen(false);
    try {
      const updated = tagsToMutation(allTags).filter((t) => t.tagId !== pt.tag.id);
      await onRemove(updated);
    } catch (e: any) {
      alert(`Failed to remove: ${e?.message ?? e}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <span className="relative inline-block">
      <button
        onClick={() => setOpen((o) => !o)}
        disabled={saving}
        className={`px-2 py-0.5 text-xs rounded hover:ring-1 hover:ring-blue-400 disabled:opacity-50 ${classes}`}
      >
        {pt.isInstructive === true && "📚 "}
        {pt.tag.name}
        {pt.role && ` (${pt.role})`}
        {pt.tagDifficulty && ` ${pt.tagDifficulty}/10`}
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute left-0 top-6 z-20 bg-white border border-gray-200 rounded shadow-lg p-2 w-64">
            <div className="text-xs font-semibold text-gray-700 mb-1">{pt.tag.name}</div>

            <div className="text-[10px] uppercase text-gray-500 mt-1">Role</div>
            <div className="flex gap-1 mb-2">
              {(["core", "secondary", "mention"] as const).map((r) => (
                <button
                  key={r}
                  onClick={() => applyPatch({ role: r })}
                  disabled={saving}
                  className={`flex-1 px-1 py-0.5 text-xs rounded border ${
                    pt.role === r ? "bg-blue-600 text-white border-blue-600" : "border-gray-300 hover:bg-gray-100"
                  }`}
                >
                  {r}
                </button>
              ))}
              <button
                onClick={() => applyPatch({ role: undefined })}
                disabled={saving}
                className={`px-1 py-0.5 text-xs rounded border ${
                  !pt.role ? "bg-blue-600 text-white border-blue-600" : "border-gray-300 hover:bg-gray-100"
                }`}
                title="Clear role"
              >
                ✕
              </button>
            </div>

            <div className="text-[10px] uppercase text-gray-500">Difficulty</div>
            <div className="flex gap-0.5 mb-2 flex-wrap">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
                <button
                  key={n}
                  onClick={() => applyPatch({ tagDifficulty: n })}
                  disabled={saving}
                  className={`w-6 h-6 text-xs rounded ${
                    pt.tagDifficulty === n ? "bg-blue-600 text-white" : "bg-gray-100 hover:bg-blue-100"
                  }`}
                >
                  {n}
                </button>
              ))}
              <button
                onClick={() => applyPatch({ tagDifficulty: undefined })}
                disabled={saving}
                className="w-6 h-6 text-xs rounded bg-gray-100 hover:bg-gray-200"
                title="Clear difficulty"
              >
                ✕
              </button>
            </div>

            <label className="flex items-center gap-1 text-xs mb-2 cursor-pointer">
              <input
                type="checkbox"
                checked={pt.isInstructive === true}
                onChange={(e) => applyPatch({ isInstructive: e.target.checked })}
                disabled={saving}
              />
              📚 Instructive
            </label>

            <div className="flex justify-between pt-1 border-t border-gray-100">
              <button
                onClick={removeTag}
                disabled={saving}
                className="text-xs text-red-600 hover:bg-red-50 px-2 py-0.5 rounded"
              >
                Remove
              </button>
              <button
                onClick={() => setOpen(false)}
                className="text-xs text-gray-600 hover:bg-gray-100 px-2 py-0.5 rounded"
              >
                Close
              </button>
            </div>
          </div>
        </>
      )}
    </span>
  );
}

export function InlineDifficulty({
  value,
  onSave,
}: {
  value: number | null;
  onSave: (v: number) => Promise<unknown>;
}) {
  const [saving, setSaving] = useState(false);
  const [open, setOpen] = useState(false);

  const handleChange = async (v: number) => {
    setSaving(true);
    setOpen(false);
    try {
      await onSave(v);
    } catch (e: any) {
      alert(`Failed to save: ${e?.message ?? e}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <span className="relative inline-flex items-center">
      <button
        onClick={() => setOpen((o) => !o)}
        disabled={saving}
        className="text-xs px-1.5 py-0.5 rounded border border-gray-200 hover:border-blue-400 hover:bg-blue-50 disabled:opacity-50"
        title="Adjust difficulty"
      >
        {saving ? "…" : value != null ? `Normalized: ${value}/10` : "Set difficulty"} ✎
      </button>
      {open && (
        <div className="absolute left-0 top-6 z-10 bg-white border border-gray-200 rounded shadow-lg p-1 flex gap-0.5">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
            <button
              key={n}
              onClick={() => handleChange(n)}
              className={`w-6 h-6 text-xs rounded hover:bg-blue-100 ${
                n === value ? "bg-blue-600 text-white" : "text-gray-700"
              }`}
            >
              {n}
            </button>
          ))}
        </div>
      )}
    </span>
  );
}

export function InlineDrillEditor({
  drillType,
  drillNotes,
  onSave,
}: {
  drillType: "mindsolve" | "implement" | null;
  drillNotes: string | null;
  onSave: (input: { drillType: "mindsolve" | "implement" | null; drillNotes: string }) => Promise<unknown>;
}) {
  const [editing, setEditing] = useState(false);
  const [typeDraft, setTypeDraft] = useState<"mindsolve" | "implement" | "">(drillType ?? "");
  const [notesDraft, setNotesDraft] = useState(drillNotes ?? "");
  const [saving, setSaving] = useState(false);

  const startEdit = () => {
    setTypeDraft(drillType ?? "");
    setNotesDraft(drillNotes ?? "");
    setEditing(true);
  };

  const save = async () => {
    setSaving(true);
    try {
      await onSave({ drillType: typeDraft === "" ? null : typeDraft, drillNotes: notesDraft });
      setEditing(false);
    } catch (e: any) {
      alert(`Failed to save: ${e?.message ?? e}`);
    } finally {
      setSaving(false);
    }
  };

  if (editing) {
    return (
      <div className="mt-2 p-2 border border-blue-200 rounded bg-blue-50/30">
        <div className="text-xs font-semibold text-gray-700 mb-1">Drill:</div>
        <div className="flex gap-3 mb-2">
          <label className="flex items-center gap-1 text-xs cursor-pointer">
            <input type="radio" checked={typeDraft === ""} onChange={() => setTypeDraft("")} />
            None
          </label>
          <label className="flex items-center gap-1 text-xs cursor-pointer">
            <input type="radio" checked={typeDraft === "mindsolve"} onChange={() => setTypeDraft("mindsolve")} />
            🧠 Mindsolve
          </label>
          <label className="flex items-center gap-1 text-xs cursor-pointer">
            <input type="radio" checked={typeDraft === "implement"} onChange={() => setTypeDraft("implement")} />
            💻 Implement
          </label>
        </div>
        <textarea
          value={notesDraft}
          onChange={(e) => setNotesDraft(e.target.value)}
          placeholder="Drill notes..."
          rows={Math.max(2, Math.min(8, notesDraft.split("\n").length + 1))}
          className="w-full text-sm text-gray-800 border border-blue-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-400"
          onKeyDown={(e) => {
            if (e.key === "Escape") setEditing(false);
            else if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
              e.preventDefault();
              save();
            }
          }}
        />
        <div className="flex gap-2 mt-1">
          <button
            onClick={save}
            disabled={saving}
            className="px-2 py-0.5 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save"}
          </button>
          <button
            onClick={() => setEditing(false)}
            disabled={saving}
            className="px-2 py-0.5 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          >
            Cancel
          </button>
          <span className="text-xs text-gray-400 self-center">⌘+Enter to save · Esc to cancel</span>
        </div>
      </div>
    );
  }

  if (!drillType) {
    return (
      <div className="mt-2">
        <button
          onClick={startEdit}
          className="text-xs text-gray-400 hover:text-blue-600 inline-flex items-center gap-1"
        >
          ✎ Add drill
        </button>
      </div>
    );
  }

  return (
    <div className="mt-2 flex items-start gap-2">
      <span className="px-2 py-1 rounded text-xs font-semibold bg-gradient-to-r from-blue-50 to-purple-50 text-purple-900 border border-purple-200">
        {drillType === "mindsolve" ? "🧠 Mindsolve" : "💻 Implement"}
      </span>
      <div className="flex-1">
        <span className="text-xs font-semibold text-gray-700">Drill Notes: </span>
        <span className="text-sm text-gray-600">
          {drillNotes || <span className="italic text-gray-400">none</span>}
        </span>
        <button
          onClick={startEdit}
          className="ml-1 text-xs text-gray-400 hover:text-blue-600"
          title="Edit drill"
        >
          ✎
        </button>
      </div>
    </div>
  );
}

export function EditProblemForm({ problemId, onClose }: { problemId: string; onClose: () => void }) {
  const utils = trpc.useUtils();
  const { data: platforms } = trpc.platform.list.useQuery();
  const { data: tags } = trpc.tag.list.useQuery();
  const { data: problem, isLoading } = trpc.problem.getById.useQuery({ id: problemId });

  const updateProblem = trpc.problem.update.useMutation({
    onSuccess: () => {
      utils.problem.list.invalidate();
      onClose();
    },
    onError: (error) => {
      console.error("Update failed:", error);
      alert(`Failed to update problem: ${error.message}`);
    },
  });

  const [formData, setFormData] = useState({
    platformId: "",
    title: "",
    url: "",
    isGreatProblem: false,
    isLeetgoat222: false,
    isLeetgoatAdvanced: false,
    platformProblemId: "",
    platformDifficulty: "",
    normalizedDifficulty: undefined as number | undefined,
    simplifiedStatement: "",
    notes: "",
    drillType: null as "mindsolve" | "implement" | null,
    drillNotes: "",
    selectedTags: [] as Array<{ tagId: string; role?: tag_role; tagDifficulty?: number; isInstructive?: boolean }>,
    solutions: [] as Array<{ submissionUrl?: string; language: programming_language | ""; githubUrl?: string }>,
  });

  useEffect(() => {
    if (problem) {
      setFormData({
        platformId: problem.platformId,
        title: problem.title,
        url: problem.url,
        isGreatProblem: problem.isGreatProblem,
        isLeetgoat222: problem.isLeetgoat222,
        isLeetgoatAdvanced: problem.isLeetgoatAdvanced,
        platformProblemId: problem.platformProblemId || "",
        platformDifficulty: problem.platformDifficulty || "",
        normalizedDifficulty: problem.normalizedDifficulty || undefined,
        simplifiedStatement: problem.simplifiedStatement || "",
        notes: problem.notes || "",
        drillType: problem.drillType || null,
        drillNotes: problem.drillNotes || "",
        selectedTags: problem.tags.map(pt => ({
          tagId: pt.tag.id,
          role: pt.role || undefined,
          tagDifficulty: pt.tagDifficulty || undefined,
          isInstructive: pt.isInstructive ?? undefined,
        })),
        solutions: problem.solutions.map(s => ({
          submissionUrl: s.submissionUrl || "",
          language: s.language,
          githubUrl: s.githubUrl || "",
        })),
      });
    }
  }, [problem]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProblem.mutate({
      id: problemId,
      platformId: formData.platformId,
      title: formData.title,
      url: formData.url,
      isGreatProblem: formData.isGreatProblem,
      isLeetgoat222: formData.isLeetgoat222,
      isLeetgoatAdvanced: formData.isLeetgoatAdvanced,
      platformProblemId: formData.platformProblemId || undefined,
      platformDifficulty: formData.platformDifficulty || undefined,
      normalizedDifficulty: formData.normalizedDifficulty,
      simplifiedStatement: formData.simplifiedStatement || undefined,
      notes: formData.notes || undefined,
      drillType: formData.drillType || null,
      drillNotes: formData.drillNotes || undefined,
      tags: formData.selectedTags.length > 0 ? formData.selectedTags : undefined,
      solutions: formData.solutions.length > 0
        ? formData.solutions
            .filter(s => s.language !== "")
            .map(s => ({
              submissionUrl: s.submissionUrl || undefined,
              language: s.language as programming_language,
              githubUrl: s.githubUrl || undefined,
            }))
        : undefined,
    });
  };

  if (isLoading) {
    return <div className="bg-white p-6 rounded-lg shadow">Loading...</div>;
  }

  if (!problem) {
    return <div className="bg-white p-6 rounded-lg shadow text-red-600">Problem not found</div>;
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow space-y-3">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-gray-900">Edit Problem</h3>
        <button
          type="button"
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700"
        >
          ✕ Cancel
        </button>
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Title *</label>
        <input
          type="text"
          required
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">URL *</label>
        <input
          type="url"
          required
          value={formData.url}
          onChange={(e) => setFormData({ ...formData, url: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Platform *</label>
        <select
          required
          value={formData.platformId}
          onChange={(e) => setFormData({ ...formData, platformId: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        >
          <option value="">Select platform</option>
          {platforms?.map((platform) => (
            <option key={platform.id} value={platform.id}>
              {platform.name}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Platform Problem ID</label>
          <input
            type="text"
            value={formData.platformProblemId}
            onChange={(e) => setFormData({ ...formData, platformProblemId: e.target.value })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Platform Difficulty</label>
          <input
            type="text"
            value={formData.platformDifficulty}
            onChange={(e) => setFormData({ ...formData, platformDifficulty: e.target.value })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Normalized Difficulty (1-10)</label>
        <input
          type="number"
          min="1"
          max="10"
          value={formData.normalizedDifficulty || ""}
          onChange={(e) => setFormData({ ...formData, normalizedDifficulty: e.target.value ? parseInt(e.target.value) : undefined })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Simplified Problem Statement</label>
        <textarea
          value={formData.simplifiedStatement}
          onChange={(e) => setFormData({ ...formData, simplifiedStatement: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          rows={2}
          placeholder="A brief summary of the problem"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Notes</label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          rows={2}
        />
      </div>

      <div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={formData.isGreatProblem}
            onChange={(e) => setFormData({ ...formData, isGreatProblem: e.target.checked })}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="text-sm font-semibold text-gray-900">Great Problem</span>
        </label>
      </div>

      <div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={formData.isLeetgoat222}
            onChange={(e) => setFormData({ ...formData, isLeetgoat222: e.target.checked })}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="text-sm font-semibold text-gray-900">LeetGoat 222</span>
        </label>
      </div>

      <div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={formData.isLeetgoatAdvanced}
            onChange={(e) => setFormData({ ...formData, isLeetgoatAdvanced: e.target.checked })}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="text-sm font-semibold text-gray-900">LeetGoat Advanced</span>
        </label>
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Drill Type</label>
        <select
          value={formData.drillType || ""}
          onChange={(e) => setFormData({ ...formData, drillType: e.target.value === "" ? null : e.target.value as "mindsolve" | "implement" })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
        >
          <option value="">None</option>
          <option value="mindsolve">🧠 Mindsolve</option>
          <option value="implement">💻 Implement</option>
        </select>
      </div>

      {formData.drillType && (
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Drill Notes</label>
          <textarea
            value={formData.drillNotes}
            onChange={(e) => setFormData({ ...formData, drillNotes: e.target.value })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            rows={2}
            placeholder="Notes about drilling this problem..."
          />
        </div>
      )}

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Tags</label>
        <div className="space-y-2">
          {tags?.map((tag) => {
            const selected = formData.selectedTags.find((t) => t.tagId === tag.id);
            return (
              <div key={tag.id} className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={!!selected}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setFormData({
                        ...formData,
                        selectedTags: [...formData.selectedTags, { tagId: tag.id }],
                      });
                    } else {
                      setFormData({
                        ...formData,
                        selectedTags: formData.selectedTags.filter((t) => t.tagId !== tag.id),
                      });
                    }
                  }}
                  className="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <div className="flex-1">
                  <label className="text-sm font-medium text-gray-900">{tag.name}</label>
                  {selected && (
                    <div className="ml-7 flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <label className="text-xs font-medium text-gray-700">Difficulty (1-10):</label>
                        <input
                          type="number"
                          min="1"
                          max="10"
                          value={selected.tagDifficulty || ""}
                          onChange={(e) => {
                            const val = e.target.value ? parseInt(e.target.value) : undefined;
                            setFormData({
                              ...formData,
                              selectedTags: formData.selectedTags.map((t) =>
                                t.tagId === tag.id ? { ...t, tagDifficulty: val } : t
                              ),
                            });
                          }}
                          placeholder="1-10"
                          className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                        />
                      </div>
                      <div className="flex items-center gap-2">
                        <label className="text-xs font-medium text-gray-700">Role:</label>
                        <select
                          value={selected.role || ""}
                          onChange={(e) => {
                            setFormData({
                              ...formData,
                              selectedTags: formData.selectedTags.map((t) =>
                                t.tagId === tag.id ? { ...t, role: e.target.value === "" ? undefined : e.target.value as "core" | "secondary" | "mention" } : t
                              ),
                            });
                          }}
                          className="px-2 py-1 border border-gray-300 rounded text-sm"
                        >
                          <option value="">None</option>
                          <option value="core">Core</option>
                          <option value="secondary">Secondary</option>
                          <option value="mention">Mention</option>
                        </select>
                      </div>
                      <div className="flex items-center gap-2">
                        <label className="text-xs font-medium text-gray-700">Instructive:</label>
                        <select
                          value={selected.isInstructive === true ? "yes" : selected.isInstructive === false ? "no" : ""}
                          onChange={(e) => {
                            const val = e.target.value === "yes" ? true : e.target.value === "no" ? false : undefined;
                            setFormData({
                              ...formData,
                              selectedTags: formData.selectedTags.map((t) =>
                                t.tagId === tag.id ? { ...t, isInstructive: val } : t
                              ),
                            });
                          }}
                          className="px-2 py-1 border border-gray-300 rounded text-sm"
                        >
                          <option value="">Not set</option>
                          <option value="yes">Yes</option>
                          <option value="no">No</option>
                        </select>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="block text-sm font-semibold text-gray-900">Solutions</label>
          <button
            type="button"
            onClick={() => {
              setFormData({
                ...formData,
                solutions: [...formData.solutions, { submissionUrl: "", language: "", githubUrl: "" }],
              });
            }}
            className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
          >
            + Add Solution
          </button>
        </div>
        {formData.solutions.length > 0 && (
          <div className="space-y-3">
            {formData.solutions.map((sol, index) => (
              <div key={index} className="p-3 border border-gray-300 rounded space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Solution {index + 1}</span>
                  <button
                    type="button"
                    onClick={() => {
                      setFormData({
                        ...formData,
                        solutions: formData.solutions.filter((_, i) => i !== index),
                      });
                    }}
                    className="text-xs text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Language *</label>
                    <select
                      required
                      value={sol.language || ""}
                      onChange={(e) => {
                        const newSolutions = [...formData.solutions];
                        newSolutions[index] = { ...newSolutions[index], language: e.target.value as programming_language | "" };
                        setFormData({ ...formData, solutions: newSolutions });
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    >
                      <option value="">Select language</option>
                      <option value="Python">Python</option>
                      <option value="Cpp">C++</option>
                      <option value="JavaScript">JavaScript</option>
                      <option value="PostgreSQL">PostgreSQL</option>
                      <option value="Shell">Shell</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">GitHub URL</label>
                    <input
                      type="url"
                      value={sol.githubUrl || ""}
                      onChange={(e) => {
                        const newSolutions = [...formData.solutions];
                        newSolutions[index] = { ...newSolutions[index], githubUrl: e.target.value };
                        setFormData({ ...formData, solutions: newSolutions });
                      }}
                      placeholder="https://github.com/..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Submission URL</label>
                  <input
                    type="url"
                    value={sol.submissionUrl || ""}
                    onChange={(e) => {
                      const newSolutions = [...formData.solutions];
                      newSolutions[index] = { ...newSolutions[index], submissionUrl: e.target.value };
                      setFormData({ ...formData, solutions: newSolutions });
                    }}
                    placeholder="https://atcoder.jp/contests/.../submissions/..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={updateProblem.isPending}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 font-medium"
        >
          {updateProblem.isPending ? "Updating..." : "Update Problem"}
        </button>
        <button
          type="button"
          onClick={onClose}
          className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 font-medium"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
