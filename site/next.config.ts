import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // the project root is this folder: a stray package-lock.json one level up would otherwise make Next.js treat
  // code/leetcode as the root, and Turbopack then can't resolve next/font/google's internal module
  turbopack: { root: path.join(__dirname) },
};

export default nextConfig;
