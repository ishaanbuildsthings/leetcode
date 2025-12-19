import { prisma } from "../prisma";
import { programming_language } from "../../src/generated/prisma/enums";

export async function unsafe_createSolution(data: {
  problemId: string;
  language: programming_language;
  submissionUrl?: string;
  githubUrl?: string;
}) {
  return prisma.solutions.create({
    data: {
      problem_id: data.problemId,
      language: data.language,
      submission_url: data.submissionUrl,
      github_url: data.githubUrl,
    },
  });
}

export async function unsafe_getSolutionById(id: string) {
  return prisma.solutions.findUnique({
    where: { id },
  });
}

export async function unsafe_deleteSolution(id: string) {
  return prisma.solutions.delete({
    where: { id },
  });
}

