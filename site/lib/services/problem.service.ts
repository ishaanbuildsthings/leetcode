import { prisma } from "../prisma";
import { Prisma } from "../../src/generated/prisma/client";
import { tag_role, programming_language, drill_type } from "../../src/generated/prisma/enums";

export async function unsafe_createProblem(data: {
  platformId: string;
  title: string;
  url: string;
  isGreatProblem: boolean;
  isLeetgoat222: boolean;
  isLeetgoatAdvanced: boolean;
  platformProblemId?: string;
  platformDifficulty?: string;
  normalizedDifficulty?: number;
  simplifiedStatement?: string;
  notes?: string;
  drillType?: drill_type | null;
  drillNotes?: string;
  implementGroupId?: string | null;
  mindsolveGroupId?: string | null;
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
      is_leetgoat_222: data.isLeetgoat222,
      is_leetgoat_advanced: data.isLeetgoatAdvanced,
      drill_type: data.drillType ?? null,
      drill_notes: data.drillNotes,
      implement_group_id: data.implementGroupId ?? null,
      mindsolve_group_id: data.mindsolveGroupId ?? null,
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
      implement_groups: true,
      mindsolve_groups: true,
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
      implement_groups: true,
      mindsolve_groups: true,
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
      implement_groups: true,
      mindsolve_groups: true,
    },
    orderBy: { created_at: "desc" },
  });
}

export async function unsafe_listProblemsPaged(opts: {
  page?: number;
  pageSize?: number;
  fullView?: boolean;
  greatOnly?: boolean;
  platformId?: string;
  tagId?: string;
  tagRoles?: { core?: boolean; secondary?: boolean; mention?: boolean };
}) {
  const where: Prisma.problemsWhereInput = {};
  if (opts.greatOnly) where.is_great_problem = true;
  if (opts.platformId) where.platform_id = opts.platformId;
  if (opts.tagId) {
    const roles = opts.tagRoles ?? { core: true, secondary: true, mention: true };
    const enabledRoles: tag_role[] = [];
    if (roles.core) enabledRoles.push(tag_role.core);
    if (roles.secondary) enabledRoles.push(tag_role.secondary);
    if (roles.mention) enabledRoles.push(tag_role.mention);
    where.problem_tags = {
      some: {
        tag_id: opts.tagId,
        OR: [{ role: { in: enabledRoles } }, { role: null }],
      },
    };
  }

  const include = {
    platforms: true,
    problem_tags: { include: { tags: true } },
    solutions: true,
    implement_groups: true,
    mindsolve_groups: true,
  } as const;

  if (opts.fullView) {
    const items = await prisma.problems.findMany({
      where,
      include,
      orderBy: { created_at: "desc" },
    });
    return { items, total: items.length };
  }

  const page = Math.max(1, opts.page ?? 1);
  const pageSize = Math.min(200, Math.max(1, opts.pageSize ?? 20));
  const [items, total] = await Promise.all([
    prisma.problems.findMany({
      where,
      include,
      orderBy: { created_at: "desc" },
      skip: (page - 1) * pageSize,
      take: pageSize,
    }),
    prisma.problems.count({ where }),
  ]);
  return { items, total };
}

export async function unsafe_updateProblem(data: {
  id: string;
  platformId?: string;
  title?: string;
  url?: string;
  isGreatProblem?: boolean;
  isLeetgoat222?: boolean;
  isLeetgoatAdvanced?: boolean;
  platformProblemId?: string;
  platformDifficulty?: string;
  normalizedDifficulty?: number;
  simplifiedStatement?: string;
  notes?: string;
  drillType?: drill_type | null;
  drillNotes?: string;
  implementGroupId?: string | null;
  mindsolveGroupId?: string | null;
  tags?: Array<{ tagId: string; role?: tag_role; tagDifficulty?: number; isInstructive?: boolean }>;
  solutions?: Array<{ submissionUrl?: string; language: programming_language; githubUrl?: string }>;
}) {
  if (data.tags !== undefined) {
    await prisma.problem_tags.deleteMany({
      where: { problem_id: data.id },
    });
  }

  if (data.solutions !== undefined) {
    await prisma.solutions.deleteMany({
      where: { problem_id: data.id },
    });
  }

  type UpdateData = {
    platform_id?: string;
    title?: string;
    url?: string;
    is_great_problem?: boolean;
    is_leetgoat_222?: boolean;
    is_leetgoat_advanced?: boolean;
    platform_problem_id?: string | null;
    platform_difficulty?: string | null;
    normalized_difficulty?: number;
    simplified_statement?: string | null;
    notes?: string | null;
    drill_type?: drill_type | null;
    drill_notes?: string | null;
    implement_group_id?: string | null;
    mindsolve_group_id?: string | null;
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
  if (data.isLeetgoat222 !== undefined) updateData.is_leetgoat_222 = data.isLeetgoat222;
  if (data.isLeetgoatAdvanced !== undefined) updateData.is_leetgoat_advanced = data.isLeetgoatAdvanced;
  if (data.platformProblemId !== undefined) updateData.platform_problem_id = data.platformProblemId || null;
  if (data.platformDifficulty !== undefined) updateData.platform_difficulty = data.platformDifficulty || null;
  if (data.normalizedDifficulty !== undefined) updateData.normalized_difficulty = data.normalizedDifficulty;
  if (data.simplifiedStatement !== undefined) updateData.simplified_statement = data.simplifiedStatement || null;
  if (data.notes !== undefined) updateData.notes = data.notes || null;
  if (data.drillType !== undefined) updateData.drill_type = data.drillType ?? null;
  if (data.drillNotes !== undefined) updateData.drill_notes = data.drillNotes || null;
  if (data.implementGroupId !== undefined) updateData.implement_group_id = data.implementGroupId ?? null;
  if (data.mindsolveGroupId !== undefined) updateData.mindsolve_group_id = data.mindsolveGroupId ?? null;

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
      implement_groups: true,
      mindsolve_groups: true,
    },
  });
}

export async function unsafe_deleteProblem(id: string) {
  return prisma.problems.delete({
    where: { id },
  });
}

export async function unsafe_markDrilled(id: string) {
  return prisma.problems.update({
    where: { id },
    data: {
      drill_completions: { increment: 1 },
      last_drilled_at: new Date(),
    },
    include: {
      platforms: true,
      problem_tags: { include: { tags: true } },
      solutions: true,
      implement_groups: true,
      mindsolve_groups: true,
    },
  });
}

export async function unsafe_undoDrilled(id: string) {
  const current = await prisma.problems.findUnique({
    where: { id },
    select: { drill_completions: true },
  });
  const next = Math.max(0, (current?.drill_completions ?? 0) - 1);
  return prisma.problems.update({
    where: { id },
    data: { drill_completions: next },
    include: {
      platforms: true,
      problem_tags: { include: { tags: true } },
      solutions: true,
      implement_groups: true,
      mindsolve_groups: true,
    },
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
      implement_groups: true,
      mindsolve_groups: true,
    },
    orderBy: { created_at: "desc" },
  });
}
