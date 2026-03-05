import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import * as tagService from "@/lib/services/tag.service";
import { transformProblemWithRelations } from "@/lib/transforms";
import type { IProblemWithRelations } from "@/lib/transforms";
import { TagBucketList } from "@/components/TagBucketList";
import { Nav } from "@/components/Nav";
import { AuthProvider } from "@/contexts/AuthContext";
import { fetchGitHubStars } from "@/lib/github";

export default async function PracticePage() {
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

  // Fetch all tags, all problems with core tags, and GitHub stars in parallel
  const [allTags, allProblemsRaw, githubStars] = await Promise.all([
    tagService.unsafe_listTags(),
    prisma.problems.findMany({
      where: {
        problem_tags: { some: { role: "core" } },
      },
      include: {
        platforms: true,
        problem_tags: { include: { tags: true } },
        solutions: true,
      },
      orderBy: { created_at: "desc" },
    }),
    fetchGitHubStars("ishaanbuildsthings/leetcode"),
  ]);

  const problems = allProblemsRaw.map(transformProblemWithRelations);

  // Group problems by their core tag slug
  const grouped = new Map<string, IProblemWithRelations[]>();
  for (const tag of allTags) {
    grouped.set(tag.slug, []);
  }
  for (const problem of problems) {
    for (const pt of problem.tags) {
      if (pt.role === "core" && grouped.has(pt.tag.slug)) {
        grouped.get(pt.tag.slug)!.push(problem);
      }
    }
  }

  // Sort each bucket by tag_difficulty ascending
  for (const [slug, bucket] of grouped) {
    bucket.sort((a, b) => {
      const aDiff =
        a.tags.find((t) => t.tag.slug === slug)?.tagDifficulty ?? 99;
      const bDiff =
        b.tags.find((t) => t.tag.slug === slug)?.tagDifficulty ?? 99;
      return aDiff - bDiff;
    });
  }

  // Build sections sorted by problem count descending, then alphabetically
  const sections = allTags
    .map((tag) => ({
      slug: tag.slug,
      name: tag.name,
      problems: grouped.get(tag.slug) ?? [],
    }))
    .sort((a, b) => {
      if (b.problems.length !== a.problems.length)
        return b.problems.length - a.problems.length;
      return a.name.localeCompare(b.name);
    });

  return (
    <AuthProvider value={{ userId, isAdmin }}>
      <div className="min-h-screen bg-slate-50">
        <Nav activePath="/practice" isDev={isDev} githubStars={githubStars} />
        <TagBucketList sections={sections} />
      </div>
    </AuthProvider>
  );
}
