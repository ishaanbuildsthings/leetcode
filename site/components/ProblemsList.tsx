"use client";

import Link from "next/link";
import type { IProblemWithRelations } from "@/lib/transforms";
import { useAuth } from "@/contexts/AuthContext";

const displayLanguage = (lang: string) => {
  return lang === "Cpp" ? "C++" : lang;
};

interface ProblemsListProps {
  problems: IProblemWithRelations[];
  title?: string;
  description?: string;
  activeNav?: "mindsolves" | "implements" | null;
}

export function ProblemsList({ problems, title = "Problems", description = "A curated list of coding problems", activeNav = null }: ProblemsListProps) {
  const { isAdmin } = useAuth();
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-gray-900">
            LeetCode Tracker
          </Link>
          
          <div className="flex gap-4">
            <Link 
              href="/mindsolves" 
              className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                activeNav === "mindsolves"
                  ? "bg-purple-600 text-white hover:bg-purple-700"
                  : "text-gray-700 hover:text-gray-900"
              }`}
            >
              Mindsolves
            </Link>
            <Link 
              href="/implements" 
              className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                activeNav === "implements"
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : "text-gray-700 hover:text-gray-900"
              }`}
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
          <h1 className="text-4xl font-bold text-gray-900 mb-2">{title}</h1>
          <p className="text-gray-600">{description}</p>
        </div>

        {problems.length > 0 ? (
          <div className="grid gap-4">
            {problems.map((problem) => (
              <div 
                key={problem.id} 
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
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
                          <span>•</span>
                          <span>{problem.platformDifficulty}</span>
                        </>
                      )}
                      {problem.normalizedDifficulty && (
                        <>
                          <span>•</span>
                          <span className="font-medium text-blue-600">{problem.normalizedDifficulty}/10</span>
                        </>
                      )}
                      {problem.isGreatProblem && (
                        <>
                          <span>•</span>
                          <span className="text-yellow-600 font-medium">⭐ Great Problem</span>
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
                            {pt.isInstructive === true && '📚 '}
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
                            {problem.drillType === 'mindsolve' ? '🧠 Mindsolve' : '💻 Implement'}
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
                                    className="text-green-600 hover:text-green-700 font-medium"
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

                    <div className="flex gap-3">
                      <a 
                        href={problem.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                      >
                        View Problem →
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

