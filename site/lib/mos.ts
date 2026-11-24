import type { FillIn } from "@/components/TemplatePicker";

// Mo's algorithm with Hilbert order (templates/ultimate-template-tool/mos/), on the Misc tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/mos/";

export const MOS: FillIn[] = [
  {
    label: "Mo's algorithm (Hilbert order)",
    title: "Offline range queries by sliding a window: sort the queries by hilbertOrder, then fill in addL / addR / remL / remR",
    folder: "_mos",
    file: "mosAndHilbert",
    ops: [
      ["hilbertOrder(l, r): sort key for the query [l, r]", "log(N)"],
      ["all the window moves together (F = the cost of one add / remove)", "N*sqrt(Q)*F"],
    ],
    githubUrl: GITHUB,
  },
];
