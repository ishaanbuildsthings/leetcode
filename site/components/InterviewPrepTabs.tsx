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
              <span className="inline-flex items-center gap-0">
                {tab.label.replace(" ∞", "")}
                <svg className="w-4 h-4 ml-1" viewBox="0 0 24 12" fill="none">
                  <path
                    d="M12 6C12 6 14.5 1.5 18 1.5C20.5 1.5 22.5 3.5 22.5 6C22.5 8.5 20.5 10.5 18 10.5C14.5 10.5 12 6 12 6ZM12 6C12 6 9.5 1.5 6 1.5C3.5 1.5 1.5 3.5 1.5 6C1.5 8.5 3.5 10.5 6 10.5C9.5 10.5 12 6 12 6Z"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <circle r="1.5" fill="currentColor" opacity="0.9">
                    <animateMotion
                      dur="2.5s"
                      repeatCount="indefinite"
                      path="M12 6C12 6 14.5 1.5 18 1.5C20.5 1.5 22.5 3.5 22.5 6C22.5 8.5 20.5 10.5 18 10.5C14.5 10.5 12 6 12 6C12 6 9.5 1.5 6 1.5C3.5 1.5 1.5 3.5 1.5 6C1.5 8.5 3.5 10.5 6 10.5C9.5 10.5 12 6 12 6Z"
                    />
                  </circle>
                </svg>
              </span>
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
