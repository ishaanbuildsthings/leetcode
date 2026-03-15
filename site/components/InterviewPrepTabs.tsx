"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  { href: "/interview-prep", label: "Topics", exact: true },
  { href: "/interview-prep/leetgoat-222", label: "LeetGoat 222", badge: "🚧 under construction" },
  { href: "/interview-prep/leetgoat-infinite", label: "LeetGoat ∞", pulseSymbol: true, badge: "soon" },
  {
    href: "/interview-prep/flashcards",
    label: "Flashcards",
    badge: "soon",
  },
];

export function InterviewPrepTabs() {
  const pathname = usePathname();

  function isActive(tab: (typeof tabs)[number]) {
    if (tab.exact) {
      // "Topics" tab is active for the dashboard AND any topics/foundations subpages
      return (
        pathname === "/interview-prep" ||
        pathname.startsWith("/interview-prep/topics") ||
        pathname.startsWith("/interview-prep/foundations")
      );
    }
    return pathname.startsWith(tab.href);
  }

  return (
    <div className="sticky top-16 z-40 border-b border-border backdrop-blur-md bg-background/80">
      <div className="mx-auto flex max-w-7xl items-center gap-8 px-6">
        {tabs.map((tab) => (
          <Link
            key={tab.href}
            href={tab.href}
            className={`relative flex items-center gap-2 py-3 font-[family-name:var(--font-dm-sans)] text-sm font-medium transition-colors ${
              isActive(tab)
                ? "text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab.pulseSymbol ? (
              <>
                {tab.label.replace(" ∞", "")}{" "}
                <svg className="inline-block w-5 h-5 -mt-0.5" viewBox="0 0 100 50" fill="none">
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
              </>
            ) : (
              tab.label
            )}
            {tab.badge && (
              <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                {tab.badge}
              </span>
            )}
            {isActive(tab) && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
