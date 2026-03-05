import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { AuthProvider } from "@/contexts/AuthContext";
import { fetchGitHubStars } from "@/lib/github";
import Link from "next/link";

export default async function HomePage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  let userId: string | null = null;
  let isAdmin = false;

  if (user) {
    userId = user.id;
    const dbUser = await prisma.users.findUnique({ where: { id: user.id } });
    isAdmin = dbUser?.is_admin ?? false;
  }

  const isDev = process.env.NODE_ENV === "development";

  const [githubStars, tagsRaw] = await Promise.all([
    fetchGitHubStars("ishaanbuildsthings/leetcode"),
    prisma.tags.findMany({
      include: {
        problem_tags: {
          where: { role: "core" },
          select: { problem_id: true },
        },
      },
    }),
  ]);

  const tags = tagsRaw
    .map((t) => ({
      name: t.name,
      slug: t.slug,
      description: t.description,
      problemCount: t.problem_tags.length,
    }))
    .filter((t) => t.problemCount > 0)
    .sort((a, b) => b.problemCount - a.problemCount);

  return (
    <AuthProvider value={{ userId, isAdmin }}>
      <div className="min-h-screen bg-white">
        <Nav activePath="/" isDev={isDev} githubStars={githubStars} />

        {/* Hero */}
        <section className="bg-gradient-to-b from-gray-50 to-white">
          <div className="mx-auto max-w-6xl px-6 pb-20 pt-20 md:pt-28">
            <h1 className="max-w-3xl text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
              Train smarter for coding interviews &amp; competitions
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-relaxed text-gray-500">
              Curated problem sets and structured paths built by someone
              who&apos;s solved{" "}
              <span className="font-semibold text-gray-900">
                4,000+ LeetCode problems
              </span>
              . No fluff, just the patterns that matter.
            </p>
            <div className="mt-10 flex flex-wrap gap-4">
              <Link
                href="/practice"
                className="inline-flex items-center gap-2 rounded-lg bg-lime-400 px-6 py-3 text-sm font-semibold text-gray-900 shadow-sm transition-colors hover:bg-lime-500"
              >
                Start Interview Prep
                <span aria-hidden="true">&rarr;</span>
              </Link>
              <Link
                href="/competitive"
                className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-semibold text-gray-700 transition-colors hover:bg-gray-50"
              >
                Explore Competition Track
              </Link>
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="border-t border-gray-100">
          <div className="mx-auto grid max-w-6xl grid-cols-1 gap-10 px-6 py-20 md:grid-cols-3">
            <div>
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-lime-100">
                <svg
                  className="h-5 w-5 text-lime-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3 className="text-base font-semibold text-gray-900">
                Battle-tested curriculum
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-gray-500">
                Every problem hand-picked from 4,000+ solved. Only the
                highest-signal patterns make the cut.
              </p>
            </div>
            <div>
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100">
                <svg
                  className="h-5 w-5 text-emerald-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M7.5 3.75H6A2.25 2.25 0 003.75 6v1.5M16.5 3.75H18A2.25 2.25 0 0120.25 6v1.5m0 9V18A2.25 2.25 0 0118 20.25h-1.5m-9 0H6A2.25 2.25 0 013.75 18v-1.5M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </div>
              <h3 className="text-base font-semibold text-gray-900">
                Two focused tracks
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-gray-500">
                Interview prep for landing offers. Competition track for pushing
                your limits. Pick your path.
              </p>
            </div>
            <div>
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100">
                <svg
                  className="h-5 w-5 text-emerald-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"
                  />
                </svg>
              </div>
              <h3 className="text-base font-semibold text-gray-900">
                Pattern-first approach
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-gray-500">
                Stop grinding randomly. Learn the underlying patterns so you can
                solve any variation.
              </p>
            </div>
          </div>
        </section>

        {/* Interview Prep Topics */}
        <section className="border-t border-gray-100 bg-gray-50/50">
          <div className="mx-auto max-w-6xl px-6 py-20">
            <div className="mb-2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-lime-100 px-3 py-1 text-xs font-semibold text-lime-700">
                🎯 Interview Prep
              </span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">
              Master the patterns that land offers
            </h2>
            <p className="mt-2 text-gray-500">
              Structured topic tracks covering every pattern you&apos;ll
              encounter at top companies.
            </p>

            <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {tags.map((tag) => (
                <Link
                  key={tag.slug}
                  href={`/practice#${tag.slug}`}
                  className="group flex items-center gap-4 rounded-xl border border-gray-200 bg-white px-5 py-4 transition-all hover:border-gray-300 hover:shadow-md"
                >
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-gray-100 text-gray-500">
                    <svg
                      className="h-5 w-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5"
                      />
                    </svg>
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="truncate font-semibold text-gray-900">
                        {tag.name}
                      </span>
                    </div>
                    {tag.description && (
                      <p className="mt-0.5 truncate text-xs text-gray-400">
                        {tag.description}
                      </p>
                    )}
                  </div>
                  <div className="flex flex-shrink-0 items-center gap-2 text-sm text-gray-400">
                    <span>
                      {tag.problemCount}{" "}
                      <span className="hidden sm:inline">problems</span>
                    </span>
                    <svg
                      className="h-4 w-4 transition-transform group-hover:translate-x-0.5"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={2}
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M8.25 4.5l7.5 7.5-7.5 7.5"
                      />
                    </svg>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* Competition Teaser */}
        <section className="border-t border-gray-100">
          <div className="mx-auto max-w-6xl px-6 py-20">
            <div className="mb-2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-100 px-3 py-1 text-xs font-semibold text-rose-600">
                ⚔️ Competition
              </span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">
              Push beyond interviews
            </h2>
            <p className="mt-2 text-gray-500">
              Olympiad-level topics for competitive programming mastery. Coming
              soon.
            </p>
          </div>
        </section>
      </div>
    </AuthProvider>
  );
}
