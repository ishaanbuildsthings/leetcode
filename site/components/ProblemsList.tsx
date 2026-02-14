"use client";

import type { IProblemWithRelations } from "@/lib/transforms";
import { Nav } from "@/components/Nav";

const displayLanguage = (lang: string) => {
  return lang === "Cpp" ? "C++" : lang;
};

interface ProblemsListProps {
  problems: IProblemWithRelations[];
  title?: string;
  description?: string;
  activePath?: string;
}

export function ProblemsList({ problems, title = "Problems", description = "A curated list of coding problems", activePath }: ProblemsListProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Nav activePath={activePath} />

      <main className="max-w-5xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-2">{title}</h1>
          <p className="text-gray-500">{description}</p>
        </div>

        {problems.length > 0 ? (
          <div className="grid gap-4">
            {problems.map((problem) => (
              <div
                key={problem.id}
                className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-sm transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {problem.title}
                    </h3>

                    <div className="flex items-center gap-3 text-sm text-gray-600 mb-3">
                      <span className="font-medium">{problem.platform.name}</span>
                      {problem.platformDifficulty && (
                        <>
                          <span>·</span>
                          <span>{problem.platformDifficulty}</span>
                        </>
                      )}
                      {problem.normalizedDifficulty && (
                        <>
                          <span>·</span>
                          <span className="font-medium text-blue-600">{problem.normalizedDifficulty}/10</span>
                        </>
                      )}
                      {problem.isGreatProblem && (
                        <>
                          <span>·</span>
                          <span className="text-yellow-600 font-medium">Great Problem</span>
                        </>
                      )}
                    </div>

                    {problem.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-3">
                        {problem.tags.map((pt) => (
                          <span
                            key={pt.tag.id}
                            className={`px-3 py-1 rounded-full text-sm font-medium ${
                              pt.isInstructive === true
                                ? 'bg-purple-100 text-purple-700 border border-purple-300'
                                : pt.role === 'core'
                                ? 'bg-blue-100 text-blue-700'
                                : pt.role === 'secondary'
                                ? 'bg-green-100 text-green-700'
                                : pt.role === 'mention'
                                ? 'bg-yellow-100 text-yellow-700'
                                : 'bg-gray-100 text-gray-700'
                            }`}
                          >
                            {pt.tag.name}
                            {pt.role && ` (${pt.role})`}
                            {pt.tagDifficulty && ` ${pt.tagDifficulty}/10`}
                          </span>
                        ))}
                      </div>
                    )}

                    {problem.simplifiedStatement && (
                      <div className="mb-3">
                        <h4 className="text-sm font-semibold text-gray-700 mb-1">Problem Summary:</h4>
                        <p className="text-gray-600 text-sm">{problem.simplifiedStatement}</p>
                      </div>
                    )}

                    {problem.notes && (
                      <div className="mb-3">
                        <h4 className="text-sm font-semibold text-gray-700 mb-1">Notes:</h4>
                        <p className="text-gray-600 text-sm">{problem.notes}</p>
                      </div>
                    )}

                    {problem.drillType && (
                      <div className="mb-3">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="text-sm font-semibold text-gray-700">
                            Drill Type:
                          </h4>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            problem.drillType === 'mindsolve'
                              ? 'bg-purple-100 text-purple-700'
                              : 'bg-blue-100 text-blue-700'
                          }`}>
                            {problem.drillType === 'mindsolve' ? 'Mindsolve' : 'Implement'}
                          </span>
                        </div>
                        {problem.drillNotes && (
                          <p className="text-gray-600 text-sm mt-1">{problem.drillNotes}</p>
                        )}
                      </div>
                    )}

                    {problem.solutions.length > 0 && (
                      <div className="mb-3 space-y-2">
                        <h4 className="text-sm font-semibold text-gray-700">Solutions:</h4>
                        {problem.solutions.map((solution) => (
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
                                  {solution.githubUrl && <span className="text-gray-300">|</span>}
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

                    <div className="flex gap-3">
                      <a
                        href={problem.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                      >
                        View Problem
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">No problems yet. Check back soon!</p>
          </div>
        )}
      </main>
    </div>
  );
}
