import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { AuthProvider } from "@/contexts/AuthContext";
import { fetchGitHubStars } from "@/lib/github";

export default async function AskPage() {
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
      <div className="min-h-screen bg-white">
        <Nav activePath="/ask" isDev={isDev} githubStars={githubStars} />
        <main className="mx-auto max-w-4xl px-6 py-24 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900">
            Ask LeetGoat
          </h1>
          <p className="mt-4 text-lg text-gray-600">
            AI-powered help for your coding interview prep is coming soon.
          </p>
        </main>
      </div>
    </AuthProvider>
  );
}
