"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  { href: "/interview-prep", label: "Topics", exact: true },
  { href: "/interview-prep/leetgoat-222", label: "LeetGoat 222", badge: "🚧 under construction" },
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
            {tab.label}
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
