"""Small grid, point updates, any rectangle: the 2D segment tree, one folder per set of aggregates.

    python3 gen_grid_seg.py        # writes range-queries-2d/grid-seg-tree-<aggregates>/template.{py,cpp}

A bottom-up (2N iterative) tree over the rows whose every node is a bottom-up tree over the columns, all in one flat
array per aggregate: entry [pr * 2C + pc] is the aggregate of the rows under row-node pr and the columns under
column-node pc. Nothing is recursive.
"""
from lib2d import AGGS, AGG_ORDER, cost_note, cpp_throw, header, indent, py_raise, read_agg, subsets, wrap_comment, write

CORNERS = [("LteLte", "<=", "<="), ("LteGte", "<=", ">="), ("GteLte", ">=", "<="), ("GteGte", ">=", ">=")]
CLASS = "SegTree2D"


def ops_of(aggs):
    ops = ["pointGet", "pointAssign", "pointAdd", "pointChmax", "pointChmin"]
    for k in aggs:
        ops += [AGGS[k].rect, AGGS[k].all]
        if k in ("min", "max", "sum"):
            ops += [f"{k}{name}" for name, _, _ in CORNERS]
    return ops


def costs_of(aggs):
    q = cost_note(aggs)
    costs = {}
    for op in ops_of(aggs):
        if op == "pointGet" or op.endswith("All"):
            costs[op] = "1"
        elif op.startswith("point"):
            costs[op] = "log(R)*log(C)*log(U) ?" if q else "log(R)*log(C)"
        elif op == "rectGcd":
            costs[op] = "log(R)*log(C)+log(U) ?"
        else:
            costs[op] = "log(R)*log(C)"
    return costs, ("R*C*log(U) ?" if q else "R*C")


def memory_of(aggs):
    return {
        "layout": "2n-iterative",
        "node": " ".join(f"{AGGS[k].arr}[4*R*C]" for k in aggs),
        "note": "one flat array per aggregate, 2R row-nodes by 2C column-nodes; the cells are the last R row-nodes' "
                "last C entries",
    }


def has_empty(aggs):
    """Cells can be empty only where a min or max array can tell an empty cell from a set one."""
    return "min" in aggs or "max" in aggs


def describe(aggs, lang):
    words = ", ".join(AGGS[k].word for k in aggs)
    text = (
        f"2D segment tree ({words}): point updates and any-rectangle queries on an R x C grid, O(log R * log C) each. "
        f"A tree over the rows whose every node is a tree over the columns, bottom-up, in one flat array per "
        f"aggregate. Rows and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2."
    )
    if not has_empty(aggs):
        return text + (" The (R, C) constructor starts with every cell 0." if lang == "cpp" else "")
    empty = []
    none = "None" if lang == "py" else " / ".join(AGGS[k].none_cpp for k in aggs if k in ("min", "max"))
    empty.append(f"a min / max over no set cell is {none}")
    if any(k in aggs for k in ("sum", "gcd", "xor", "or")):
        empty.append("a " + " / ".join(AGGS[k].word for k in aggs if k in ("sum", "gcd", "xor", "or")) + " over none is 0")
    if "and" in aggs:
        empty.append("an AND over none is -1 (every bit set)")
    how_empty = "None in the grid" if lang == "py" else "the (R, C) constructor starts with every cell empty"
    return text + f" A cell can be empty ({how_empty}) and queries only see set cells: {'; '.join(empty)}."


# ------------------------------------------------------------------------------------------------ Python
def py_inner_query(agg, n):
    """The column loop over one row-node whose row starts at `base` (n = indent depth)."""
    body = [
        "lc = cl",
        "rc = cr",
        "while lc < rc:",
        "    if lc & 1:",
        *indent(agg.py_take("res", f"{agg.arr}[base + lc]"), 2),
        "        lc += 1",
        "    if rc & 1:",
        "        rc -= 1",
        *indent(agg.py_take("res", f"{agg.arr}[base + rc]"), 2),
        "    lc >>= 1",
        "    rc >>= 1",
    ]
    return indent(body, n)


def py_template(aggs):
    A = [AGGS[k] for k in aggs]
    rd = read_agg(aggs)
    arrs = ", ".join(a.arr for a in A)
    self_arrs = ", ".join(f"self.{a.arr}" for a in A)
    L = []
    if "gcd" in aggs:
        L += ["from math import gcd", ""]
    if "max" in aggs:
        L.append('NEG = float("-inf")  # an empty cell in the max array')
    if "min" in aggs:
        L.append('POS = float("inf")  # an empty cell in the min array')
    if "max" in aggs or "min" in aggs:
        L.append("")
    L.append("")
    L += wrap_comment(describe(aggs, "py"), "#")
    L.append(f"class {CLASS}:")
    slots = ", ".join(f'"{s}"' for s in ["R", "C", "W"] + [a.arr for a in A])
    L.append(f"    __slots__ = ({slots})")
    L.append("")
    mm = has_empty(aggs)
    L.append("    # O(R*C) -- grid: R rows of C values each" + (" (None = an empty cell)" if mm else "")
             + "; needs R >= 1 and C >= 1, else ValueError")
    L.append("    def __init__(self, grid):")
    b = [
        "R = self.R = len(grid)",
        "C = self.C = len(grid[0]) if R else 0",
        "if R < 1 or C < 1 or any(len(row) != C for row in grid):",
        f'    raise ValueError("{CLASS}: needs a grid of R >= 1 rows, each of the same C >= 1 values")',
        "W = self.W = 2 * C",
    ]
    for a in A:
        b.append(f"{a.arr} = self.{a.arr} = [{a.py_id if mm else 0}] * (2 * R * W)")
    b += ["for r in range(R):", "    base = (r + R) * W", "    i = base + C", "    for v in grid[r]:"]
    if mm:
        b.append("        if v is not None:")
    for a in A:
        b.append(f"{'            ' if mm else '        '}{a.arr}[i] = v")
    b += ["        i += 1", "    for pc in range(C - 1, 0, -1):"]
    for a in A:
        b += indent(a.py_merge(f"{a.arr}[base + pc]", f"{a.arr}[base + 2 * pc]", f"{a.arr}[base + 2 * pc + 1]"), 2)
    b += ["for pr in range(R - 1, 0, -1):", "    base = pr * W", "    lo = 2 * base", "    hi = lo + W", "    for pc in range(1, W):"]
    for a in A:
        b += indent(a.py_merge(f"{a.arr}[base + pc]", f"{a.arr}[lo + pc]", f"{a.arr}[hi + pc]"), 2)
    L += indent(b, 2)
    L.append("")

    # ---- _set
    L.append("    # cell (r, c) = v, then every node above it")
    L.append("    def _set(self, r, c, v):")
    b = ["R, C, W = self.R, self.C, self.W", f"{arrs} = {self_arrs}" if len(A) > 1 else f"{arrs} = {self_arrs}",
         "base = (r + R) * W", "i = base + c + C"]
    for a in A:
        b.append(f"{a.arr}[i] = v")
    b += ["pc = (c + C) >> 1", "while pc:"]
    for a in A:
        b += indent(a.py_merge(f"{a.arr}[base + pc]", f"{a.arr}[base + 2 * pc]", f"{a.arr}[base + 2 * pc + 1]"))
    b += ["    pc >>= 1", "pr = (r + R) >> 1", "while pr:", "    base = pr * W", "    lo = 2 * base", "    hi = lo + W",
          "    pc = c + C", "    while pc:"]
    for a in A:
        b += indent(a.py_merge(f"{a.arr}[base + pc]", f"{a.arr}[lo + pc]", f"{a.arr}[hi + pc]"), 2)
    b += ["        pc >>= 1", "    pr >>= 1"]
    L += indent(b, 2)
    L.append("")

    point_rule = "needs 0 <= r < R and 0 <= c < C, else IndexError"

    def point_check(name):
        return ["if not (0 <= r < self.R and 0 <= c < self.C):"] + indent(py_raise(
            "IndexError", f"{name}: needs 0 <= r < R and 0 <= c < C, got r = {{r}}, c = {{c}}, R = {{self.R}}, C = {{self.C}}", 3))

    is_empty = {"max": "cur == NEG", "min": "cur == POS"}.get(rd.key)
    leaf = f"self.{rd.arr}[(r + self.R) * self.W + c + self.C]"
    if_empty = "; an empty cell becomes v" if mm else ""

    L.append(f"    # O(1) -- the value at (r, c){', None if the cell is empty' if mm else ''}; {point_rule}")
    L.append("    def pointGet(self, r, c):")
    b = point_check("pointGet")
    if is_empty:
        b += [f"cur = {leaf}", f"return None if {is_empty} else cur"]
    else:
        b.append(f"return {leaf}")
    L += indent(b, 2)
    L.append("")

    upd = "O(log R * log C)" + (" gcds" if "gcd" in aggs else "")
    L.append(f"    # {upd} -- the cell at (r, c) becomes v (it may go down as well as up); {point_rule}")
    L.append("    def pointAssign(self, r, c, v):")
    L += indent(point_check("pointAssign") + ["self._set(r, c, v)"], 2)
    L.append("")
    if "pointAdd" in ops_of(aggs):
        L.append(f"    # {upd} -- adds v to the cell at (r, c){if_empty}; {point_rule}")
        L.append("    def pointAdd(self, r, c, v):")
        b = point_check("pointAdd") + [f"cur = {leaf}"]
        b.append(f"self._set(r, c, v if {is_empty} else cur + v)" if is_empty else "self._set(r, c, cur + v)")
        L += indent(b, 2)
        L.append("")
        for name, sym, word in (("pointChmax", ">", "max"), ("pointChmin", "<", "min")):
            L.append(f"    # {upd} -- the cell at (r, c) becomes {word}(itself, v){if_empty}; {point_rule}")
            L.append(f"    def {name}(self, r, c, v):")
            b = point_check(name) + [f"cur = {leaf}"]
            if is_empty:
                b += [f"if {is_empty} or v {sym} cur:", "    self._set(r, c, v)"]
            else:
                b += [f"if v {sym} cur:", "    self._set(r, c, v)"]
            L += indent(b, 2)
            L.append("")

    rect_rule = "needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else IndexError"
    for a in A:
        L.append(f"    def _{a.key}Of(self, r1, c1, r2, c2):")
        b = ["R, C, W = self.R, self.C, self.W", f"{a.arr} = self.{a.arr}", f"res = {a.py_id}", "lr = r1 + R",
             "rr = r2 + R + 1", "cl = c1 + C", "cr = c2 + C + 1", "while lr < rr:", "    if lr & 1:", "        base = lr * W"]
        b += py_inner_query(a, 2)
        b += ["        lr += 1", "    if rr & 1:", "        rr -= 1", "        base = rr * W"]
        b += py_inner_query(a, 2)
        b += ["    lr >>= 1", "    rr >>= 1", f"return {a.py_result('res')}"]
        L += indent(b, 2)
        L.append("")
        what = (f"{a.word} of the set cells in rows r1..r2, columns c1..c2 ({a.none_words_py} if there are none)" if mm
                else f"{a.word} of rows r1..r2, columns c1..c2")
        cost = "O(log R * log C + log U)" if a.key == "gcd" else "O(log R * log C)"
        L += indent(wrap_comment(f"{cost} -- {what}; {rect_rule}", "#"))
        L.append(f"    def {a.rect}(self, r1, c1, r2, c2):")
        L += indent(
            ["if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):"]
            + indent(py_raise("IndexError", f"{a.rect}: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {{r1}}, "
                              "c1 = {c1}, r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}", 3))
            + [f"return self._{a.key}Of(r1, c1, r2, c2)"], 2)
        L.append("")
        L.append(f"    # O(1) -- {a.word} of every set cell ({a.none_words_py} if there are none)" if mm
                 else f"    # O(1) -- {a.word} of the whole grid")
        L.append(f"    def {a.all}(self):")
        root = f"self.{a.arr}[self.W + 1]"
        if a.key in ("min", "max"):
            L += indent([f"res = {root}", f"return {a.py_result('res')}"], 2)
        elif a.key == "gcd":
            L += indent([f"return abs({root})"], 2)
        else:
            L += indent([f"return {root}"], 2)
        L.append("")
        if a.key in ("min", "max", "sum"):
            for name, rs, cs in CORNERS:
                rows = "0, r" if rs == "<=" else "r, self.R - 1"
                cols = "0, c" if cs == "<=" else "c, self.C - 1"
                r_lo, r_hi = rows.split(", ")
                c_lo, c_hi = cols.split(", ")
                L += indent(wrap_comment(
                    f"O(log R * log C) -- {a.word} of the set cells with row {rs} r and column {cs} c"
                    f"{' (None if there are none)' if a.key != 'sum' else ''}; {point_rule}", "#"))
                L.append(f"    def {a.key}{name}(self, r, c):")
                L += indent(point_check(f"{a.key}{name}") + [f"return self._{a.key}Of({r_lo}, {c_lo}, {r_hi}, {c_hi})"], 2)
                L.append("")
    return L


# ------------------------------------------------------------------------------------------------ C++
def cpp_inner_query(agg, n):
    body = [
        "for (int lc = cl, rc = cr; lc < rc; lc >>= 1, rc >>= 1) {",
        f"    if (lc & 1) {agg.cpp_take('res', f'{agg.arr}[base + lc++]')}",
        f"    if (rc & 1) {agg.cpp_take('res', f'{agg.arr}[base + --rc]')}",
        "}",
    ]
    return indent(body, n)


def cpp_template(aggs):
    A = [AGGS[k] for k in aggs]
    rd = read_agg(aggs)
    L = []
    L += wrap_comment(describe(aggs, "cpp"), "//")
    L.append("// T is any integer type (int, long long, ...)" + ("; sums are kept in S (long long for a smaller T)." if "sum" in aggs else "."))
    L.append("template <typename T>")
    L.append(f"struct {CLASS} {{")
    if "sum" in aggs:
        L.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;")
    if "max" in aggs:
        L.append("    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no set cell gives")
    if "min" in aggs:
        L.append("    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set cell gives")
    L.append("    int R, C, W;")
    for a in A:
        L.append(f"    vector<{a.cpp_type}> {a.arr};")
    L.append("")
    if "gcd" in aggs:
        L += ["    static T gcdOf(T a, T b) { return std::gcd(a, b); }", ""]

    def merge_line(a, dst, x, y):
        return f"{a.arr}[{dst}] = {a.cpp_comb(f'{a.arr}[{x}]', f'{a.arr}[{y}]')};"

    mm = has_empty(aggs)
    L.append(f"    // O(R*C) -- R rows by C columns, every cell {'empty' if mm else '0'}; needs R >= 1 and C >= 1, else throws "
             "invalid_argument")
    L.append(f"    {CLASS}(int rows, int cols) : R(rows), C(cols), W(2 * cols) {{")
    L.append(f'        if (R < 1 || C < 1) throw invalid_argument("{CLASS}: needs R >= 1 and C >= 1");')
    for a in A:
        L.append(f"        {a.arr}.assign((size_t)2 * R * W, {a.cpp_id if mm else a.cpp_type + '(0)'});")
    L.append("    }")
    L.append("")
    L.append("    // O(R*C) -- grid: R rows of C values each; needs R >= 1 and C >= 1, else throws invalid_argument")
    L.append(f"    explicit {CLASS}(const vector<vector<T>>& grid)")
    L.append(f"        : {CLASS}((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {{")
    b = ["for (int r = 0; r < R; r++) {",
         f'    if ((int)grid[r].size() != C) throw invalid_argument("{CLASS}: every row needs the same C values");',
         "    int base = (r + R) * W;",
         "    for (int c = 0; c < C; c++) {"]
    for a in A:
        b.append(f"        {a.arr}[base + C + c] = grid[r][c];")
    b += ["    }", "    for (int pc = C - 1; pc >= 1; pc--) {"]
    for a in A:
        b.append("        " + merge_line(a, "base + pc", "base + 2 * pc", "base + 2 * pc + 1"))
    b += ["    }", "}", "for (int pr = R - 1; pr >= 1; pr--) {", "    int base = pr * W, lo = 2 * base, hi = lo + W;",
          "    for (int pc = 1; pc < W; pc++) {"]
    for a in A:
        b.append("        " + merge_line(a, "base + pc", "lo + pc", "hi + pc"))
    b += ["    }", "}"]
    L += indent(b, 2)
    L.append("    }")
    L.append("")

    L.append("    // cell (r, c) = v, then every node above it")
    L.append("    void setCell(int r, int c, T v) {")
    b = ["int base = (r + R) * W;"]
    for a in A:
        b.append(f"{a.arr}[base + c + C] = v;")
    b.append("for (int pc = (c + C) >> 1; pc >= 1; pc >>= 1) {")
    for a in A:
        b.append("    " + merge_line(a, "base + pc", "base + 2 * pc", "base + 2 * pc + 1"))
    b += ["}", "for (int pr = (r + R) >> 1; pr >= 1; pr >>= 1) {", "    base = pr * W;", "    int lo = 2 * base, hi = lo + W;",
          "    for (int pc = c + C; pc >= 1; pc >>= 1) {"]
    for a in A:
        b.append("        " + merge_line(a, "base + pc", "lo + pc", "hi + pc"))
    b += ["    }", "}"]
    L += indent(b, 2)
    L.append("    }")
    L.append("")

    point_rule = "needs 0 <= r < R and 0 <= c < C, else throws out_of_range"

    def point_check(name):
        return "\n        ".join(cpp_throw("r < 0 || r >= R || c < 0 || c >= C", "out_of_range",
                                          f"{name}: needs 0 <= r < R and 0 <= c < C", 2))

    is_empty = {"max": "cur == NO_MAX", "min": "cur == NO_MIN"}.get(rd.key)
    leaf = f"{rd.arr}[(r + R) * W + c + C]"
    if_empty = "; an empty cell becomes v" if mm else ""
    L.append(f"    // O(1) -- the value at (r, c){', ' + rd.none_words_cpp + ' if the cell is empty' if mm else ''}; {point_rule}")
    L.append("    T pointGet(int r, int c) const {")
    L.append("        " + point_check("pointGet"))
    L.append(f"        return T({leaf});")
    L.append("    }")
    L.append("")
    upd = "O(log R * log C)" + (" gcds" if "gcd" in aggs else "")
    L.append(f"    // {upd} -- the cell at (r, c) becomes v (it may go down as well as up); {point_rule}")
    L.append("    void pointAssign(int r, int c, T v) {")
    L.append("        " + point_check("pointAssign"))
    L.append("        setCell(r, c, v);")
    L.append("    }")
    L.append("")
    if "pointAdd" in ops_of(aggs):
        L.append(f"    // {upd} -- adds v to the cell at (r, c){if_empty}; {point_rule}")
        L.append("    void pointAdd(int r, int c, T v) {")
        L.append("        " + point_check("pointAdd"))
        L.append(f"        T cur = T({leaf});")
        L.append(f"        setCell(r, c, {is_empty} ? v : T(cur + v));" if is_empty else "        setCell(r, c, T(cur + v));")
        L.append("    }")
        L.append("")
        for name, sym, word in (("pointChmax", ">", "max"), ("pointChmin", "<", "min")):
            L.append(f"    // {upd} -- the cell at (r, c) becomes {word}(itself, v){if_empty}; {point_rule}")
            L.append(f"    void {name}(int r, int c, T v) {{")
            L.append("        " + point_check(name))
            L.append(f"        T cur = T({leaf});")
            L.append(f"        if ({is_empty} || v {sym} cur) setCell(r, c, v);" if is_empty else f"        if (v {sym} cur) setCell(r, c, v);")
            L.append("    }")
            L.append("")

    rect_rule = "needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range"
    for a in A:
        L.append(f"    {a.cpp_type} {a.key}Of(int r1, int c1, int r2, int c2) const {{")
        b = [f"{a.cpp_type} res = {a.cpp_id};", "int cl = c1 + C, cr = c2 + C + 1;",
             "for (int lr = r1 + R, rr = r2 + R + 1; lr < rr; lr >>= 1, rr >>= 1) {", "    if (lr & 1) {", "        int base = lr++ * W;"]
        b += cpp_inner_query(a, 2)
        b += ["    }", "    if (rr & 1) {", "        int base = --rr * W;"]
        b += cpp_inner_query(a, 2)
        b += ["    }", "}", "return res;"]
        L += indent(b, 2)
        L.append("    }")
        L.append("")
        what = (f"{a.word} of the set cells in rows r1..r2, columns c1..c2 ({a.none_words_cpp} if there are none)" if mm
                else f"{a.word} of rows r1..r2, columns c1..c2")
        cost = "O(log R * log C + log U)" if a.key == "gcd" else "O(log R * log C)"
        L += indent(wrap_comment(f"{cost} -- {what}; {rect_rule}", "//"))
        L.append(f"    {a.cpp_type} {a.rect}(int r1, int c1, int r2, int c2) const {{")
        L.append("        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)")
        L.append(f'            throw out_of_range("{a.rect}: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");')
        L.append(f"        return {a.key}Of(r1, c1, r2, c2);")
        L.append("    }")
        L.append("")
        L.append(f"    // O(1) -- {a.word} of every set cell ({a.none_words_cpp} if there are none)" if mm
                 else f"    // O(1) -- {a.word} of the whole grid")
        L.append(f"    {a.cpp_type} {a.all}() const {{")
        root = f"{a.arr}[W + 1]"
        L.append(f"        return gcdOf({root}, T(0));" if a.key == "gcd" else f"        return {root};")
        L.append("    }")
        L.append("")
        if a.key in ("min", "max", "sum"):
            for name, rs, cs in CORNERS:
                r_lo, r_hi = ("0", "r") if rs == "<=" else ("r", "R - 1")
                c_lo, c_hi = ("0", "c") if cs == "<=" else ("c", "C - 1")
                L += indent(wrap_comment(
                    f"O(log R * log C) -- {a.word} of the set cells with row {rs} r and column {cs} c"
                    f"{f' ({a.none_words_cpp} if there are none)' if a.key != 'sum' else ''}; {point_rule}", "//"))
                L.append(f"    {a.cpp_type} {a.key}{name}(int r, int c) const {{")
                L.append("        " + point_check(f"{a.key}{name}"))
                L.append(f"        return {a.key}Of({r_lo}, {c_lo}, {r_hi}, {c_hi});")
                L.append("    }")
                L.append("")
    while L[-1] == "":
        L.pop()
    L.append("};")
    return L


def main():
    for aggs in subsets(AGG_ORDER):
        folder = "grid-seg-tree-" + "-".join(aggs)
        costs, build = costs_of(aggs)
        args = (ops_of(aggs), "seg-tree", costs, build, memory_of(aggs), "grid", [("empty-cells", "yes")] if has_empty(aggs) else [])
        write(folder, header(folder, "py", *args) + py_template(aggs), header(folder, "cpp", *args) + cpp_template(aggs))
    print(f"grid-seg-tree: {len(subsets(AGG_ORDER))} folders")


if __name__ == "__main__":
    main()
