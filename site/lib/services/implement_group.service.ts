import { prisma } from "../prisma";

export async function unsafe_listImplementGroups() {
  return prisma.implement_groups.findMany({
    orderBy: { name: "asc" },
  });
}

export async function unsafe_createImplementGroup(data: { name: string }) {
  return prisma.implement_groups.create({
    data: { name: data.name },
  });
}

export async function unsafe_updateImplementGroup(id: string, data: { name?: string }) {
  return prisma.implement_groups.update({
    where: { id },
    data: { name: data.name },
  });
}

export async function unsafe_deleteImplementGroup(id: string) {
  return prisma.implement_groups.delete({
    where: { id },
  });
}
