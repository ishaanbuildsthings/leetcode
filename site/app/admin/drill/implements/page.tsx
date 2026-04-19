"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { trpc } from "../../../providers";
import type { IProblemWithRelations } from "@/lib/transforms";

type SortKey = "completions" | "lastDrilled";

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
  key: SortKey
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
  } else {
    copy.sort((a, b) => {
      const aT = a.lastDrilledAt ? new Date(a.lastDrilledAt).getTime() : 0;
      const bT = b.lastDrilledAt ? new Date(b.lastDrilledAt).getTime() : 0;
      if (aT !== bT) return aT - bT;
      return a.drillCompletions - b.drillCompletions;
    });
  }
  return copy;
}

export default function ImplementDrillPage() {
  const [sortKey, setSortKey] = useState<SortKey>("completions");

  const listQuery = trpc.problem.list.useQuery();
  const utils = trpc.useUtils();

  const markDrilled = trpc.problem.markDrilled.useMutation({
    onSuccess: () => utils.problem.list.invalidate(),
  });
  const undoDrilled = trpc.problem.undoDrilled.useMutation({
    onSuccess: () => utils.problem.list.invalidate(),
  });

  const problems = useMemo(() => {
    const all = listQuery.data ?? [];
    const implements_ = all.filter((p) => p.drillType === "implement");
    return sortProblems(implements_, sortKey);
  }, [listQuery.data, sortKey]);

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
          <h1 className="text-3xl font-bold text-gray-900">Implement Drills</h1>
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
          </div>
        </div>

        {listQuery.isLoading ? (
          <div className="text-gray-500">Loading…</div>
        ) : problems.length === 0 ? (
          <div className="text-gray-500">No implement-tagged problems yet.</div>
        ) : (
          <div className="grid gap-4">
            {problems.map((p, idx) => {
              const isInCurrentRound = p.drillCompletions === minCompletions;
              const pending =
                (markDrilled.isPending && markDrilled.variables?.id === p.id) ||
                (undoDrilled.isPending && undoDrilled.variables?.id === p.id);
              return (
                <div
                  key={p.id}
                  className={`bg-white rounded-lg border p-6 transition-shadow hover:shadow-sm ${
                    isInCurrentRound
                      ? "border-gray-200"
                      : "border-gray-200 opacity-60"
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-baseline gap-3 mb-2">
                        <span className="text-sm text-gray-400 tabular-nums">
                          #{idx + 1}
                        </span>
                        <h3 className="text-xl font-semibold text-gray-900">
                          {p.title}
                        </h3>
                      </div>

                      <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600 mb-3">
                        <span className="font-medium">{p.platform.name}</span>
                        {p.platformDifficulty && (
                          <>
                            <span>·</span>
                            <span>{p.platformDifficulty}</span>
                          </>
                        )}
                        {p.normalizedDifficulty && (
                          <>
                            <span>·</span>
                            <span className="font-medium text-blue-600">
                              {p.normalizedDifficulty}/10
                            </span>
                          </>
                        )}
                        <span>·</span>
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

                      {p.drillNotes && (
                        <div className="mb-3">
                          <h4 className="text-sm font-semibold text-gray-700 mb-1">
                            Drill Notes:
                          </h4>
                          <p className="text-gray-700 text-sm whitespace-pre-wrap">
                            {p.drillNotes}
                          </p>
                        </div>
                      )}

                      {p.solutions.length > 0 && (
                        <div className="mb-3 space-y-2">
                          <h4 className="text-sm font-semibold text-gray-700">
                            Solutions:
                          </h4>
                          {p.solutions.map((solution) => (
                            <div
                              key={solution.id}
                              className="flex items-center gap-3 text-sm bg-gray-50 rounded-md px-3 py-2"
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
                                    className="text-blue-600 hover:text-blue-700 font-medium"
                                  >
                                    GitHub
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
                                      className="text-green-600 hover:text-green-700 font-medium"
                                    >
                                      Submission
                                    </a>
                                  </>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      <a
                        href={p.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                      >
                        View Problem →
                      </a>
                    </div>

                    <div className="flex flex-col gap-2 shrink-0">
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
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
