"use client";

import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

interface NavProps {
  activePath?: string;
  isDev?: boolean;
  githubStars?: number;
}

export function Nav({ activePath, isDev }: NavProps) {
  const { isAdmin } = useAuth();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-background/80 border-b border-border">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 h-16">
        {/* Logo */}
        <Link href="/" className="group flex items-center gap-2">
          <span className="inline-block text-2xl transition-transform duration-200 group-hover:rotate-12">🐐</span>
          <span className="font-[family-name:var(--font-fraunces)] text-xl font-bold text-foreground tracking-tight">
            LeetGoat
          </span>
        </Link>

        {/* Center nav links */}
        <div className="hidden items-center gap-8 md:flex font-[family-name:var(--font-dm-sans)] text-sm font-medium">
          <Link
            href="/interview-prep"
            className={`transition-colors ${
              activePath === "/interview-prep"
                ? "text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Interview Prep
          </Link>
          <Link
            href="/competitive"
            className={`transition-colors ${
              activePath === "/competitive"
                ? "text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Competitive Programming
          </Link>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {isDev && isAdmin && (
            <Link
              href="/admin"
              className={`text-sm font-medium transition-colors ${
                activePath === "/admin"
                  ? "text-foreground underline underline-offset-4"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Admin
            </Link>
          )}

          <a
            href="https://discord.gg/ENypyH9n"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground transition-colors hover:text-foreground font-[family-name:var(--font-dm-sans)] text-sm font-medium"
          >
            Discord
          </a>

          {/* Sign in — hidden for now
          <button className="font-[family-name:var(--font-dm-sans)] text-sm font-medium text-muted-foreground transition-colors hover:text-foreground">
            Sign in
          </button>
          */}
        </div>
      </div>
    </nav>
  );
}
