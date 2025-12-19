import { PrismaClient } from "../src/generated/prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";
import type { PoolConfig } from "pg";
import { env } from "./env";

declare global {
  var prisma: PrismaClient | undefined;
}

const connectionString =
  env.PRISMA_USE_NON_POOLING === "1"
    ? env.POSTGRES_URL_NON_POOLING
    : env.POSTGRES_PRISMA_URL;

console.log("NODE_ENV:", env.NODE_ENV);
console.log("Parsing connection string to apply SSL config...");

const parsed = new URL(connectionString);
const prismaPgConfig: PoolConfig = {
  host: parsed.hostname,
  port: parseInt(parsed.port),
  user: parsed.username,
  password: parsed.password,
  database: parsed.pathname.slice(1),
  ssl: {
    rejectUnauthorized: false,
  },
};

const adapter = new PrismaPg(prismaPgConfig);

export const prisma =
  globalThis.prisma ??
  new PrismaClient({
    adapter,
    log: env.NODE_ENV === "development" ? ["query", "error", "warn"] : ["error"],
  });

if (process.env.NODE_ENV !== "production") {
  globalThis.prisma = prisma;
} 