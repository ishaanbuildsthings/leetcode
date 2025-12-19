import { router, publicProcedure, adminProcedure } from "../trpc";
import { z } from "zod";
import * as solutionService from "../../lib/services/solution.service";
import { transformSolution } from "../../lib/transforms";

export const solutionRouter = router({
  getById: publicProcedure.input(z.object({ id: z.string() })).query(async ({ input }) => {
    const solution = await solutionService.unsafe_getSolutionById(input.id);
    if (!solution) return null;
    return transformSolution(solution);
  }),

  create: adminProcedure
    .input(
      z.object({
        problemId: z.string(),
        language: z.string().optional(),
        url: z.string().url(),
        solution: z.string().optional(),
      })
    )
    .mutation(async ({ input }) => {
      const solution = await solutionService.unsafe_createSolution(input);
      return transformSolution(solution);
    }),

  delete: adminProcedure.input(z.object({ id: z.string() })).mutation(async ({ input }) => {
    await solutionService.unsafe_deleteSolution(input.id);
    return { success: true };
  }),
});

