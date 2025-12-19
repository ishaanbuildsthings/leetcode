import { router, publicProcedure, adminProcedure } from "../trpc";
import { z } from "zod";
import * as platformService from "../../lib/services/platform.service";
import { transformPlatform } from "../../lib/transforms";

export const platformRouter = router({
  list: publicProcedure.query(async () => {
    const platforms = await platformService.unsafe_listPlatforms();
    return platforms.map(transformPlatform);
  }),

  getById: publicProcedure.input(z.object({ id: z.string() })).query(async ({ input }) => {
    const platform = await platformService.unsafe_getPlatformById(input.id);
    if (!platform) return null;
    return transformPlatform(platform);
  }),

  create: adminProcedure
    .input(
      z.object({
        name: z.string().min(1),
        slug: z.string().min(1),
      })
    )
    .mutation(async ({ input }) => {
      const platform = await platformService.unsafe_createPlatform(input);
      return transformPlatform(platform);
    }),

  update: adminProcedure
    .input(
      z.object({
        id: z.string(),
        name: z.string().min(1).optional(),
        slug: z.string().min(1).optional(),
      })
    )
    .mutation(async ({ input }) => {
      const { id, ...data } = input;
      const platform = await platformService.unsafe_updatePlatform(id, data);
      return transformPlatform(platform);
    }),

  delete: adminProcedure.input(z.object({ id: z.string() })).mutation(async ({ input }) => {
    await platformService.unsafe_deletePlatform(input.id);
    return { success: true };
  }),
});

