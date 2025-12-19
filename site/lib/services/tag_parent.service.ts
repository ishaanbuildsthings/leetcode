import { prisma } from "@/lib/prisma";

export async function unsafe_createTagParent(data: {
  childTagId: string;
  parentTagId: string;
}) {
  return await prisma.tag_parents.create({
    data: {
      child_tag_id: data.childTagId,
      parent_tag_id: data.parentTagId,
    },
    include: {
      tags_tag_parents_child_tag_idTotags: true,
      tags_tag_parents_parent_tag_idTotags: true,
    },
  });
}

export async function unsafe_deleteTagParent(childTagId: string, parentTagId: string) {
  return await prisma.tag_parents.delete({
    where: {
      child_tag_id_parent_tag_id: {
        child_tag_id: childTagId,
        parent_tag_id: parentTagId,
      },
    },
  });
}

export async function unsafe_listTagParents() {
  return await prisma.tag_parents.findMany({
    include: {
      tags_tag_parents_child_tag_idTotags: true,
      tags_tag_parents_parent_tag_idTotags: true,
    },
  });
}

export async function unsafe_getTagWithHierarchy(tagId: string) {
  const tag = await prisma.tags.findUnique({
    where: { id: tagId },
    include: {
      tag_parents_tag_parents_child_tag_idTotags: {
        include: {
          tags_tag_parents_parent_tag_idTotags: true,
        },
      },
      tag_parents_tag_parents_parent_tag_idTotags: {
        include: {
          tags_tag_parents_child_tag_idTotags: true,
        },
      },
    },
  });
  
  return tag;
}

