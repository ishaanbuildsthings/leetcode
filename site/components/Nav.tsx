"use client";

import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

interface NavProps {
  activePath?: string;
  githubStars?: number;
}

export function Nav({ activePath, githubStars }: NavProps) {
  const { isAdmin } = useAuth();

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link
          href="/"
          className="text-lg font-semibold tracking-tight text-gray-900"
        >
          leetgoat.io
        </Link>

        <div className="flex items-center gap-6">
          {isAdmin && (
            <>
              <Link
                href="/mindsolves"
                className={`text-sm font-medium transition-colors ${
                  activePath === "/mindsolves"
                    ? "text-gray-900 underline underline-offset-4"
                    : "text-gray-500 hover:text-gray-900"
                }`}
              >
                Mindsolves
              </Link>
              <Link
                href="/implements"
                className={`text-sm font-medium transition-colors ${
                  activePath === "/implements"
                    ? "text-gray-900 underline underline-offset-4"
                    : "text-gray-500 hover:text-gray-900"
                }`}
              >
                Implements
              </Link>
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
            </>
          )}
          <a
            href="https://github.com/ishaanbuildsthings/leetcode"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-sm font-medium text-gray-500 transition-colors hover:text-gray-900"
          >
            GitHub
            {githubStars != null && githubStars > 0 && (
              <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-semibold text-gray-700">
                {githubStars.toLocaleString()}
              </span>
            )}
          </a>
        </div>
      </div>
    </nav>
  );
}
