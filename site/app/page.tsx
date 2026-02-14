import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import * as problemService from "@/lib/services/problem.service";
import { transformProblemWithRelations } from "@/lib/transforms";
import type { IProblemWithRelations } from "@/lib/transforms";
import { TagBucketList } from "@/components/TagBucketList";
import { Nav } from "@/components/Nav";
import { AuthProvider } from "@/contexts/AuthContext";
import { fetchGitHubStars } from "@/lib/github";

const TAG_SLUGS_ORDERED = [
  "kadanes",
  "binary-search",
  "binary-search-on-answer",
  "sliding-window-fixed",
  "sliding-window-variable",
  "prefix-suffix",
  "two-pointers",
  "knapsack-dp",
  "stacks",
];

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

  // Fetch data in parallel
  const [problemsData, githubStars] = await Promise.all([
    problemService.unsafe_listProblemsByPlatformAndTags(
      "leetcode",
      TAG_SLUGS_ORDERED
    ),
    fetchGitHubStars("ishaanbuildsthings/leetcode"),
  ]);

  const problems = problemsData.map(transformProblemWithRelations);

  // Group problems by their core tag slug
  const grouped = new Map<string, IProblemWithRelations[]>();
  for (const slug of TAG_SLUGS_ORDERED) {
    grouped.set(slug, []);
  }
  for (const problem of problems) {
    for (const pt of problem.tags) {
      if (pt.role === "core" && TAG_SLUGS_ORDERED.includes(pt.tag.slug)) {
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

  // Build ordered sections with tag names from the data
  const tagNameMap = new Map<string, string>();
  for (const problem of problems) {
    for (const pt of problem.tags) {
      if (!tagNameMap.has(pt.tag.slug)) {
        tagNameMap.set(pt.tag.slug, pt.tag.name);
      }
    }
  }

  const sections = TAG_SLUGS_ORDERED.map((slug) => ({
    slug,
    name: tagNameMap.get(slug) ?? slug,
    problems: grouped.get(slug) ?? [],
  }));

  return (
    <AuthProvider value={{ userId, isAdmin }}>
      <div className="min-h-screen bg-gray-50">
        <Nav activePath="/" />
        <TagBucketList sections={sections} githubStars={githubStars} />
      </div>
    </AuthProvider>
  );
}
