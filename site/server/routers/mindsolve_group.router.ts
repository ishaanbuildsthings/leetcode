import { router, publicProcedure, adminProcedure } from "../trpc";
import { z } from "zod";
import * as mindsolveGroupService from "../../lib/services/mindsolve_group.service";
import { transformMindsolveGroup } from "../../lib/transforms";

export const mindsolveGroupRouter = router({
  list: publicProcedure.query(async () => {
    const groups = await mindsolveGroupService.unsafe_listMindsolveGroups();
    return groups.map(transformMindsolveGroup);
  }),

  create: adminProcedure
    .input(z.object({ name: z.string().min(1) }))
    .mutation(async ({ input }) => {
      const group = await mindsolveGroupService.unsafe_createMindsolveGroup(input);
      return transformMindsolveGroup(group);
    }),

  update: adminProcedure
    .input(z.object({ id: z.string(), name: z.string().min(1) }))
    .mutation(async ({ input }) => {
      const { id, ...data } = input;
      const group = await mindsolveGroupService.unsafe_updateMindsolveGroup(id, data);
      return transformMindsolveGroup(group);
    }),

  delete: adminProcedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ input }) => {
      await mindsolveGroupService.unsafe_deleteMindsolveGroup(input.id);
      return { success: true };
    }),
});
