import { prisma } from "../prisma";
import { tag_role } from "../../src/generated/prisma/enums";

export async function unsafe_createProblem(data: {
  platformId: string;
  title: string;
  url: string;
  isGreatProblem: boolean;
  platformProblemId?: string;
  platformDifficulty?: string;
  normalizedDifficulty?: number;
  notes?: string;
  tags?: Array<{ tagId: string; role?: tag_role; tagDifficulty?: number; isInstructive?: boolean }>;
  solutions?: Array<{ url: string; language?: string; solution?: string; githubUrl?: string }>;
}) {
  return prisma.problems.create({
    data: {
      platform_id: data.platformId,
      platform_problem_id: data.platformProblemId,
      title: data.title,
      url: data.url,
      platform_difficulty: data.platformDifficulty,
      normalized_difficulty: data.normalizedDifficulty,
      notes: data.notes,
      is_great_problem: data.isGreatProblem,
      problem_tags: data.tags
        ? {
            create: data.tags.map((t) => ({
              tag_id: t.tagId,
              role: t.role,
              tag_difficulty: t.tagDifficulty,
              is_instructive: t.isInstructive ?? null,
            })),
          }
        : undefined,
      solutions: data.solutions
        ? {
            create: data.solutions.map((s) => ({
              url: s.url,
              language: s.language,
              solution: s.solution,
              github_url: s.githubUrl,
            })),
          }
        : undefined,
    },
    include: {
      platforms: true,
      problem_tags: {
        include: { tags: true },
      },
      solutions: true,
    },
  });
}

export async function unsafe_getProblemById(id: string) {
  return prisma.problems.findUnique({
    where: { id },
    include: {
      platforms: true,
      problem_tags: {
        include: { tags: true },
      },
      solutions: true,
    },
  });
}

export async function unsafe_listProblems() {
  return prisma.problems.findMany({
    include: {
      platforms: true,
      problem_tags: {
        include: { tags: true },
      },
      solutions: true,
    },
    orderBy: { created_at: "desc" },
  });
}

export async function unsafe_deleteProblem(id: string) {
  return prisma.problems.delete({
    where: { id },
  });
}
