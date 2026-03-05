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

  const [githubStars, problemCount, tagCount] = await Promise.all([
    fetchGitHubStars("ishaanbuildsthings/leetcode"),
    prisma.problems.count(),
    prisma.tags.count(),
  ]);

  return (
    <AuthProvider value={{ userId, isAdmin }}>
      <div className="min-h-screen bg-slate-50">
        <Nav activePath="/" isDev={isDev} githubStars={githubStars} />

        {/* Hero */}
        <section className="relative overflow-hidden bg-gradient-to-br from-rose-50 via-white to-pink-50">
          <div className="mx-auto flex max-w-6xl flex-col-reverse items-center gap-12 px-6 py-20 md:flex-row md:py-28">
            {/* Left – copy */}
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl">
                Learn from someone who solved{" "}
                <span className="text-rose-600">4,000+</span> problems
              </h1>
              <p className="mt-4 max-w-lg text-lg text-gray-600">
                Stop grinding randomly. Practice curated patterns from an expert
                who&apos;s been through it all &mdash; organized by topic so you
                build real intuition.
              </p>
              <Link
                href="/practice"
                className="mt-8 inline-block rounded-lg bg-rose-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-rose-700"
              >
                Start Practicing
              </Link>
            </div>

            {/* Right – hero image */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/hero.png"
              alt=""
              className="hidden w-72 flex-shrink-0 md:block lg:w-96"
              onError={undefined}
            />
          </div>
        </section>

        {/* Stats */}
        <section className="border-y border-gray-200 bg-white">
          <div className="mx-auto grid max-w-4xl grid-cols-3 divide-x divide-gray-200 py-10 text-center">
            <div>
              <p className="text-3xl font-bold text-gray-900">
                {problemCount.toLocaleString()}+
              </p>
              <p className="mt-1 text-sm text-gray-500">Problems</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-gray-900">{tagCount}</p>
              <p className="mt-1 text-sm text-gray-500">Patterns</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-gray-900">
                {githubStars != null ? githubStars.toLocaleString() : "—"}
              </p>
              <p className="mt-1 text-sm text-gray-500">GitHub Stars</p>
            </div>
          </div>
        </section>
      </div>
    </AuthProvider>
  );
}
