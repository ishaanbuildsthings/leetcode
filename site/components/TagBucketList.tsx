"use client";

import { useState } from "react";
import Link from "next/link";
import type { IProblemWithRelations } from "@/lib/transforms";
import { useAuth } from "@/contexts/AuthContext";

interface TagSection {
  slug: string;
  name: string;
  problems: IProblemWithRelations[];
}

interface TagBucketListProps {
  sections: TagSection[];
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
  if (diffs.length === 0) return "—";
  return (diffs.reduce((a, b) => a + b, 0) / diffs.length).toFixed(1);
}

export function TagBucketList({ sections }: TagBucketListProps) {
  const { isAdmin } = useAuth();
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
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-gray-900">
            LeetCode Tracker
          </Link>

          <div className="flex gap-4">
            <Link
              href="/leetcode"
              className="px-4 py-2 rounded-lg transition-colors font-medium bg-orange-600 text-white hover:bg-orange-700"
            >
              LeetCode
            </Link>
            <Link
              href="/mindsolves"
              className="px-4 py-2 rounded-lg transition-colors font-medium text-gray-700 hover:text-gray-900"
            >
              Mindsolves
            </Link>
            <Link
              href="/implements"
              className="px-4 py-2 rounded-lg transition-colors font-medium text-gray-700 hover:text-gray-900"
            >
              Implements
            </Link>
            {isAdmin ? (
              <Link
                href="/admin"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Admin Dashboard
              </Link>
            ) : (
              <Link
                href="/login"
                className="px-4 py-2 text-blue-600 hover:text-blue-700 font-medium"
              >
                Admin Login
              </Link>
            )}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">LeetCode Patterns</h1>
          <p className="text-gray-600">Practice problems organized by technique</p>
        </div>

        <div className="space-y-2">
          {sections.map((section) => {
            const isOpen = openSlugs.has(section.slug);
            const avg = avgDifficulty(section.problems, section.slug);

            return (
              <div key={section.slug} className="bg-white rounded-lg border border-gray-200">
                <button
                  onClick={() => toggle(section.slug)}
                  className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-gray-400 text-sm w-4">
                      {isOpen ? "\u25BE" : "\u25B8"}
                    </span>
                    <span className="font-semibold text-gray-900">{section.name}</span>
                    <span className="text-sm text-gray-500">
                      {section.problems.length} problem{section.problems.length !== 1 ? "s" : ""}
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
                          className={`px-5 py-3 flex items-start gap-4 ${
                            i > 0 ? "border-t border-gray-50" : ""
                          } hover:bg-gray-50 transition-colors`}
                        >
                          {/* Difficulty badge */}
                          <div className="flex-shrink-0 pt-0.5">
                            {tagDiff != null ? (
                              <span
                                className={`inline-block w-12 text-center text-xs font-bold rounded py-0.5 ${difficultyColor(
                                  tagDiff
                                )}`}
                              >
                                {tagDiff}/10
                              </span>
                            ) : (
                              <span className="inline-block w-12 text-center text-xs text-gray-400">
                                —
                              </span>
                            )}
                          </div>

                          {/* Main content */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <a
                                href={problem.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="font-medium text-gray-900 hover:text-blue-600 transition-colors"
                              >
                                {problem.title}
                              </a>
                              {problem.isGreatProblem && (
                                <span className="text-yellow-500" title="Great Problem">
                                  *
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-3 mt-1 text-sm">
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
                                <span className="text-gray-500 truncate">
                                  {problem.simplifiedStatement}
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Links */}
                          <div className="flex-shrink-0 flex items-center gap-2 pt-0.5">
                            {problem.solutions.map((sol) => (
                              <div key={sol.id} className="flex items-center gap-1.5">
                                {sol.githubUrl && (
                                  <a
                                    href={sol.githubUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs font-medium text-gray-500 hover:text-gray-900 transition-colors"
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
                                    className="text-xs font-medium text-green-600 hover:text-green-700 transition-colors"
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
    </div>
  );
}
