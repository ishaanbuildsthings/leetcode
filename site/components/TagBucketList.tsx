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
  githubStars: number;
}

function difficultyColor(d: number): string {
  if (d <= 2) return "bg-emerald-100 text-emerald-700";
  if (d <= 4) return "bg-amber-100 text-amber-700";
  if (d <= 6) return "bg-orange-100 text-orange-700";
  if (d <= 8) return "bg-red-100 text-red-700";
  return "bg-red-200 text-red-800";
}

function platformDifficultyColor(d: string | null): string {
  if (!d) return "text-gray-500";
  const lower = d.toLowerCase();
  if (lower === "easy") return "text-emerald-600";
  if (lower === "medium") return "text-amber-600";
  if (lower === "hard") return "text-red-600";
  return "text-gray-600";
}

export function TagBucketList({ sections, githubStars }: TagBucketListProps) {
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
    <main>
      {/* Hero */}
      <div className="bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 border-b border-amber-100">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <div className="flex flex-col md:flex-row md:items-center gap-10">
            {/* Solved count card */}
            <div className="flex-shrink-0 rounded-2xl bg-white shadow-lg border border-amber-200/80 px-10 py-8 text-center">
              <p className="text-5xl font-extrabold text-orange-600 tracking-tight">
                4,000+
              </p>
              <p className="mt-1.5 text-sm font-semibold uppercase tracking-wide text-gray-500">
                problems solved
              </p>
            </div>

            {/* Explanation */}
            <div className="max-w-lg">
              <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
                Learn LeetCode the right way
              </h1>
              <p className="mt-4 text-lg leading-relaxed text-gray-600">
                I solved over 4,000 LeetCode problems. I picked the best ones
                and organized them by pattern so you can learn the techniques
                that actually matter.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Open source + templates bar */}
      <div className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-5 flex flex-wrap items-center gap-x-6 gap-y-3 text-sm">
          <p className="text-gray-600">
            All code for this website and solutions is{" "}
            <a
              href="https://github.com/ishaanbuildsthings/leetcode"
              target="_blank"
              rel="noopener noreferrer"
              className="font-semibold text-gray-900 underline decoration-orange-300 underline-offset-2 hover:decoration-orange-500 transition-colors"
            >
              open source on GitHub
            </a>
            <span className="ml-1.5 inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-800">
              {githubStars > 0
                ? `${githubStars.toLocaleString()} stars`
                : "240+ stars"}
            </span>
          </p>
          <span className="hidden sm:inline text-gray-300">|</span>
          <a
            href="https://github.com/ishaanbuildsthings/leetcode/tree/main/templates"
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-orange-600 hover:text-orange-700 transition-colors"
          >
            Competitive programming templates
          </a>
        </div>
      </div>

      {/* Practice sections */}
      <div className="bg-gray-50 pb-16">
        <div className="mx-auto max-w-6xl px-6 pt-10">
          <h2 className="mb-6 text-xl font-bold text-gray-900">
            Recommended Practice
          </h2>

          <div className="space-y-2">
            {sections.map((section) => {
              const isOpen = openSlugs.has(section.slug);

              return (
                <div
                  key={section.slug}
                  className={`rounded-lg border bg-white transition-all ${
                    isOpen
                      ? "border-l-[3px] border-l-orange-400 border-gray-200 shadow-sm"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <button
                    onClick={() => toggle(section.slug)}
                    className="flex w-full items-center justify-between px-5 py-4 text-left transition-colors hover:bg-gray-50"
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className={`w-4 text-sm ${
                          isOpen ? "text-orange-500" : "text-gray-400"
                        }`}
                      >
                        {isOpen ? "\u25BE" : "\u25B8"}
                      </span>
                      <span className="font-semibold text-gray-900">
                        {section.name}
                      </span>
                      <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
                        {section.problems.length} problem
                        {section.problems.length !== 1 ? "s" : ""}
                      </span>
                    </div>
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
                            className={`flex items-center gap-4 px-5 py-3 transition-colors hover:bg-gray-50 ${
                              i > 0 ? "border-t border-gray-50" : ""
                            }`}
                          >
                            {/* Difficulty badge */}
                            <div className="flex-shrink-0">
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

                            {/* Title */}
                            <div className="min-w-0 flex-1 flex items-center gap-2">
                              <a
                                href={problem.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="font-medium text-gray-900 transition-colors hover:text-orange-600"
                              >
                                {problem.title}
                              </a>
                              {problem.isGreatProblem && (
                                <span
                                  className="text-amber-500"
                                  title="Great Problem"
                                >
                                  *
                                </span>
                              )}
                            </div>

                            {/* Platform difficulty */}
                            {problem.platformDifficulty && (
                              <span
                                className={`flex-shrink-0 text-sm font-medium ${platformDifficultyColor(
                                  problem.platformDifficulty
                                )}`}
                              >
                                {problem.platformDifficulty}
                              </span>
                            )}

                            {/* Links */}
                            <div className="flex-shrink-0 flex items-center gap-3">
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
                                      className="text-xs font-medium text-gray-500 transition-colors hover:text-gray-900"
                                    >
                                      GitHub
                                    </a>
                                  )}
                                  {sol.submissionUrl && (
                                    <a
                                      href={sol.submissionUrl}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-xs font-medium text-emerald-600 transition-colors hover:text-emerald-700"
                                    >
                                      Submission
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
        </div>
      </div>
    </main>
  );
}
