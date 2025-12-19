import { prisma } from "../prisma";

export async function unsafe_createPlatform(data: { name: string; slug: string }) {
  return prisma.platforms.create({
    data: {
      name: data.name,
      slug: data.slug,
    },
  });
}

export async function unsafe_getPlatformById(id: string) {
  return prisma.platforms.findUnique({
    where: { id },
  });
}

export async function unsafe_listPlatforms() {
  return prisma.platforms.findMany({
    orderBy: { name: "asc" },
  });
}

export async function unsafe_updatePlatform(id: string, data: {
  name?: string;
  slug?: string;
}) {
  return prisma.platforms.update({
    where: { id },
    data: {
      name: data.name,
      slug: data.slug,
    },
  });
}

export async function unsafe_deletePlatform(id: string) {
  return prisma.platforms.delete({
    where: { id },
  });
}
