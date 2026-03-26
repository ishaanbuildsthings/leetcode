"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { topics } from "@/lib/interview-prep-data";
import type { Problem } from "@/lib/interview-prep-data";

type Selection = { type: "overview" } | { type: "problem"; index: number };

export default function TopicDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const topic = topics.find((t) => t.slug === slug);
  const [selection, setSelection] = useState<Selection>({ type: "overview" });
  const [expanded, setExpanded] = useState(false);

  if (!topic) {
    return (
      <main className="flex min-h-[60vh] items-center justify-center">
        <p className="text-muted-foreground">Topic not found.</p>
      </main>
    );
  }


  const easy = topic.problemList.filter((p) => p.difficulty === "easy");
  const medium = topic.problemList.filter((p) => p.difficulty === "medium");
  const hard = topic.problemList.filter((p) => p.difficulty === "hard");

  const VISIBLE_LIMIT = 8;
  const allProblems = topic.problemList;
  const showExpand = allProblems.length > VISIBLE_LIMIT && !expanded;
  const hiddenCount = allProblems.length - VISIBLE_LIMIT;

  // For prev/next navigation
  const currentProblemIndex =
    selection.type === "problem" ? selection.index : -1;

  function difficultyColor(d: Problem["difficulty"]) {
    if (d === "easy") return "bg-green-100 text-green-700";
    if (d === "medium") return "bg-amber-100 text-amber-700";
    return "bg-red-100 text-red-700";
  }

  function renderSidebarGroup(
    label: string,
    problems: Problem[],
    globalOffset: number
  ) {
    if (problems.length === 0) return null;
    // Check if all problems in this group are hidden
    const groupIndices = problems.map((_, i) => {
      const globalIdx = allProblems.indexOf(problems[i]);
      return globalIdx;
    });

    return (
      <div key={label}>
        <p className="mb-1 mt-4 px-3 font-[family-name:var(--font-dm-sans)] text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
          {label}
        </p>
        {problems.map((problem) => {
          const globalIdx = allProblems.indexOf(problem);
          if (!expanded && globalIdx >= VISIBLE_LIMIT) return null;
          const isActive =
            selection.type === "problem" && selection.index === globalIdx;
          return (
            <button
              key={problem.id}
              onClick={() =>
                setSelection({ type: "problem", index: globalIdx })
              }
              className={`flex w-full items-center gap-2 rounded-md px-3 py-1.5 text-left font-[family-name:var(--font-dm-sans)] text-sm transition-colors ${
                isActive
                  ? "border-l-2 border-primary bg-[#f0f7f4] text-primary"
                  : "text-foreground hover:bg-muted"
              }`}
            >
              <span className="flex h-4 w-4 flex-shrink-0 items-center justify-center rounded border border-border bg-white" />
              <span className="truncate">
                {problem.id}. {problem.name}
              </span>
            </button>
          );
        })}
      </div>
    );
  }

  return (
    <div className="flex gap-0 bg-background/85 backdrop-blur-md min-h-screen">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 border-r border-border px-4 py-6">
        <Link
          href="/interview-prep"
          className="font-[family-name:var(--font-dm-sans)] text-sm font-medium text-primary hover:text-primary/80"
        >
          &larr; All topics
        </Link>

        <h2 className="mt-4 font-[family-name:var(--font-dm-sans)] text-lg font-bold text-foreground">
          {topic.name}
        </h2>
        <p className="font-[family-name:var(--font-dm-sans)] text-xs text-muted-foreground">
          {topic.problems} problems &middot; 0 completed
        </p>

        {/* Overview */}
        <p className="mb-1 mt-6 px-3 font-[family-name:var(--font-dm-sans)] text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
          Overview
        </p>
        <button
          onClick={() => setSelection({ type: "overview" })}
          className={`w-full rounded-md px-3 py-1.5 text-left font-[family-name:var(--font-dm-sans)] text-sm transition-colors ${
            selection.type === "overview"
              ? "border-l-2 border-primary bg-[#f0f7f4] text-primary"
              : "text-foreground hover:bg-muted"
          }`}
        >
          {topic.overviewTitle}
        </button>

        {/* Problem list by difficulty */}
        {renderSidebarGroup("Easy", easy, 0)}
        {renderSidebarGroup("Medium", medium, easy.length)}
        {renderSidebarGroup("Hard", hard, easy.length + medium.length)}

        {showExpand && (
          <button
            onClick={() => setExpanded(true)}
            className="mt-2 px-3 font-[family-name:var(--font-dm-sans)] text-xs text-muted-foreground hover:text-foreground"
          >
            + {hiddenCount} more
          </button>
        )}

        {/* Progress */}
        <div className="mt-8 border-t border-border pt-4">
          <div className="h-1 w-full rounded-full bg-border">
            <div
              className="h-1 rounded-full bg-primary"
              style={{ width: "0%" }}
            />
          </div>
          <p className="mt-2 font-[family-name:var(--font-dm-sans)] text-xs text-muted-foreground">
            0 of {topic.problems} complete
          </p>
        </div>
      </aside>

      {/* Main content */}
      <main className="mx-auto flex-1 max-w-5xl px-10 py-6">
        {selection.type === "overview" ? (
          <>
            <h1 className="font-[family-name:var(--font-playfair)] text-2xl font-bold text-foreground">
              {topic.overviewTitle}
            </h1>
            <p className="mt-2 font-[family-name:var(--font-dm-sans)] text-base text-muted-foreground">
              {topic.overviewSubtitle}
            </p>

            {/* Video placeholder */}
            <div className="mt-8 flex aspect-video w-full items-center justify-center rounded-xl border border-border bg-white">
              <div className="flex flex-col items-center gap-2">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                  <svg
                    className="h-5 w-5 text-primary"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>
                <span className="font-[family-name:var(--font-dm-sans)] text-sm text-muted-foreground">
                  Video embed
                </span>
              </div>
            </div>

            {/* Notes */}
            <h2 className="mt-10 font-[family-name:var(--font-playfair)] text-xl font-bold text-foreground">
              Notes
            </h2>
            <div className="mt-4 space-y-4">
              {topic.notes.map((note) => (
                <div
                  key={note.title}
                  className="rounded-xl border border-border bg-white p-5"
                >
                  <h3 className="font-[family-name:var(--font-dm-sans)] text-sm font-bold text-foreground">
                    {note.title}
                  </h3>
                  <p className="mt-1 font-[family-name:var(--font-dm-sans)] text-sm text-muted-foreground">
                    {note.description}
                  </p>
                </div>
              ))}
            </div>

            {/* Ready to practice banner */}
            <div className="mt-8 flex items-center justify-between rounded-xl bg-[#E1F5EE] p-5">
              <div>
                <p className="font-[family-name:var(--font-dm-sans)] text-sm font-bold text-primary">
                  Ready to practice?
                </p>
                <p className="font-[family-name:var(--font-dm-sans)] text-sm text-muted-foreground">
                  Start with {allProblems[0]?.id}. {allProblems[0]?.name} in the
                  sidebar.
                </p>
              </div>
              <button
                onClick={() =>
                  setSelection({ type: "problem", index: 0 })
                }
                className="font-[family-name:var(--font-dm-sans)] text-sm font-semibold text-primary hover:text-primary/80"
              >
                Start first problem &rarr;
              </button>
            </div>

            {/* Discord */}
            <p className="mt-6 font-[family-name:var(--font-dm-sans)] text-sm text-muted-foreground">
              Questions about {topic.name.toLowerCase()}?{" "}
              <a
                href="https://discord.gg/HYqgVAvC"
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-foreground underline underline-offset-4 hover:text-primary"
              >
                Ask in Discord &rarr;
              </a>
            </p>
          </>
        ) : (
          <>
            {/* Problem view */}
            {(() => {
              const problem = allProblems[currentProblemIndex];
              if (!problem) return null;
              return (
                <>
                  <div className="flex items-center gap-3">
                    <h1 className="font-[family-name:var(--font-playfair)] text-2xl font-bold text-foreground">
                      {problem.id}. {problem.name}
                    </h1>
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${difficultyColor(problem.difficulty)}`}
                    >
                      {problem.difficulty}
                    </span>
                  </div>

                  <a
                    href={`https://leetcode.com/problems/${problem.name.toLowerCase().replace(/\s+/g, "-")}/`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 inline-block font-[family-name:var(--font-dm-sans)] text-sm text-primary underline underline-offset-4 hover:text-primary/80"
                  >
                    Open on LeetCode &rarr;
                  </a>

                  {/* Video placeholder */}
                  <div className="mt-8 flex aspect-video w-full items-center justify-center rounded-xl border border-border bg-white">
                    <div className="flex flex-col items-center gap-2">
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                        <svg
                          className="h-5 w-5 text-primary"
                          fill="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path d="M8 5v14l11-7z" />
                        </svg>
                      </div>
                      <span className="font-[family-name:var(--font-dm-sans)] text-sm text-muted-foreground">
                        Video walkthrough coming soon
                      </span>
                    </div>
                  </div>

                  {/* Key insight */}
                  <h2 className="mt-10 font-[family-name:var(--font-playfair)] text-xl font-bold text-foreground">
                    Key insight
                  </h2>
                  <div className="mt-4 rounded-xl border border-border bg-white p-5">
                    <p className="font-[family-name:var(--font-dm-sans)] text-sm text-muted-foreground">
                      Detailed walkthrough and key insights coming soon.
                    </p>
                  </div>

                  {/* Prev / Next */}
                  <div className="mt-8 flex items-center justify-between">
                    {currentProblemIndex > 0 ? (
                      <button
                        onClick={() =>
                          setSelection({
                            type: "problem",
                            index: currentProblemIndex - 1,
                          })
                        }
                        className="font-[family-name:var(--font-dm-sans)] text-sm font-medium text-foreground hover:text-primary"
                      >
                        &larr; Previous
                      </button>
                    ) : (
                      <span />
                    )}
                    {currentProblemIndex < allProblems.length - 1 ? (
                      <button
                        onClick={() =>
                          setSelection({
                            type: "problem",
                            index: currentProblemIndex + 1,
                          })
                        }
                        className="font-[family-name:var(--font-dm-sans)] text-sm font-medium text-foreground hover:text-primary"
                      >
                        Next &rarr;
                      </button>
                    ) : (
                      <span />
                    )}
                  </div>

                  {/* Discord */}
                  <p className="mt-6 font-[family-name:var(--font-dm-sans)] text-sm text-muted-foreground">
                    Stuck on this problem?{" "}
                    <a
                      href="https://discord.gg/HYqgVAvC"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-foreground underline underline-offset-4 hover:text-primary"
                    >
                      Ask in Discord &rarr;
                    </a>
                  </p>
                </>
              );
            })()}
          </>
        )}
      </main>
    </div>
  );
}
