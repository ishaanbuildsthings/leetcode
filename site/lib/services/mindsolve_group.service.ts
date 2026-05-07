import { prisma } from "../prisma";

export async function unsafe_listMindsolveGroups() {
  return prisma.mindsolve_groups.findMany({
    orderBy: { name: "asc" },
  });
}

export async function unsafe_createMindsolveGroup(data: { name: string }) {
  return prisma.mindsolve_groups.create({
    data: { name: data.name },
  });
}

export async function unsafe_updateMindsolveGroup(id: string, data: { name?: string }) {
  return prisma.mindsolve_groups.update({
    where: { id },
    data: { name: data.name },
  });
}

export async function unsafe_deleteMindsolveGroup(id: string) {
  return prisma.mindsolve_groups.delete({
    where: { id },
  });
}
