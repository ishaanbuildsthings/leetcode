import { prisma } from "../prisma";

export async function unsafe_createSolution(data: {
  problemId: string;
  language?: string;
  url: string;
  solution?: string;
}) {
  return prisma.solutions.create({
    data: {
      problem_id: data.problemId,
      language: data.language,
      url: data.url,
      solution: data.solution,
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

