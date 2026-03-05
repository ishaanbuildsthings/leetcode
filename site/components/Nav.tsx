"use client";

import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

interface NavProps {
  activePath?: string;
  isDev?: boolean;
  githubStars?: number;
}

const navLinks = [
  { href: "/practice", label: "Interview Prep" },
  { href: "/competitive", label: "Competitive Programming" },
  { href: "/questions", label: "Mega Questions List (Free)" },
];

export function Nav({ activePath, isDev, githubStars }: NavProps) {
  const { isAdmin } = useAuth();

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2 text-lg font-bold tracking-tight text-gray-900"
        >
          <span className="flex h-7 w-7 items-center justify-center rounded bg-lime-400 text-sm">
            🐐
          </span>
          leetgoat
        </Link>

        {/* Center nav links */}
        <div className="hidden items-center gap-8 md:flex">
          {navLinks.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={`text-sm font-medium transition-colors ${
                activePath === href
                  ? "text-gray-900"
                  : "text-gray-500 hover:text-gray-900"
              }`}
            >
              {label}
            </Link>
          ))}
        </div>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {isDev && isAdmin && (
            <Link
              href="/admin"
              className={`text-sm font-medium transition-colors ${
                activePath === "/admin"
                  ? "text-gray-900 underline underline-offset-4"
                  : "text-gray-500 hover:text-gray-900"
              }`}
            >
              Admin
            </Link>
          )}

          <a
            href="https://github.com/ishaanbuildsthings/leetcode"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-sm font-medium text-slate-500 transition-colors hover:text-gray-900"
          >
            <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>
            {githubStars != null && githubStars > 0 && (
              <span className="text-xs font-semibold text-slate-400">
                {githubStars.toLocaleString()}
              </span>
            )}
          </a>

          <Link
            href="/practice"
            className="rounded-lg border border-gray-900 px-4 py-1.5 text-sm font-semibold text-gray-900 transition-colors hover:bg-gray-900 hover:text-white"
          >
            Start Training
          </Link>
        </div>
      </div>
    </nav>
  );
}
