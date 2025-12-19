import { router } from "../trpc";
import { problemRouter } from "./problem.router";
import { tagRouter } from "./tag.router";
import { platformRouter } from "./platform.router";
import { solutionRouter } from "./solution.router";
import { tagParentRouter } from "./tag_parent.router";

export const appRouter = router({
  problem: problemRouter,
  tag: tagRouter,
  platform: platformRouter,
  solution: solutionRouter,
  tagParent: tagParentRouter,
});

export type AppRouter = typeof appRouter;

