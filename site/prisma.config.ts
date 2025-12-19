import { defineConfig, env } from "prisma/config";
import "dotenv/config";

export default defineConfig({
  schema: "prisma/schema.prisma",
  datasource: {
    url:
      process.env.PRISMA_USE_NON_POOLING === "1"
        ? env("POSTGRES_URL_NON_POOLING")
        : env("POSTGRES_PRISMA_URL"),
  },
});
