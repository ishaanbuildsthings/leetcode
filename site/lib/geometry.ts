import type { FillIn } from "@/components/TemplatePicker";

// The geometry templates (templates/ultimate-template-tool/geometry/), on the Geometry tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/geometry/";

export const GEOMETRY: FillIn[] = [
  {
    label: "polygonArea2(points) O(N)",
    title: "Twice the signed area of a polygon (shoelace), exact in integers: > 0 counterclockwise, < 0 clockwise",
    folder: "_geometry",
    file: "polygonArea",
    ops: [["polygonArea2(points) -> 2 * signed area, corners in order around the polygon", "N"]],
    githubUrl: GITHUB,
  },
];
