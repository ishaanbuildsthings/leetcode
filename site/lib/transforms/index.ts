import type { tagsModel as tags, platformsModel as platforms, solutionsModel as solutions, problemsModel as problems, problem_tagsModel as problem_tags } from "../../src/generated/prisma/models";
import type { ITag, IPlatform, ISolution, IProblem, IProblemWithRelations } from "./types";

export * from "./types";

export function transformTag(tag: tags): ITag {
  return {
    id: tag.id,
    name: tag.name,
    slug: tag.slug,
    description: tag.description,
  };
}

export function transformPlatform(platform: platforms): IPlatform {
  return {
    id: platform.id,
    name: platform.name,
    slug: platform.slug,
  };
}

export function transformSolution(solution: solutions): ISolution {
  return {
    id: solution.id,
    problemId: solution.problem_id,
    language: solution.language,
    submissionUrl: solution.submission_url,
    githubUrl: solution.github_url,
  };
}

export function transformProblem(problem: problems): IProblem {
  return {
    id: problem.id,
    platformId: problem.platform_id,
    platformProblemId: problem.platform_problem_id,
    title: problem.title,
    url: problem.url,
    platformDifficulty: problem.platform_difficulty,
    normalizedDifficulty: problem.normalized_difficulty,
    simplifiedStatement: problem.simplified_statement,
    notes: problem.notes,
    isGreatProblem: problem.is_great_problem,
  };
}

export function transformProblemWithRelations(
  problem: problems & {
    platforms: platforms;
    problem_tags: Array<problem_tags & { tags: tags }>;
    solutions: solutions[];
  }
): IProblemWithRelations {
  return {
    ...transformProblem(problem),
    platform: transformPlatform(problem.platforms),
    tags: problem.problem_tags.map((pt: problem_tags & { tags: tags }) => ({
      tag: transformTag(pt.tags),
      role: pt.role,
      tagDifficulty: pt.tag_difficulty,
      isInstructive: pt.is_instructive,
    })),
    solutions: problem.solutions.map(transformSolution),
  };
}

