"""Small grid, rectangle chmax with rectangle max (and chmin with min): a 2D segment tree whose tags are never pushed
down.

    python3 gen_grid_tags.py       # writes range-queries-2d/grid-kept-tags-<max|min>/template.{py,cpp}

A tree of trees can't push a tag down its outer tree (a row-node's tag would have to be merged into two whole column
trees). For chmax that isn't needed: a tag can stay where it was put, and a query collects the tags it passes.
"""
from gen_grid_static import (POINT_RULE_CPP, POINT_RULE_PY, RECT_RULE_CPP, RECT_RULE_PY, cpp_point_check, cpp_rect_check, emit,
                             py_grid_check, py_point_check, py_rect_check)
from lib2d import AGGS, indent, wrap_comment

CORNERS = [("LteLte", "<=", "<="), ("LteGte", "<=", ">="), ("GteLte", ">=", "<="), ("GteGte", ">=", ">=")]


def kept_tags(kind):
    a = AGGS[kind]
    cls = f"RectCh{kind}Rect{a.cap}2D"
    better = ">" if kind == "max" else "<"
    upd, pupd = f"rectCh{kind}", f"pointCh{kind}"
    ident_py = "NEG" if kind == "max" else "POS"
    none = a.none_cpp
    ops = [upd, pupd, "pointGet", a.rect, a.all] + [f"{kind}{n}" for n, _, _ in CORNERS]
    costs = {op: "log(R)*log(C)" for op in ops}
    costs[a.all] = "1"
    memory = {"layout": "2n-iterative", "node": "fullBest[4*R*C] partBest[4*R*C]", "tags": "fullTag[4*R*C] partTag[4*R*C]",
              "note": "per row-node two column trees (updates covering all of its rows; updates touching any of its rows), each "
                      "a tag array and a best-below array, 2R row-nodes by 2C column-nodes, flat"}
    doc = (f"Rectangle ch{kind} and rectangle {kind} on an R x C grid, O(log R * log C) each: a 2D segment tree whose tags "
           f"stay where they are put (no push-down, which a tree of trees can't do). {upd}(r1, c1, r2, c2, v) makes every "
           f"cell of the rectangle {kind}(itself, v). Every row-node keeps two column trees: one for the updates that cover "
           f"all of its rows, and one for the updates that touch any of its rows. A query takes, from the row-nodes that "
           f"make up its rows, the second kind, and from the row-nodes above those, the first kind (an update covering a "
           f"whole row-node above covers the query's rows too). Each column tree works the same way one level down. This "
           f"only works because ch{kind} never has to be undone: there is no rectangle assign or add here. A cell can be "
           f"empty and queries only see set cells. Rows and columns are 0-based and rectangles are inclusive: rows "
           f"r1..r2, columns c1..c2.")

    py = [f'{ident_py} = float("{"-inf" if kind == "max" else "inf"}")  # an empty cell', "", ""]
    py += wrap_comment(doc + f" An empty cell is None in the grid, and a {kind} over no set cell is None.", "#") + [f"class {cls}:"]
    py.append('    __slots__ = ("R", "C", "W", "best", "fullTag", "fullBest", "partTag", "partBest")')
    py += ["", "    # O(R*C) -- grid: R rows of C values each (None = an empty cell); needs R >= 1 and C >= 1, else ValueError", "    def __init__(self, grid):"]
    py += indent(py_grid_check(cls) + [
        "W = self.W = 2 * C",
        f"self.fullTag = [{ident_py}] * (2 * R * W)",
        f"self.partTag = [{ident_py}] * (2 * R * W)",
        f"full = self.fullBest = [{ident_py}] * (2 * R * W)",
        f"best = {ident_py}",
        "for r in range(R):",
        "    base = (r + R) * W",
        "    i = base + C",
        "    for v in grid[r]:",
        "        if v is not None:",
        "            full[i] = v",
        f"            if v {better} best:",
        "                best = v",
        "        i += 1",
        "    for pc in range(C - 1, 0, -1):",
        "        x = full[base + 2 * pc]",
        "        y = full[base + 2 * pc + 1]",
        f"        full[base + pc] = x if x {better} y else y",
        "part = self.partBest = full[:]  # a single row: the two trees agree",
        "for pr in range(R - 1, 0, -1):",
        "    base = pr * W",
        "    lo = 2 * base",
        "    hi = lo + W",
        "    for pc in range(1, W):",
        "        x = part[lo + pc]",
        "        y = part[hi + pc]",
        f"        part[base + pc] = x if x {better} y else y",
        "self.best = best",
    ], 2) + [""]
    py += ["    # one column tree (the one starting at `base`): columns c1..c2 become " + kind + "(themselves, v)", "    def _colsUpdate(self, tag, best, base, c1, c2, v):"]
    py += indent([
        "C = self.C",
        "lc = c1 + C",
        "rc = c2 + C + 1",
        "a = lc >> 1  # every node above the two ends has v somewhere below it now",
        "b = (rc - 1) >> 1",
        "while a or b:",
        f"    if a and v {better} best[base + a]:",
        "        best[base + a] = v",
        f"    if b and v {better} best[base + b]:",
        "        best[base + b] = v",
        "    a >>= 1",
        "    b >>= 1",
        "while lc < rc:",
        "    if lc & 1:",
        f"        if v {better} tag[base + lc]:",
        "            tag[base + lc] = v",
        f"            if v {better} best[base + lc]:",
        "                best[base + lc] = v",
        "        lc += 1",
        "    if rc & 1:",
        "        rc -= 1",
        f"        if v {better} tag[base + rc]:",
        "            tag[base + rc] = v",
        f"            if v {better} best[base + rc]:",
        "                best[base + rc] = v",
        "    lc >>= 1",
        "    rc >>= 1",
    ], 2) + [""]
    py += [f"    # one column tree: the {kind} over columns c1..c2", "    def _colsQuery(self, tag, best, base, c1, c2):"]
    py += indent([
        "C = self.C",
        "lc = c1 + C",
        "rc = c2 + C + 1",
        f"res = {ident_py}",
        "a = lc >> 1  # a tag on a node above either end covers that end, which is inside c1..c2",
        "b = (rc - 1) >> 1",
        "while a or b:",
        "    if a:",
        "        x = tag[base + a]",
        f"        if x {better} res:",
        "            res = x",
        "    if b:",
        "        x = tag[base + b]",
        f"        if x {better} res:",
        "            res = x",
        "    a >>= 1",
        "    b >>= 1",
        "while lc < rc:",
        "    if lc & 1:",
        "        x = best[base + lc]",
        f"        if x {better} res:",
        "            res = x",
        "        lc += 1",
        "    if rc & 1:",
        "        rc -= 1",
        "        x = best[base + rc]",
        f"        if x {better} res:",
        "            res = x",
        "    lc >>= 1",
        "    rc >>= 1",
        "return res",
    ], 2) + [""]
    py += ["    def _update(self, r1, c1, r2, c2, v):"]
    py += indent([
        "R, W = self.R, self.W",
        "fullTag, fullBest, partTag, partBest = self.fullTag, self.fullBest, self.partTag, self.partBest",
        "cols = self._colsUpdate",
        f"if v {better} self.best:",
        "    self.best = v",
        "lr = r1 + R",
        "rr = r2 + R + 1",
        "a = lr >> 1  # every row-node above the two ends is touched",
        "b = (rr - 1) >> 1",
        "while a or b:",
        "    if a:",
        "        cols(partTag, partBest, a * W, c1, c2, v)",
        "    if b and b != a:",
        "        cols(partTag, partBest, b * W, c1, c2, v)",
        "    a >>= 1",
        "    b >>= 1",
        "while lr < rr:",
        "    if lr & 1:",
        "        cols(fullTag, fullBest, lr * W, c1, c2, v)",
        "        cols(partTag, partBest, lr * W, c1, c2, v)",
        "        lr += 1",
        "    if rr & 1:",
        "        rr -= 1",
        "        cols(fullTag, fullBest, rr * W, c1, c2, v)",
        "        cols(partTag, partBest, rr * W, c1, c2, v)",
        "    lr >>= 1",
        "    rr >>= 1",
    ], 2) + [""]
    py += ["    def _query(self, r1, c1, r2, c2):"]
    py += indent([
        "R, W = self.R, self.W",
        "fullTag, fullBest, partTag, partBest = self.fullTag, self.fullBest, self.partTag, self.partBest",
        "cols = self._colsQuery",
        f"res = {ident_py}",
        "lr = r1 + R",
        "rr = r2 + R + 1",
        "a = lr >> 1  # an update covering a whole row-node above either end covers that end's row",
        "b = (rr - 1) >> 1",
        "while a or b:",
        "    if a:",
        "        x = cols(fullTag, fullBest, a * W, c1, c2)",
        f"        if x {better} res:",
        "            res = x",
        "    if b and b != a:",
        "        x = cols(fullTag, fullBest, b * W, c1, c2)",
        f"        if x {better} res:",
        "            res = x",
        "    a >>= 1",
        "    b >>= 1",
        "while lr < rr:",
        "    if lr & 1:",
        "        x = cols(partTag, partBest, lr * W, c1, c2)",
        f"        if x {better} res:",
        "            res = x",
        "        lr += 1",
        "    if rr & 1:",
        "        rr -= 1",
        "        x = cols(partTag, partBest, rr * W, c1, c2)",
        f"        if x {better} res:",
        "            res = x",
        "    lr >>= 1",
        "    rr >>= 1",
        f"return None if res == {ident_py} else res",
    ], 2) + [""]
    cost = "O(log R * log C)"
    py += indent(wrap_comment(f"{cost} -- every cell of rows r1..r2, columns c1..c2 becomes {kind}(itself, v); an empty cell becomes v; {RECT_RULE_PY}", "#"))
    py.append(f"    def {upd}(self, r1, c1, r2, c2, v):")
    py += indent(py_rect_check(upd) + ["self._update(r1, c1, r2, c2, v)"], 2) + [""]
    py += indent(wrap_comment(f"{cost} -- the cell at (r, c) becomes {kind}(itself, v); an empty cell becomes v; {POINT_RULE_PY}", "#"))
    py.append(f"    def {pupd}(self, r, c, v):")
    py += indent(py_point_check(pupd) + ["self._update(r, c, r, c, v)"], 2) + [""]
    py += indent(wrap_comment(f"{cost} -- the value at (r, c), None if the cell is empty; {POINT_RULE_PY}", "#"))
    py.append("    def pointGet(self, r, c):")
    py += indent(py_point_check("pointGet") + ["return self._query(r, c, r, c)"], 2) + [""]
    py += indent(wrap_comment(f"{cost} -- {kind} of the set cells in rows r1..r2, columns c1..c2 (None if there are none); {RECT_RULE_PY}", "#"))
    py.append(f"    def {a.rect}(self, r1, c1, r2, c2):")
    py += indent(py_rect_check(a.rect) + ["return self._query(r1, c1, r2, c2)"], 2) + [""]
    for n, rs, cs in CORNERS:
        r_lo, r_hi = ("0", "r") if rs == "<=" else ("r", "self.R - 1")
        c_lo, c_hi = ("0", "c") if cs == "<=" else ("c", "self.C - 1")
        py += indent(wrap_comment(f"{cost} -- {kind} of the set cells with row {rs} r and column {cs} c (None if there are none); {POINT_RULE_PY}", "#"))
        py.append(f"    def {kind}{n}(self, r, c):")
        py += indent(py_point_check(f"{kind}{n}") + [f"return self._query({r_lo}, {c_lo}, {r_hi}, {c_hi})"], 2) + [""]
    py += [f"    # O(1) -- {kind} of every set cell (None if there are none)", f"    def {a.all}(self):",
           f"        return None if self.best == {ident_py} else self.best"]

    cpp = wrap_comment(doc + f" The (R, C) constructor starts with every cell empty, and a {kind} over no set cell is {none}.", "//")
    cpp += ["// T is any integer type (int, long long, ...).", "template <typename T>", f"struct {cls} {{",
            f"    static constexpr T {none} = numeric_limits<T>::{'min' if kind == 'max' else 'max'}();  // what a {kind} over no set cell gives",
            "    int R, C, W;", f"    T best = {none};", "    vector<T> fullTag, fullBest, partTag, partBest;", "",
            "    // O(R*C) -- R rows by C columns, every cell empty; needs R >= 1 and C >= 1, else throws invalid_argument",
            f"    {cls}(int rows, int cols) : R(rows), C(cols), W(2 * cols) {{",
            f'        if (R < 1 || C < 1) throw invalid_argument("{cls}: needs R >= 1 and C >= 1");',
            f"        fullTag.assign((size_t)2 * R * W, {none});", "        fullBest = partTag = partBest = fullTag;", "    }", "",
            "    // O(R*C) -- grid: R rows of C values each, every cell set; needs R >= 1 and C >= 1, else throws invalid_argument",
            f"    explicit {cls}(const vector<vector<T>>& grid)", f"        : {cls}((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {{"]
    cpp += indent([
        "for (int r = 0; r < R; r++) {",
        f'    if ((int)grid[r].size() != C) throw invalid_argument("{cls}: every row needs the same C values");',
        "    int base = (r + R) * W;",
        "    for (int c = 0; c < C; c++) {",
        "        fullBest[base + C + c] = grid[r][c];",
        f"        best = {kind}(best, grid[r][c]);",
        "    }",
        f"    for (int pc = C - 1; pc >= 1; pc--) fullBest[base + pc] = {kind}(fullBest[base + 2 * pc], fullBest[base + 2 * pc + 1]);",
        "}",
        "partBest = fullBest;  // a single row: the two trees agree",
        "for (int pr = R - 1; pr >= 1; pr--) {",
        "    int base = pr * W, lo = 2 * base, hi = lo + W;",
        f"    for (int pc = 1; pc < W; pc++) partBest[base + pc] = {kind}(partBest[lo + pc], partBest[hi + pc]);",
        "}",
    ], 2) + ["    }", ""]
    cpp += [f"    // one column tree (the one starting at `base`): columns c1..c2 become {kind}(themselves, v)",
            "    void colsUpdate(HotVector<T>& tag, HotVector<T>& bst, int base, int c1, int c2, T v) {"]
    cpp += indent([
        "int lc = c1 + C, rc = c2 + C + 1;",
        "// every node above the two ends has v somewhere below it now",
        f"for (int a = lc >> 1; a >= 1; a >>= 1) bst[base + a] = {kind}(bst[base + a], v);",
        f"for (int b = (rc - 1) >> 1; b >= 1; b >>= 1) bst[base + b] = {kind}(bst[base + b], v);",
        "for (; lc < rc; lc >>= 1, rc >>= 1) {",
        "    if (lc & 1) {",
        f"        tag[base + lc] = {kind}(tag[base + lc], v);",
        f"        bst[base + lc] = {kind}(bst[base + lc], v);",
        "        lc++;",
        "    }",
        "    if (rc & 1) {",
        "        --rc;",
        f"        tag[base + rc] = {kind}(tag[base + rc], v);",
        f"        bst[base + rc] = {kind}(bst[base + rc], v);",
        "    }",
        "}",
    ], 2) + ["    }", ""]
    cpp += [f"    // one column tree: the {kind} over columns c1..c2", "    T colsQuery(const HotVector<T>& tag, const HotVector<T>& bst, int base, int c1, int c2) const {"]
    cpp += indent([
        "int lc = c1 + C, rc = c2 + C + 1;",
        f"T res = {none};",
        "// a tag on a node above either end covers that end, which is inside c1..c2",
        f"for (int a = lc >> 1; a >= 1; a >>= 1) res = {kind}(res, tag[base + a]);",
        f"for (int b = (rc - 1) >> 1; b >= 1; b >>= 1) res = {kind}(res, tag[base + b]);",
        "for (; lc < rc; lc >>= 1, rc >>= 1) {",
        f"    if (lc & 1) res = {kind}(res, bst[base + lc++]);",
        f"    if (rc & 1) res = {kind}(res, bst[base + --rc]);",
        "}",
        "return res;",
    ], 2) + ["    }", ""]
    cpp += ["    void update(int r1, int c1, int r2, int c2, T v) {"]
    cpp += indent([
        f"best = {kind}(best, v);",
        "int lr = r1 + R, rr = r2 + R + 1;",
        "// every row-node above the two ends is touched",
        "for (int a = lr >> 1; a >= 1; a >>= 1) colsUpdate(partTag, partBest, a * W, c1, c2, v);",
        "for (int b = (rr - 1) >> 1; b >= 1; b >>= 1) colsUpdate(partTag, partBest, b * W, c1, c2, v);",
        "for (; lr < rr; lr >>= 1, rr >>= 1) {",
        "    if (lr & 1) {",
        "        colsUpdate(fullTag, fullBest, lr * W, c1, c2, v);",
        "        colsUpdate(partTag, partBest, lr * W, c1, c2, v);",
        "        lr++;",
        "    }",
        "    if (rr & 1) {",
        "        --rr;",
        "        colsUpdate(fullTag, fullBest, rr * W, c1, c2, v);",
        "        colsUpdate(partTag, partBest, rr * W, c1, c2, v);",
        "    }",
        "}",
    ], 2) + ["    }", ""]
    cpp += ["    T query(int r1, int c1, int r2, int c2) const {"]
    cpp += indent([
        f"T res = {none};",
        "int lr = r1 + R, rr = r2 + R + 1;",
        "// an update covering a whole row-node above either end covers that end's row",
        f"for (int a = lr >> 1; a >= 1; a >>= 1) res = {kind}(res, colsQuery(fullTag, fullBest, a * W, c1, c2));",
        f"for (int b = (rr - 1) >> 1; b >= 1; b >>= 1) res = {kind}(res, colsQuery(fullTag, fullBest, b * W, c1, c2));",
        "for (; lr < rr; lr >>= 1, rr >>= 1) {",
        f"    if (lr & 1) res = {kind}(res, colsQuery(partTag, partBest, lr++ * W, c1, c2));",
        f"    if (rr & 1) res = {kind}(res, colsQuery(partTag, partBest, --rr * W, c1, c2));",
        "}",
        "return res;",
    ], 2) + ["    }", ""]
    cpp += indent(wrap_comment(f"{cost} -- every cell of rows r1..r2, columns c1..c2 becomes {kind}(itself, v); an empty cell becomes v; {RECT_RULE_CPP}", "//"))
    cpp.append(f"    void {upd}(int r1, int c1, int r2, int c2, T v) {{")
    cpp += indent(cpp_rect_check(upd) + ["update(r1, c1, r2, c2, v);"], 2) + ["    }", ""]
    cpp += indent(wrap_comment(f"{cost} -- the cell at (r, c) becomes {kind}(itself, v); an empty cell becomes v; {POINT_RULE_CPP}", "//"))
    cpp.append(f"    void {pupd}(int r, int c, T v) {{")
    cpp += indent(cpp_point_check(pupd) + ["update(r, c, r, c, v);"], 2) + ["    }", ""]
    cpp += indent(wrap_comment(f"{cost} -- the value at (r, c), {none} if the cell is empty; {POINT_RULE_CPP}", "//"))
    cpp.append("    T pointGet(int r, int c) const {")
    cpp += indent(cpp_point_check("pointGet") + ["return query(r, c, r, c);"], 2) + ["    }", ""]
    cpp += indent(wrap_comment(f"{cost} -- {kind} of the set cells in rows r1..r2, columns c1..c2 ({none} if there are none); {RECT_RULE_CPP}", "//"))
    cpp.append(f"    T {a.rect}(int r1, int c1, int r2, int c2) const {{")
    cpp += indent(cpp_rect_check(a.rect) + ["return query(r1, c1, r2, c2);"], 2) + ["    }", ""]
    for n, rs, cs in CORNERS:
        r_lo, r_hi = ("0", "r") if rs == "<=" else ("r", "R - 1")
        c_lo, c_hi = ("0", "c") if cs == "<=" else ("c", "C - 1")
        cpp += indent(wrap_comment(f"{cost} -- {kind} of the set cells with row {rs} r and column {cs} c ({none} if there are none); {POINT_RULE_CPP}", "//"))
        cpp.append(f"    T {kind}{n}(int r, int c) const {{")
        cpp += indent(cpp_point_check(f"{kind}{n}") + [f"return query({r_lo}, {c_lo}, {r_hi}, {c_hi});"], 2) + ["    }", ""]
    cpp += [f"    // O(1) -- {kind} of every set cell ({none} if there are none)", f"    T {a.all}() const {{", "        return best;", "    }", "};"]
    emit(f"grid-kept-tags-{kind}", ops, "seg-tree-kept-tags", costs, "R*C", memory, py, cpp, [("empty-cells", "yes")])


def main():
    kept_tags("max")
    kept_tags("min")
    print("grid kept tags: 2 folders")


if __name__ == "__main__":
    main()
