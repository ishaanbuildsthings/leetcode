"use client";

import { useState } from "react";
import type { IProblemWithRelations } from "@/lib/transforms";

interface TagSection {
  slug: string;
  name: string;
  problems: IProblemWithRelations[];
}

interface TagBucketListProps {
  sections: TagSection[];
}

function difficultyColor(d: number): string {
  if (d <= 2) return "bg-emerald-100 text-emerald-700";
  if (d <= 4) return "bg-amber-100 text-amber-700";
  if (d <= 6) return "bg-orange-100 text-orange-700";
  if (d <= 8) return "bg-red-100 text-red-700";
  return "bg-red-200 text-red-800";
}

function platformDifficultyColor(d: string | null): string {
  if (!d) return "text-gray-400";
  const lower = d.toLowerCase();
  if (lower === "easy") return "text-emerald-600";
  if (lower === "medium") return "text-amber-600";
  if (lower === "hard") return "text-red-600";
  return "text-gray-600";
}

export function TagBucketList({ sections }: TagBucketListProps) {
  const [openSlugs, setOpenSlugs] = useState<Set<string>>(new Set());

  const toggle = (slug: string) => {
    setOpenSlugs((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) next.delete(slug);
      else next.add(slug);
      return next;
    });
  };

  const totalProblems = sections.reduce(
    (sum, s) => sum + s.problems.length,
    0
  );

  return (
    <main>
      {/* Hero */}
      <div className="bg-gradient-to-br from-rose-50 via-pink-50 to-fuchsia-50 border-b border-rose-100">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <div className="flex flex-col md:flex-row md:items-center gap-10">
            <div className="max-w-lg">
              <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
                Learn LeetCode the right way
              </h1>
              <p className="mt-4 text-lg leading-relaxed text-slate-600">
                I solved over 4,000 LeetCode problems. I picked the best ones
                and organized them by pattern so you can learn the techniques
                that actually matter.
              </p>
              <div className="mt-6 flex flex-wrap items-center gap-4">
                <span className="rounded-full bg-white/80 border border-rose-200 px-4 py-1.5 text-sm font-semibold text-rose-600 shadow-sm">
                  {totalProblems.toLocaleString()} curated problems
                </span>
                <span className="rounded-full bg-white/80 border border-rose-200 px-4 py-1.5 text-sm font-semibold text-rose-600 shadow-sm">
                  {sections.length} patterns
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tag sections */}
      <div className="bg-slate-50 pb-16">
        <div className="mx-auto max-w-6xl px-6 pt-10">
          <h2 className="mb-6 text-xl font-bold text-slate-900">
            All Patterns
          </h2>

          <div className="space-y-2">
            {sections.map((section) => {
              const isOpen = openSlugs.has(section.slug);

              return (
                <div
                  key={section.slug}
                  className={`rounded-xl border bg-white transition-all ${
                    isOpen
                      ? "border-l-[3px] border-l-rose-400 border-rose-200 shadow-md"
                      : "border-gray-200 shadow-sm hover:border-rose-200 hover:shadow-md"
                  }`}
                >
                  <button
                    onClick={() => toggle(section.slug)}
                    className="flex w-full items-center justify-between px-5 py-4 text-left transition-colors hover:bg-rose-50/40 rounded-xl"
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className={`w-4 text-sm transition-transform ${
                          isOpen
                            ? "text-rose-500 rotate-0"
                            : "text-slate-400 rotate-0"
                        }`}
                      >
                        {isOpen ? "\u25BE" : "\u25B8"}
                      </span>
                      <span className="font-semibold text-slate-900">
                        {section.name}
                      </span>
                      <span className="rounded-full bg-rose-50 px-2.5 py-0.5 text-xs font-bold text-rose-600">
                        {section.problems.length}
                      </span>
                    </div>
                  </button>

                  {isOpen && section.problems.length > 0 && (
                    <div className="border-t border-gray-100">
                      {/* Table header */}
                      <div className="flex items-center gap-4 px-5 py-2 text-xs font-semibold uppercase tracking-wide text-slate-400 border-b border-gray-50">
                        <div className="w-16 text-center">Tag Diff</div>
                        <div className="w-16 text-center">Norm Diff</div>
                        <div className="min-w-0 flex-1">Problem</div>
                        <div className="w-20 text-center">Platform</div>
                        <div className="w-16 text-center">Level</div>
                        <div className="w-32 text-right">Links</div>
                      </div>

                      {section.problems.map((problem, i) => {
                        const tagDiff = problem.tags.find(
                          (t) => t.tag.slug === section.slug
                        )?.tagDifficulty;

                        return (
                          <div
                            key={problem.id}
                            className={`flex items-center gap-4 px-5 py-3 transition-colors hover:bg-rose-50/30 ${
                              i > 0 ? "border-t border-gray-50" : ""
                            }`}
                          >
                            {/* Tag difficulty */}
                            <div className="w-16 flex-shrink-0 text-center">
                              {tagDiff != null ? (
                                <span
                                  className={`inline-block w-12 rounded-md py-0.5 text-center text-xs font-bold ${difficultyColor(
                                    tagDiff
                                  )}`}
                                >
                                  {tagDiff}/10
                                </span>
                              ) : (
                                <span className="text-xs text-gray-300">
                                  —
                                </span>
                              )}
                            </div>

                            {/* Normalized difficulty */}
                            <div className="w-16 flex-shrink-0 text-center">
                              {problem.normalizedDifficulty != null ? (
                                <span
                                  className={`inline-block w-12 rounded-md py-0.5 text-center text-xs font-bold ${difficultyColor(
                                    problem.normalizedDifficulty
                                  )}`}
                                >
                                  {problem.normalizedDifficulty}/10
                                </span>
                              ) : (
                                <span className="text-xs text-gray-300">
                                  —
                                </span>
                              )}
                            </div>

                            {/* Title */}
                            <div className="min-w-0 flex-1 flex items-center gap-2">
                              <a
                                href={problem.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="font-medium text-slate-900 transition-colors hover:text-rose-600 truncate"
                              >
                                {problem.title}
                              </a>
                              {problem.isGreatProblem && (
                                <span
                                  className="text-rose-400 flex-shrink-0"
                                  title="Great Problem"
                                >
                                  ★
                                </span>
                              )}
                            </div>

                            {/* Platform */}
                            <div className="w-20 flex-shrink-0 text-center">
                              <span className="text-xs font-medium text-slate-500 capitalize">
                                {problem.platform.name}
                              </span>
                            </div>

                            {/* Platform difficulty */}
                            <div className="w-16 flex-shrink-0 text-center">
                              {problem.platformDifficulty && (
                                <span
                                  className={`text-xs font-semibold ${platformDifficultyColor(
                                    problem.platformDifficulty
                                  )}`}
                                >
                                  {problem.platformDifficulty}
                                </span>
                              )}
                            </div>

                            {/* Links */}
                            <div className="w-32 flex-shrink-0 flex items-center justify-end gap-2">
                              {problem.solutions.map((sol) => (
                                <div
                                  key={sol.id}
                                  className="flex items-center gap-2"
                                >
                                  {sol.githubUrl && (
                                    <a
                                      href={sol.githubUrl}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600 transition-colors hover:bg-rose-100 hover:text-rose-700"
                                    >
                                      Code
                                    </a>
                                  )}
                                  {sol.submissionUrl && (
                                    <a
                                      href={sol.submissionUrl}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="rounded-md bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-600 transition-colors hover:bg-emerald-100 hover:text-emerald-700"
                                    >
                                      AC
                                    </a>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {isOpen && section.problems.length === 0 && (
                    <div className="border-t border-gray-100 px-5 py-4 text-sm text-slate-400">
                      No problems in this section yet.
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </main>
  );
}
