"use client";

import { useState } from "react";
import Link from "next/link";
import { complexityLessons } from "@/lib/interview-prep-data";

export default function ComplexityPage() {
  const [activeIndex, setActiveIndex] = useState(0);
  const lesson = complexityLessons[activeIndex];

  return (
    <div className="flex gap-0 bg-background/85 backdrop-blur-md min-h-screen">
      {/* Sidebar */}
      <aside className="w-72 flex-shrink-0 border-r border-border px-4 py-6">
        <Link
          href="/interview-prep"
          className="font-[family-name:var(--font-dm-sans)] text-sm font-medium text-primary hover:text-primary/80"
        >
          &larr; All topics
        </Link>

        <h2 className="mt-4 font-[family-name:var(--font-dm-sans)] text-lg font-bold text-foreground">
          Complexity &amp; Constraints
        </h2>
        <p className="font-[family-name:var(--font-dm-sans)] text-xs text-muted-foreground">
          {complexityLessons.length} lessons &middot; 0 completed
        </p>

        {/* Lesson list */}
        <div className="mt-6 space-y-1">
          {complexityLessons.map((l, i) => (
            <button
              key={l.slug}
              onClick={() => setActiveIndex(i)}
              className={`flex w-full items-center gap-2 rounded-md border-l-2 px-3 py-2 text-left font-[family-name:var(--font-dm-sans)] text-sm transition-colors ${
                i === activeIndex
                  ? "border-primary bg-[#f0f7f4] text-primary"
                  : "border-transparent text-foreground hover:bg-muted"
              }`}
            >
              <span className="flex h-4 w-4 flex-shrink-0 items-center justify-center rounded border border-border bg-white" />
              <span className="flex-1">{l.title}</span>
              <span className="flex-shrink-0 text-[11px] text-muted-foreground">
                {l.duration}
              </span>
            </button>
          ))}
        </div>

        {/* Progress */}
        <div className="mt-8 border-t border-border pt-4">
          <div className="h-1 w-full rounded-full bg-border">
            <div
              className="h-1 rounded-full bg-primary"
              style={{ width: "0%" }}
            />
          </div>
          <p className="mt-2 font-[family-name:var(--font-dm-sans)] text-xs text-muted-foreground">
            0 of {complexityLessons.length} complete
          </p>
        </div>
      </aside>

      {/* Main content */}
      <main className="mx-auto flex-1 max-w-5xl px-10 py-6">
        <h1 className="font-[family-name:var(--font-playfair)] text-2xl font-bold text-foreground">
          {lesson.title}
        </h1>
        <p className="mt-2 font-[family-name:var(--font-dm-sans)] text-base text-muted-foreground">
          {lesson.subtitle}
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

        {/* Key takeaways */}
        <h2 className="mt-10 font-[family-name:var(--font-playfair)] text-xl font-bold text-foreground">
          Key takeaways
        </h2>
        <div className="mt-4 space-y-4">
          {lesson.notes.map((note) => (
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

        {/* Up next */}
        {activeIndex < complexityLessons.length - 1 && (
          <button
            onClick={() => setActiveIndex(activeIndex + 1)}
            className="mt-8 font-[family-name:var(--font-dm-sans)] text-sm font-medium text-foreground hover:text-primary"
          >
            Up next: {complexityLessons[activeIndex + 1].title} &rarr;
          </button>
        )}

        {/* Discord */}
        <p className="mt-6 font-[family-name:var(--font-dm-sans)] text-sm text-muted-foreground">
          Have questions?{" "}
          <a
            href="https://discord.gg/HYqgVAvC"
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-foreground underline underline-offset-4 hover:text-primary"
          >
            Ask in Discord &rarr;
          </a>
        </p>
      </main>
    </div>
  );
}
