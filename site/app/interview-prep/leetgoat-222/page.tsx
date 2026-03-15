import { prisma } from "@/lib/prisma";
import { transformProblemWithRelations } from "@/lib/transforms";
import type { IProblemWithRelations } from "@/lib/transforms";

function GoatRating({ normalizedDifficulty }: { normalizedDifficulty: number | null }) {
  const filled = normalizedDifficulty
    ? Math.min(Math.ceil(normalizedDifficulty / 2), 5)
    : 0;
  const empty = 5 - filled;

  return (
    <span className="inline-flex gap-0.5 text-sm select-none" title={`Difficulty: ${normalizedDifficulty ?? "?"}/10`}>
      {Array.from({ length: filled }).map((_, i) => (
        <span key={`f${i}`}>🐐</span>
      ))}
      {Array.from({ length: empty }).map((_, i) => (
        <span key={`e${i}`} className="opacity-20">🐐</span>
      ))}
    </span>
  );
}

function lcDifficultyColor(difficulty: string | null) {
  switch (difficulty?.toLowerCase()) {
    case "easy": return "text-green-600";
    case "medium": return "text-amber-500";
    case "hard": return "text-red-500";
    default: return "text-muted-foreground";
  }
}

export default async function LeetGoat222Page() {
  const problemsRaw = await prisma.problems.findMany({
    where: { is_leetgoat_222: true },
    include: {
      platforms: true,
      problem_tags: {
        include: { tags: true },
      },
      solutions: true,
    },
    orderBy: { normalized_difficulty: "asc" },
  });

  const problems: IProblemWithRelations[] = problemsRaw.map(transformProblemWithRelations);

  return (
    <main className="flex flex-col items-center px-6 py-12">
      <div className="w-full max-w-5xl">
        <div className="mb-8 text-center">
          <h1 className="font-[family-name:var(--font-playfair)] text-4xl font-bold text-foreground">
            LeetGoat 222{" "}
            <span className="inline-block text-3xl">
              🐐
            </span>
          </h1>
          <p className="mt-3 font-[family-name:var(--font-dm-sans)] text-base text-foreground">
            After solving &gt;3000 problems, these are the 222 questions I recommend to do for passing interviews! &ndash; leetgoat{" "}
            <span className="inline-block animate-[wiggle_1.5s_ease-in-out_infinite]">🐐</span>
          </p>
        </div>

        <div className="rounded-2xl border border-border bg-background/90 shadow-lg backdrop-blur-sm">
          {/* Header row */}
          <div className="flex items-center gap-4 px-5 py-2.5 border-b border-border bg-muted/50">
            <div className="w-32 shrink-0 font-[family-name:var(--font-dm-sans)] text-[11px] font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
              <span>LeetGoat Difficulty</span>
              <span className="relative group cursor-help">
                <svg className="w-3.5 h-3.5 text-muted-foreground/60" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 16v-4M12 8h.01" />
                </svg>
                <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 rounded-lg bg-foreground text-background text-[11px] font-normal normal-case tracking-normal px-3 py-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 shadow-lg">
                  I found the LeetCode difficulties inaccurate, so I gave my own ratings!
                </span>
              </span>
            </div>
            <div className="w-16 shrink-0 font-[family-name:var(--font-dm-sans)] text-[11px] font-semibold uppercase tracking-wider text-muted-foreground text-center">
              LC Difficulty
            </div>
            <div className="flex-1 font-[family-name:var(--font-dm-sans)] text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Problem
            </div>
            <div className="w-24 shrink-0 font-[family-name:var(--font-dm-sans)] text-[11px] font-semibold uppercase tracking-wider text-muted-foreground text-center">
              Topics
            </div>
            <div className="w-12 shrink-0 font-[family-name:var(--font-dm-sans)] text-[11px] font-semibold uppercase tracking-wider text-muted-foreground text-right">
              Code
            </div>
          </div>

          {/* Problem rows */}
          <div className="divide-y divide-border/60">
            {problems.map((problem) => {
              const coreTags = problem.tags
                .filter((t) => t.role === "core")
                .map((t) => t.tag.name);
              const githubUrl = problem.solutions.find((s) => s.githubUrl)?.githubUrl;

              return (
                <div
                  key={problem.id}
                  className="flex items-center gap-4 px-5 py-3 hover:bg-muted/40 transition-colors"
                >
                  <div className="w-32 shrink-0">
                    <GoatRating normalizedDifficulty={problem.normalizedDifficulty} />
                  </div>

                  <div className={`w-16 shrink-0 text-center font-[family-name:var(--font-dm-sans)] text-xs font-semibold ${lcDifficultyColor(problem.platformDifficulty)}`}>
                    {problem.platformDifficulty || "—"}
                  </div>

                  <div className="flex-1 min-w-0">
                    <a
                      href={problem.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-[family-name:var(--font-dm-sans)] text-sm font-medium text-foreground hover:text-primary transition-colors"
                    >
                      {problem.title}
                    </a>
                  </div>

                  <div className="w-24 shrink-0 flex flex-wrap gap-1 justify-center">
                    {coreTags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-block rounded-full bg-muted px-2 py-0.5 text-[11px] text-muted-foreground font-medium"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  <div className="w-12 shrink-0 flex justify-end">
                    {githubUrl && (
                      <a
                        href={githubUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-foreground transition-colors"
                        title="View solution on GitHub"
                      >
                        <svg
                          className="w-5 h-5"
                          fill="currentColor"
                          viewBox="0 0 24 24"
                          aria-hidden="true"
                        >
                          <path
                            fillRule="evenodd"
                            d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </a>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </main>
  );
}
