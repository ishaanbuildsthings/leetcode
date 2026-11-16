"""Small grid, Fenwick trees (lighter than a segment tree where they apply), and the static corner tables.

    python3 gen_grid_bit.py        # writes range-queries-2d/grid-bit-.../ and grid-corner-table-.../

  grid-bit-sum, -xor, -sum-xor      point updates, rectangle sum / xor
  grid-bit-rect-add                 rectangle add, point read
  grid-bit-rect-add-rect-sum        rectangle add, rectangle sum (four trees)
  grid-bit-corner-<max|min>-...     point chmax (chmin), max (min) over a corner: one tree per corner direction asked for
  grid-corner-table-<max|min>-...   the same corner queries with no updates, O(1)
"""
from gen_grid_static import (POINT_RULE_CPP, POINT_RULE_PY, RECT_RULE_CPP, RECT_RULE_PY, cpp_grid_check, cpp_point_check,
                             cpp_rect_check, emit, py_grid_check, py_point_check, py_rect_check)
from lib2d import AGGS, indent, subsets, wrap_comment

CORNERS = [("LteLte", "<=", "<="), ("LteGte", "<=", ">="), ("GteLte", ">=", "<="), ("GteGte", ">=", ">=")]
SIZED_CPP = "needs R >= 1 and C >= 1, else throws invalid_argument"


# ------------------------------------------------------------------------------------------------ point update, rect sum / xor
def bit_sum(aggs):
    cls = "Fenwick2D"
    A = [AGGS[k] for k in aggs]
    sym = {"sum": "+", "xor": "^"}
    words = " and ".join(a.word for a in A)
    ops = ["pointGet", "pointAssign", "pointAdd", "pointChmax", "pointChmin"] + [x for a in A for x in (a.rect, a.all)]
    costs = {op: "log(R)*log(C)" for op in ops}
    costs.update({"pointGet": "1", **{a.all: "1" for a in A}})
    memory = {"layout": "none", "node": " ".join(f"{a.arr}[1*R*C]" for a in A), "other": "vals[1*R*C]",
              "note": "each Fenwick tree is (R + 1) by (C + 1), flat, 1-based; vals keeps the cells themselves for O(1) reads"}
    doc = (f"2D Fenwick tree ({words}): point updates and any-rectangle {words} on an R x C grid, O(log R * log C) each, "
           f"with a quarter of a 2D segment tree's memory and a smaller constant. A rectangle is four prefix queries "
           f"(the big corner, minus the strip above, minus the strip to the left, plus the corner both took off). "
           f"Rows and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.")
    arrs = [a.arr for a in A]
    py = ["", ""] + wrap_comment(doc, "#") + [f"class {cls}:"]
    py.append("    __slots__ = (" + ", ".join(f'"{s}"' for s in ["R", "C", "W", "vals"] + arrs + [f"total{a.cap}" for a in A]) + ")")
    py += ["", "    # O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else ValueError", "    def __init__(self, grid):"]
    b = py_grid_check(cls) + ["W = self.W = C + 1", "vals = self.vals = [v for row in grid for v in row]"]
    for a in A:
        s = sym[a.key]
        b += [f"t = self.{a.arr} = [0] * ((R + 1) * W)", "total = 0", "for v in vals:", f"    total {s}= v", "for r in range(R):", "    at = (r + 1) * W",
              "    t[at + 1:at + W] = grid[r]", "    for c in range(1, C + 1):  # each entry is added into the next one that covers it",
              "        j = c + (c & -c)", "        if j <= C:", f"            t[at + j] {s}= t[at + c]",
              "for r in range(1, R + 1):", "    j = r + (r & -r)", "    if j <= R:", "        a = r * W", "        b = j * W",
              "        for c in range(1, C + 1):", f"            t[b + c] {s}= t[a + c]", f"self.total{a.cap} = total"]
    py += indent(b, 2) + [""]
    py += ["    # cell (r, c) becomes v", "    def _set(self, r, c, v):"]
    b = ["R, C, W = self.R, self.C, self.W", "old = self.vals[r * C + c]", "self.vals[r * C + c] = v"]
    for a in A:
        s = sym[a.key]
        b += [f"d = {'v - old' if a.key == 'sum' else 'v ^ old'}", f"self.total{a.cap} {s}= d", f"t = self.{a.arr}", "i = r + 1", "while i <= R:",
              "    base = i * W", "    j = c + 1", "    while j <= C:", f"        t[base + j] {s}= d", "        j += j & -j", "    i += i & -i"]
    py += indent(b, 2) + [""]
    for a in A:
        s = sym[a.key]
        py += [f"    # {a.word} of the first r rows and first c columns", f"    def _prefix{a.cap}(self, r, c):"]
        py += indent(["W, t, res = self.W, self." + a.arr + ", 0", "while r > 0:", "    base = r * W", "    j = c", "    while j > 0:",
                      f"        res {s}= t[base + j]", "        j &= j - 1", "    r &= r - 1", "return res"], 2) + [""]
    py.append(f"    # O(1) -- the value at (r, c); {POINT_RULE_PY}")
    py.append("    def pointGet(self, r, c):")
    py += indent(py_point_check("pointGet") + ["return self.vals[r * self.C + c]"], 2) + [""]
    for name, text, expr, guard in (
        ("pointAssign", "the cell at (r, c) becomes v", "v", None),
        ("pointAdd", "adds v to the cell at (r, c)", "self.vals[r * self.C + c] + v", None),
        ("pointChmax", "the cell at (r, c) becomes max(itself, v)", "v", "v > self.vals[r * self.C + c]"),
        ("pointChmin", "the cell at (r, c) becomes min(itself, v)", "v", "v < self.vals[r * self.C + c]"),
    ):
        py += indent(wrap_comment(f"O(log R * log C) -- {text}; {POINT_RULE_PY}", "#"))
        py.append(f"    def {name}(self, r, c, v):")
        body = [f"self._set(r, c, {expr})"]
        if guard:
            body = [f"if {guard}:", f"    self._set(r, c, {expr})"]
        py += indent(py_point_check(name) + body, 2) + [""]
    for a in A:
        s = sym[a.key]
        m = "-" if a.key == "sum" else "^"
        py += indent(wrap_comment(f"O(log R * log C) -- {a.word} of rows r1..r2, columns c1..c2; {RECT_RULE_PY}", "#"))
        py.append(f"    def {a.rect}(self, r1, c1, r2, c2):")
        py += indent(py_rect_check(a.rect) + [f"p = self._prefix{a.cap}",
                                              f"return p(r2 + 1, c2 + 1) {m} p(r1, c2 + 1) {m} p(r2 + 1, c1) {s} p(r1, c1)"], 2)
        py += ["", f"    # O(1) -- {a.word} of the whole grid", f"    def {a.all}(self):", f"        return self.total{a.cap}", ""]
    while py[-1] == "":
        py.pop()

    cpp = wrap_comment(doc + " The (R, C) constructor starts with every cell 0.", "//")
    cpp.append("// T is any integer type (int, long long, ...)" + ("; sums are kept in S (long long for a smaller T)." if "sum" in aggs else "."))
    cpp += ["template <typename T>", f"struct {cls} {{"]
    if "sum" in aggs:
        cpp.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;")
    cpp += ["    int R, C, W;", "    vector<T> vals;"]
    for a in A:
        cpp += [f"    vector<{a.cpp_type}> {a.arr};", f"    {a.cpp_type} total{a.cap} = 0;"]
    cpp += ["", f"    // O(R*C) -- R rows by C columns, every cell 0; {SIZED_CPP}",
            f"    {cls}(int rows, int cols) : R(rows), C(cols), W(cols + 1) {{",
            f'        if (R < 1 || C < 1) throw invalid_argument("{cls}: needs R >= 1 and C >= 1");',
            "        vals.assign((size_t)R * C, T(0));"]
    for a in A:
        cpp.append(f"        {a.arr}.assign((size_t)(R + 1) * W, 0);")
    cpp += ["    }", "", f"    // O(R*C) -- grid: R rows of C numbers each; {SIZED_CPP}",
            f"    explicit {cls}(const vector<vector<T>>& grid)",
            f"        : {cls}((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {{"]
    b = ["for (int r = 0; r < R; r++) {",
         f'    if ((int)grid[r].size() != C) throw invalid_argument("{cls}: every row needs the same C values");',
         "    for (int c = 0; c < C; c++) vals[(size_t)r * C + c] = grid[r][c];", "}"]
    for a in A:
        s = sym[a.key]
        b += [f"auto& t{a.cap} = {a.arr};", "for (int r = 1; r <= R; r++) {", "    int at = r * W;",
              "    for (int c = 1; c <= C; c++) {",
              f"        t{a.cap}[at + c] {s}= grid[r - 1][c - 1];",
              f"        total{a.cap} {s}= grid[r - 1][c - 1];",
              "        int j = c + (c & -c);  // each entry is added into the next one that covers it",
              f"        if (j <= C) t{a.cap}[at + j] {s}= t{a.cap}[at + c];", "    }", "}",
              "for (int r = 1; r <= R; r++) {", "    int j = r + (r & -r);", "    if (j > R) continue;",
              f"    for (int c = 1; c <= C; c++) t{a.cap}[j * W + c] {s}= t{a.cap}[r * W + c];", "}"]
    cpp += indent(b, 2) + ["    }", ""]
    cpp += ["    // cell (r, c) becomes v", "    void setCell(int r, int c, T v) {"]
    b = ["T old = vals[(size_t)r * C + c];", "vals[(size_t)r * C + c] = v;"]
    for a in A:
        s = sym[a.key]
        b += [f"{a.cpp_type} d{a.cap} = {f'{a.cpp_type}(v) - old' if a.key == 'sum' else 'v ^ old'};", f"total{a.cap} {s}= d{a.cap};",
              "for (int i = r + 1; i <= R; i += i & -i)", f"    for (int j = c + 1; j <= C; j += j & -j) {a.arr}[i * W + j] {s}= d{a.cap};"]
    cpp += indent(b, 2) + ["    }", ""]
    for a in A:
        s = sym[a.key]
        cpp += [f"    // {a.word} of the first r rows and first c columns", f"    {a.cpp_type} prefix{a.cap}(int r, int c) const {{",
                f"        {a.cpp_type} res = 0;", "        for (int i = r; i > 0; i &= i - 1)",
                f"            for (int j = c; j > 0; j &= j - 1) res {s}= {a.arr}[i * W + j];", "        return res;", "    }", ""]
    cpp.append(f"    // O(1) -- the value at (r, c); {POINT_RULE_CPP}")
    cpp.append("    T pointGet(int r, int c) const {")
    cpp += indent(cpp_point_check("pointGet") + ["return vals[(size_t)r * C + c];"], 2) + ["    }", ""]
    for name, text, body in (
        ("pointAssign", "the cell at (r, c) becomes v", "setCell(r, c, v);"),
        ("pointAdd", "adds v to the cell at (r, c)", "setCell(r, c, T(vals[(size_t)r * C + c] + v));"),
        ("pointChmax", "the cell at (r, c) becomes max(itself, v)", "if (v > vals[(size_t)r * C + c]) setCell(r, c, v);"),
        ("pointChmin", "the cell at (r, c) becomes min(itself, v)", "if (v < vals[(size_t)r * C + c]) setCell(r, c, v);"),
    ):
        cpp += indent(wrap_comment(f"O(log R * log C) -- {text}; {POINT_RULE_CPP}", "//"))
        cpp.append(f"    void {name}(int r, int c, T v) {{")
        cpp += indent(cpp_point_check(name) + [body], 2) + ["    }", ""]
    for a in A:
        s = sym[a.key]
        m = "-" if a.key == "sum" else "^"
        p = f"prefix{a.cap}"
        cpp += indent(wrap_comment(f"O(log R * log C) -- {a.word} of rows r1..r2, columns c1..c2; {RECT_RULE_CPP}", "//"))
        cpp.append(f"    {a.cpp_type} {a.rect}(int r1, int c1, int r2, int c2) const {{")
        cpp += indent(cpp_rect_check(a.rect) + [f"return {p}(r2 + 1, c2 + 1) {m} {p}(r1, c2 + 1) {m} {p}(r2 + 1, c1) {s} {p}(r1, c1);"], 2)
        cpp += ["    }", "", f"    // O(1) -- {a.word} of the whole grid", f"    {a.cpp_type} {a.all}() const {{", f"        return total{a.cap};", "    }", ""]
    while cpp[-1] == "":
        cpp.pop()
    cpp.append("};")
    emit("grid-bit-" + "-".join(aggs), ops, "BIT", costs, "R*C", memory, py, cpp)


# ------------------------------------------------------------------------------------------------ rectangle add
def bit_rect_add(with_sum):
    cls = "RectAddRectSumFenwick2D" if with_sum else "RectAddFenwick2D"
    ops = ["rectAdd", "pointGet", "pointAssign", "pointAdd", "pointChmax", "pointChmin"] + (["rectSum", "sumAll"] if with_sum else [])
    costs = {op: "log(R)*log(C)" for op in ops}
    if with_sum:
        costs["sumAll"] = "1"
    trees = ["b1", "bx", "by", "bxy"] if with_sum else ["bit"]
    memory = {"layout": "none", "node": " ".join(f"{t}[1*R*C]" for t in trees),
              "note": ("four Fenwick trees over the marks a rectangle add leaves at its corners: the mark itself, times "
                       "its row, times its column, times both" if with_sum else
                       "one Fenwick tree over the marks a rectangle add leaves at its four corners") + "; each is (R + 1) by (C + 1), flat"}
    if with_sum:
        doc = ("Rectangle add and rectangle sum on an R x C grid with four 2D Fenwick trees, O(log R * log C) each, no "
               "lazy tags. An add of v on rows r1..r2, columns c1..c2 leaves four marks, +v at (r1, c1) and (r2 + 1, c2 + "
               "1), -v at (r1, c2 + 1) and (r2 + 1, c1): a cell's value is the sum of the marks above-left of it. The sum "
               "of the first x rows and y columns is then, over the marks (i, j, d) above-left, the sum of d * (x - i) * "
               "(y - j), which splits into x*y * sum(d) - y * sum(d*i) - x * sum(d*j) + sum(d*i*j): one tree per sum. Rows "
               "and columns are 0-based and rectangles are inclusive.")
    else:
        doc = ("Rectangle add and point read on an R x C grid with one 2D Fenwick tree, O(log R * log C) each. An add of v "
               "on rows r1..r2, columns c1..c2 leaves four marks, +v at (r1, c1) and (r2 + 1, c2 + 1), -v at (r1, c2 + 1) "
               "and (r2 + 1, c1); a cell's value is the sum of the marks above-left of it, a prefix query. When every "
               "add comes before any read, the difference array does this in O(1) per add. Rows and columns are 0-based "
               "and rectangles are inclusive.")
    # ---- Python
    py = ["", ""] + wrap_comment(doc, "#") + [f"class {cls}:"]
    py.append("    __slots__ = (" + ", ".join(f'"{s}"' for s in ["R", "C", "W"] + trees + (["total"] if with_sum else [])) + ")")
    py += ["", "    # O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else ValueError", "    def __init__(self, grid):"]
    b = py_grid_check(cls) + ["W = self.W = C + 1"]
    for t in trees:
        b.append(f"{t} = self.{t} = [0] * ((R + 1) * W)")
    b += ["above = [0] * C", "for r in range(R):", "    row = grid[r]", "    at = (r + 1) * W", "    left = 0", "    aboveLeft = 0",
          "    for c in range(C):", "        d = row[c] - left - above[c] + aboveLeft  # the mark that makes this cell's value come out right",
          "        left = row[c]", "        aboveLeft = above[c]"]
    if with_sum:
        b += ["        b1[at + c + 1] = d", "        bx[at + c + 1] = d * r", "        by[at + c + 1] = d * c", "        bxy[at + c + 1] = d * r * c"]
    else:
        b += ["        bit[at + c + 1] = d"]
    b += ["    above = row"]
    b += ["for t in (" + ", ".join(trees) + ("," if len(trees) == 1 else "") + "):", "    for r in range(1, R + 1):", "        at = r * W",
          "        for c in range(1, C + 1):", "            j = c + (c & -c)", "            if j <= C:", "                t[at + j] += t[at + c]",
          "    for r in range(1, R + 1):", "        j = r + (r & -r)", "        if j <= R:", "            a = r * W", "            b = j * W",
          "            for c in range(1, C + 1):", "                t[b + c] += t[a + c]"]
    if with_sum:
        b.append("self.total = sum(v for row in grid for v in row)")
    py += indent(b, 2) + [""]
    py += ["    # a mark d at (r, c): every cell at or below-right of it gains d", "    def _mark(self, r, c, d):"]
    if with_sum:
        b = ["R, C, W = self.R, self.C, self.W", "b1, bx, by, bxy = self.b1, self.bx, self.by, self.bxy", "dx = d * r", "dy = d * c", "dxy = dx * c",
             "i = r + 1", "while i <= R:", "    base = i * W", "    j = c + 1", "    while j <= C:", "        b1[base + j] += d", "        bx[base + j] += dx",
             "        by[base + j] += dy", "        bxy[base + j] += dxy", "        j += j & -j", "    i += i & -i"]
    else:
        b = ["R, C, W, bit = self.R, self.C, self.W, self.bit", "i = r + 1", "while i <= R:", "    base = i * W", "    j = c + 1", "    while j <= C:",
             "        bit[base + j] += d", "        j += j & -j", "    i += i & -i"]
    py += indent(b, 2) + [""]
    py += ["    def _add(self, r1, c1, r2, c2, v):"]
    b = ["self._mark(r1, c1, v)", "if c2 + 1 < self.C:", "    self._mark(r1, c2 + 1, -v)", "if r2 + 1 < self.R:", "    self._mark(r2 + 1, c1, -v)",
         "    if c2 + 1 < self.C:", "        self._mark(r2 + 1, c2 + 1, v)"]
    if with_sum:
        b.append("self.total += v * (r2 - r1 + 1) * (c2 - c1 + 1)")
    py += indent(b, 2) + [""]
    if with_sum:
        py += ["    # sum of the first x rows and first y columns", "    def _prefix(self, x, y):"]
        py += indent(["W = self.W", "b1, bx, by, bxy = self.b1, self.bx, self.by, self.bxy", "s1 = sx = sy = sxy = 0", "i = x", "while i > 0:",
                      "    base = i * W", "    j = y", "    while j > 0:", "        s1 += b1[base + j]", "        sx += bx[base + j]", "        sy += by[base + j]",
                      "        sxy += bxy[base + j]", "        j &= j - 1", "    i &= i - 1", "return x * y * s1 - y * sx - x * sy + sxy"], 2) + [""]
        py += ["    def _sumOf(self, r1, c1, r2, c2):", "        p = self._prefix",
               "        return p(r2 + 1, c2 + 1) - p(r1, c2 + 1) - p(r2 + 1, c1) + p(r1, c1)", "",
               "    def _get(self, r, c):", "        return self._sumOf(r, c, r, c)", ""]
    else:
        py += ["    def _get(self, r, c):"]
        py += indent(["W, bit, res = self.W, self.bit, 0", "i = r + 1", "while i > 0:", "    base = i * W", "    j = c + 1", "    while j > 0:",
                      "        res += bit[base + j]", "        j &= j - 1", "    i &= i - 1", "return res"], 2) + [""]
    py += indent(wrap_comment(f"O(log R * log C) -- adds v to every cell of rows r1..r2, columns c1..c2; {RECT_RULE_PY}", "#"))
    py.append("    def rectAdd(self, r1, c1, r2, c2, v):")
    py += indent(py_rect_check("rectAdd") + ["self._add(r1, c1, r2, c2, v)"], 2) + [""]
    py.append(f"    # O(log R * log C) -- the value at (r, c); {POINT_RULE_PY}")
    py.append("    def pointGet(self, r, c):")
    py += indent(py_point_check("pointGet") + ["return self._get(r, c)"], 2) + [""]
    for name, text, body in (
        ("pointAssign", "the cell at (r, c) becomes v", ["self._add(r, c, r, c, v - self._get(r, c))"]),
        ("pointAdd", "adds v to the cell at (r, c)", ["self._add(r, c, r, c, v)"]),
        ("pointChmax", "the cell at (r, c) becomes max(itself, v)", ["cur = self._get(r, c)", "if v > cur:", "    self._add(r, c, r, c, v - cur)"]),
        ("pointChmin", "the cell at (r, c) becomes min(itself, v)", ["cur = self._get(r, c)", "if v < cur:", "    self._add(r, c, r, c, v - cur)"]),
    ):
        py += indent(wrap_comment(f"O(log R * log C) -- {text}; {POINT_RULE_PY}", "#"))
        py.append(f"    def {name}(self, r, c, v):")
        py += indent(py_point_check(name) + body, 2) + [""]
    if with_sum:
        py += indent(wrap_comment(f"O(log R * log C) -- sum of rows r1..r2, columns c1..c2; {RECT_RULE_PY}", "#"))
        py.append("    def rectSum(self, r1, c1, r2, c2):")
        py += indent(py_rect_check("rectSum") + ["return self._sumOf(r1, c1, r2, c2)"], 2)
        py += ["", "    # O(1) -- sum of the whole grid", "    def sumAll(self):", "        return self.total", ""]
    while py[-1] == "":
        py.pop()

    # ---- C++
    cpp = wrap_comment(doc + " The (R, C) constructor starts with every cell 0.", "//")
    cpp += ["// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T).", "template <typename T>", f"struct {cls} {{",
            "    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;", "    int R, C, W;",
            f"    vector<S> {', '.join(trees)};"]
    if with_sum:
        cpp.append("    S total = 0;")
    cpp += ["", f"    // O(R*C) -- R rows by C columns, every cell 0; {SIZED_CPP}", f"    {cls}(int rows, int cols) : R(rows), C(cols), W(cols + 1) {{",
            f'        if (R < 1 || C < 1) throw invalid_argument("{cls}: needs R >= 1 and C >= 1");']
    for t in trees:
        cpp.append(f"        {t}.assign((size_t)(R + 1) * W, 0);")
    cpp += ["    }", "", f"    // O(R*C) -- grid: R rows of C numbers each; {SIZED_CPP}", f"    explicit {cls}(const vector<vector<T>>& grid)",
            f"        : {cls}((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {{"]
    b = ["for (auto& row : grid)", f'    if ((int)row.size() != C) throw invalid_argument("{cls}: every row needs the same C values");',
         "for (int r = 0; r < R; r++) {", "    for (int c = 0; c < C; c++) {",
         "        // the mark that makes this cell's value come out right",
         "        S left = c ? S(grid[r][c - 1]) : 0, up = r ? S(grid[r - 1][c]) : 0;",
         "        S upLeft = r && c ? S(grid[r - 1][c - 1]) : 0;",
         "        S d = S(grid[r][c]) - left - up + upLeft;",
         "        size_t at = (size_t)(r + 1) * W + c + 1;"]
    if with_sum:
        b += ["        b1[at] = d, bx[at] = d * r, by[at] = d * c, bxy[at] = d * r * c;", "        total += grid[r][c];"]
    else:
        b += ["        bit[at] = d;"]
    b += ["    }", "}", "for (auto* t : {" + ", ".join("&" + t for t in trees) + "}) {", "    for (int r = 1; r <= R; r++)", "        for (int c = 1; c <= C; c++) {",
          "            int j = c + (c & -c);", "            if (j <= C) (*t)[r * W + j] += (*t)[r * W + c];", "        }",
          "    for (int r = 1; r <= R; r++) {", "        int j = r + (r & -r);", "        if (j > R) continue;",
          "        for (int c = 1; c <= C; c++) (*t)[j * W + c] += (*t)[r * W + c];", "    }", "}"]
    cpp += indent(b, 2) + ["    }", ""]
    cpp += ["    // a mark d at (r, c): every cell at or below-right of it gains d", "    void mark(int r, int c, S d) {"]
    if with_sum:
        cpp += indent(["S dx = d * r, dy = d * c, dxy = dx * c;", "for (int i = r + 1; i <= R; i += i & -i)", "    for (int j = c + 1; j <= C; j += j & -j) {",
                       "        int at = i * W + j;", "        b1[at] += d, bx[at] += dx, by[at] += dy, bxy[at] += dxy;", "    }"], 2)
    else:
        cpp += indent(["for (int i = r + 1; i <= R; i += i & -i)", "    for (int j = c + 1; j <= C; j += j & -j) bit[i * W + j] += d;"], 2)
    cpp += ["    }", "", "    void addRect(int r1, int c1, int r2, int c2, S v) {"]
    b = ["mark(r1, c1, v);", "if (c2 + 1 < C) mark(r1, c2 + 1, -v);", "if (r2 + 1 < R) mark(r2 + 1, c1, -v);", "if (r2 + 1 < R && c2 + 1 < C) mark(r2 + 1, c2 + 1, v);"]
    if with_sum:
        b.append("total += v * (r2 - r1 + 1) * (c2 - c1 + 1);")
    cpp += indent(b, 2) + ["    }", ""]
    if with_sum:
        cpp += ["    // sum of the first x rows and first y columns", "    S prefix(int x, int y) const {"]
        cpp += indent(["S s1 = 0, sx = 0, sy = 0, sxy = 0;", "for (int i = x; i > 0; i &= i - 1)", "    for (int j = y; j > 0; j &= j - 1) {",
                       "        int at = i * W + j;", "        s1 += b1[at], sx += bx[at], sy += by[at], sxy += bxy[at];", "    }",
                       "return S(x) * y * s1 - S(y) * sx - S(x) * sy + sxy;"], 2)
        cpp += ["    }", "", "    S sumOf(int r1, int c1, int r2, int c2) const {",
                "        return prefix(r2 + 1, c2 + 1) - prefix(r1, c2 + 1) - prefix(r2 + 1, c1) + prefix(r1, c1);", "    }", "",
                "    S get(int r, int c) const { return sumOf(r, c, r, c); }", ""]
    else:
        cpp += ["    S get(int r, int c) const {"]
        cpp += indent(["S res = 0;", "for (int i = r + 1; i > 0; i &= i - 1)", "    for (int j = c + 1; j > 0; j &= j - 1) res += bit[i * W + j];", "return res;"], 2)
        cpp += ["    }", ""]
    cpp += indent(wrap_comment(f"O(log R * log C) -- adds v to every cell of rows r1..r2, columns c1..c2; {RECT_RULE_CPP}", "//"))
    cpp.append("    void rectAdd(int r1, int c1, int r2, int c2, T v) {")
    cpp += indent(cpp_rect_check("rectAdd") + ["addRect(r1, c1, r2, c2, v);"], 2) + ["    }", ""]
    cpp.append(f"    // O(log R * log C) -- the value at (r, c); {POINT_RULE_CPP}")
    cpp.append("    T pointGet(int r, int c) const {")
    cpp += indent(cpp_point_check("pointGet") + ["return T(get(r, c));"], 2) + ["    }", ""]
    for name, text, body in (
        ("pointAssign", "the cell at (r, c) becomes v", ["addRect(r, c, r, c, S(v) - get(r, c));"]),
        ("pointAdd", "adds v to the cell at (r, c)", ["addRect(r, c, r, c, v);"]),
        ("pointChmax", "the cell at (r, c) becomes max(itself, v)", ["S cur = get(r, c);", "if (S(v) > cur) addRect(r, c, r, c, S(v) - cur);"]),
        ("pointChmin", "the cell at (r, c) becomes min(itself, v)", ["S cur = get(r, c);", "if (S(v) < cur) addRect(r, c, r, c, S(v) - cur);"]),
    ):
        cpp += indent(wrap_comment(f"O(log R * log C) -- {text}; {POINT_RULE_CPP}", "//"))
        cpp.append(f"    void {name}(int r, int c, T v) {{")
        cpp += indent(cpp_point_check(name) + body, 2) + ["    }", ""]
    if with_sum:
        cpp += indent(wrap_comment(f"O(log R * log C) -- sum of rows r1..r2, columns c1..c2; {RECT_RULE_CPP}", "//"))
        cpp.append("    S rectSum(int r1, int c1, int r2, int c2) const {")
        cpp += indent(cpp_rect_check("rectSum") + ["return sumOf(r1, c1, r2, c2);"], 2)
        cpp += ["    }", "", "    // O(1) -- sum of the whole grid", "    S sumAll() const {", "        return total;", "    }", ""]
    while cpp[-1] == "":
        cpp.pop()
    cpp.append("};")
    emit("grid-bit-rect-add" + ("-rect-sum" if with_sum else ""), ops, "BIT", costs, "R*C", memory, py, cpp)


# ------------------------------------------------------------------------------------------------ corner max / min
def corner_bit(kind, corners):
    """Point chmax + max over a corner (or chmin + min): one Fenwick tree per corner direction."""
    a = AGGS[kind]
    cls = f"Corner{a.cap}Fenwick2D"
    better = ">" if kind == "max" else "<"
    upd = "pointChmax" if kind == "max" else "pointChmin"
    names = [c[0] for c in corners]
    ops = [upd, a.all] + [f"{kind}{n}" for n in names]
    costs = {op: "log(R)*log(C)" for op in ops}
    costs[a.all] = "1"
    memory = {"layout": "none", "node": " ".join(f"t{n}[1*R*C]" for n in names),
              "note": "one Fenwick tree per corner direction, each (R + 1) by (C + 1), flat; a >= direction is the same tree with that axis mirrored"}
    doc = (f"Corner {kind} with a 2D Fenwick tree: {upd} at a cell and the {kind} over a corner of the grid (every cell with "
           f"row <= r or >= r, and column <= c or >= c), O(log R * log C) each, with a quarter of a 2D segment tree's memory "
           f"per direction and a much smaller constant. This works because values only move one way: a cell can only go "
           f"{'up' if kind == 'max' else 'down'} ({upd}), so a tree entry never has to forget a value. For a cell that can move "
           f"both ways, or for rectangles that aren't corners, use the 2D segment tree. A cell can be empty and queries "
           f"only see set cells. Rows and columns are 0-based.")
    ident_py = "NEG" if kind == "max" else "POS"
    py = [f'{ident_py} = float("{"-inf" if kind == "max" else "inf"}")  # an empty cell', "", ""]
    py += wrap_comment(doc + f" An empty cell is None in the grid, and a {kind} over no set cell is None.", "#") + [f"class {cls}:"]
    py.append("    __slots__ = (" + ", ".join(f'"{s}"' for s in ["R", "C", "W", "best"] + [f"t{n}" for n in names]) + ")")
    py += ["", "    # O(R*C) -- grid: R rows of C values each (None = an empty cell); needs R >= 1 and C >= 1, else ValueError", "    def __init__(self, grid):"]
    b = py_grid_check(cls) + ["W = self.W = C + 1", f"best = {ident_py}"]
    for n, rs, cs in corners:
        ri = "r + 1" if rs == "<=" else "R - r"
        b += [f"t = self.t{n} = [{ident_py}] * ((R + 1) * W)", "for r in range(R):", f"    at = ({ri}) * W", "    row = grid[r]", "    for c in range(C):",
              "        v = row[c]", "        if v is not None:", f"            t[at + {'c + 1' if cs == '<=' else 'C - c'}] = v",
              f"            if v {better} best:", "                best = v",
              "for i in range(1, R + 1):", "    at = i * W", "    for j in range(1, C + 1):  # each entry is folded into the next one that covers it",
              "        p = j + (j & -j)", f"        if p <= C and t[at + j] {better} t[at + p]:", "            t[at + p] = t[at + j]",
              "for i in range(1, R + 1):", "    p = i + (i & -i)", "    if p <= R:", "        a = i * W", "        b = p * W", "        for j in range(1, C + 1):",
              f"            if t[a + j] {better} t[b + j]:", "                t[b + j] = t[a + j]"]
    b.append("self.best = best")
    py += indent(b, 2) + [""]
    py += indent(wrap_comment(f"O(log R * log C) -- the cell at (r, c) becomes {kind}(itself, v); an empty cell becomes v; {POINT_RULE_PY}", "#"))
    py.append(f"    def {upd}(self, r, c, v):")
    b = py_point_check(upd) + ["R, C, W = self.R, self.C, self.W", f"if v {better} self.best:", "    self.best = v"]
    for n, rs, cs in corners:
        b += [f"t = self.t{n}", f"i = {'r + 1' if rs == '<=' else 'R - r'}", f"cj = {'c + 1' if cs == '<=' else 'C - c'}", "while i <= R:", "    base = i * W", "    j = cj",
              "    while j <= C:", f"        if v {better} t[base + j]:", "            t[base + j] = v", "        j += j & -j", "    i += i & -i"]
    py += indent(b, 2) + [""]
    for n, rs, cs in corners:
        py += indent(wrap_comment(f"O(log R * log C) -- {kind} of the set cells with row {rs} r and column {cs} c (None if there are none); {POINT_RULE_PY}", "#"))
        py.append(f"    def {kind}{n}(self, r, c):")
        py += indent(py_point_check(f"{kind}{n}") + [
            f"W, t, res = self.W, self.t{n}, {ident_py}", f"i = {'r + 1' if rs == '<=' else 'self.R - r'}", f"cj = {'c + 1' if cs == '<=' else 'self.C - c'}",
            "while i > 0:", "    base = i * W", "    j = cj", "    while j > 0:", "        x = t[base + j]", f"        if x {better} res:", "            res = x",
            "        j &= j - 1", "    i &= i - 1", f"return None if res == {ident_py} else res"], 2) + [""]
    py += [f"    # O(1) -- {kind} of every set cell (None if there are none)", f"    def {a.all}(self):",
           f"        return None if self.best == {ident_py} else self.best"]

    none = a.none_cpp
    cpp = wrap_comment(doc + f" The (R, C) constructor starts with every cell empty, and a {kind} over no set cell is {none}.", "//")
    cpp += ["// T is any integer type (int, long long, ...).", "template <typename T>", f"struct {cls} {{",
            f"    static constexpr T {none} = numeric_limits<T>::{'min' if kind == 'max' else 'max'}();  // what a {kind} over no set cell gives",
            "    int R, C, W;", f"    T best = {none};", f"    vector<T> {', '.join('t' + n for n in names)};", "",
            f"    // O(R*C) -- R rows by C columns, every cell empty; {SIZED_CPP}", f"    {cls}(int rows, int cols) : R(rows), C(cols), W(cols + 1) {{",
            f'        if (R < 1 || C < 1) throw invalid_argument("{cls}: needs R >= 1 and C >= 1");']
    for n in names:
        cpp.append(f"        t{n}.assign((size_t)(R + 1) * W, {none});")
    cpp += ["    }", "", f"    // O(R*C) -- grid: R rows of C values each, every cell set; {SIZED_CPP}", f"    explicit {cls}(const vector<vector<T>>& grid)",
            f"        : {cls}((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {{"]
    b = ["for (auto& row : grid)", f'    if ((int)row.size() != C) throw invalid_argument("{cls}: every row needs the same C values");']
    b += ["for (auto& row : grid)", f"    for (T v : row) best = {kind}(best, v);"]
    for n, rs, cs in corners:
        b += ["for (int r = 0; r < R; r++)", f"    for (int c = 0; c < C; c++) t{n}[({'r + 1' if rs == '<=' else 'R - r'}) * W + {'c + 1' if cs == '<=' else 'C - c'}] = grid[r][c];"]
    b += ["for (auto* t : {" + ", ".join("&t" + n for n in names) + "}) {", "    for (int i = 1; i <= R; i++)", "        for (int j = 1; j <= C; j++) {",
          "            int p = j + (j & -j);  // each entry is folded into the next one that covers it",
          f"            if (p <= C) (*t)[i * W + p] = {kind}((*t)[i * W + p], (*t)[i * W + j]);", "        }",
          "    for (int i = 1; i <= R; i++) {", "        int p = i + (i & -i);", "        if (p > R) continue;",
          f"        for (int j = 1; j <= C; j++) (*t)[p * W + j] = {kind}((*t)[p * W + j], (*t)[i * W + j]);", "    }", "}"]
    cpp += indent(b, 2) + ["    }", ""]
    cpp += indent(wrap_comment(f"O(log R * log C) -- the cell at (r, c) becomes {kind}(itself, v); an empty cell becomes v; {POINT_RULE_CPP}", "//"))
    cpp.append(f"    void {upd}(int r, int c, T v) {{")
    b = cpp_point_check(upd) + [f"best = {kind}(best, v);"]
    for n, rs, cs in corners:
        b += [f"for (int i = {'r + 1' if rs == '<=' else 'R - r'}; i <= R; i += i & -i)",
              f"    for (int j = {'c + 1' if cs == '<=' else 'C - c'}; j <= C; j += j & -j) t{n}[i * W + j] = {kind}(t{n}[i * W + j], v);"]
    cpp += indent(b, 2) + ["    }", ""]
    for n, rs, cs in corners:
        cpp += indent(wrap_comment(f"O(log R * log C) -- {kind} of the set cells with row {rs} r and column {cs} c ({none} if there are none); {POINT_RULE_CPP}", "//"))
        cpp.append(f"    T {kind}{n}(int r, int c) const {{")
        cpp += indent(cpp_point_check(f"{kind}{n}") + [
            f"T res = {none};", f"for (int i = {'r + 1' if rs == '<=' else 'R - r'}; i > 0; i &= i - 1)",
            f"    for (int j = {'c + 1' if cs == '<=' else 'C - c'}; j > 0; j &= j - 1) res = {kind}(res, t{n}[i * W + j]);", "return res;"], 2) + ["    }", ""]
    cpp += [f"    // O(1) -- {kind} of every set cell ({none} if there are none)", f"    T {a.all}() const {{", "        return best;", "    }", "};"]
    emit(f"grid-bit-corner-{kind}-" + "-".join(n.lower() for n in names), ops, "BIT", costs, "R*C", memory, py, cpp, [("empty-cells", "yes")])


def corner_table(kind, corners):
    """No updates: the max (min) over each corner, precomputed, O(1) per query."""
    a = AGGS[kind]
    cls = f"Corner{a.cap}Table2D"
    better = ">" if kind == "max" else "<"
    names = [c[0] for c in corners]
    ops = [a.all] + [f"{kind}{n}" for n in names]
    costs = {op: "1" for op in ops}
    memory = {"layout": "none", "node": " ".join(f"t{n}[1*R*C]" for n in names), "note": "one R by C table per corner direction, flat"}
    doc = (f"Static corner {kind}: the {kind} over a corner of the grid (every cell with row <= r or >= r, and column <= c or "
           f">= c) in O(1), from one R x C table per direction filled in a single pass (a cell's corner is its own row's "
           f"running {kind} joined with the corner of the cell one row back). No updates. Rows and columns are 0-based.")
    py = ["", ""] + wrap_comment(doc, "#") + [f"class {cls}:"]
    py.append("    __slots__ = (" + ", ".join(f'"{s}"' for s in ["R", "C", "best"] + [f"t{n}" for n in names]) + ")")
    py += ["", "    # O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else ValueError", "    def __init__(self, grid):"]
    b = py_grid_check(cls) + [f"self.best = {kind}({kind}(row) for row in grid)"]
    for n, rs, cs in corners:
        rows = "range(R)" if rs == "<=" else "range(R - 1, -1, -1)"
        cols = "range(C)" if cs == "<=" else "range(C - 1, -1, -1)"
        back = "at - C" if rs == "<=" else "at + C"
        first = "r > 0" if rs == "<=" else "r < R - 1"
        b += [f"t = self.t{n} = [0] * (R * C)", f"for r in {rows}:", "    row = grid[r]", "    at = r * C", f"    run = row[{'0' if cs == '<=' else 'C - 1'}]",
              f"    if {first}:", f"        back = {back}", f"        for c in {cols}:", "            v = row[c]", f"            if v {better} run:", "                run = v",
              "            x = t[back + c]", f"            t[at + c] = run if run {better} x else x", "    else:", f"        for c in {cols}:", "            v = row[c]",
              f"            if v {better} run:", "                run = v", "            t[at + c] = run"]
    py += indent(b, 2) + [""]
    for n, rs, cs in corners:
        py += indent(wrap_comment(f"O(1) -- {kind} of the cells with row {rs} r and column {cs} c; {POINT_RULE_PY}", "#"))
        py.append(f"    def {kind}{n}(self, r, c):")
        py += indent(py_point_check(f"{kind}{n}") + [f"return self.t{n}[r * self.C + c]"], 2) + [""]
    py += [f"    # O(1) -- {kind} of the whole grid", f"    def {a.all}(self):", "        return self.best"]

    cpp = wrap_comment(doc, "//") + ["// T is any type with < (int, long long, double, ...).", "template <typename T>", f"struct {cls} {{", "    int R, C;", "    T best;",
                                      f"    vector<T> {', '.join('t' + n for n in names)};", "",
                                      f"    // O(R*C) -- grid: R rows of C numbers each; {SIZED_CPP}", f"    explicit {cls}(const vector<vector<T>>& grid)",
                                      "        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()) {"]
    b = cpp_grid_check(cls) + ["best = grid[0][0];", "for (auto& row : grid)", f"    for (const T& v : row) best = {kind}(best, v);"]
    for n, rs, cs in corners:
        rloop = "for (int r = 0; r < R; r++) {" if rs == "<=" else "for (int r = R - 1; r >= 0; r--) {"
        cloop = "for (int c = 0; c < C; c++) {" if cs == "<=" else "for (int c = C - 1; c >= 0; c--) {"
        b += [f"t{n}.resize((size_t)R * C);", rloop, f"    T run = grid[r][{'0' if cs == '<=' else 'C - 1'}];",
              f"    bool hasBack = {'r > 0' if rs == '<=' else 'r < R - 1'};", f"    size_t at = (size_t)r * C, back = {'at - C' if rs == '<=' else 'at + C'};",
              "    " + cloop, f"        run = {kind}(run, grid[r][c]);", f"        t{n}[at + c] = hasBack ? {kind}(run, t{n}[back + c]) : run;", "    }", "}"]
    cpp += indent(b, 2) + ["    }", ""]
    for n, rs, cs in corners:
        cpp += indent(wrap_comment(f"O(1) -- {kind} of the cells with row {rs} r and column {cs} c; {POINT_RULE_CPP}", "//"))
        cpp.append(f"    T {kind}{n}(int r, int c) const {{")
        cpp += indent(cpp_point_check(f"{kind}{n}") + [f"return t{n}[(size_t)r * C + c];"], 2) + ["    }", ""]
    cpp += [f"    // O(1) -- {kind} of the whole grid", f"    T {a.all}() const {{", "        return best;", "    }", "};"]
    emit(f"grid-corner-table-{kind}-" + "-".join(n.lower() for n in names), ops, "corner-table", costs, "R*C", memory, py, cpp)


def main():
    n = 0
    for aggs in (["sum"], ["xor"], ["sum", "xor"]):
        bit_sum(aggs)
        n += 1
    bit_rect_add(False)
    bit_rect_add(True)
    n += 2
    for kind in ("max", "min"):
        for mask in range(1, 16):
            corners = [c for i, c in enumerate(CORNERS) if mask >> i & 1]
            corner_bit(kind, corners)
            corner_table(kind, corners)
            n += 2
    print(f"grid bit + corner tables: {n} folders")


if __name__ == "__main__":
    main()
