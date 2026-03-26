import Link from "next/link";
import { topics, gettingStartedLessons, complexityLessons } from "@/lib/interview-prep-data";

const tiers = [
  {
    label: "Beginner",
    color: "bg-green-100 text-green-700",
    slugs: ["arrays-hashing", "two-pointers", "sliding-window", "binary-search"],
  },
  {
    label: "Intermediate",
    color: "bg-amber-100 text-amber-700",
    slugs: ["stack", "queues", "linked-lists", "heaps", "trees", "strings", "greedy"],
  },
  {
    label: "Advanced",
    color: "bg-red-100 text-red-700",
    slugs: ["graphs", "dynamic-programming", "backtracking"],
  },
];

export default function InterviewPrepPage() {
  const startHereTotal = gettingStartedLessons.length + complexityLessons.length;

  return (
    <main className="px-6 py-10 min-h-screen">
      <div className="mx-auto max-w-7xl space-y-6">

        {/* Start Here card */}
        <div className="rounded-2xl bg-white p-6 shadow-sm">
          <h2 className="font-[family-name:var(--font-dm-sans)] text-sm font-semibold uppercase tracking-wider text-foreground">
            Start Here
          </h2>

          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div
              className="flex flex-col rounded-xl border border-border p-4 opacity-60"
            >
              <div className="flex items-center gap-2">
              <h3 className="font-[family-name:var(--font-dm-sans)] text-sm font-semibold text-foreground">
                Getting Started
              </h3>
              <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                Coming soon
              </span>
              </div>
              <p className="mt-1 font-[family-name:var(--font-dm-sans)] text-xs text-muted-foreground">
                {gettingStartedLessons.length} videos
              </p>
              <p className="mt-2 font-[family-name:var(--font-dm-sans)] text-[11px] text-muted-foreground line-clamp-2">
                Everything I&apos;ve learned from solving 3,000+ LeetCode problems. Most common mistakes, how to prepare for interviews on different timelines, what language to use, and more. Hope this is useful :&apos;)
              </p>
              <div className="mt-auto pt-3 flex items-center gap-2">
                <div className="flex gap-1">
                  {Array.from({ length: gettingStartedLessons.length }).map((_, i) => (
                    <span key={i} className="h-1.5 w-1.5 rounded-full bg-border" />
                  ))}
                </div>
                <span className="flex-shrink-0 font-[family-name:var(--font-dm-sans)] text-[11px] text-muted-foreground">
                  0/{gettingStartedLessons.length}
                </span>
              </div>
            </div>

            <div
              className="flex flex-col rounded-xl border border-border p-4 opacity-60"
            >
              <div className="flex items-center gap-2">
              <h3 className="font-[family-name:var(--font-dm-sans)] text-sm font-semibold text-foreground">
                Complexity &amp; Constraints
              </h3>
              <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                Coming soon
              </span>
              </div>
              <p className="mt-1 font-[family-name:var(--font-dm-sans)] text-xs text-muted-foreground">
                {complexityLessons.length} videos
              </p>
              <p className="mt-2 font-[family-name:var(--font-dm-sans)] text-[11px] text-muted-foreground line-clamp-2">
                My most important tips on how to use complexity to your advantage &ndash; and the mistakes I see people making over and over.
              </p>
              <div className="mt-auto pt-3 flex items-center gap-2">
                <div className="flex gap-1">
                  {Array.from({ length: complexityLessons.length }).map((_, i) => (
                    <span key={i} className="h-1.5 w-1.5 rounded-full bg-border" />
                  ))}
                </div>
                <span className="flex-shrink-0 font-[family-name:var(--font-dm-sans)] text-[11px] text-muted-foreground">
                  0/{complexityLessons.length}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* More content coming soon */}
        <div className="rounded-2xl bg-white p-6 shadow-sm">
          <p className="font-[family-name:var(--font-dm-sans)] text-sm text-muted-foreground">
            More content coming soon &ndash; topics like arrays, trees, graphs, DP, and more.
          </p>
          <p className="mt-3 font-[family-name:var(--font-dm-sans)] text-sm text-muted-foreground">
            &ndash; leetgoat{" "}
            <span className="inline-block animate-[wiggle_1.5s_ease-in-out_infinite] text-base">
              🐐
            </span>
          </p>
          <a
            href="https://discord.gg/HYqgVAvC"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-block font-[family-name:var(--font-dm-sans)] text-sm font-medium text-primary underline underline-offset-4 hover:text-primary/80"
          >
            Join the Discord for updates &rarr;
          </a>
        </div>

      </div>
    </main>
  );
}
