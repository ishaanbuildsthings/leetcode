import { router, publicProcedure, adminProcedure } from "../trpc";
import { z } from "zod";
import * as implementGroupService from "../../lib/services/implement_group.service";
import { transformImplementGroup } from "../../lib/transforms";

export const implementGroupRouter = router({
  list: publicProcedure.query(async () => {
    const groups = await implementGroupService.unsafe_listImplementGroups();
    return groups.map(transformImplementGroup);
  }),

  create: adminProcedure
    .input(z.object({ name: z.string().min(1) }))
    .mutation(async ({ input }) => {
      const group = await implementGroupService.unsafe_createImplementGroup(input);
      return transformImplementGroup(group);
    }),

  update: adminProcedure
    .input(z.object({ id: z.string(), name: z.string().min(1) }))
    .mutation(async ({ input }) => {
      const { id, ...data } = input;
      const group = await implementGroupService.unsafe_updateImplementGroup(id, data);
      return transformImplementGroup(group);
    }),

  delete: adminProcedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ input }) => {
      await implementGroupService.unsafe_deleteImplementGroup(input.id);
      return { success: true };
    }),
});
