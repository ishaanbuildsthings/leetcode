import { prisma } from "../prisma";
import { tag_role, programming_language, drill_type } from "../../src/generated/prisma/enums";

export async function unsafe_createProblem(data: {
  platformId: string;
  title: string;
  url: string;
  isGreatProblem: boolean;
  platformProblemId?: string;
  platformDifficulty?: string;
  normalizedDifficulty?: number;
  simplifiedStatement?: string;
  notes?: string;
  drillType?: drill_type | null;
  drillNotes?: string;
  tags?: Array<{ tagId: string; role?: tag_role; tagDifficulty?: number; isInstructive?: boolean }>;
  solutions?: Array<{ submissionUrl?: string; language: programming_language; githubUrl?: string }>;
}) {
  return prisma.problems.create({
    data: {
      platform_id: data.platformId,
      platform_problem_id: data.platformProblemId,
      title: data.title,
      url: data.url,
      platform_difficulty: data.platformDifficulty,
      normalized_difficulty: data.normalizedDifficulty,
      simplified_statement: data.simplifiedStatement,
      notes: data.notes,
      is_great_problem: data.isGreatProblem,
      drill_type: data.drillType ?? null,
      drill_notes: data.drillNotes,
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
              submission_url: s.submissionUrl || undefined,
              language: s.language,
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

export async function unsafe_updateProblem(data: {
  id: string;
  platformId?: string;
  title?: string;
  url?: string;
  isGreatProblem?: boolean;
  platformProblemId?: string;
  platformDifficulty?: string;
  normalizedDifficulty?: number;
  simplifiedStatement?: string;
  notes?: string;
  drillType?: drill_type | null;
  drillNotes?: string;
  tags?: Array<{ tagId: string; role?: tag_role; tagDifficulty?: number; isInstructive?: boolean }>;
  solutions?: Array<{ submissionUrl?: string; language: programming_language; githubUrl?: string }>;
}) {
  await prisma.problem_tags.deleteMany({
    where: { problem_id: data.id },
  });
  
  await prisma.solutions.deleteMany({
    where: { problem_id: data.id },
  });

  type UpdateData = {
    platform_id?: string;
    title?: string;
    url?: string;
    is_great_problem?: boolean;
    platform_problem_id?: string | null;
    platform_difficulty?: string | null;
    normalized_difficulty?: number;
    simplified_statement?: string | null;
    notes?: string | null;
    drill_type?: drill_type | null;
    drill_notes?: string | null;
    problem_tags?: {
      create: Array<{
        tag_id: string;
        role?: tag_role;
        tag_difficulty?: number;
        is_instructive: boolean | null;
      }>;
    };
    solutions?: {
      create: Array<{
        submission_url: string | null;
        language: programming_language;
        github_url: string | null;
      }>;
    };
  };

  const updateData: UpdateData = {};
  
  if (data.platformId !== undefined) updateData.platform_id = data.platformId;
  if (data.title !== undefined) updateData.title = data.title;
  if (data.url !== undefined) updateData.url = data.url;
  if (data.isGreatProblem !== undefined) updateData.is_great_problem = data.isGreatProblem;
  if (data.platformProblemId !== undefined) updateData.platform_problem_id = data.platformProblemId || null;
  if (data.platformDifficulty !== undefined) updateData.platform_difficulty = data.platformDifficulty || null;
  if (data.normalizedDifficulty !== undefined) updateData.normalized_difficulty = data.normalizedDifficulty;
  if (data.simplifiedStatement !== undefined) updateData.simplified_statement = data.simplifiedStatement || null;
  if (data.notes !== undefined) updateData.notes = data.notes || null;
  if (data.drillType !== undefined) updateData.drill_type = data.drillType ?? null;
  if (data.drillNotes !== undefined) updateData.drill_notes = data.drillNotes || null;

  if (data.tags) {
    updateData.problem_tags = {
      create: data.tags.map((t) => ({
        tag_id: t.tagId,
        role: t.role,
        tag_difficulty: t.tagDifficulty,
        is_instructive: t.isInstructive ?? null,
      })),
    };
  }

  if (data.solutions) {
    updateData.solutions = {
      create: data.solutions.map((s) => ({
        submission_url: s.submissionUrl || null,
        language: s.language,
        github_url: s.githubUrl || null,
      })),
    };
  }

  return prisma.problems.update({
    where: { id: data.id },
    data: updateData,
    include: {
      platforms: true,
      problem_tags: {
        include: { tags: true },
      },
      solutions: true,
    },
  });
}

export async function unsafe_deleteProblem(id: string) {
  return prisma.problems.delete({
    where: { id },
  });
}

export async function unsafe_countProblemsByPlatform(platformSlug: string) {
  return prisma.problems.count({
    where: { platforms: { slug: platformSlug } },
  });
}

export async function unsafe_listProblemsByPlatformAndTags(
  platformSlug: string,
  tagSlugs: string[]
) {
  return prisma.problems.findMany({
    where: {
      platforms: { slug: platformSlug },
      problem_tags: {
        some: {
          role: "core",
          tags: { slug: { in: tagSlugs } },
        },
      },
    },
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
