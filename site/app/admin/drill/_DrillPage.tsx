"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { trpc } from "../../providers";
import type { IProblemWithRelations } from "@/lib/transforms";
import {
  InlineEditText,
  InlineDifficulty,
  InlineDrillEditor,
  InlineTagEditor,
  EditProblemForm,
  type ProblemTagRow,
} from "../_components/inline-editors";

type SortKey = "completions" | "lastDrilled" | "random";

type DrillKind = "implement" | "mindsolve";

interface DrillPageProps {
  drillType: DrillKind;
  title: string;
}

const displayLanguage = (lang: string) => (lang === "Cpp" ? "C++" : lang);

function formatRelative(iso: string | null): string {
  if (!iso) return "never";
  const then = new Date(iso).getTime();
  const now = Date.now();
  const secs = Math.max(0, Math.floor((now - then) / 1000));
  if (secs < 60) return `${secs}s ago`;
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  const months = Math.floor(days / 30);
  if (months < 12) return `${months}mo ago`;
  return `${Math.floor(months / 12)}y ago`;
}

function sortProblems(
  problems: IProblemWithRelations[],
  key: SortKey,
  randomOrder: string[]
): IProblemWithRelations[] {
  const copy = [...problems];
  if (key === "completions") {
    copy.sort((a, b) => {
      if (a.drillCompletions !== b.drillCompletions) {
        return a.drillCompletions - b.drillCompletions;
      }
      const aT = a.lastDrilledAt ? new Date(a.lastDrilledAt).getTime() : 0;
      const bT = b.lastDrilledAt ? new Date(b.lastDrilledAt).getTime() : 0;
      return aT - bT;
    });
  } else if (key === "lastDrilled") {
    copy.sort((a, b) => {
      const aT = a.lastDrilledAt ? new Date(a.lastDrilledAt).getTime() : 0;
      const bT = b.lastDrilledAt ? new Date(b.lastDrilledAt).getTime() : 0;
      if (aT !== bT) return aT - bT;
      return a.drillCompletions - b.drillCompletions;
    });
  } else {
    const rank = new Map(randomOrder.map((id, idx) => [id, idx]));
    copy.sort((a, b) => {
      const aR = rank.get(a.id) ?? Number.MAX_SAFE_INTEGER;
      const bR = rank.get(b.id) ?? Number.MAX_SAFE_INTEGER;
      return aR - bR;
    });
  }
  return copy;
}

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function DrillPage({ drillType, title }: DrillPageProps) {
  const [sortKey, setSortKey] = useState<SortKey>("completions");
  const [editingProblem, setEditingProblem] = useState<string | null>(null);
  const [randomOrder, setRandomOrder] = useState<string[]>([]);

  const listQuery = trpc.problem.list.useQuery();
  const utils = trpc.useUtils();

  const markDrilled = trpc.problem.markDrilled.useMutation({
    onSuccess: () => utils.problem.list.invalidate(),
  });
  const undoDrilled = trpc.problem.undoDrilled.useMutation({
    onSuccess: () => utils.problem.list.invalidate(),
  });
  const updateProblem = trpc.problem.update.useMutation({
    onSuccess: () => utils.problem.list.invalidate(),
    onError: (err) => alert(`Failed to update: ${err.message}`),
  });
  const deleteProblem = trpc.problem.delete.useMutation({
    onSuccess: () => utils.problem.list.invalidate(),
  });

  const problems = useMemo(() => {
    const all = listQuery.data ?? [];
    const filtered = all.filter((p) => p.drillType === drillType);
    return sortProblems(filtered, sortKey, randomOrder);
  }, [listQuery.data, sortKey, drillType, randomOrder]);

  const handleShuffle = () => {
    const ids = (listQuery.data ?? [])
      .filter((p) => p.drillType === drillType)
      .map((p) => p.id);
    setRandomOrder(shuffle(ids));
    setSortKey("random");
  };

  const minCompletions =
    problems.length > 0
      ? Math.min(...problems.map((p) => p.drillCompletions))
      : 0;
  const currentRoundTotal = problems.filter(
    (p) => p.drillCompletions === minCompletions
  ).length;
  const currentRoundDone = problems.length - currentRoundTotal;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-6">
          <Link
            href="/admin"
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            ← Admin
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
        </div>

        <div className="mb-6 flex flex-wrap items-center gap-4 text-sm text-gray-700">
          <div>
            Round <span className="font-semibold">{minCompletions + 1}</span> ·{" "}
            <span className="font-semibold">{currentRoundDone}</span> /{" "}
            {problems.length} done this round
          </div>
          <div className="ml-auto flex items-center gap-2">
            <span className="text-gray-500">Sort:</span>
            <button
              onClick={() => setSortKey("completions")}
              className={`px-3 py-1 rounded-md border text-sm ${
                sortKey === "completions"
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
              }`}
            >
              Least drilled
            </button>
            <button
              onClick={() => setSortKey("lastDrilled")}
              className={`px-3 py-1 rounded-md border text-sm ${
                sortKey === "lastDrilled"
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
              }`}
            >
              Oldest last drilled
            </button>
            <button
              onClick={handleShuffle}
              className={`px-3 py-1 rounded-md border text-sm ${
                sortKey === "random"
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
              }`}
              title={sortKey === "random" ? "Reshuffle" : "Random order"}
            >
              {sortKey === "random" ? "🔀 Reshuffle" : "🔀 Random"}
            </button>
          </div>
        </div>

        {listQuery.isLoading ? (
          <div className="text-gray-500">Loading…</div>
        ) : problems.length === 0 ? (
          <div className="text-gray-500">No {drillType}-tagged problems yet.</div>
        ) : (
          <div className="bg-white rounded-lg shadow divide-y">
            {problems.map((p, idx) => {
              const isInCurrentRound = p.drillCompletions === minCompletions;
              const pending =
                (markDrilled.isPending && markDrilled.variables?.id === p.id) ||
                (undoDrilled.isPending && undoDrilled.variables?.id === p.id);
              return (
                <div key={p.id}>
                  <div
                    className={`p-4 hover:bg-gray-50 ${
                      isInCurrentRound ? "" : "opacity-60"
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm text-gray-400 tabular-nums">
                            #{idx + 1}
                          </span>
                          <h3 className="font-semibold text-gray-900">
                            {p.title}
                          </h3>
                          <label
                            className="flex items-center gap-1 cursor-pointer"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <input
                              type="checkbox"
                              checked={p.isGreatProblem}
                              onChange={() =>
                                updateProblem.mutate({
                                  id: p.id,
                                  isGreatProblem: !p.isGreatProblem,
                                })
                              }
                              className="w-3 h-3 text-yellow-600 border-gray-300 rounded"
                            />
                            <span
                              className={`text-xs px-1.5 py-0.5 rounded ${
                                p.isGreatProblem
                                  ? "bg-yellow-100 text-yellow-800"
                                  : "text-gray-600"
                              }`}
                            >
                              Great
                            </span>
                          </label>
                          <label
                            className="flex items-center gap-1 cursor-pointer"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <input
                              type="checkbox"
                              checked={p.isLeetgoat222}
                              onChange={() =>
                                updateProblem.mutate({
                                  id: p.id,
                                  isLeetgoat222: !p.isLeetgoat222,
                                })
                              }
                              className="w-3 h-3 text-blue-600 border-gray-300 rounded"
                            />
                            <span className="text-xs text-gray-600">222</span>
                          </label>
                          <label
                            className="flex items-center gap-1 cursor-pointer"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <input
                              type="checkbox"
                              checked={p.isLeetgoatAdvanced}
                              onChange={() =>
                                updateProblem.mutate({
                                  id: p.id,
                                  isLeetgoatAdvanced: !p.isLeetgoatAdvanced,
                                })
                              }
                              className="w-3 h-3 text-purple-600 border-gray-300 rounded"
                            />
                            <span className="text-xs text-gray-600">Adv</span>
                          </label>
                        </div>

                        <div className="text-sm text-gray-600 mb-2 flex items-center gap-1 flex-wrap">
                          <span>{p.platform.name}</span>
                          {p.platformDifficulty && (
                            <span>• {p.platformDifficulty}</span>
                          )}
                          <span>•</span>
                          <InlineDifficulty
                            value={p.normalizedDifficulty ?? null}
                            onSave={(v) =>
                              updateProblem.mutateAsync({
                                id: p.id,
                                normalizedDifficulty: v ?? undefined,
                              })
                            }
                          />
                          <span>•</span>
                          <span>
                            Drilled{" "}
                            <span className="font-semibold text-gray-900 tabular-nums">
                              {p.drillCompletions}
                            </span>
                            {"× · last "}
                            <span className="text-gray-700">
                              {formatRelative(p.lastDrilledAt)}
                            </span>
                          </span>
                        </div>

                        <a
                          href={p.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 hover:underline"
                        >
                          {p.url}
                        </a>

                        <InlineEditText
                          label="Summary"
                          value={p.simplifiedStatement ?? ""}
                          valueClassName="text-gray-600"
                          onSave={(v) =>
                            updateProblem.mutateAsync({
                              id: p.id,
                              simplifiedStatement: v,
                            })
                          }
                        />
                        <InlineEditText
                          label="Notes"
                          value={p.notes ?? ""}
                          valueClassName="text-gray-500"
                          onSave={(v) =>
                            updateProblem.mutateAsync({
                              id: p.id,
                              notes: v,
                            })
                          }
                        />
                        <InlineDrillEditor
                          drillType={p.drillType as DrillKind | null}
                          drillNotes={p.drillNotes ?? null}
                          onSave={({ drillType: newType, drillNotes }) =>
                            updateProblem.mutateAsync({
                              id: p.id,
                              drillType: newType,
                              drillNotes,
                            })
                          }
                        />

                        <div className="flex flex-wrap gap-1 mt-2">
                          {p.tags.map((pt) => (
                            <InlineTagEditor
                              key={pt.tag.id}
                              pt={pt as ProblemTagRow}
                              allTags={p.tags as ProblemTagRow[]}
                              onChange={(tags) =>
                                updateProblem.mutateAsync({ id: p.id, tags })
                              }
                              onRemove={(tags) =>
                                updateProblem.mutateAsync({ id: p.id, tags })
                              }
                            />
                          ))}
                        </div>

                        {p.solutions.length > 0 && (
                          <div className="mt-3 space-y-1">
                            <h4 className="text-xs font-semibold text-gray-600">
                              Solutions:
                            </h4>
                            {p.solutions.map((solution) => (
                              <div
                                key={solution.id}
                                className="flex items-center gap-2 text-xs bg-gray-50 rounded px-2 py-1"
                              >
                                <span className="font-medium text-gray-700">
                                  {displayLanguage(solution.language)}
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
                                      {solution.githubUrl && (
                                        <span className="text-gray-300">|</span>
                                      )}
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

                      <div className="ml-4 flex flex-col gap-2 shrink-0">
                        <button
                          disabled={pending}
                          onClick={() => markDrilled.mutate({ id: p.id })}
                          className="px-3 py-1.5 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                        >
                          Mark drilled
                        </button>
                        {p.drillCompletions > 0 && (
                          <button
                            disabled={pending}
                            onClick={() => undoDrilled.mutate({ id: p.id })}
                            className="px-3 py-1.5 text-xs rounded-md border border-gray-300 text-gray-600 hover:bg-gray-100 disabled:opacity-50"
                            title="Decrement count"
                          >
                            − Undo
                          </button>
                        )}
                        <button
                          onClick={() => setEditingProblem(p.id)}
                          className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => {
                            if (confirm("Delete this problem?")) {
                              deleteProblem.mutate({ id: p.id });
                            }
                          }}
                          className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                  {editingProblem === p.id && (
                    <div className="border-t border-b border-blue-200 bg-blue-50/30">
                      <EditProblemForm
                        problemId={p.id}
                        onClose={() => setEditingProblem(null)}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
