import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { AuthProvider } from "@/contexts/AuthContext";
import { fetchGitHubStars } from "@/lib/github";

export default async function CompetitivePage() {
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
  const githubStars = await fetchGitHubStars("ishaanbuildsthings/leetcode");

  return (
    <AuthProvider value={{ userId, isAdmin }}>
      <div className="min-h-screen bg-slate-50">
        <Nav activePath="/competitive" isDev={isDev} githubStars={githubStars} />
        <main className="mx-auto max-w-4xl px-6 py-24 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900">
            Competitive Programming
          </h1>
          <p className="mt-4 text-lg text-gray-600">
            Curated competitive programming prep content is coming soon.
          </p>
          <p className="mt-2 text-sm text-gray-400">
            CSES, Codeforces, AtCoder, and more.
          </p>
        </main>
      </div>
    </AuthProvider>
  );
}
