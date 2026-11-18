"""Rectangle assign with point reads on a small grid: grid-rect-assign-point-get.

    python3 gen_grid_assign.py     # writes range-queries-2d/grid-rect-assign-point-get/template.{py,cpp}

A cell's value is whichever write covering it came last. Every write gets the next timestamp, and a 2D segment tree
keeps, at the nodes that make up the write's rectangle, the newest timestamp (tags stay where they are put: a newer
write always wins, so nothing has to be pushed down or undone). A point read takes the newest timestamp on its leaf's
path through both trees, and looks up the value written then.
"""
from lib2d import header, indent, wrap_comment, write

FOLDER = "grid-rect-assign-point-get"
OPS = ["pointAssign", "pointGet", "rectAssign"]
COST = "log(R)*log(C)"
DOC = ("Rectangle assign and point get on an R x C grid, O(log R * log C) each. rectAssign(r1, c1, r2, c2, v) makes "
       "every cell of the rectangle v; pointGet(r, c) reads one cell. Every write gets the next timestamp, and a 2D "
       "segment tree keeps the newest timestamp at the nodes that make up the write's rectangle (no push-down: a newer "
       "write always wins, so nothing is ever undone). A read takes the newest timestamp on its cell's path up both "
       "trees and returns the value written at that time. Rows and columns are 0-based and rectangles are inclusive: "
       "rows r1..r2, columns c1..c2. For rectangle sums or maxes after rectangle assigns, there is no log^2 template: "
       "loop the rows with a 1D lazy segment tree each.")
MEMORY = {"layout": "2n-iterative", "node": "stamp[4*R*C]", "tags": "none", "other": "vals[1*R*C]",
          "note": "2R row-nodes by 2C column-nodes of timestamps, flat; vals holds the grid's values then one more per "
                  "write (the value written at each timestamp)"}
CTOR = "O(R*C) -- grid: R rows of C values each; needs R >= 1 and C >= 1, else {err}"
POINT_RULE = "needs 0 <= r < R and 0 <= c < C, else {err}"
RECT_RULE = "needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else {err}"


def python():
    err = "IndexError"
    py = wrap_comment(DOC, "#") + ["class RectAssignPointGet2D:", '    __slots__ = ("R", "C", "W", "stamp", "vals")', ""]
    py += indent(wrap_comment(CTOR.format(err="ValueError"), "#"))
    py += ["    def __init__(self, grid):",
           "        R = self.R = len(grid)",
           "        C = self.C = len(grid[0]) if R else 0",
           "        if R < 1 or C < 1 or any(len(row) != C for row in grid):",
           '            raise ValueError("RectAssignPointGet2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")',
           "        W = self.W = 2 * C",
           "        stamp = self.stamp = [0] * (2 * R * W)",
           "        vals = self.vals = [None]  # vals[t]: the value written at timestamp t; 1..R*C are the grid's own",
           "        for r in range(R):",
           "            base = (r + R) * W + C",
           "            for c in range(C):",
           "                vals.append(grid[r][c])",
           "                stamp[base + c] = len(vals) - 1",
           "",
           "    # one column tree (the one starting at `base`): columns c1..c2 get timestamp t",
           "    def _mark(self, base, c1, c2, t):",
           "        stamp = self.stamp",
           "        lo = c1 + self.C",
           "        hi = c2 + self.C + 1",
           "        while lo < hi:",
           "            if lo & 1:",
           "                stamp[base + lo] = t",
           "                lo += 1",
           "            if hi & 1:",
           "                hi -= 1",
           "                stamp[base + hi] = t",
           "            lo >>= 1",
           "            hi >>= 1",
           "",
           "    # every cell of the rectangle gets the next timestamp, which stands for v",
           "    def _write(self, r1, c1, r2, c2, v):",
           "        self.vals.append(v)",
           "        t = len(self.vals) - 1",
           "        W = self.W",
           "        lo = r1 + self.R",
           "        hi = r2 + self.R + 1",
           "        while lo < hi:",
           "            if lo & 1:",
           "                self._mark(lo * W, c1, c2, t)",
           "                lo += 1",
           "            if hi & 1:",
           "                hi -= 1",
           "                self._mark(hi * W, c1, c2, t)",
           "            lo >>= 1",
           "            hi >>= 1",
           ""]
    py += indent(wrap_comment(f"O(log R * log C) -- every cell of rows r1..r2, columns c1..c2 becomes v; "
                              f"{RECT_RULE.format(err=err)}", "#"))
    py += ["    def rectAssign(self, r1, c1, r2, c2, v):",
           "        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):",
           '            raise IndexError(f"rectAssign: needs 0 <= r1 <= r2 < R = {self.R} and 0 <= c1 <= c2 < C = {self.C}, "',
           '                             f"got r1 = {r1}, c1 = {c1}, r2 = {r2}, c2 = {c2}")',
           "        self._write(r1, c1, r2, c2, v)",
           ""]
    py += indent(wrap_comment(f"O(log R * log C) -- the cell (r, c) becomes v; {POINT_RULE.format(err=err)}", "#"))
    py += ["    def pointAssign(self, r, c, v):",
           "        if not (0 <= r < self.R and 0 <= c < self.C):",
           '            raise IndexError(f"pointAssign: needs 0 <= r < R = {self.R} and 0 <= c < C = {self.C}, "',
           '                             f"got r = {r}, c = {c}")',
           "        self._write(r, c, r, c, v)",
           ""]
    py += indent(wrap_comment(f"O(log R * log C) -- the value at (r, c); {POINT_RULE.format(err=err)}", "#"))
    py += ["    def pointGet(self, r, c):",
           "        R, C, W, stamp = self.R, self.C, self.W, self.stamp",
           "        if not (0 <= r < R and 0 <= c < C):",
           '            raise IndexError(f"pointGet: needs 0 <= r < R = {R} and 0 <= c < C = {C}, got r = {r}, c = {c}")',
           "        best = 0",
           "        pr = r + R",
           "        while pr:",
           "            base = pr * W",
           "            pc = c + C",
           "            while pc:",
           "                s = stamp[base + pc]",
           "                if s > best:",
           "                    best = s",
           "                pc >>= 1",
           "            pr >>= 1",
           "        return self.vals[best]"]
    return py


def cpp():
    err = "throws out_of_range"
    c = [""] + wrap_comment(DOC, "//") + ["template <typename T>", "struct RectAssignPointGet2D {",
                                          "    int R, C, W;",
                                          "    vector<int> stamp;  // per row-node, per column-node: the newest timestamp put there",
                                          "    vector<T> vals;  // vals[t]: the value written at timestamp t; 1..R*C are the grid's own", ""]
    c += indent(wrap_comment(CTOR.format(err="throws invalid_argument"), "//"))
    c += ["    explicit RectAssignPointGet2D(const vector<vector<T>>& grid) {",
          "        R = (int)grid.size();",
          "        C = R ? (int)grid[0].size() : 0;",
          '        if (R < 1 || C < 1) throw invalid_argument("RectAssignPointGet2D: needs R >= 1 rows of C >= 1 values");',
          "        for (const auto& row : grid)",
          '            if ((int)row.size() != C) throw invalid_argument("RectAssignPointGet2D: every row needs the same C values");',
          "        W = 2 * C;",
          "        stamp.assign((size_t)2 * R * W, 0);",
          "        vals.reserve((size_t)R * C + 1);",
          "        vals.push_back(T());",
          "        for (int r = 0; r < R; r++)",
          "            for (int c = 0; c < C; c++) {",
          "                vals.push_back(grid[r][c]);",
          "                stamp[(size_t)(r + R) * W + C + c] = (int)vals.size() - 1;",
          "            }",
          "    }",
          "",
          "    // one column tree (the one starting at `base`): columns c1..c2 get timestamp t",
          "    void mark(size_t base, int c1, int c2, int t) {",
          "        int* s = stamp.data() + base;",
          "        for (int lo = c1 + C, hi = c2 + C + 1; lo < hi; lo >>= 1, hi >>= 1) {",
          "            if (lo & 1) s[lo++] = t;",
          "            if (hi & 1) s[--hi] = t;",
          "        }",
          "    }",
          "",
          "    // every cell of the rectangle gets the next timestamp, which stands for v",
          "    void write(int r1, int c1, int r2, int c2, T v) {",
          "        vals.push_back(v);",
          "        int t = (int)vals.size() - 1;",
          "        for (int lo = r1 + R, hi = r2 + R + 1; lo < hi; lo >>= 1, hi >>= 1) {",
          "            if (lo & 1) mark((size_t)lo++ * W, c1, c2, t);",
          "            if (hi & 1) mark((size_t)--hi * W, c1, c2, t);",
          "        }",
          "    }",
          ""]
    c += indent(wrap_comment(f"O(log R * log C) -- every cell of rows r1..r2, columns c1..c2 becomes v; "
                             f"{RECT_RULE.format(err=err)}", "//"))
    c += ["    void rectAssign(int r1, int c1, int r2, int c2, T v) {",
          "        if (!(0 <= r1 && r1 <= r2 && r2 < R && 0 <= c1 && c1 <= c2 && c2 < C))",
          '            throw out_of_range("rectAssign: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");',
          "        write(r1, c1, r2, c2, v);",
          "    }",
          ""]
    c += indent(wrap_comment(f"O(log R * log C) -- the cell (r, c) becomes v; {POINT_RULE.format(err=err)}", "//"))
    c += ["    void pointAssign(int r, int c, T v) {",
          '        if (!(0 <= r && r < R && 0 <= c && c < C)) throw out_of_range("pointAssign: needs 0 <= r < R and 0 <= c < C");',
          "        write(r, c, r, c, v);",
          "    }",
          ""]
    c += indent(wrap_comment(f"O(log R * log C) -- the value at (r, c); {POINT_RULE.format(err=err)}", "//"))
    c += ["    T pointGet(int r, int c) const {",
          '        if (!(0 <= r && r < R && 0 <= c && c < C)) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");',
          "        int best = 0;",
          "        for (int pr = r + R; pr; pr >>= 1) {",
          "            const int* s = stamp.data() + (size_t)pr * W;",
          "            for (int pc = c + C; pc; pc >>= 1)",
          "                if (s[pc] > best) best = s[pc];",
          "        }",
          "        return vals[best];",
          "    }",
          "};"]
    return c


def main():
    costs = {op: COST for op in OPS}
    args = (OPS, "seg-tree-kept-tags", costs, "R*C", MEMORY, "grid")
    write(FOLDER, header(FOLDER, "py", *args) + python(), header(FOLDER, "cpp", *args) + cpp())
    print("grid rect assign: 1 folder")


if __name__ == "__main__":
    main()
