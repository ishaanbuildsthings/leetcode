"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";

export function GoatModeWrapper({ children }: { children: React.ReactNode }) {
  const [goatMode, setGoatMode] = useState(true);
  const pathname = usePathname();

  // Hide goat mode entirely inside individual topic/foundations pages
  const isDetailPage =
    pathname.startsWith("/interview-prep/topics/") ||
    pathname === "/interview-prep/foundations" ||
    pathname === "/interview-prep/complexity";

  const showGoat = goatMode && !isDetailPage;

  return (
    <div
      className="min-h-screen bg-[#faf9f6] bg-cover bg-center bg-no-repeat bg-fixed transition-all duration-500"
      style={showGoat ? { backgroundImage: "url('/goat-field-bg.jpg')" } : {}}
    >
      {children}

      {/* Goat Mode toggle — hidden on detail pages */}
      {!isDetailPage && (
        <div className="fixed bottom-5 right-5 z-50 flex items-center gap-2 rounded-full bg-background/90 px-3 py-2 shadow-md backdrop-blur-sm border border-border">
          <span className="font-[family-name:var(--font-dm-sans)] text-xs font-medium text-muted-foreground">
            🐐 Goat Mode
          </span>
          <button
            onClick={() => setGoatMode(!goatMode)}
            className={`relative h-5 w-9 rounded-full transition-colors duration-200 ${
              goatMode ? "bg-primary" : "bg-border"
            }`}
            aria-label="Toggle goat mode background"
          >
            <span
              className={`absolute top-0.5 left-0.5 h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-200 ${
                goatMode ? "translate-x-4" : "translate-x-0"
              }`}
            />
          </button>
        </div>
      )}
    </div>
  );
}
