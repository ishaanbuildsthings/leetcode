import { router } from "../trpc";
import { problemRouter } from "./problem.router";
import { tagRouter } from "./tag.router";
import { platformRouter } from "./platform.router";
import { solutionRouter } from "./solution.router";
import { tagParentRouter } from "./tag_parent.router";
import { implementGroupRouter } from "./implement_group.router";
import { mindsolveGroupRouter } from "./mindsolve_group.router";

export const appRouter = router({
  problem: problemRouter,
  tag: tagRouter,
  platform: platformRouter,
  solution: solutionRouter,
  tagParent: tagParentRouter,
  implementGroup: implementGroupRouter,
  mindsolveGroup: mindsolveGroupRouter,
});

export type AppRouter = typeof appRouter;

