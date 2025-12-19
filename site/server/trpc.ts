import { initTRPC, TRPCError } from "@trpc/server";

export type Context = {
  userId: string | null;
  isAdmin: boolean;
};

const t = initTRPC.context<Context>().create();

export const router = t.router;
export const publicProcedure = t.procedure;

export const adminProcedure = t.procedure.use(async (opts) => {
  if (!opts.ctx.userId) {
    throw new TRPCError({ code: "UNAUTHORIZED", message: "Not authenticated" });
  }
  if (!opts.ctx.isAdmin) {
    throw new TRPCError({ code: "FORBIDDEN", message: "Admin access required" });
  }
  return opts.next({
    ctx: {
      userId: opts.ctx.userId,
      isAdmin: true,
    },
  });
});

