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
  stats: {
    totalProblems: number;
    githubStars: number;
  };
}

function difficultyColor(d: number): string {
  if (d <= 2) return "bg-green-100 text-green-700";
  if (d <= 4) return "bg-yellow-100 text-yellow-700";
  if (d <= 6) return "bg-orange-100 text-orange-700";
  if (d <= 8) return "bg-red-100 text-red-700";
  return "bg-red-200 text-red-800";
}

function platformDifficultyColor(d: string | null): string {
  if (!d) return "text-gray-500";
  const lower = d.toLowerCase();
  if (lower === "easy") return "text-green-600";
  if (lower === "medium") return "text-yellow-600";
  if (lower === "hard") return "text-red-600";
  return "text-gray-600";
}

function avgDifficulty(problems: IProblemWithRelations[], slug: string): string {
  const diffs = problems
    .map((p) => p.tags.find((t) => t.tag.slug === slug)?.tagDifficulty)
    .filter((d): d is number => d != null);
  if (diffs.length === 0) return "\u2014";
  return (diffs.reduce((a, b) => a + b, 0) / diffs.length).toFixed(1);
}

export function TagBucketList({ sections, stats }: TagBucketListProps) {
  const [openSlugs, setOpenSlugs] = useState<Set<string>>(new Set());

  const toggle = (slug: string) => {
    setOpenSlugs((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) next.delete(slug);
      else next.add(slug);
      return next;
    });
  };

  return (
    <main className="mx-auto max-w-5xl px-6 py-12">
      {/* Hero */}
      <div className="mb-12">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
          LeetCode Solutions &amp; Patterns
        </h1>
        <p className="mt-2 text-lg text-gray-500">
          4000+ problems solved. Curated practice sets organized by technique.
        </p>

        <div className="mt-8 flex gap-8">
          <div>
            <p className="text-2xl font-bold text-gray-900">
              {stats.totalProblems.toLocaleString()}+
            </p>
            <p className="text-sm text-gray-500">problems solved</p>
          </div>
          {stats.githubStars > 0 && (
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {stats.githubStars.toLocaleString()}
              </p>
              <p className="text-sm text-gray-500">GitHub stars</p>
            </div>
          )}
          <div>
            <p className="text-2xl font-bold text-gray-900">
              {sections.length}
            </p>
            <p className="text-sm text-gray-500">topics covered</p>
          </div>
        </div>
      </div>

      {/* Divider */}
      <hr className="mb-8 border-gray-200" />

      {/* Section heading */}
      <h2 className="mb-4 text-lg font-semibold text-gray-900">
        Recommended Practice
      </h2>

      {/* Accordion sections */}
      <div className="space-y-2">
        {sections.map((section) => {
          const isOpen = openSlugs.has(section.slug);
          const avg = avgDifficulty(section.problems, section.slug);

          return (
            <div
              key={section.slug}
              className={`rounded-lg border bg-white ${
                isOpen
                  ? "border-l-2 border-l-orange-400 border-gray-200"
                  : "border-gray-200"
              }`}
            >
              <button
                onClick={() => toggle(section.slug)}
                className="flex w-full items-center justify-between px-5 py-4 text-left transition-colors hover:bg-gray-50"
              >
                <div className="flex items-center gap-3">
                  <span className="w-4 text-sm text-gray-400">
                    {isOpen ? "\u25BE" : "\u25B8"}
                  </span>
                  <span className="font-semibold text-gray-900">
                    {section.name}
                  </span>
                  <span className="text-sm text-gray-500">
                    {section.problems.length} problem
                    {section.problems.length !== 1 ? "s" : ""}
                  </span>
                </div>
                <span className="text-sm text-gray-500">avg {avg}/10</span>
              </button>

              {isOpen && section.problems.length > 0 && (
                <div className="border-t border-gray-100">
                  {section.problems.map((problem, i) => {
                    const tagDiff = problem.tags.find(
                      (t) => t.tag.slug === section.slug
                    )?.tagDifficulty;

                    return (
                      <div
                        key={problem.id}
                        className={`flex items-start gap-4 px-5 py-3 transition-colors hover:bg-gray-50 ${
                          i > 0 ? "border-t border-gray-50" : ""
                        }`}
                      >
                        {/* Difficulty badge */}
                        <div className="flex-shrink-0 pt-0.5">
                          {tagDiff != null ? (
                            <span
                              className={`inline-block w-12 rounded py-0.5 text-center text-xs font-bold ${difficultyColor(
                                tagDiff
                              )}`}
                            >
                              {tagDiff}/10
                            </span>
                          ) : (
                            <span className="inline-block w-12 text-center text-xs text-gray-400">
                              {"\u2014"}
                            </span>
                          )}
                        </div>

                        {/* Main content */}
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <a
                              href={problem.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="font-medium text-gray-900 transition-colors hover:text-blue-600"
                            >
                              {problem.title}
                            </a>
                            {problem.isGreatProblem && (
                              <span
                                className="text-yellow-500"
                                title="Great Problem"
                              >
                                *
                              </span>
                            )}
                          </div>
                          <div className="mt-1 flex items-center gap-3 text-sm">
                            {problem.platformDifficulty && (
                              <span
                                className={`font-medium ${platformDifficultyColor(
                                  problem.platformDifficulty
                                )}`}
                              >
                                {problem.platformDifficulty}
                              </span>
                            )}
                            {problem.simplifiedStatement && (
                              <span className="truncate text-gray-500">
                                {problem.simplifiedStatement}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Links */}
                        <div className="flex flex-shrink-0 items-center gap-2 pt-0.5">
                          {problem.solutions.map((sol) => (
                            <div
                              key={sol.id}
                              className="flex items-center gap-1.5"
                            >
                              {sol.githubUrl && (
                                <a
                                  href={sol.githubUrl}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-xs font-medium text-gray-500 transition-colors hover:text-gray-900"
                                  title="GitHub"
                                >
                                  GitHub
                                </a>
                              )}
                              {sol.submissionUrl && (
                                <a
                                  href={sol.submissionUrl}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-xs font-medium text-green-600 transition-colors hover:text-green-700"
                                  title="Submission"
                                >
                                  Sub
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
                <div className="border-t border-gray-100 px-5 py-4 text-sm text-gray-400">
                  No problems in this section yet.
                </div>
              )}
            </div>
          );
        })}
      </div>
    </main>
  );
}
