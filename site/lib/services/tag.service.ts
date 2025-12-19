import { prisma } from "../prisma";

export async function unsafe_createTag(data: { 
  name: string; 
  slug: string; 
  description?: string;
}) {
  return prisma.tags.create({
    data: {
      name: data.name,
      slug: data.slug,
      description: data.description,
    },
  });
}

export async function unsafe_getTagById(id: string) {
  return prisma.tags.findUnique({
    where: { id },
  });
}

export async function unsafe_listTags() {
  return prisma.tags.findMany({
    orderBy: { name: "asc" },
  });
}

export async function unsafe_updateTag(id: string, data: {
  name?: string;
  slug?: string;
  description?: string;
}) {
  return prisma.tags.update({
    where: { id },
    data: {
      name: data.name,
      slug: data.slug,
      description: data.description,
    },
  });
}

export async function unsafe_deleteTag(id: string) {
  return prisma.tags.delete({
    where: { id },
  });
}
