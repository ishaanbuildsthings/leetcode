"""Small grid, nothing changes after the build: prefix sums, per-bit counts, 2D hashing, sparse tables (any rectangle)
and the difference array (rectangle adds first, one read of the grid at the end). Square-only queries are left to the
generic square sparse table (generic-2d/GenericSquareSparseTable).

    python3 gen_grid_static.py     # writes range-queries-2d/grid-<family>-.../template.{py,cpp}
"""
from lib2d import AGGS, cpp_throw, header, indent, py_raise, subsets, wrap_comment, write

CORNERS = [("LteLte", "<=", "<="), ("LteGte", "<=", ">="), ("GteLte", ">=", "<="), ("GteGte", ">=", ">=")]
PY_GRID_CHECK = [
    "R = self.R = len(grid)",
    "C = self.C = len(grid[0]) if R else 0",
    "if R < 1 or C < 1 or any(len(row) != C for row in grid):",
]
RECT_RULE_PY = "needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else IndexError"
RECT_RULE_CPP = "needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else throws out_of_range"
POINT_RULE_PY = "needs 0 <= r < R and 0 <= c < C, else IndexError"
POINT_RULE_CPP = "needs 0 <= r < R and 0 <= c < C, else throws out_of_range"


def py_grid_check(cls):
    return PY_GRID_CHECK + [f'    raise ValueError("{cls}: needs a grid of R >= 1 rows, each of the same C >= 1 values")']


def cpp_grid_check(cls):
    return [
        f'if (R < 1 || C < 1) throw invalid_argument("{cls}: needs R >= 1 and C >= 1");',
        "for (auto& row : grid)",
        f'    if ((int)row.size() != C) throw invalid_argument("{cls}: every row needs the same C values");',
    ]


def py_rect_check(name, depth=2):
    return ["if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):"] + indent(py_raise(
        "IndexError", f"{name}: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {{r1}}, c1 = {{c1}}, r2 = {{r2}}, "
        "c2 = {c2}, R = {self.R}, C = {self.C}", depth + 1))


def py_point_check(name, depth=2):
    return ["if not (0 <= r < self.R and 0 <= c < self.C):"] + indent(py_raise(
        "IndexError", f"{name}: needs 0 <= r < R and 0 <= c < C, got r = {{r}}, c = {{c}}, R = {{self.R}}, C = {{self.C}}",
        depth + 1))


def cpp_rect_check(name, depth=2):
    return cpp_throw("r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C", "out_of_range",
                     f"{name}: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C", depth)


def cpp_point_check(name, depth=2):
    return cpp_throw("r < 0 || r >= R || c < 0 || c >= C", "out_of_range", f"{name}: needs 0 <= r < R and 0 <= c < C", depth)


def emit(folder, ops, dstype, costs, build, memory, py, cpp, extra=()):
    args = (ops, dstype, costs, build, memory, "grid", list(extra))
    write(folder, header(folder, "py", *args) + py, header(folder, "cpp", *args) + cpp)


# ------------------------------------------------------------------------------------------------ prefix sums / xors
SUM_CORNERS = [("LteLte", "<=", "<="), ("LteGte", "<=", ">="), ("GteLte", ">=", "<="), ("GteGte", ">=", ">=")]


def grid_sum_corners(cost, lang, body=None, ret="S"):
    """sumLteLte(r, c) ... sumGteGte: the sum from one corner of the grid. body(name) gives the return expression;
    without it each is a rectSum of that corner's rectangle."""
    out = []
    for n, rs, cs in SUM_CORNERS:
        r_lo, r_hi = ("0", "r") if rs == "<=" else ("r", "R - 1")
        c_lo, c_hi = ("0", "c") if cs == "<=" else ("c", "C - 1")
        if lang == "py":
            expr = body(n) if body else f"self.rectSum({r_lo}, {c_lo}, {r_hi.replace('R', 'self.R')}, {c_hi.replace('C', 'self.C')})"
            out += indent(wrap_comment(f"{cost} -- sum of the cells with row {rs} r and column {cs} c; {POINT_RULE_PY}", "#"))
            out.append(f"    def sum{n}(self, r, c):")
            out += indent(py_point_check(f"sum{n}") + [f"return {expr}"], 2) + [""]
        else:
            expr = body(n) if body else f"rectSum({r_lo}, {c_lo}, {r_hi}, {c_hi})"
            out += indent(wrap_comment(f"{cost} -- sum of the cells with row {rs} r and column {cs} c; {POINT_RULE_CPP}", "//"))
            out.append(f"    {ret} sum{n}(int r, int c) const {{")
            out += indent(cpp_point_check(f"sum{n}") + [f"return {expr};"], 2) + ["    }", ""]
    return out


def prefix(aggs):
    cls = "PrefixSums2D" if aggs == ["sum"] else "PrefixXors2D" if aggs == ["xor"] else "PrefixSumsXors2D"
    A = [AGGS[k] for k in aggs]
    words = " and ".join(a.word for a in A)
    ops = ["pointGet"] + [x for a in A for x in (a.rect, a.all)] + ([f"sum{n}" for n, _, _ in SUM_CORNERS] if "sum" in aggs else [])
    costs = {op: "1" for op in ops}
    memory = {"layout": "none", "node": " ".join(f"{a.arr}[1*R*C]" for a in A),
              "note": "each table is (R + 1) by (C + 1), flat: entry [r][c] covers the rows above r and the columns left of c"}
    doc = (f"Static 2D prefix {words}s: any rectangle in O(1) from four table entries (the big corner, minus the strip "
           f"above, minus the strip to the left, plus the corner both took off). No updates. Rows and columns are "
           f"0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.")
    sym = {"sum": ("+", "-"), "xor": ("^", "^")}
    py = ["", ""] + wrap_comment(doc, "#") + [f"class {cls}:"]
    py.append("    __slots__ = (" + ", ".join(f'"{s}"' for s in ["R", "C", "W"] + [a.arr for a in A]) + ")")
    py += ["", "    # O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else ValueError", "    def __init__(self, grid):"]
    b = py_grid_check(cls) + ["W = self.W = C + 1"]
    for a in A:
        b.append(f"{a.arr} = self.{a.arr} = [0] * ((R + 1) * W)")
    b += ["for r in range(R):", "    row = grid[r]", "    up = r * W", "    at = up + W"]
    for a in A:
        b.append(f"    run{a.cap} = 0")
    b.append("    for c in range(C):")
    for a in A:
        plus = sym[a.key][0]
        b.append(f"        run{a.cap} {plus}= row[c]")
        b.append(f"        {a.arr}[at + c + 1] = {a.arr}[up + c + 1] {plus} run{a.cap}")
    py += indent(b, 2) + [""]
    for a in A:
        plus, minus = sym[a.key]
        py += indent(wrap_comment(f"O(1) -- {a.word} of rows r1..r2, columns c1..c2; {RECT_RULE_PY}", "#"))
        py.append(f"    def {a.rect}(self, r1, c1, r2, c2):")
        py += indent(py_rect_check(a.rect) + [
            f"{a.arr}, W = self.{a.arr}, self.W", "top = r1 * W", "bot = (r2 + 1) * W",
            f"return {a.arr}[bot + c2 + 1] {minus} {a.arr}[top + c2 + 1] {minus} {a.arr}[bot + c1] {plus} {a.arr}[top + c1]"], 2)
        py += ["", f"    # O(1) -- {a.word} of the whole grid", f"    def {a.all}(self):", f"        return self.{a.arr}[-1]", ""]
    a = A[0]
    plus, minus = sym[a.key]
    py.append(f"    # O(1) -- the value at (r, c); {POINT_RULE_PY}")
    py.append("    def pointGet(self, r, c):")
    py += indent(py_point_check("pointGet") + [
        f"{a.arr}, W = self.{a.arr}, self.W", "top = r * W", "bot = top + W",
        f"return {a.arr}[bot + c + 1] {minus} {a.arr}[top + c + 1] {minus} {a.arr}[bot + c] {plus} {a.arr}[top + c]"], 2)
    if "sum" in aggs:
        py += [""] + grid_sum_corners("O(1)", "py")
        while py[-1] == "":
            py.pop()

    cpp = wrap_comment(doc, "//")
    cpp.append("// T is any integer type (int, long long, ...)" + ("; sums are kept in S (long long for a smaller T)." if "sum" in aggs else "."))
    cpp += ["template <typename T>", f"struct {cls} {{"]
    if "sum" in aggs:
        cpp.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;")
    cpp.append("    int R, C, W;")
    for a in A:
        cpp.append(f"    vector<{a.cpp_type}> {a.arr};")
    cpp += ["", "    // O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws invalid_argument",
            f"    explicit {cls}(const vector<vector<T>>& grid)",
            "        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()), W(C + 1) {"]
    b = cpp_grid_check(cls)
    for a in A:
        b.append(f"{a.arr}.assign((size_t)(R + 1) * W, 0);")
    b += ["for (int r = 0; r < R; r++) {", "    int up = r * W, at = up + W;"]
    for a in A:
        b.append(f"    {a.cpp_type} run{a.cap} = 0;")
    b.append("    for (int c = 0; c < C; c++) {")
    for a in A:
        plus = sym[a.key][0]
        b.append(f"        run{a.cap} {plus}= grid[r][c];")
        b.append(f"        {a.arr}[at + c + 1] = {a.arr}[up + c + 1] {plus} run{a.cap};")
    b += ["    }", "}"]
    cpp += indent(b, 2) + ["    }", ""]
    for a in A:
        plus, minus = sym[a.key]
        cpp += indent(wrap_comment(f"O(1) -- {a.word} of rows r1..r2, columns c1..c2; {RECT_RULE_CPP}", "//"))
        cpp.append(f"    {a.cpp_type} {a.rect}(int r1, int c1, int r2, int c2) const {{")
        cpp += indent(cpp_rect_check(a.rect) + [
            "int top = r1 * W, bot = (r2 + 1) * W;",
            f"return {a.arr}[bot + c2 + 1] {minus} {a.arr}[top + c2 + 1] {minus} {a.arr}[bot + c1] {plus} {a.arr}[top + c1];"], 2)
        cpp += ["    }", "", f"    // O(1) -- {a.word} of the whole grid", f"    {a.cpp_type} {a.all}() const {{",
                f"        return {a.arr}.back();", "    }", ""]
    a = A[0]
    plus, minus = sym[a.key]
    cpp.append(f"    // O(1) -- the value at (r, c); {POINT_RULE_CPP}")
    cpp.append("    T pointGet(int r, int c) const {")
    cpp += indent(cpp_point_check("pointGet") + [
        "int top = r * W, bot = top + W;",
        f"return T({a.arr}[bot + c + 1] {minus} {a.arr}[top + c + 1] {minus} {a.arr}[bot + c] {plus} {a.arr}[top + c]);"], 2)
    cpp += ["    }"]
    if "sum" in aggs:
        cpp += [""] + grid_sum_corners("O(1)", "cpp")
        while cpp[-1] == "":
            cpp.pop()
    cpp += ["};"]
    emit("grid-prefix-" + "-".join(aggs), ops, "prefix-sum", costs, "R*C", memory, py, cpp)


# ------------------------------------------------------------------------------------------------ per-bit counts
def bit_counts(aggs):
    """Static AND / OR with one prefix-count table per bit: far less memory than a sparse table when log R * log C is
    more than the number of bits, for O(bits) per query."""
    cls = "BitCounts2D"
    A = [AGGS[k] for k in aggs]
    ops = ["pointGet"] + [x for a in A for x in (a.rect, a.all)]
    costs = {op: "log(U)" for op in ops}
    costs["pointGet"] = "1"
    memory = {"layout": "none", "node": "cnt[1*R*C*log(U)]", "other": "vals[1*R*C]",
              "note": "one (R + 1) by (C + 1) prefix-count table per bit of the largest value"}
    words = " and ".join(a.word for a in A)
    doc = (f"Static rectangle {words} from one 2D prefix-count table per bit: a bit is in the OR when some cell of the "
           f"rectangle has it, and in the AND when every cell does. O(bits) per query, bits = bit length of the largest "
           f"value, and bits * R * C memory (a sparse table answers in O(1) but takes log R * log C tables). Values must "
           f"be >= 0. No updates. Rows and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.")
    py = ["", ""] + wrap_comment(doc, "#") + [f"class {cls}:", '    __slots__ = ("R", "C", "W", "bits", "cnt", "vals")', ""]
    py += ["    # O(R*C*bits) -- grid: R rows of C numbers each, all >= 0; needs R >= 1 and C >= 1, else ValueError",
           "    def __init__(self, grid):"]
    py += indent(py_grid_check(cls) + [
        "if any(v < 0 for row in grid for v in row):",
        f'    raise ValueError("{cls}: values must be >= 0")',
        "W = self.W = C + 1",
        "self.vals = [v for row in grid for v in row]",
        "bits = self.bits = max(1, max(self.vals).bit_length())",
        "cnt = self.cnt = []",
        "for b in range(bits):",
        "    t = [0] * ((R + 1) * W)",
        "    for r in range(R):",
        "        row = grid[r]",
        "        up = r * W",
        "        at = up + W",
        "        run = 0",
        "        for c in range(C):",
        "            run += row[c] >> b & 1",
        "            t[at + c + 1] = t[up + c + 1] + run",
        "    cnt.append(t)",
    ], 2) + [""]
    py += ["    # how many cells of the rectangle have each bit, one count per bit", "    def _counts(self, r1, c1, r2, c2):"]
    py += indent(["W = self.W", "a = (r2 + 1) * W + c2 + 1", "b = r1 * W + c2 + 1", "c = (r2 + 1) * W + c1", "d = r1 * W + c1",
                  "return [t[a] - t[b] - t[c] + t[d] for t in self.cnt]"], 2) + [""]
    for a in A:
        test = "n == area" if a.key == "and" else "n"
        for name, rule, call, check in ((a.rect, f"rows r1..r2, columns c1..c2; {RECT_RULE_PY}", "r1, c1, r2, c2", True),
                                        (a.all, "the whole grid", "", False)):
            py += indent(wrap_comment(f"O(bits) -- {a.word} of {rule}", "#"))
            py.append(f"    def {name}(self{', ' + call if call else ''}):")
            b = py_rect_check(name) if check else ["r1, c1, r2, c2 = 0, 0, self.R - 1, self.C - 1"]
            if a.key == "and":
                b.append("area = (r2 - r1 + 1) * (c2 - c1 + 1)")
            b += ["res = 0", "for b, n in enumerate(self._counts(r1, c1, r2, c2)):", f"    if {test}:", "        res |= 1 << b", "return res"]
            py += indent(b, 2) + [""]
    py.append(f"    # O(1) -- the value at (r, c); {POINT_RULE_PY}")
    py.append("    def pointGet(self, r, c):")
    py += indent(py_point_check("pointGet") + ["return self.vals[r * self.C + c]"], 2)

    cpp = wrap_comment(doc, "//") + ["// T is any integer type (int, long long, ...).", "template <typename T>", f"struct {cls} {{",
                                      "    int R, C, W, bits;", "    size_t plane;  // one table's size, (R + 1) * (C + 1)",
                                      "    vector<int> cnt;  // the prefix counts of bit b are the plane starting at b * plane",
                                      "    vector<T> vals;", "",
                                      "    // O(R*C*bits) -- grid: R rows of C numbers each, all >= 0; needs R >= 1 and C >= 1, else throws "
                                      "invalid_argument",
                                      f"    explicit {cls}(const vector<vector<T>>& grid)",
                                      "        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()), W(C + 1), bits(1) {"]
    cpp += indent(cpp_grid_check(cls) + [
        "T top = 0;",
        "for (auto& row : grid)",
        "    for (T v : row) {",
        f'        if (v < 0) throw invalid_argument("{cls}: values must be >= 0");',
        "        vals.push_back(v);",
        "        top = max(top, v);",
        "    }",
        "while (bits < 63 && (top >> bits) > 0) bits++;",
        "plane = (size_t)(R + 1) * W;",
        "cnt.assign(bits * plane, 0);",
        "for (int b = 0; b < bits; b++) {",
        "    int* t = &cnt[b * plane];",
        "    for (int r = 0; r < R; r++) {",
        "        int up = r * W, at = up + W, run = 0;",
        "        for (int c = 0; c < C; c++) {",
        "            run += (int)(grid[r][c] >> b & 1);",
        "            t[at + c + 1] = t[up + c + 1] + run;",
        "        }",
        "    }",
        "}",
    ], 2) + ["    }", ""]
    cpp += ["    // how many cells of the rectangle have bit b", "    int countOf(int b, int r1, int c1, int r2, int c2) const {",
            "        const int* t = &cnt[b * plane];",
            "        return t[(r2 + 1) * W + c2 + 1] - t[r1 * W + c2 + 1] - t[(r2 + 1) * W + c1] + t[r1 * W + c1];", "    }", ""]
    for a in A:
        for name, rule, sig, check in ((a.rect, f"rows r1..r2, columns c1..c2; {RECT_RULE_CPP}", "int r1, int c1, int r2, int c2", True),
                                       (a.all, "the whole grid", "", False)):
            cpp += indent(wrap_comment(f"O(bits) -- {a.word} of {rule}", "//"))
            cpp.append(f"    T {name}({sig}) const {{")
            b = cpp_rect_check(name) if check else ["int r1 = 0, c1 = 0, r2 = R - 1, c2 = C - 1;"]
            test = "countOf(b, r1, c1, r2, c2) == area" if a.key == "and" else "countOf(b, r1, c1, r2, c2) > 0"
            if a.key == "and":
                b.append("int area = (r2 - r1 + 1) * (c2 - c1 + 1);")
            b += ["T res = 0;", "for (int b = 0; b < bits; b++)", f"    if ({test}) res |= T(1) << b;", "return res;"]
            cpp += indent(b, 2) + ["    }", ""]
    cpp.append(f"    // O(1) -- the value at (r, c); {POINT_RULE_CPP}")
    cpp.append("    T pointGet(int r, int c) const {")
    cpp += indent(cpp_point_check("pointGet") + ["return vals[(size_t)r * C + c];"], 2) + ["    }", "};"]
    emit("grid-bit-counts-" + "-".join(aggs), ops, "bit-counts", costs, "R*C*log(U)", memory, py, cpp, [("values", "non-negative")])


# ------------------------------------------------------------------------------------------------ sparse tables
ST_AGGS = ["min", "max", "gcd", "and", "or"]


def py_four(a, names):
    """One expression combining four values."""
    w, x, y, z = names
    if a.key in ("min", "max"):
        return f"{a.key}({w}, {x}, {y}, {z})"
    if a.key == "gcd":
        return f"gcd({w}, {x}, {y}, {z})"
    s = {"and": "&", "or": "|"}[a.key]
    return f"{w} {s} {x} {s} {y} {s} {z}"


def py_two(a):
    if a.key == "min":
        return "x if x < y else y"
    if a.key == "max":
        return "x if x > y else y"
    if a.key == "gcd":
        return "gcd(x, y)"
    return {"and": "x & y", "or": "x | y"}[a.key]


def cpp_two(a, x, y):
    if a.key in ("min", "max"):
        return f"{a.key}({x}, {y})"
    if a.key == "gcd":
        return f"std::gcd({x}, {y})"
    return f"{x} {'&' if a.key == 'and' else '|'} {y}"


def sparse_rect(aggs):
    cls = "SparseTable2D"
    A = [AGGS[k] for k in aggs]
    g = "gcd" in aggs
    ops = ["pointGet"]
    for a in A:
        ops += [a.rect, a.all]
        if a.key in ("min", "max"):
            ops += [f"{a.key}{n}" for n, _, _ in CORNERS]
    costs = {op: "1" for op in ops}
    if g:
        costs.update({"rectGcd": "log(U) ?", "gcdAll": "log(U) ?"})
    memory = {"layout": "none", "node": " ".join(f"{a.arr}[1*R*C*log(R)*log(C)]" for a in A),
              "note": "per aggregate, one table for every pair of a power-of-two height and a power-of-two width "
                      "(the 1 x 1 table is the grid itself, shared)"}
    words = ", ".join(a.word for a in A)
    doc = (f"Static 2D sparse table ({words}): any rectangle in O(1){' (one gcd run, O(log U))' if g else ''}. For every "
           f"power-of-two height and power-of-two width there is a table holding the aggregate of each window of that "
           f"size; a rectangle is covered by four such windows, one in each corner (they overlap, which is fine: each of "
           f"these gives the same answer when a cell is counted twice). Memory and build are R * C * log R * log C. No "
           f"updates. Rows and columns are "
           f"0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.")
    py = []
    if g:
        py += ["from math import gcd", ""]
    py += ["", ""] + wrap_comment(doc, "#") + [f"class {cls}:"]
    py.append("    __slots__ = (" + ", ".join(f'"{s}"' for s in ["R", "C"] + [a.arr for a in A]) + ")")
    py += ["", f"    # O(R*C*logR*logC{'*logU' if g else ''}) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else ValueError",
           "    def __init__(self, grid):"]
    b = py_grid_check(cls) + ["flat = [v for row in grid for v in row]", "levelsR = R.bit_length()", "levelsC = C.bit_length()"]
    for a in A:
        b += [
            f"t = self.{a.arr} = [[None] * levelsC for _ in range(levelsR)]  # t[kr][kc]: windows of 2^kr rows by 2^kc columns",
            "t[0][0] = flat",
            "for kc in range(1, levelsC):",
            "    half = 1 << (kc - 1)",
            "    prevW = C - half + 1",
            "    prev = t[0][kc - 1]",
            "    cur = []",
            "    for r in range(R):",
            "        seg = prev[r * prevW:(r + 1) * prevW]",
            f"        cur += [{py_two(a)} for x, y in zip(seg, seg[half:])]",
            "    t[0][kc] = cur",
            "for kr in range(1, levelsR):",
            "    half = 1 << (kr - 1)",
            "    for kc in range(levelsC):",
            "        prev = t[kr - 1][kc]",
            "        off = half * (C - (1 << kc) + 1)",
            f"        t[kr][kc] = [{py_two(a)} for x, y in zip(prev, prev[off:])]",
        ]
    py += indent(b, 2) + [""]
    for a in A:
        py.append(f"    def _{a.key}Of(self, r1, c1, r2, c2):")
        py += indent([
            "kr = (r2 - r1 + 1).bit_length() - 1",
            "kc = (c2 - c1 + 1).bit_length() - 1",
            f"t = self.{a.arr}[kr][kc]",
            "w = self.C - (1 << kc) + 1",
            "i = r1 * w + c1",
            "j = (r2 - (1 << kr) + 1) * w + c1",
            "d = c2 - (1 << kc) + 1 - c1",
            f"return {py_four(a, ['t[i]', 't[i + d]', 't[j]', 't[j + d]'])}",
        ], 2) + [""]
        cost = "O(log U)" if a.key == "gcd" else "O(1)"
        py += indent(wrap_comment(f"{cost} -- {a.word} of rows r1..r2, columns c1..c2; {RECT_RULE_PY}", "#"))
        py.append(f"    def {a.rect}(self, r1, c1, r2, c2):")
        py += indent(py_rect_check(a.rect) + [f"return self._{a.key}Of(r1, c1, r2, c2)"], 2) + [""]
        py += [f"    # {cost} -- {a.word} of the whole grid", f"    def {a.all}(self):",
               f"        return self._{a.key}Of(0, 0, self.R - 1, self.C - 1)", ""]
        if a.key in ("min", "max"):
            for name, rs, cs in CORNERS:
                r_lo, r_hi = ("0", "r") if rs == "<=" else ("r", "self.R - 1")
                c_lo, c_hi = ("0", "c") if cs == "<=" else ("c", "self.C - 1")
                py += indent(wrap_comment(f"O(1) -- {a.word} of the cells with row {rs} r and column {cs} c; {POINT_RULE_PY}", "#"))
                py.append(f"    def {a.key}{name}(self, r, c):")
                py += indent(py_point_check(f"{a.key}{name}") + [f"return self._{a.key}Of({r_lo}, {c_lo}, {r_hi}, {c_hi})"], 2) + [""]
    py.append(f"    # O(1) -- the value at (r, c); {POINT_RULE_PY}")
    py.append("    def pointGet(self, r, c):")
    py += indent(py_point_check("pointGet") + [f"return self.{A[0].arr}[0][0][r * self.C + c]"], 2)

    cpp = wrap_comment(doc, "//") + ["// T is any integer type (int, long long, ...).", "template <typename T>", f"struct {cls} {{", "    int R, C, levelsR, levelsC;",
                                      "    vector<size_t> at;  // at[kr * levelsC + kc]: where the table of 2^kr rows by 2^kc columns starts in each array"]
    for a in A:
        cpp.append(f"    vector<T> {a.arr};  // every table back to back, each flat: (R - 2^kr + 1) rows of (C - 2^kc + 1)")
    cpp += ["", f"    // O(R*C*logR*logC{'*logU' if g else ''}) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws "
            "invalid_argument", f"    explicit {cls}(const vector<vector<T>>& grid)",
            "        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()) {"]
    b = cpp_grid_check(cls) + ["levelsR = 32 - __builtin_clz(R), levelsC = 32 - __builtin_clz(C);", "at.assign((size_t)levelsR * levelsC + 1, 0);",
                               "for (int kr = 0; kr < levelsR; kr++)", "    for (int kc = 0; kc < levelsC; kc++)",
                               "        at[kr * levelsC + kc + 1] = at[kr * levelsC + kc] + (size_t)(R - (1 << kr) + 1) * (C - (1 << kc) + 1);"]
    for a in A:
        b += [f"{a.arr}.assign(at.back(), T(0));", "for (int r = 0; r < R; r++)", f"    for (int c = 0; c < C; c++) {a.arr}[(size_t)r * C + c] = grid[r][c];"]
    b.append("buildLevels();")
    cpp += indent(b, 2) + ["    }", "", "    // every table from the ones half its size: first the wider ones of single rows, then the taller ones",
                           "    void buildLevels() {"]
    b = []
    for a in A:
        b += [
            "for (int kc = 1; kc < levelsC; kc++) {",
            "    int half = 1 << (kc - 1), prevW = C - half + 1, w = C - (1 << kc) + 1;",
            f"    const T* prev = &{a.arr}[at[kc - 1]];",
            f"    T* cur = &{a.arr}[at[kc]];",
            "    for (int r = 0; r < R; r++)",
            f"        for (int c = 0; c < w; c++) cur[(size_t)r * w + c] = {cpp_two(a, 'prev[(size_t)r * prevW + c]', 'prev[(size_t)r * prevW + c + half]')};",
            "}",
            "for (int kr = 1; kr < levelsR; kr++) {",
            "    int half = 1 << (kr - 1), h = R - (1 << kr) + 1;",
            "    for (int kc = 0; kc < levelsC; kc++) {",
            "        size_t w = C - (1 << kc) + 1, off = half * w, count = h * w;",
            f"        const T* prev = &{a.arr}[at[(kr - 1) * levelsC + kc]];",
            f"        T* cur = &{a.arr}[at[kr * levelsC + kc]];",
            f"        for (size_t i = 0; i < count; i++) cur[i] = {cpp_two(a, 'prev[i]', 'prev[i + off]')};",
            "    }",
            "}",
        ]
    cpp += indent(b, 2) + ["    }", ""]
    for a in A:
        cpp.append(f"    T {a.key}Of(int r1, int c1, int r2, int c2) const {{")
        cpp += indent([
            "int kr = 31 - __builtin_clz(r2 - r1 + 1), kc = 31 - __builtin_clz(c2 - c1 + 1);",
            f"const T* t = &{a.arr}[at[kr * levelsC + kc]];",
            "int w = C - (1 << kc) + 1, d = c2 - (1 << kc) + 1 - c1;",
            "size_t i = (size_t)r1 * w + c1, j = (size_t)(r2 - (1 << kr) + 1) * w + c1;",
            f"return {cpp_two(a, cpp_two(a, 't[i]', 't[i + d]'), cpp_two(a, 't[j]', 't[j + d]'))};"
            if a.key in ("min", "max", "gcd") else f"return {cpp_two(a, 't[i]', 't[i + d]')} {'&' if a.key == 'and' else '|'} "
                                                    f"{cpp_two(a, 't[j]', 't[j + d]')};",
        ], 2) + ["    }", ""]
        cost = "O(log U)" if a.key == "gcd" else "O(1)"
        cpp += indent(wrap_comment(f"{cost} -- {a.word} of rows r1..r2, columns c1..c2; {RECT_RULE_CPP}", "//"))
        cpp.append(f"    T {a.rect}(int r1, int c1, int r2, int c2) const {{")
        cpp += indent(cpp_rect_check(a.rect) + [f"return {a.key}Of(r1, c1, r2, c2);"], 2) + ["    }", ""]
        cpp += [f"    // {cost} -- {a.word} of the whole grid", f"    T {a.all}() const {{", f"        return {a.key}Of(0, 0, R - 1, C - 1);", "    }", ""]
        if a.key in ("min", "max"):
            for name, rs, cs in CORNERS:
                r_lo, r_hi = ("0", "r") if rs == "<=" else ("r", "R - 1")
                c_lo, c_hi = ("0", "c") if cs == "<=" else ("c", "C - 1")
                cpp += indent(wrap_comment(f"O(1) -- {a.word} of the cells with row {rs} r and column {cs} c; {POINT_RULE_CPP}", "//"))
                cpp.append(f"    T {a.key}{name}(int r, int c) const {{")
                cpp += indent(cpp_point_check(f"{a.key}{name}") + [f"return {a.key}Of({r_lo}, {c_lo}, {r_hi}, {c_hi});"], 2) + ["    }", ""]
    cpp.append(f"    // O(1) -- the value at (r, c); {POINT_RULE_CPP}")
    cpp.append("    T pointGet(int r, int c) const {")
    cpp += indent(cpp_point_check("pointGet") + [f"return {A[0].arr}[(size_t)r * C + c];"], 2) + ["    }", "};"]
    build = "R*C*log(R)*log(C)*log(U) ?" if g else "R*C*log(R)*log(C)"
    emit("grid-sparse-table-" + "-".join(aggs), ops, "sparse-table", costs, build, memory, py, cpp)


def difference_array():
    cls = "DifferenceArray2D"
    ops = ["rectAdd", "getAll"]
    costs = {"rectAdd": "1", "getAll": "R*C"}
    memory = {"layout": "none", "node": "diff[1*R*C]", "other": "base[1*R*C]",
              "note": "diff is (R + 1) by (C + 1), flat: each rectAdd writes its four corners"}
    doc = ("2D difference array: rectangle adds in O(1) each, then one O(R * C) pass (getAll) that turns them into the "
           "final grid. For when every update comes before any read: there are no queries in between (a Fenwick tree "
           "does rectAdd with pointGet in between at O(log R * log C) each). An add of v on rows r1..r2, columns c1..c2 "
           "marks +v at (r1, c1) and (r2 + 1, c2 + 1), and -v at (r1, c2 + 1) and (r2 + 1, c1); the 2D prefix sum of "
           "the marks is what every cell gained. Rows and columns are 0-based and rectangles are inclusive.")
    py = ["", ""] + wrap_comment(doc, "#") + [f"class {cls}:", '    __slots__ = ("R", "C", "W", "base", "diff")', "",
                                                "    # O(R*C) -- grid: R rows of C numbers each (the starting values); needs R >= 1 and C >= 1, else ValueError",
                                                "    def __init__(self, grid):"]
    py += indent(py_grid_check(cls) + ["self.W = C + 1", "self.base = [list(row) for row in grid]", "self.diff = [0] * ((R + 1) * (C + 1))"], 2)
    py += ["", f"    # O(1) -- adds v to every cell of rows r1..r2, columns c1..c2; {RECT_RULE_PY}", "    def rectAdd(self, r1, c1, r2, c2, v):"]
    py += indent(py_rect_check("rectAdd") + ["diff, W = self.diff, self.W", "diff[r1 * W + c1] += v", "diff[r1 * W + c2 + 1] -= v",
                                             "diff[(r2 + 1) * W + c1] -= v", "diff[(r2 + 1) * W + c2 + 1] += v"], 2)
    py += ["", "    # O(R*C) -- the whole grid as it stands (R rows of C values); more rectAdd calls can follow", "    def getAll(self):"]
    py += indent(["R, C, W, diff = self.R, self.C, self.W, self.diff", "out = []", "above = [0] * C",
                  "for r in range(R):", "    run = 0", "    at = r * W", "    row = self.base[r]", "    cur = []",
                  "    for c in range(C):", "        run += diff[at + c]", "        cur.append(above[c] + run)",
                  "    above = cur", "    out.append([cur[c] + row[c] for c in range(C)])", "return out"], 2)
    cpp = wrap_comment(doc, "//") + ["// T is any number type (int, long long, ...).", "template <typename T>", f"struct {cls} {{",
                                      "    int R, C, W;", "    vector<vector<T>> base;", "    vector<T> diff;", "",
                                      "    // O(R*C) -- grid: R rows of C numbers each (the starting values); needs R >= 1 and C >= 1, else throws",
                                      "    // invalid_argument",
                                      f"    explicit {cls}(const vector<vector<T>>& grid)",
                                      "        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()), W(C + 1), base(grid) {"]
    cpp += indent(cpp_grid_check(cls) + ["diff.assign((size_t)(R + 1) * W, 0);"], 2) + ["    }", ""]
    cpp += [f"    // O(1) -- adds v to every cell of rows r1..r2, columns c1..c2; {RECT_RULE_CPP}", "    void rectAdd(int r1, int c1, int r2, int c2, T v) {"]
    cpp += indent(cpp_rect_check("rectAdd") + ["diff[r1 * W + c1] += v;", "diff[r1 * W + c2 + 1] -= v;", "diff[(r2 + 1) * W + c1] -= v;",
                                               "diff[(r2 + 1) * W + c2 + 1] += v;"], 2) + ["    }", ""]
    cpp += ["    // O(R*C) -- the whole grid as it stands (R rows of C values); more rectAdd calls can follow", "    vector<vector<T>> getAll() const {"]
    cpp += indent(["vector<vector<T>> out(R, vector<T>(C));", "vector<T> above(C, 0);", "for (int r = 0; r < R; r++) {", "    T run = 0;",
                   "    for (int c = 0; c < C; c++) {", "        run += diff[r * W + c];", "        above[c] += run;",
                   "        out[r][c] = above[c] + base[r][c];", "    }", "}", "return out;"], 2) + ["    }", "};"]
    emit("grid-difference-array", ops, "difference-array", costs, "R*C", memory, py, cpp)


# ------------------------------------------------------------------------------------------------ 2D hashing
def hashing():
    cls = "Hash2D"
    ops = ["rectHash", "rectsEqual", "hashAll"]
    costs = {op: "1" for op in ops}
    memory = {"layout": "none", "node": "pre[1*R*C]", "other": "powR[1*R] powC[1*C]",
              "note": "pre is (R + 1) by (C + 1), flat: the hash of the rows above r and the columns left of c"}
    doc = ("2D hashing of a board (the 1D polynomial hash with one base per direction): the hash of any rectangle in O(1), "
           "and equal rectangles hash equal wherever they sit, so two rectangles of the same size can be compared in "
           "O(1). A cell (i, j) of a rectangle counts as value * A^(rows below it) * B^(columns right of it), mod the "
           "prime 2^61 - 1; the prefix table then gives a rectangle from four entries, each shifted by a power of A "
           "and B. Both bases and a value offset are picked at random each run, so no test can be built against them. "
           "Cells can be numbers or single characters. No updates. Rows and columns are 0-based and rectangles are "
           "inclusive: rows r1..r2, columns c1..c2.")
    py = ["import random", "", "_HP = (1 << 61) - 1  # hashes are mod this prime",
          "_HA = random.randrange(1 << 40, _HP - 1)  # the base down the rows, picked at random each run",
          "_HB = random.randrange(1 << 40, _HP - 1)  # the base along the columns",
          "_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0", "", ""]
    py += wrap_comment(doc, "#") + [f"class {cls}:", '    __slots__ = ("R", "C", "W", "pre", "powR", "powC")', "",
                                    "    # O(R*C) -- grid: R rows of C cells each (numbers or single characters; a list of strings works); needs R >= 1",
                                    "    # and C >= 1, else ValueError", "    def __init__(self, grid):"]
    py += indent(py_grid_check(cls) + [
        "W = self.W = C + 1",
        "P, A, B = _HP, _HA, _HB",
        "powR = self.powR = [1] * (R + 1)",
        "for i in range(R):",
        "    powR[i + 1] = powR[i] * A % P",
        "powC = self.powC = [1] * (C + 1)",
        "for j in range(C):",
        "    powC[j + 1] = powC[j] * B % P",
        "pre = self.pre = [0] * ((R + 1) * W)",
        "for r in range(R):",
        "    row = grid[r]",
        "    up = r * W",
        "    at = up + W",
        "    run = 0  # this row alone, left to right",
        "    for c in range(C):",
        "        v = row[c]",
        "        run = (run * B + (ord(v) if isinstance(v, str) else v) + _HO) % P",
        "        pre[at + c + 1] = (pre[up + c + 1] * A + run) % P",
    ], 2)
    py += ["", "    def _hashOf(self, r1, c1, r2, c2):"]
    py += indent(["pre, W, P = self.pre, self.W, _HP", "a = self.powR[r2 - r1 + 1]", "b = self.powC[c2 - c1 + 1]",
                  "top = r1 * W", "bot = (r2 + 1) * W",
                  "return (pre[bot + c2 + 1] - pre[top + c2 + 1] * a - pre[bot + c1] * b + pre[top + c1] * a % P * b) % P"], 2)
    py += [""] + indent(wrap_comment(f"O(1) -- hash of rows r1..r2, columns c1..c2: rectangles with equal cells hash equal; {RECT_RULE_PY}", "#"))
    py.append("    def rectHash(self, r1, c1, r2, c2):")
    py += indent(py_rect_check("rectHash") + ["return self._hashOf(r1, c1, r2, c2)"], 2)
    py += [""] + indent(wrap_comment("O(1) -- is the rectangle rows r1..r2, columns c1..c2 equal, cell by cell, to the same-size "
                                     "rectangle whose top-left cell is (r3, c3); needs both inside the grid, else IndexError", "#"))
    py.append("    def rectsEqual(self, r1, c1, r2, c2, r3, c3):")
    py += indent(["r4 = r3 + r2 - r1", "c4 = c3 + c2 - c1",
                  "ok = 0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C",
                  "if not (ok and 0 <= r3 and r4 < self.R and 0 <= c3 and c4 < self.C):"]
                 + indent(py_raise("IndexError", "rectsEqual: needs both rectangles inside the grid, got r1 = {r1}, c1 = {c1}, r2 = {r2}, "
                                   "c2 = {c2}, r3 = {r3}, c3 = {c3}, R = {self.R}, C = {self.C}", 3))
                 + ["return self._hashOf(r1, c1, r2, c2) == self._hashOf(r3, c3, r4, c4)"], 2)
    py += ["", "    # O(1) -- hash of the whole grid", "    def hashAll(self):", "        return self.pre[-1]"]

    cpp = wrap_comment(doc, "//") + ["// T is any integer or character type (int, long long, char, ...).", "template <typename T>", f"struct {cls} {{",
                                      "    using U64 = unsigned long long;", "    int R, C, W;", "    vector<U64> pre, powR, powC;", "",
                                      "    static U64 rnd() {",
                                      "        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());",
                                      "        return g();", "    }",
                                      "    // mod the prime 2^61 - 1, with both bases and the value offset picked at random each run",
                                      "    static constexpr U64 HP = (1ULL << 61) - 1;",
                                      "    static U64 HA() {", "        static U64 a = (1ULL << 40) + rnd() % (HP - (1ULL << 41));", "        return a;", "    }",
                                      "    static U64 HB() {", "        static U64 b = (1ULL << 40) + rnd() % (HP - (1ULL << 41));", "        return b;", "    }",
                                      "    static U64 HO() {", "        static U64 o = 1 + rnd() % (HP - 1);", "        return o;", "    }",
                                      "    static U64 hmul(U64 a, U64 b) {", "        __uint128_t c = (__uint128_t)a * b;",
                                      "        U64 r = (U64)(c & HP) + (U64)(c >> 61);", "        r = (r & HP) + (r >> 61);",
                                      "        return r >= HP ? r - HP : r;", "    }",
                                      "    static U64 hadd(U64 a, U64 b) { return a + b >= HP ? a + b - HP : a + b; }",
                                      "    static U64 hsub(U64 a, U64 b) { return a >= b ? a - b : a + HP - b; }",
                                      "    // a cell's own hash: its value mod the prime (negatives wrap around), shifted by the offset",
                                      "    static U64 cell(T v) {", "        long long x = (long long)v % (long long)HP;",
                                      "        return hadd(x < 0 ? (U64)(x + (long long)HP) : (U64)x, HO());", "    }", "",
                                      "    // O(R*C) -- grid: R rows of C cells each (a vector<string> works with T = char); needs R >= 1 and C >= 1, else",
                                      "    // throws invalid_argument",
                                      "    template <typename Row>",
                                      f"    explicit {cls}(const vector<Row>& grid)",
                                      "        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()), W(C + 1) {"]
    cpp += indent(cpp_grid_check(cls) + [
        "powR.assign(R + 1, 1);",
        "for (int i = 0; i < R; i++) powR[i + 1] = hmul(powR[i], HA());",
        "powC.assign(C + 1, 1);",
        "for (int j = 0; j < C; j++) powC[j + 1] = hmul(powC[j], HB());",
        "pre.assign((size_t)(R + 1) * W, 0);",
        "for (int r = 0; r < R; r++) {",
        "    int up = r * W, at = up + W;",
        "    U64 run = 0;  // this row alone, left to right",
        "    for (int c = 0; c < C; c++) {",
        "        run = hadd(hmul(run, HB()), cell(grid[r][c]));",
        "        pre[at + c + 1] = hadd(hmul(pre[up + c + 1], HA()), run);",
        "    }",
        "}",
    ], 2) + ["    }", ""]
    cpp += ["    U64 hashOf(int r1, int c1, int r2, int c2) const {"]
    cpp += indent(["U64 a = powR[r2 - r1 + 1], b = powC[c2 - c1 + 1];", "int top = r1 * W, bot = (r2 + 1) * W;",
                   "U64 res = hsub(pre[bot + c2 + 1], hmul(pre[top + c2 + 1], a));",
                   "res = hsub(res, hmul(pre[bot + c1], b));",
                   "return hadd(res, hmul(hmul(pre[top + c1], a), b));"], 2) + ["    }", ""]
    cpp += indent(wrap_comment(f"O(1) -- hash of rows r1..r2, columns c1..c2: rectangles with equal cells hash equal; {RECT_RULE_CPP}", "//"))
    cpp.append("    U64 rectHash(int r1, int c1, int r2, int c2) const {")
    cpp += indent(cpp_rect_check("rectHash") + ["return hashOf(r1, c1, r2, c2);"], 2) + ["    }", ""]
    cpp += indent(wrap_comment("O(1) -- is the rectangle rows r1..r2, columns c1..c2 equal, cell by cell, to the same-size rectangle "
                               "whose top-left cell is (r3, c3); needs both inside the grid, else throws out_of_range", "//"))
    cpp.append("    bool rectsEqual(int r1, int c1, int r2, int c2, int r3, int c3) const {")
    cpp += indent(["int r4 = r3 + r2 - r1, c4 = c3 + c2 - c1;",
                   "if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C || r3 < 0 || r4 >= R || c3 < 0 || c4 >= C)",
                   '    throw out_of_range("rectsEqual: needs both rectangles inside the grid");',
                   "return hashOf(r1, c1, r2, c2) == hashOf(r3, c3, r4, c4);"], 2) + ["    }", ""]
    cpp += ["    // O(1) -- hash of the whole grid", "    U64 hashAll() const {", "        return pre.back();", "    }", "};"]
    emit("grid-hash", ops, "hash", costs, "R*C", memory, py, cpp)


def main():
    n = 0
    for aggs in (["sum"], ["xor"], ["sum", "xor"]):
        prefix(aggs)
        n += 1
    for aggs in subsets(["and", "or"]):
        bit_counts(aggs)
        n += 1
    for aggs in subsets(ST_AGGS):
        sparse_rect(aggs)
        n += 1
    difference_array()
    hashing()
    print(f"grid static: {n + 2} folders")


if __name__ == "__main__":
    main()
