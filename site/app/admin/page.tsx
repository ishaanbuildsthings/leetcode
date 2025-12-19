"use client";

import { useState, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { trpc } from "../providers";
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
  Position,
} from "reactflow";
import "reactflow/dist/style.css";
import dagre from "dagre";

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<"problems" | "tags" | "platforms" | "hierarchies">("problems");
  const router = useRouter();

  const handleLogout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
    router.refresh();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <Link 
              href="/" 
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              ← Back to Home
            </Link>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
          >
            Log Out
          </button>
        </div>

        <div className="border-b border-gray-200 mb-6">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab("problems")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "problems"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              Problems
            </button>
            <button
              onClick={() => setActiveTab("tags")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "tags"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              Tags
            </button>
            <button
              onClick={() => setActiveTab("platforms")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "platforms"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              Platforms
            </button>
            <button
              onClick={() => setActiveTab("hierarchies")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "hierarchies"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              Tag Hierarchies
            </button>
          </nav>
        </div>

        {activeTab === "problems" && <ProblemsTab />}
        {activeTab === "tags" && <TagsTab />}
        {activeTab === "platforms" && <PlatformsTab />}
        {activeTab === "hierarchies" && <TagHierarchiesTab />}
      </div>
    </div>
  );
}

function ProblemsTab() {
  const [showCreateForm, setShowCreateForm] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-900">Problems</h2>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          {showCreateForm ? "Cancel" : "Create Problem"}
        </button>
      </div>

      {showCreateForm && <CreateProblemForm onSuccess={() => setShowCreateForm(false)} />}

      <ProblemsList />
    </div>
  );
}

function CreateProblemForm({ onSuccess }: { onSuccess: () => void }) {
  const utils = trpc.useUtils();
  const { data: platforms } = trpc.platform.list.useQuery();
  const { data: tags } = trpc.tag.list.useQuery();

  const createProblem = trpc.problem.create.useMutation({
    onSuccess: () => {
      utils.problem.list.invalidate();
      onSuccess();
    },
  });

  const [formData, setFormData] = useState({
    platformId: "",
    title: "",
    url: "",
    isGreatProblem: false,
    platformProblemId: "",
    platformDifficulty: "",
    normalizedDifficulty: undefined as number | undefined,
    notes: "",
    selectedTags: [] as Array<{ tagId: string; role?: "core" | "secondary" | "mention"; tagDifficulty?: number; isInstructive?: boolean }>,
    solutions: [] as Array<{ url: string; language?: string; solution?: string; githubUrl?: string }>,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createProblem.mutate({
      platformId: formData.platformId,
      title: formData.title,
      url: formData.url,
      isGreatProblem: formData.isGreatProblem,
      platformProblemId: formData.platformProblemId || undefined,
      platformDifficulty: formData.platformDifficulty || undefined,
      normalizedDifficulty: formData.normalizedDifficulty,
      notes: formData.notes || undefined,
      tags: formData.selectedTags.length > 0 ? formData.selectedTags : undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-6">
      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Title *</label>
        <input
          type="text"
          required
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">URL *</label>
        <input
          type="url"
          required
          value={formData.url}
          onChange={(e) => setFormData({ ...formData, url: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Platform *</label>
        <select
          required
          value={formData.platformId}
          onChange={(e) => setFormData({ ...formData, platformId: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900"
        >
          <option value="">Select a platform</option>
          {platforms?.map((platform) => (
            <option key={platform.id} value={platform.id}>
              {platform.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Platform Problem ID</label>
        <input
          type="text"
          value={formData.platformProblemId}
          onChange={(e) => setFormData({ ...formData, platformProblemId: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">
            Platform Difficulty
          </label>
          <input
            type="text"
            value={formData.platformDifficulty}
            onChange={(e) => setFormData({ ...formData, platformDifficulty: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            placeholder="e.g., Hard, 2200"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">
            Normalized Difficulty (1-10)
          </label>
          <input
            type="number"
            min="1"
            max="10"
            value={formData.normalizedDifficulty || ""}
            onChange={(e) => setFormData({ ...formData, normalizedDifficulty: e.target.value ? parseInt(e.target.value) : undefined })}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            placeholder="1-10"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Notes</label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          rows={3}
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.isGreatProblem}
          onChange={(e) => setFormData({ ...formData, isGreatProblem: e.target.checked })}
          className="w-4 h-4 text-blue-600 border-gray-300 rounded mr-3"
        />
        <label className="text-sm font-semibold text-gray-900">Great Problem</label>
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-3">Tags</label>
        <div className="space-y-3 border border-gray-200 rounded-md p-4">
          {tags?.map((tag) => {
            const selected = formData.selectedTags.find((t) => t.tagId === tag.id);
            return (
              <div key={tag.id} className="space-y-2">
                <div className="flex items-center gap-3">
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
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded"
                  />
                  <span className="flex-1 text-gray-900 font-medium">{tag.name}</span>
                  {selected && (
                    <select
                      value={selected.role || ""}
                      onChange={(e) => {
                        setFormData({
                          ...formData,
                          selectedTags: formData.selectedTags.map((t) =>
                            t.tagId === tag.id
                              ? { ...t, role: e.target.value as "core" | "secondary" | "mention" | undefined }
                              : t
                          ),
                        });
                      }}
                      className="px-3 py-1 border border-gray-300 rounded-md text-sm bg-white"
                    >
                      <option value="">No role</option>
                      <option value="core">Core</option>
                      <option value="secondary">Secondary</option>
                      <option value="mention">Mention</option>
                    </select>
                  )}
                </div>
                {selected && (
                  <div className="ml-7 flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <label className="text-xs font-medium text-gray-700">Difficulty (1-3 stars):</label>
                      <input
                        type="number"
                        min="1"
                        max="3"
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
                        placeholder="1-3"
                        className="w-16 px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    </div>
                    <div className="flex items-center gap-2">
                      <select
                        value={selected.isInstructive === null || selected.isInstructive === undefined ? "" : String(selected.isInstructive)}
                        onChange={(e) => {
                          const val = e.target.value === "" ? undefined : e.target.value === "true";
                          setFormData({
                            ...formData,
                            selectedTags: formData.selectedTags.map((t) =>
                              t.tagId === tag.id ? { ...t, isInstructive: val } : t
                            ),
                          });
                        }}
                        className="px-2 py-1 border border-gray-300 rounded text-xs"
                      >
                        <option value="">Instructive: Not set</option>
                        <option value="true">Instructive: Yes</option>
                        <option value="false">Instructive: No</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <button
        type="submit"
        disabled={createProblem.isPending}
        className="w-full px-4 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {createProblem.isPending ? "Creating..." : "Create Problem"}
      </button>

      {createProblem.error && (
        <p className="text-red-600 text-sm font-medium">{createProblem.error.message}</p>
      )}
    </form>
  );
}

function ProblemsList() {
  const { data: problems, isLoading } = trpc.problem.list.useQuery();
  const deleteProblem = trpc.problem.delete.useMutation({
    onSuccess: () => {
      trpc.useUtils().problem.list.invalidate();
    },
  });

  if (isLoading) {
    return <div className="text-center py-8">Loading problems...</div>;
  }

  if (!problems || problems.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
        No problems yet. Create your first problem above!
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow divide-y">
      {problems.map((problem) => (
        <div key={problem.id} className="p-4 hover:bg-gray-50">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-gray-900">{problem.title}</h3>
                {problem.isGreatProblem && (
                  <span className="px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs rounded">
                    Great
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600 mb-2">
                {problem.platform.name}
                {problem.platformDifficulty && ` • ${problem.platformDifficulty}`}
                {problem.normalizedDifficulty && ` • Normalized: ${problem.normalizedDifficulty}/10`}
              </p>
              <a
                href={problem.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:underline"
              >
                {problem.url}
              </a>
              {problem.notes && (
                <p className="text-sm text-gray-500 mt-2">{problem.notes}</p>
              )}
              <div className="flex flex-wrap gap-1 mt-2">
                {problem.tags.map((pt) => (
                  <span
                    key={pt.tag.id}
                    className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded"
                  >
                    {pt.tag.name}
                    {pt.role && ` (${pt.role})`}
                  </span>
                ))}
              </div>
            </div>
            <button
              onClick={() => {
                if (confirm("Delete this problem?")) {
                  deleteProblem.mutate({ id: problem.id });
                }
              }}
              className="ml-4 px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded"
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

function TagsTab() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTag, setEditingTag] = useState<string | null>(null);
  const { data: tags, isLoading } = trpc.tag.list.useQuery();
  const utils = trpc.useUtils();
  const deleteTag = trpc.tag.delete.useMutation({
    onSuccess: () => {
      utils.tag.list.invalidate();
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-900">Tags</h2>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          {showCreateForm ? "Cancel" : "Create Tag"}
        </button>
      </div>

      {showCreateForm && <CreateTagForm onSuccess={() => setShowCreateForm(false)} />}

      {isLoading ? (
        <div className="text-center py-8">Loading tags...</div>
      ) : !tags || tags.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No tags yet. Create your first tag above!
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tags.map((tag) => (
            <div key={tag.id}>
              {editingTag === tag.id ? (
                <EditTagForm
                  tag={tag}
                  onSuccess={() => setEditingTag(null)}
                  onCancel={() => setEditingTag(null)}
                />
              ) : (
                <div className="bg-white p-4 rounded-lg shadow">
                  <h3 className="font-semibold text-gray-900">{tag.name}</h3>
                  <p className="text-sm text-gray-600">{tag.slug}</p>
                  {tag.description && (
                    <p className="text-sm text-gray-500 mt-2">{tag.description}</p>
                  )}
                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={() => setEditingTag(tag.id)}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => {
                        if (confirm(`Delete tag "${tag.name}"?`)) {
                          deleteTag.mutate({ id: tag.id });
                        }
                      }}
                      className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function CreateTagForm({ onSuccess }: { onSuccess: () => void }) {
  const utils = trpc.useUtils();
  const createTag = trpc.tag.create.useMutation({
    onSuccess: () => {
      utils.tag.list.invalidate();
      onSuccess();
    },
  });

  const [formData, setFormData] = useState({
    name: "",
    slug: "",
    description: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createTag.mutate({
      name: formData.name,
      slug: formData.slug,
      description: formData.description || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-6">
      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Name *</label>
        <input
          type="text"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Slug *</label>
        <input
          type="text"
          required
          value={formData.slug}
          onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          rows={3}
        />
      </div>

      <button
        type="submit"
        disabled={createTag.isPending}
        className="w-full px-4 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {createTag.isPending ? "Creating..." : "Create Tag"}
      </button>

      {createTag.error && <p className="text-red-600 text-sm font-medium">{createTag.error.message}</p>}
    </form>
  );
}

function EditTagForm({ tag, onSuccess, onCancel }: { tag: { id: string; name: string; slug: string; description: string | null }; onSuccess: () => void; onCancel: () => void }) {
  const utils = trpc.useUtils();
  const updateTag = trpc.tag.update.useMutation({
    onSuccess: () => {
      utils.tag.list.invalidate();
      onSuccess();
    },
  });

  const [formData, setFormData] = useState({
    name: tag.name,
    slug: tag.slug,
    description: tag.description || "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateTag.mutate({
      id: tag.id,
      name: formData.name,
      slug: formData.slug,
      description: formData.description || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-6">
      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Name *</label>
        <input
          type="text"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Slug *</label>
        <input
          type="text"
          required
          value={formData.slug}
          onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          rows={3}
        />
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={updateTag.isPending}
          className="flex-1 px-4 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {updateTag.isPending ? "Updating..." : "Update Tag"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-3 bg-gray-200 text-gray-700 font-semibold rounded-md hover:bg-gray-300"
        >
          Cancel
        </button>
      </div>

      {updateTag.error && <p className="text-red-600 text-sm font-medium">{updateTag.error.message}</p>}
    </form>
  );
}

function PlatformsTab() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingPlatform, setEditingPlatform] = useState<string | null>(null);
  const { data: platforms, isLoading } = trpc.platform.list.useQuery();
  const utils = trpc.useUtils();
  const deletePlatform = trpc.platform.delete.useMutation({
    onSuccess: () => {
      utils.platform.list.invalidate();
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-900">Platforms</h2>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          {showCreateForm ? "Cancel" : "Create Platform"}
        </button>
      </div>

      {showCreateForm && <CreatePlatformForm onSuccess={() => setShowCreateForm(false)} />}

      {isLoading ? (
        <div className="text-center py-8">Loading platforms...</div>
      ) : !platforms || platforms.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No platforms yet. Create your first platform above!
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {platforms.map((platform) => (
            <div key={platform.id}>
              {editingPlatform === platform.id ? (
                <EditPlatformForm
                  platform={platform}
                  onSuccess={() => setEditingPlatform(null)}
                  onCancel={() => setEditingPlatform(null)}
                />
              ) : (
                <div className="bg-white p-4 rounded-lg shadow">
                  <h3 className="font-semibold text-gray-900">{platform.name}</h3>
                  <p className="text-sm text-gray-600">{platform.slug}</p>
                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={() => setEditingPlatform(platform.id)}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => {
                        if (confirm(`Delete platform "${platform.name}"?`)) {
                          deletePlatform.mutate({ id: platform.id });
                        }
                      }}
                      className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function CreatePlatformForm({ onSuccess }: { onSuccess: () => void }) {
  const utils = trpc.useUtils();
  const createPlatform = trpc.platform.create.useMutation({
    onSuccess: () => {
      utils.platform.list.invalidate();
      onSuccess();
    },
  });

  const [formData, setFormData] = useState({
    name: "",
    slug: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createPlatform.mutate(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-6">
      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Name *</label>
        <input
          type="text"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Slug *</label>
        <input
          type="text"
          required
          value={formData.slug}
          onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <button
        type="submit"
        disabled={createPlatform.isPending}
        className="w-full px-4 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {createPlatform.isPending ? "Creating..." : "Create Platform"}
      </button>

      {createPlatform.error && <p className="text-red-600 text-sm font-medium">{createPlatform.error.message}</p>}
    </form>
  );
}

function EditPlatformForm({ platform, onSuccess, onCancel }: { platform: { id: string; name: string; slug: string }; onSuccess: () => void; onCancel: () => void }) {
  const utils = trpc.useUtils();
  const updatePlatform = trpc.platform.update.useMutation({
    onSuccess: () => {
      utils.platform.list.invalidate();
      onSuccess();
    },
  });

  const [formData, setFormData] = useState({
    name: platform.name,
    slug: platform.slug,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updatePlatform.mutate({
      id: platform.id,
      ...formData,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-6">
      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Name *</label>
        <input
          type="text"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Slug *</label>
        <input
          type="text"
          required
          value={formData.slug}
          onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={updatePlatform.isPending}
          className="flex-1 px-4 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {updatePlatform.isPending ? "Updating..." : "Update Platform"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-3 bg-gray-200 text-gray-700 font-semibold rounded-md hover:bg-gray-300"
        >
          Cancel
        </button>
      </div>

      {updatePlatform.error && <p className="text-red-600 text-sm font-medium">{updatePlatform.error.message}</p>}
    </form>
  );
}

function TagHierarchiesTab() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { data: tags, isLoading: tagsLoading } = trpc.tag.list.useQuery();
  const { data: hierarchies, isLoading: hierarchiesLoading } = trpc.tagParent.list.useQuery();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-900">Tag Hierarchies</h2>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          {showCreateForm ? "Cancel" : "Create Hierarchy"}
        </button>
      </div>

      {showCreateForm && <CreateTagHierarchyForm onSuccess={() => setShowCreateForm(false)} />}

      {tagsLoading || hierarchiesLoading ? (
        <div className="text-center py-8">Loading hierarchies...</div>
      ) : !hierarchies || hierarchies.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No hierarchies yet. Create relationships between tags above!
        </div>
      ) : (
        <TagHierarchyFlow tags={tags || []} hierarchies={hierarchies} />
      )}
    </div>
  );
}

function TagHierarchyFlow({ tags, hierarchies }: { tags: any[]; hierarchies: any[] }) {
  const utils = trpc.useUtils();
  const deleteHierarchy = trpc.tagParent.delete.useMutation({
    onSuccess: () => {
      utils.tagParent.list.invalidate();
    },
  });

  const childrenByParent = useMemo(() => {
    return hierarchies.reduce((acc, rel) => {
      if (!acc[rel.parent_tag_id]) {
        acc[rel.parent_tag_id] = [];
      }
      acc[rel.parent_tag_id].push(rel.child_tag_id);
      return acc;
    }, {} as Record<string, string[]>);
  }, [hierarchies]);

  const parentsOfChild = useMemo(() => {
    return hierarchies.reduce((acc, rel) => {
      if (!acc[rel.child_tag_id]) {
        acc[rel.child_tag_id] = [];
      }
      acc[rel.child_tag_id].push(rel.parent_tag_id);
      return acc;
    }, {} as Record<string, string[]>);
  }, [hierarchies]);

  const rootTags = useMemo(() => {
    return tags.filter((tag) => !parentsOfChild[tag.id]);
  }, [tags, parentsOfChild]);

  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    
    const nodeWidth = 220;
    const nodeHeight = 80;
    
    dagreGraph.setGraph({ 
      rankdir: 'TB',
      nodesep: 80,
      ranksep: 100,
      marginx: 50,
      marginy: 50,
    });

    const nodes: Node[] = [];
    const edges: Edge[] = [];

    tags.forEach((tag) => {
      dagreGraph.setNode(tag.id, { width: nodeWidth, height: nodeHeight });
      
      nodes.push({
        id: tag.id,
        type: 'default',
        data: { 
          label: (
            <div className="px-4 py-2 text-center">
              <div className="font-semibold text-gray-900">{tag.name}</div>
              <div className="text-xs text-gray-500">{tag.slug}</div>
            </div>
          )
        },
        position: { x: 0, y: 0 },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
        style: {
          background: '#EFF6FF',
          border: '2px solid #3B82F6',
          borderRadius: '8px',
          width: nodeWidth,
          height: nodeHeight,
        },
      });
    });

    hierarchies.forEach((rel) => {
      const parentTag = tags.find(t => t.id === rel.parent_tag_id);
      const childTag = tags.find(t => t.id === rel.child_tag_id);
      
      dagreGraph.setEdge(rel.parent_tag_id, rel.child_tag_id);
      
      edges.push({
        id: `${rel.parent_tag_id}-${rel.child_tag_id}`,
        source: rel.parent_tag_id,
        target: rel.child_tag_id,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#3B82F6', strokeWidth: 2 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#3B82F6',
        },
        label: '✕',
        labelStyle: { 
          fill: '#DC2626', 
          fontWeight: 700,
          cursor: 'pointer',
        },
        labelBgStyle: { 
          fill: '#FEE2E2',
          fillOpacity: 0.9,
        },
        data: {
          onLabelClick: () => {
            if (childTag && parentTag && confirm(`Remove "${childTag.name}" as a child of "${parentTag.name}"?`)) {
              deleteHierarchy.mutate({
                childTagId: rel.child_tag_id,
                parentTagId: rel.parent_tag_id,
              });
            }
          }
        }
      });
    });

    dagre.layout(dagreGraph);

    nodes.forEach((node) => {
      const nodeWithPosition = dagreGraph.node(node.id);
      node.position = {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      };
    });

    return { nodes, edges };
  }, [tags, hierarchies, deleteHierarchy]);

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  const onEdgeClick = useCallback((event: React.MouseEvent, edge: Edge) => {
    if (edge.data?.onLabelClick) {
      edge.data.onLabelClick();
    }
  }, []);

  return (
    <div className="bg-white rounded-lg shadow" style={{ height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onEdgeClick={onEdgeClick}
        fitView
        fitViewOptions={{ padding: 0.2 }}
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}

function CreateTagHierarchyForm({ onSuccess }: { onSuccess: () => void }) {
  const { data: tags } = trpc.tag.list.useQuery();
  const utils = trpc.useUtils();
  const createHierarchy = trpc.tagParent.create.useMutation({
    onSuccess: () => {
      utils.tagParent.list.invalidate();
      onSuccess();
    },
  });

  const [formData, setFormData] = useState({
    childTagId: "",
    parentTagId: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.childTagId === formData.parentTagId) {
      alert("A tag cannot be its own parent!");
      return;
    }
    createHierarchy.mutate(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-6">
      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Child Tag *</label>
        <select
          required
          value={formData.childTagId}
          onChange={(e) => setFormData({ ...formData, childTagId: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        >
          <option value="">Select a child tag</option>
          {tags?.map((tag) => (
            <option key={tag.id} value={tag.id}>
              {tag.name} ({tag.slug})
            </option>
          ))}
        </select>
        <p className="text-xs text-gray-600 mt-1">The more specific/narrow tag</p>
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-900 mb-2">Parent Tag *</label>
        <select
          required
          value={formData.parentTagId}
          onChange={(e) => setFormData({ ...formData, parentTagId: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        >
          <option value="">Select a parent tag</option>
          {tags?.map((tag) => (
            <option key={tag.id} value={tag.id}>
              {tag.name} ({tag.slug})
            </option>
          ))}
        </select>
        <p className="text-xs text-gray-600 mt-1">The more general/broad tag (e.g., "BFS" is parent of "0-1 BFS")</p>
      </div>

      <button
        type="submit"
        disabled={createHierarchy.isPending}
        className="w-full px-4 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {createHierarchy.isPending ? "Creating..." : "Create Hierarchy"}
      </button>

      {createHierarchy.error && <p className="text-red-600 text-sm font-medium">{createHierarchy.error.message}</p>}
    </form>
  );
}

