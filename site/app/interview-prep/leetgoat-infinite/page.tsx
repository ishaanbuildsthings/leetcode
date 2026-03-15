export default function LeetGoatInfinitePage() {
  return (
    <main className="flex min-h-[60vh] items-center justify-center px-6">
      <div className="rounded-2xl border border-border bg-background/90 px-12 py-16 text-center shadow-lg backdrop-blur-sm">
        <h1 className="font-[family-name:var(--font-playfair)] text-4xl font-bold text-foreground">
          LeetGoat{" "}
          <svg className="inline-block w-12 h-12 -mt-1" viewBox="0 0 100 50" fill="none">
            <path
              d="M50 25C50 25 62 5 78 5C90 5 95 15 95 25C95 35 90 45 78 45C62 45 50 25 50 25C50 25 38 5 22 5C10 5 5 15 5 25C5 35 10 45 22 45C38 45 50 25 50 25Z"
              stroke="#3b82f6"
              strokeWidth="5"
              strokeLinecap="round"
            />
            <circle r="4" fill="#3b82f6">
              <animateMotion
                dur="2s"
                repeatCount="indefinite"
                path="M50 25C50 25 62 5 78 5C90 5 95 15 95 25C95 35 90 45 78 45C62 45 50 25 50 25C50 25 38 5 22 5C10 5 5 15 5 25C5 35 10 45 22 45C38 45 50 25 50 25Z"
              />
            </circle>
          </svg>
        </h1>
        <p className="mx-auto mt-4 max-w-md font-[family-name:var(--font-dm-sans)] text-base text-foreground">
          Every single solution I&apos;ve written, categorized by topic.
          All 3,000+ problems in one place.
        </p>
        <p className="mt-6 font-[family-name:var(--font-dm-sans)] text-sm text-muted-foreground">
          Coming soon &ndash; leetgoat{" "}
          <span className="inline-block animate-[wiggle_1.5s_ease-in-out_infinite]">
            🐐
          </span>
        </p>
      </div>
    </main>
  );
}
