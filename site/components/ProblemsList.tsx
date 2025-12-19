"use client";

import Link from "next/link";
import type { IProblemWithRelations } from "@/lib/transforms";
import { useAuth } from "@/contexts/AuthContext";

interface ProblemsListProps {
  problems: IProblemWithRelations[];
}

export function ProblemsList({ problems }: ProblemsListProps) {
  const { isAdmin } = useAuth();
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-gray-900">
            LeetCode Tracker
          </Link>
          
          <div>
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
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Problems</h1>
          <p className="text-gray-600">A curated list of coding problems</p>
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
                            {pt.tagDifficulty && ` ${pt.tagDifficulty}★`}
                          </span>
                        ))}
                      </div>
                    )}

                    {problem.notes && (
                      <p className="text-gray-600 text-sm mb-3">{problem.notes}</p>
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
                      {problem.solutions.length > 0 && (
                        <>
                          <span className="text-gray-300">|</span>
                          <span className="text-sm text-gray-600">
                            {problem.solutions.length} solution{problem.solutions.length > 1 ? 's' : ''}
                          </span>
                        </>
                      )}
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

