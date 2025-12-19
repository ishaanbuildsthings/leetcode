import { router, publicProcedure, adminProcedure } from "../trpc";
import { z } from "zod";
import * as tagService from "../../lib/services/tag.service";
import { transformTag } from "../../lib/transforms";

export const tagRouter = router({
  list: publicProcedure.query(async () => {
    const tags = await tagService.unsafe_listTags();
    return tags.map(transformTag);
  }),

  getById: publicProcedure.input(z.object({ id: z.string() })).query(async ({ input }) => {
    const tag = await tagService.unsafe_getTagById(input.id);
    if (!tag) return null;
    return transformTag(tag);
  }),

  create: adminProcedure
    .input(
      z.object({
        name: z.string().min(1),
        slug: z.string().min(1),
        description: z.string().optional(),
      })
    )
    .mutation(async ({ input }) => {
      const tag = await tagService.unsafe_createTag(input);
      return transformTag(tag);
    }),

  update: adminProcedure
    .input(
      z.object({
        id: z.string(),
        name: z.string().min(1).optional(),
        slug: z.string().min(1).optional(),
        description: z.string().optional(),
      })
    )
    .mutation(async ({ input }) => {
      const { id, ...data } = input;
      const tag = await tagService.unsafe_updateTag(id, data);
      return transformTag(tag);
    }),

  delete: adminProcedure.input(z.object({ id: z.string() })).mutation(async ({ input }) => {
    await tagService.unsafe_deleteTag(input.id);
    return { success: true };
  }),
});

