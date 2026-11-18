import type { FillIn } from "@/components/TemplatePicker";

// The chess templates (templates/ultimate-template-tool/chess/), on the Misc tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/chess/";

export const CHESS: FillIn[] = [
  {
    label: "Knight distance O(1)",
    title: "Fewest knight moves between two squares: on an infinite board, or from the corner of a board that's infinite in one quarter",
    folder: "_chess",
    file: "KnightDistance",
    ops: [
      ["knightDistanceFullyInfiniteChessboard(x1, y1, x2, y2)", "1"],
      ["knightDistanceFromCorner(x, y), corner (0, 0), x, y >= 0", "1"],
    ],
    githubUrl: GITHUB,
  },
];
