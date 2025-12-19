import { router, publicProcedure, adminProcedure } from "../trpc";
import { z } from "zod";
import * as tagParentService from "../../lib/services/tag_parent.service";

export const tagParentRouter = router({
  list: publicProcedure.query(async () => {
    return await tagParentService.unsafe_listTagParents();
  }),

  create: adminProcedure
    .input(
      z.object({
        childTagId: z.string(),
        parentTagId: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      return await tagParentService.unsafe_createTagParent(input);
    }),

  delete: adminProcedure
    .input(
      z.object({
        childTagId: z.string(),
        parentTagId: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      return await tagParentService.unsafe_deleteTagParent(
        input.childTagId,
        input.parentTagId
      );
    }),
});

