import { router, publicProcedure, adminProcedure } from "../trpc";
import { z } from "zod";
import * as problemService from "../../lib/services/problem.service";
import { transformProblemWithRelations } from "../../lib/transforms";

export const problemRouter = router({
  list: publicProcedure.query(async () => {
    const problems = await problemService.unsafe_listProblems();
    return problems.map(transformProblemWithRelations);
  }),

  getById: publicProcedure.input(z.object({ id: z.string() })).query(async ({ input }) => {
    const problem = await problemService.unsafe_getProblemById(input.id);
    if (!problem) return null;
    return transformProblemWithRelations(problem);
  }),

  create: adminProcedure
    .input(
      z.object({
        platformId: z.string(),
        title: z.string().min(1),
        url: z.string().url(),
        isGreatProblem: z.boolean(),
        platformProblemId: z.string().optional(),
        platformDifficulty: z.string().optional(),
        normalizedDifficulty: z.number().int().min(1).max(10).optional(),
        notes: z.string().optional(),
        tags: z
          .array(
            z.object({
              tagId: z.string(),
              role: z.enum(["core", "secondary", "mention"]).optional(),
              tagDifficulty: z.number().int().optional(),
              isInstructive: z.boolean().optional(),
            })
          )
          .optional(),
      })
    )
    .mutation(async ({ input }) => {
      const problem = await problemService.unsafe_createProblem(input);
      return transformProblemWithRelations(problem);
    }),

  delete: adminProcedure.input(z.object({ id: z.string() })).mutation(async ({ input }) => {
    await problemService.unsafe_deleteProblem(input.id);
    return { success: true };
  }),
});

