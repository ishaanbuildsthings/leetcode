export default function LeetGoatInfinitePage() {
  return (
    <main className="flex min-h-[60vh] items-center justify-center px-6">
      <div className="rounded-2xl border border-border bg-background/90 px-12 py-16 text-center shadow-lg backdrop-blur-sm">
        <h1 className="font-[family-name:var(--font-playfair)] text-4xl font-bold text-foreground">
          LeetGoat{" "}
          <svg className="inline-block w-14 h-14 -mt-1" viewBox="0 0 24 12" fill="none">
            <defs>
              <filter id="flash-blur-lg" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="0.8" />
              </filter>
            </defs>
            <path
              d="M12 6C12 6 14.5 1.5 18 1.5C20.5 1.5 22.5 3.5 22.5 6C22.5 8.5 20.5 10.5 18 10.5C14.5 10.5 12 6 12 6ZM12 6C12 6 9.5 1.5 6 1.5C3.5 1.5 1.5 3.5 1.5 6C1.5 8.5 3.5 10.5 6 10.5C9.5 10.5 12 6 12 6Z"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <rect x="-2.5" y="-0.9" width="5" height="1.8" rx="0.9" fill="white" filter="url(#flash-blur-lg)" opacity="0.9">
              <animateMotion
                dur="2.5s"
                repeatCount="indefinite"
                rotate="auto"
                path="M12 6C12 6 14.5 1.5 18 1.5C20.5 1.5 22.5 3.5 22.5 6C22.5 8.5 20.5 10.5 18 10.5C14.5 10.5 12 6 12 6C12 6 9.5 1.5 6 1.5C3.5 1.5 1.5 3.5 1.5 6C1.5 8.5 3.5 10.5 6 10.5C9.5 10.5 12 6 12 6Z"
              />
            </rect>
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
