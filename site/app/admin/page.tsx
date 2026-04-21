"use client";

import { useState, useCallback, useMemo, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { trpc } from "../providers";
import { programming_language, tag_role } from "@/src/generated/prisma/enums";
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
          <div className="flex items-center gap-3">
            <Link
              href="/admin/drill/implements"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Drill Implements
            </Link>
            <Link
              href="/admin/drill/mindsolves"
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
            >
              Drill Mindsolves
            </Link>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
            >
              Log Out
            </button>
          </div>
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
  const [showDatabaseForm, setShowDatabaseForm] = useState(false);
  const [showLeetcodeForm, setShowLeetcodeForm] = useState(false);
  const [editingProblem, setEditingProblem] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-900">Problems</h2>
        <div className="flex gap-3">
          <button
            onClick={() => {
              setShowLeetcodeForm(!showLeetcodeForm);
              if (!showLeetcodeForm) {
                setShowCreateForm(false);
                setShowDatabaseForm(false);
              }
            }}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            {showLeetcodeForm ? "Cancel" : "Add Leetcode Problem"}
          </button>
          <button
            onClick={() => {
              setShowDatabaseForm(!showDatabaseForm);
              if (!showDatabaseForm) {
                setShowCreateForm(false);
                setShowLeetcodeForm(false);
              }
            }}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
          >
            {showDatabaseForm ? "Cancel" : "Add Database Leetcode Problem"}
          </button>
          <button
            onClick={() => {
              setShowCreateForm(!showCreateForm);
              if (!showCreateForm) {
                setShowDatabaseForm(false);
                setShowLeetcodeForm(false);
              }
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            {showCreateForm ? "Cancel" : "Create Problem"}
          </button>
        </div>
      </div>

      {showCreateForm && <CreateProblemForm onSuccess={() => setShowCreateForm(false)} />}
      {showLeetcodeForm && <CreateLeetcodeProblemForm onSuccess={() => setShowLeetcodeForm(false)} />}
      {showDatabaseForm && <CreateDatabaseLeetcodeProblemForm onSuccess={() => setShowDatabaseForm(false)} />}
      <ProblemsList
        editingProblem={editingProblem}
        onEdit={setEditingProblem}
        onCloseEdit={() => setEditingProblem(null)}
      />
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

  const parseAtCoderUrl = (url: string) => {
    const atcoderPattern = /^https?:\/\/atcoder\.jp\/contests\/([^\/]+)\/tasks\/([^\/\?#]+)/;
    const match = url.match(atcoderPattern);
    
    if (match) {
      const problemId = match[2];
      const atcoderPlatform = platforms?.find(p => p.slug === 'atcoder' || p.name.toLowerCase() === 'atcoder');
      
      return {
        platformId: atcoderPlatform?.id || null,
        problemId: problemId,
      };
    }
    
    return null;
  };

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
    solutions: [{ submissionUrl: "", language: "Python" as programming_language | "", githubUrl: "" }],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createProblem.mutate({
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

  return (
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Title *</label>
          <input
            type="text"
            required
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className={`w-full px-3 py-1.5 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 text-sm ${formData.title ? 'border border-gray-300' : 'border-2 border-red-400'}`}
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">URL *</label>
          <input
            type="url"
            required
            value={formData.url}
            onChange={(e) => {
              const url = e.target.value;
              setFormData({ ...formData, url });

              const parsed = parseAtCoderUrl(url);
              if (parsed) {
                setFormData(prev => ({
                  ...prev,
                  url,
                  platformId: parsed.platformId || prev.platformId,
                  platformProblemId: parsed.problemId,
                }));
              }
            }}
            className={`w-full px-3 py-1.5 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 text-sm ${formData.url ? 'border border-gray-300' : 'border-2 border-red-400'}`}
            placeholder="https://atcoder.jp/contests/..."
          />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Platform *</label>
          <select
            required
            value={formData.platformId}
            onChange={(e) => setFormData({ ...formData, platformId: e.target.value })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-gray-900 text-sm"
          >
            <option value="">Select</option>
            {platforms?.map((platform) => (
              <option key={platform.id} value={platform.id}>
                {platform.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Problem ID</label>
          <input
            type="text"
            value={formData.platformProblemId}
            onChange={(e) => setFormData({ ...formData, platformProblemId: e.target.value })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Difficulty</label>
          <input
            type="text"
            value={formData.platformDifficulty}
            onChange={(e) => setFormData({ ...formData, platformDifficulty: e.target.value })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 text-sm"
            placeholder="e.g., Hard, 2200"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Norm Diff (1-10)</label>
          <input
            type="number"
            min="1"
            max="10"
            value={formData.normalizedDifficulty || ""}
            onChange={(e) => setFormData({ ...formData, normalizedDifficulty: e.target.value ? parseInt(e.target.value) : undefined })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 text-sm"
            placeholder="1-10"
          />
        </div>
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

      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.isGreatProblem}
          onChange={(e) => setFormData({ ...formData, isGreatProblem: e.target.checked })}
          className="w-4 h-4 text-blue-600 border-gray-300 rounded mr-3"
        />
        <label className="text-sm font-semibold text-gray-900">Great Problem</label>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.isLeetgoat222}
          onChange={(e) => setFormData({ ...formData, isLeetgoat222: e.target.checked })}
          className="w-4 h-4 text-blue-600 border-gray-300 rounded mr-3"
        />
        <label className="text-sm font-semibold text-gray-900">LeetGoat 222</label>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.isLeetgoatAdvanced}
          onChange={(e) => setFormData({ ...formData, isLeetgoatAdvanced: e.target.checked })}
          className="w-4 h-4 text-blue-600 border-gray-300 rounded mr-3"
        />
        <label className="text-sm font-semibold text-gray-900">LeetGoat Advanced</label>
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
        <div className="flex justify-between items-center mb-3">
          <label className="block text-sm font-semibold text-gray-900">Solutions (optional)</label>
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
          <div className="space-y-4">
            {formData.solutions.map((sol, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-lg bg-gray-50 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-semibold text-gray-700">Solution {index + 1}</span>
                  <button
                    type="button"
                    onClick={() => {
                      setFormData({
                        ...formData,
                        solutions: formData.solutions.filter((_, i) => i !== index),
                      });
                    }}
                    className="text-xs text-red-600 hover:text-red-700 px-2 py-1 hover:bg-red-50 rounded"
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

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Tags</label>
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
                              ? { ...t, role: e.target.value === "" ? undefined : e.target.value as "core" | "secondary" | "mention" }
                              : t
                          ),
                        });
                      }}
                      className="px-3 py-1 border border-gray-300 rounded-md text-sm bg-white text-gray-900 font-medium"
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
                        className="w-20 px-2 py-1 border border-gray-300 rounded text-sm text-gray-900 font-medium"
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
                        className="px-2 py-1 border border-gray-300 rounded text-xs text-gray-900 font-medium"
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

function CreateLeetcodeProblemForm({ onSuccess }: { onSuccess: () => void }) {
  const utils = trpc.useUtils();
  const { data: platforms } = trpc.platform.list.useQuery();
  const { data: tags } = trpc.tag.list.useQuery();

  const createProblem = trpc.problem.create.useMutation({
    onSuccess: () => {
      utils.problem.list.invalidate();
      onSuccess();
    },
  });

  // Find Leetcode platform
  const leetcodePlatform = platforms?.find(p => p.slug === 'leetcode' || p.name.toLowerCase() === 'leetcode');

  // Extract problem ID from title (e.g., "2339. Problem Name" -> "2339")
  const extractProblemId = (title: string): string => {
    const match = title.match(/^(\d+)\./);
    return match ? match[1] : "";
  };

  const [formData, setFormData] = useState({
    platformId: leetcodePlatform?.id || "",
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
    solutions: [{ submissionUrl: "", language: "Python" as programming_language | "", githubUrl: "" }],
  });

  // Update platform when platforms load
  useEffect(() => {
    if (leetcodePlatform && !formData.platformId) {
      setFormData(prev => ({ ...prev, platformId: leetcodePlatform.id }));
    }
  }, [leetcodePlatform, formData.platformId]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createProblem.mutate({
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

  const handleTitleChange = (newTitle: string) => {
    const problemId = extractProblemId(newTitle);
    setFormData({
      ...formData,
      title: newTitle,
      platformProblemId: problemId,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow space-y-3 border-2 border-green-200">
      <div className="bg-green-50 border border-green-200 rounded-md px-3 py-2">
        <span className="text-sm font-semibold text-green-900">💻 Leetcode Problem</span>
        <span className="ml-2 text-xs text-green-700">Platform auto-set, problem ID auto-extracted from title.</span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Title *</label>
          <input
            type="text"
            required
            value={formData.title}
            onChange={(e) => handleTitleChange(e.target.value)}
            className={`w-full px-3 py-1.5 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 text-sm ${formData.title ? 'border border-gray-300' : 'border-2 border-red-400'}`}
            placeholder="e.g., 3737. Count Subarrays With Majority Element I"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">URL *</label>
          <input
            type="url"
            required
            value={formData.url}
            onChange={(e) => setFormData({ ...formData, url: e.target.value })}
            className={`w-full px-3 py-1.5 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 text-sm ${formData.url ? 'border border-gray-300' : 'border-2 border-red-400'}`}
            placeholder="https://leetcode.com/problems/..."
          />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Platform *</label>
          <select
            required
            value={formData.platformId}
            onChange={(e) => setFormData({ ...formData, platformId: e.target.value })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white text-gray-900 text-sm"
          >
            <option value="">Select</option>
            {platforms?.map((platform) => (
              <option key={platform.id} value={platform.id}>
                {platform.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">
            Problem ID
            {formData.platformProblemId && (
              <span className="ml-1 text-xs text-green-600 font-normal">({formData.platformProblemId})</span>
            )}
          </label>
          <input
            type="text"
            value={formData.platformProblemId}
            onChange={(e) => setFormData({ ...formData, platformProblemId: e.target.value })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Difficulty</label>
          <input
            type="text"
            value={formData.platformDifficulty}
            onChange={(e) => setFormData({ ...formData, platformDifficulty: e.target.value })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 text-sm"
            placeholder="Easy, Medium, Hard"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Norm Diff (1-10)</label>
          <input
            type="number"
            min="1"
            max="10"
            value={formData.normalizedDifficulty || ""}
            onChange={(e) => setFormData({ ...formData, normalizedDifficulty: e.target.value ? parseInt(e.target.value) : undefined })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 text-sm"
            placeholder="1-10"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Simplified Problem Statement</label>
        <textarea
          value={formData.simplifiedStatement}
          onChange={(e) => setFormData({ ...formData, simplifiedStatement: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900"
          rows={2}
          placeholder="A brief summary of the problem"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Notes</label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900"
          rows={2}
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.isGreatProblem}
          onChange={(e) => setFormData({ ...formData, isGreatProblem: e.target.checked })}
          className="w-4 h-4 text-green-600 border-gray-300 rounded mr-3"
        />
        <label className="text-sm font-semibold text-gray-900">Great Problem</label>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.isLeetgoat222}
          onChange={(e) => setFormData({ ...formData, isLeetgoat222: e.target.checked })}
          className="w-4 h-4 text-green-600 border-gray-300 rounded mr-3"
        />
        <label className="text-sm font-semibold text-gray-900">LeetGoat 222</label>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.isLeetgoatAdvanced}
          onChange={(e) => setFormData({ ...formData, isLeetgoatAdvanced: e.target.checked })}
          className="w-4 h-4 text-green-600 border-gray-300 rounded mr-3"
        />
        <label className="text-sm font-semibold text-gray-900">LeetGoat Advanced</label>
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Drill Type</label>
        <select
          value={formData.drillType || ""}
          onChange={(e) => setFormData({ ...formData, drillType: e.target.value === "" ? null : e.target.value as "mindsolve" | "implement" })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white text-gray-900"
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
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900"
            rows={2}
            placeholder="Notes about drilling this problem..."
          />
        </div>
      )}

      <div>
        <div className="flex justify-between items-center mb-3">
          <label className="block text-sm font-semibold text-gray-900">Solutions (optional)</label>
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
          <div className="space-y-4">
            {formData.solutions.map((sol, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-lg bg-gray-50 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-semibold text-gray-700">Solution {index + 1}</span>
                  <button
                    type="button"
                    onClick={() => {
                      setFormData({
                        ...formData,
                        solutions: formData.solutions.filter((_, i) => i !== index),
                      });
                    }}
                    className="text-xs text-red-600 hover:text-red-700 px-2 py-1 hover:bg-red-50 rounded"
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
                    placeholder="https://leetcode.com/submissions/..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Tags</label>
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
                    className="w-4 h-4 text-green-600 border-gray-300 rounded"
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
                              ? { ...t, role: e.target.value === "" ? undefined : e.target.value as "core" | "secondary" | "mention" }
                              : t
                          ),
                        });
                      }}
                      className="px-3 py-1 border border-gray-300 rounded-md text-sm bg-white text-gray-900 font-medium"
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
                        className="w-20 px-2 py-1 border border-gray-300 rounded text-sm text-gray-900 font-medium"
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
                        className="px-2 py-1 border border-gray-300 rounded text-xs text-gray-900 font-medium"
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
        className="w-full px-4 py-3 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {createProblem.isPending ? "Creating..." : "Create Leetcode Problem"}
      </button>

      {createProblem.error && (
        <p className="text-red-600 text-sm font-medium">{createProblem.error.message}</p>
      )}
    </form>
  );
}

function CreateDatabaseLeetcodeProblemForm({ onSuccess }: { onSuccess: () => void }) {
  const utils = trpc.useUtils();
  const { data: platforms } = trpc.platform.list.useQuery();
  const { data: tags } = trpc.tag.list.useQuery();

  const createProblem = trpc.problem.create.useMutation({
    onSuccess: () => {
      utils.problem.list.invalidate();
      onSuccess();
    },
  });

  // Find Leetcode platform and Database tag
  const leetcodePlatform = platforms?.find(p => p.slug === 'leetcode' || p.name.toLowerCase() === 'leetcode');
  const databaseTag = tags?.find(t => t.slug === 'database' || t.name.toLowerCase() === 'database');

  // Extract problem ID from title (e.g., "2339. Problem Name" -> "2339")
  const extractProblemId = (title: string): string => {
    const match = title.match(/^(\d+)\./);
    return match ? match[1] : "";
  };

  const [formData, setFormData] = useState({
    platformId: leetcodePlatform?.id || "",
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
    selectedTags: databaseTag ? [{ tagId: databaseTag.id, role: "core" as tag_role, isInstructive: false }] : [] as Array<{ tagId: string; role?: tag_role; tagDifficulty?: number; isInstructive?: boolean }>,
    solutions: [{ submissionUrl: "", language: "PostgreSQL" as programming_language | "", githubUrl: "" }],
  });

  // Update platform when platforms load
  useEffect(() => {
    if (leetcodePlatform && !formData.platformId) {
      setFormData(prev => ({ ...prev, platformId: leetcodePlatform.id }));
    }
  }, [leetcodePlatform, formData.platformId]);

  // Update database tag when tags load
  useEffect(() => {
    if (databaseTag && formData.selectedTags.length === 0) {
      setFormData(prev => ({
        ...prev,
        selectedTags: [{ tagId: databaseTag.id, role: "core" as tag_role, isInstructive: false }]
      }));
    }
  }, [databaseTag, formData.selectedTags.length]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createProblem.mutate({
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

  const handleTitleChange = (newTitle: string) => {
    const problemId = extractProblemId(newTitle);
    setFormData({
      ...formData,
      title: newTitle,
      platformProblemId: problemId,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow space-y-3 border-2 border-purple-200">
      <div className="bg-purple-50 border border-purple-200 rounded-md px-3 py-2">
        <span className="text-sm font-semibold text-purple-900">🗃️ Database Leetcode Problem</span>
        <span className="ml-2 text-xs text-purple-700">DB tag auto-selected (core, non-instructive). ID auto-extracted.</span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Title *</label>
          <input
            type="text"
            required
            value={formData.title}
            onChange={(e) => handleTitleChange(e.target.value)}
            className={`w-full px-3 py-1.5 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 text-sm ${formData.title ? 'border border-gray-300' : 'border-2 border-red-400'}`}
            placeholder="e.g., 2339. All the Matches of the League"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">URL *</label>
          <input
            type="url"
            required
            value={formData.url}
            onChange={(e) => setFormData({ ...formData, url: e.target.value })}
            className={`w-full px-3 py-1.5 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 text-sm ${formData.url ? 'border border-gray-300' : 'border-2 border-red-400'}`}
            placeholder="https://leetcode.com/problems/..."
          />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Platform *</label>
          <select
            required
            value={formData.platformId}
            onChange={(e) => setFormData({ ...formData, platformId: e.target.value })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white text-gray-900 text-sm"
          >
            <option value="">Select</option>
            {platforms?.map((platform) => (
              <option key={platform.id} value={platform.id}>
                {platform.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">
            Problem ID
            {formData.platformProblemId && (
              <span className="ml-1 text-xs text-purple-600 font-normal">({formData.platformProblemId})</span>
            )}
          </label>
          <input
            type="text"
            value={formData.platformProblemId}
            onChange={(e) => setFormData({ ...formData, platformProblemId: e.target.value })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Difficulty</label>
          <input
            type="text"
            value={formData.platformDifficulty}
            onChange={(e) => setFormData({ ...formData, platformDifficulty: e.target.value })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 text-sm"
            placeholder="Easy, Medium, Hard"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-900 mb-1">Norm Diff (1-10)</label>
          <input
            type="number"
            min="1"
            max="10"
            value={formData.normalizedDifficulty || ""}
            onChange={(e) => setFormData({ ...formData, normalizedDifficulty: e.target.value ? parseInt(e.target.value) : undefined })}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 text-sm"
            placeholder="1-10"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Simplified Problem Statement</label>
        <textarea
          value={formData.simplifiedStatement}
          onChange={(e) => setFormData({ ...formData, simplifiedStatement: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900"
          rows={2}
          placeholder="A brief summary of the problem"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Notes</label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900"
          rows={2}
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.isGreatProblem}
          onChange={(e) => setFormData({ ...formData, isGreatProblem: e.target.checked })}
          className="w-4 h-4 text-purple-600 border-gray-300 rounded mr-3"
        />
        <label className="text-sm font-semibold text-gray-900">Great Problem</label>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.isLeetgoat222}
          onChange={(e) => setFormData({ ...formData, isLeetgoat222: e.target.checked })}
          className="w-4 h-4 text-purple-600 border-gray-300 rounded mr-3"
        />
        <label className="text-sm font-semibold text-gray-900">LeetGoat 222</label>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.isLeetgoatAdvanced}
          onChange={(e) => setFormData({ ...formData, isLeetgoatAdvanced: e.target.checked })}
          className="w-4 h-4 text-purple-600 border-gray-300 rounded mr-3"
        />
        <label className="text-sm font-semibold text-gray-900">LeetGoat Advanced</label>
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Drill Type</label>
        <select
          value={formData.drillType || ""}
          onChange={(e) => setFormData({ ...formData, drillType: e.target.value === "" ? null : e.target.value as "mindsolve" | "implement" })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white text-gray-900"
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
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900"
            rows={2}
            placeholder="Notes about drilling this problem..."
          />
        </div>
      )}

      <div>
        <div className="flex justify-between items-center mb-3">
          <label className="block text-sm font-semibold text-gray-900">Solutions (optional)</label>
          <button
            type="button"
            onClick={() => {
              setFormData({
                ...formData,
                solutions: [...formData.solutions, { submissionUrl: "", language: "PostgreSQL", githubUrl: "" }],
              });
            }}
            className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
          >
            + Add Solution
          </button>
        </div>
        {formData.solutions.length > 0 && (
          <div className="space-y-4">
            {formData.solutions.map((sol, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-lg bg-gray-50 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-semibold text-gray-700">Solution {index + 1}</span>
                  <button
                    type="button"
                    onClick={() => {
                      setFormData({
                        ...formData,
                        solutions: formData.solutions.filter((_, i) => i !== index),
                      });
                    }}
                    className="text-xs text-red-600 hover:text-red-700 px-2 py-1 hover:bg-red-50 rounded"
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
                    placeholder="https://leetcode.com/submissions/..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Tags</label>
        <div className="space-y-3 border border-gray-200 rounded-md p-4">
          {tags
            ?.filter(tag => tag.slug === 'database' || tag.name.toLowerCase() === 'database')
            .map((tag) => {
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
                            selectedTags: [...formData.selectedTags, { tagId: tag.id, role: "core" as tag_role, isInstructive: false }],
                          });
                        } else {
                          setFormData({
                            ...formData,
                            selectedTags: formData.selectedTags.filter((t) => t.tagId !== tag.id),
                          });
                        }
                      }}
                      className="w-4 h-4 text-purple-600 border-gray-300 rounded"
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
                                ? { ...t, role: e.target.value === "" ? undefined : e.target.value as "core" | "secondary" | "mention" }
                                : t
                            ),
                          });
                        }}
                        className="px-3 py-1 border border-gray-300 rounded-md text-sm bg-white text-gray-900 font-medium"
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
                          className="w-20 px-2 py-1 border border-gray-300 rounded text-sm text-gray-900 font-medium"
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
                          className="px-2 py-1 border border-gray-300 rounded text-xs text-gray-900 font-medium"
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
        <div className="mt-3 text-xs text-gray-600">
          Only showing Database tag. To add other tags, use the regular form.
        </div>
      </div>

      <button
        type="submit"
        disabled={createProblem.isPending}
        className="w-full px-4 py-3 bg-purple-600 text-white font-semibold rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {createProblem.isPending ? "Creating..." : "Create Database Problem"}
      </button>

      {createProblem.error && (
        <p className="text-red-600 text-sm font-medium">{createProblem.error.message}</p>
      )}
    </form>
  );
}

const PROBLEMS_PER_PAGE = 20;

function InlineEditText({
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

type ProblemTagRow = {
  tag: { id: string; name: string };
  role: tag_role | null;
  tagDifficulty: number | null;
  isInstructive: boolean | null;
};

type TagMutationInput = { tagId: string; role?: tag_role; tagDifficulty?: number; isInstructive?: boolean };

function tagsToMutation(tags: ProblemTagRow[]): TagMutationInput[] {
  return tags.map((pt) => ({
    tagId: pt.tag.id,
    role: pt.role ?? undefined,
    tagDifficulty: pt.tagDifficulty ?? undefined,
    isInstructive: pt.isInstructive ?? undefined,
  }));
}

function InlineTagEditor({
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

function InlineDifficulty({
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

function InlineDrillEditor({
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

function ProblemsList({ editingProblem, onEdit, onCloseEdit }: { editingProblem: string | null; onEdit: (id: string) => void; onCloseEdit: () => void }) {
  const utils = trpc.useUtils();
  const { data: problems, isLoading } = trpc.problem.list.useQuery();
  const [page, setPage] = useState(1);
  const [fullView, setFullView] = useState(false);
  const [greatOnly, setGreatOnly] = useState(false);
  const deleteProblem = trpc.problem.delete.useMutation({
    onSuccess: () => {
      utils.problem.list.invalidate();
    },
  });
  const updateProblem = trpc.problem.update.useMutation({
    onSuccess: () => {
      utils.problem.list.invalidate();
    },
    onError: (error) => {
      alert(`Failed to update: ${error.message}`);
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

  const filteredProblems = greatOnly ? problems.filter((p) => p.isGreatProblem) : problems;
  const totalPages = Math.max(1, Math.ceil(filteredProblems.length / PROBLEMS_PER_PAGE));
  const currentPage = Math.min(page, totalPages);
  const startIdx = (currentPage - 1) * PROBLEMS_PER_PAGE;
  const pageProblems = fullView ? filteredProblems : filteredProblems.slice(startIdx, startIdx + PROBLEMS_PER_PAGE);

  const Pager = () => (
    <div className="flex items-center justify-between gap-2 px-4 py-3 bg-gray-50 flex-wrap">
      <div className="text-sm text-gray-600">
        {fullView
          ? `Showing all ${filteredProblems.length}`
          : `Showing ${filteredProblems.length === 0 ? 0 : startIdx + 1}–${Math.min(startIdx + PROBLEMS_PER_PAGE, filteredProblems.length)} of ${filteredProblems.length}`}
        {greatOnly && <span className="ml-2 text-yellow-700">(great only)</span>}
      </div>
      <div className="flex items-center gap-1">
        <label className="flex items-center gap-1 text-sm mr-2 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={greatOnly}
            onChange={(e) => { setGreatOnly(e.target.checked); setPage(1); }}
            className="w-3.5 h-3.5 text-yellow-600 border-gray-300 rounded"
          />
          <span className={greatOnly ? "text-yellow-800 font-medium" : "text-gray-700"}>Great only</span>
        </label>
        {!fullView && (
          <>
            <button
              onClick={() => setPage(1)}
              disabled={currentPage === 1}
              className="px-2 py-1 text-sm rounded border border-gray-300 bg-white disabled:opacity-40 hover:bg-gray-100"
            >
              « First
            </button>
            <button
              onClick={() => setPage(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-2 py-1 text-sm rounded border border-gray-300 bg-white disabled:opacity-40 hover:bg-gray-100"
            >
              ‹ Prev
            </button>
            <span className="px-2 text-sm text-gray-700">
              Page {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => setPage(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-2 py-1 text-sm rounded border border-gray-300 bg-white disabled:opacity-40 hover:bg-gray-100"
            >
              Next ›
            </button>
            <button
              onClick={() => setPage(totalPages)}
              disabled={currentPage === totalPages}
              className="px-2 py-1 text-sm rounded border border-gray-300 bg-white disabled:opacity-40 hover:bg-gray-100"
            >
              Last »
            </button>
          </>
        )}
        <button
          onClick={() => setFullView((f) => !f)}
          className={`ml-2 px-2 py-1 text-sm rounded border ${
            fullView
              ? "border-blue-600 bg-blue-600 text-white hover:bg-blue-700"
              : "border-gray-300 bg-white hover:bg-gray-100"
          }`}
          title={fullView ? "Switch to paginated view" : "Render all problems (may be slow)"}
        >
          {fullView ? "Paginate" : "Full view"}
        </button>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow divide-y">
      <Pager />
      {pageProblems.map((problem) => (
        <div key={problem.id}>
        <div className="p-4 hover:bg-gray-50">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-gray-900">{problem.title}</h3>
                <label className="flex items-center gap-1 cursor-pointer" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="checkbox"
                    checked={problem.isGreatProblem}
                    onChange={() => updateProblem.mutate({ id: problem.id, isGreatProblem: !problem.isGreatProblem })}
                    className="w-3 h-3 text-yellow-600 border-gray-300 rounded"
                  />
                  <span className={`text-xs px-1.5 py-0.5 rounded ${problem.isGreatProblem ? 'bg-yellow-100 text-yellow-800' : 'text-gray-600'}`}>
                    Great
                  </span>
                </label>
                <label className="flex items-center gap-1 cursor-pointer" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="checkbox"
                    checked={problem.isLeetgoat222}
                    onChange={() => updateProblem.mutate({ id: problem.id, isLeetgoat222: !problem.isLeetgoat222 })}
                    className="w-3 h-3 text-blue-600 border-gray-300 rounded"
                  />
                  <span className="text-xs text-gray-600">222</span>
                </label>
                <label className="flex items-center gap-1 cursor-pointer" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="checkbox"
                    checked={problem.isLeetgoatAdvanced}
                    onChange={() => updateProblem.mutate({ id: problem.id, isLeetgoatAdvanced: !problem.isLeetgoatAdvanced })}
                    className="w-3 h-3 text-purple-600 border-gray-300 rounded"
                  />
                  <span className="text-xs text-gray-600">Adv</span>
                </label>
              </div>
              <div className="text-sm text-gray-600 mb-2 flex items-center gap-1 flex-wrap">
                <span>{problem.platform.name}</span>
                {problem.platformDifficulty && <span>• {problem.platformDifficulty}</span>}
                <span>•</span>
                <InlineDifficulty
                  value={problem.normalizedDifficulty ?? null}
                  onSave={(v) => updateProblem.mutateAsync({ id: problem.id, normalizedDifficulty: v ?? undefined })}
                />
              </div>
              <a
                href={problem.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:underline"
              >
                {problem.url}
              </a>
              <InlineEditText
                label="Summary"
                value={problem.simplifiedStatement ?? ""}
                valueClassName="text-gray-600"
                onSave={(v) => updateProblem.mutateAsync({ id: problem.id, simplifiedStatement: v })}
              />
              <InlineEditText
                label="Notes"
                value={problem.notes ?? ""}
                valueClassName="text-gray-500"
                onSave={(v) => updateProblem.mutateAsync({ id: problem.id, notes: v })}
              />
              <InlineDrillEditor
                drillType={(problem.drillType as "mindsolve" | "implement" | null) ?? null}
                drillNotes={problem.drillNotes ?? null}
                onSave={({ drillType, drillNotes }) =>
                  updateProblem.mutateAsync({ id: problem.id, drillType, drillNotes })
                }
              />
              <div className="flex flex-wrap gap-1 mt-2">
                {problem.tags.map((pt: any) => (
                  <InlineTagEditor
                    key={pt.tag.id}
                    pt={pt as ProblemTagRow}
                    allTags={problem.tags as ProblemTagRow[]}
                    onChange={(tags) => updateProblem.mutateAsync({ id: problem.id, tags })}
                    onRemove={(tags) => updateProblem.mutateAsync({ id: problem.id, tags })}
                  />
                ))}
              </div>
              {problem.solutions.length > 0 && (
                <div className="mt-3 space-y-1">
                  <h4 className="text-xs font-semibold text-gray-600">Solutions:</h4>
                  {problem.solutions.map((solution: any) => (
                    <div 
                      key={solution.id} 
                      className="flex items-center gap-2 text-xs bg-gray-50 rounded px-2 py-1"
                    >
                      <span className="font-medium text-gray-700">
                        {solution.language === 'Cpp' ? 'C++' : solution.language}
                      </span>
                      <div className="flex gap-2">
                        {solution.githubUrl && (
                          <a
                            href={solution.githubUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-700"
                          >
                            GitHub →
                          </a>
                        )}
                        {solution.submissionUrl && (
                          <>
                            {solution.githubUrl && <span className="text-gray-300">|</span>}
                            <a
                              href={solution.submissionUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-green-600 hover:text-green-700"
                            >
                              Submission →
                            </a>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="ml-4 flex gap-2">
              <button
                onClick={() => onEdit(problem.id)}
                className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded"
              >
                Edit
              </button>
              <button
                onClick={() => {
                  if (confirm("Delete this problem?")) {
                    deleteProblem.mutate({ id: problem.id });
                  }
                }}
                className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
        {editingProblem === problem.id && (
          <div className="border-t border-b border-blue-200 bg-blue-50/30">
            <EditProblemForm problemId={problem.id} onClose={onCloseEdit} />
          </div>
        )}
        </div>
      ))}
      <Pager />
    </div>
  );
}

function EditProblemForm({ problemId, onClose }: { problemId: string; onClose: () => void }) {
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
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow space-y-3">
      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Name *</label>
        <input
          type="text"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Slug *</label>
        <input
          type="text"
          required
          value={formData.slug}
          onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          rows={2}
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
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow space-y-3">
      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Name *</label>
        <input
          type="text"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Slug *</label>
        <input
          type="text"
          required
          value={formData.slug}
          onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          rows={2}
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
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow space-y-3">
      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Name *</label>
        <input
          type="text"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Slug *</label>
        <input
          type="text"
          required
          value={formData.slug}
          onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
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
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow space-y-3">
      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Name *</label>
        <input
          type="text"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Slug *</label>
        <input
          type="text"
          required
          value={formData.slug}
          onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
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
        <>
          <TagHierarchyFlow tags={tags || []} hierarchies={hierarchies} />
          <TagHierarchyList tags={tags || []} hierarchies={hierarchies} />
        </>
      )}
    </div>
  );
}

function TagHierarchyList({ tags, hierarchies }: { tags: any[]; hierarchies: any[] }) {
  const utils = trpc.useUtils();
  const deleteHierarchy = trpc.tagParent.delete.useMutation({
    onSuccess: () => {
      utils.tagParent.list.invalidate();
    },
  });

  const handleDelete = (childTagId: string, parentTagId: string) => {
    const childTag = tags.find(t => t.id === childTagId);
    const parentTag = tags.find(t => t.id === parentTagId);
    
    if (childTag && parentTag && confirm(`Remove "${childTag.name}" as a child of "${parentTag.name}"?`)) {
      deleteHierarchy.mutate({ childTagId, parentTagId });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow mt-6">
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">All Connections</h3>
        <p className="text-sm text-gray-600 mt-1">
          {hierarchies.length} relationship{hierarchies.length !== 1 ? 's' : ''}
        </p>
      </div>
      <div className="divide-y divide-gray-200">
        {hierarchies.map((rel) => {
          const parentTag = tags.find(t => t.id === rel.parent_tag_id);
          const childTag = tags.find(t => t.id === rel.child_tag_id);
          
          if (!parentTag || !childTag) return null;
          
          return (
            <div key={`${rel.parent_tag_id}-${rel.child_tag_id}`} className="p-4 flex items-center justify-between hover:bg-gray-50">
              <div className="flex items-center gap-3">
                <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded">
                  {parentTag.name}
                </span>
                <span className="text-gray-400">→</span>
                <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded">
                  {childTag.name}
                </span>
              </div>
              <button
                onClick={() => handleDelete(rel.child_tag_id, rel.parent_tag_id)}
                className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded-md font-medium transition-colors"
                disabled={deleteHierarchy.isPending}
              >
                {deleteHierarchy.isPending ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          );
        })}
      </div>
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
        label: '✕ Delete',
        labelStyle: { 
          fill: '#DC2626', 
          fontWeight: 700,
          fontSize: 14,
          cursor: 'pointer',
        },
        labelBgStyle: { 
          fill: '#FEE2E2',
          fillOpacity: 1,
          rx: 4,
          ry: 4,
        },
        labelBgPadding: [8, 8] as [number, number],
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
    <div className="bg-white rounded-lg shadow p-4" style={{ height: '600px' }}>
      <div className="mb-3">
        <p className="text-sm text-gray-600">
          Click the <span className="text-red-600 font-bold">✕</span> on any connection to remove it
        </p>
      </div>
      <div style={{ height: 'calc(100% - 40px)' }}>
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
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow space-y-3">
      <div>
        <label className="block text-xs font-semibold text-gray-900 mb-1">Child Tag *</label>
        <select
          required
          value={formData.childTagId}
          onChange={(e) => setFormData({ ...formData, childTagId: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
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
        <label className="block text-xs font-semibold text-gray-900 mb-1">Parent Tag *</label>
        <select
          required
          value={formData.parentTagId}
          onChange={(e) => setFormData({ ...formData, parentTagId: e.target.value })}
          className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
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

