"""3D grids, X by Y by Z: a small set (sum, min, max; no bit ops).

    python3 gen_3d.py              # writes range-queries-2d/3d-.../template.{py,cpp}

  3d-seg-tree-<aggregates>         point updates, any box: a tree over x of trees over y of trees over z, one flat array
  3d-bit-sum                       point updates, box sum: a 3D Fenwick tree
  3d-bit-corner-<max|min>-...      point chmax (chmin), max (min) over a corner (all three <=, or all three >=)

The constructor takes the three sides; cells start empty (0 in a template with no min or max).
"""
from lib2d import AGGS, cpp_throw, header, indent, py_raise, read_agg, subsets, wrap_comment, write

CORNERS = [("LteLteLte", "<="), ("GteGteGte", ">=")]
POINT_RULE_PY = "needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else IndexError"
POINT_RULE_CPP = "needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range"
BOX_RULE_PY = "needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z, else IndexError"
BOX_RULE_CPP = "needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z, else throws out_of_range"
BOX_OP = {"sum": "boxSum", "min": "boxMin", "max": "boxMax"}


def emit(folder, ops, dstype, costs, build, memory, py, cpp, extra=()):
    args = (ops, dstype, costs, build, memory, "grid-3d", list(extra))
    write(folder, header(folder, "py", *args) + py, header(folder, "cpp", *args) + cpp)


def py_point_check(name):
    return ["if not (0 <= x < self.X and 0 <= y < self.Y and 0 <= z < self.Z):"] + indent(py_raise(
        "IndexError", f"{name}: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, got x = {{x}}, y = {{y}}, z = {{z}}, X = {{self.X}}, "
        "Y = {self.Y}, Z = {self.Z}", 3))


def py_box_check(name):
    return ["if not (0 <= x1 <= x2 < self.X and 0 <= y1 <= y2 < self.Y and 0 <= z1 <= z2 < self.Z):"] + indent(py_raise(
        "IndexError", f"{name}: needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z, got x1 = {{x1}}, y1 = {{y1}}, "
        "z1 = {z1}, x2 = {x2}, y2 = {y2}, z2 = {z2}, X = {self.X}, Y = {self.Y}, Z = {self.Z}", 3))


def cpp_point_check(name):
    return cpp_throw("x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z", "out_of_range",
                     f"{name}: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z", 2)


def cpp_box_check(name):
    return ["if (x1 < 0 || x1 > x2 || x2 >= X || y1 < 0 || y1 > y2 || y2 >= Y || z1 < 0 || z1 > z2 || z2 >= Z)",
            f'    throw out_of_range("{name}: needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z");']


def py_size_check(cls):
    return ["if X < 1 or Y < 1 or Z < 1:", f'    raise ValueError(f"{cls}: needs X >= 1, Y >= 1 and Z >= 1, got X = {{X}}, Y = {{Y}}, Z = {{Z}}")']


# ------------------------------------------------------------------------------------------------ segment tree
def seg_tree(aggs):
    cls = "SegTree3D"
    A = [AGGS[k] for k in aggs]
    mm = "min" in aggs or "max" in aggs
    rd = read_agg(aggs)
    ops = ["pointGet", "pointAssign", "pointAdd", "pointChmax", "pointChmin"]
    for a in A:
        ops += [BOX_OP[a.key], a.all]
        if a.key in ("min", "max"):
            ops += [f"{a.key}{n}" for n, _ in CORNERS]
    costs = {op: "log(X)*log(Y)*log(Z)" for op in ops}
    costs.update({"pointGet": "1", **{a.all: "1" for a in A}})
    memory = {"layout": "2n-iterative", "node": " ".join(f"{a.arr}[8*X*Y*Z]" for a in A),
              "note": "one flat array per aggregate, 2X x-nodes by 2Y y-nodes by 2Z z-nodes"}
    words = ", ".join(a.word for a in A)
    text = (f"3D segment tree ({words}): point updates and any-box queries on an X x Y x Z grid, O(log X * log Y * log Z) each. "
            f"A bottom-up tree over x whose every node is a tree over y whose every node is a tree over z, in one flat array "
            f"per aggregate (8 * X * Y * Z entries each, so the three sides have to be small: compress coordinates first). "
            f"Coordinates are 0-based and boxes are inclusive: x1..x2, y1..y2, z1..z2.")
    if mm:
        empty = ["a min / max over no set cell is {NONE}"] + (["a sum over none is 0"] if "sum" in aggs else [])
        text += f" Every cell starts empty and queries only see set cells: {'; '.join(empty)}."
    else:
        text += " Every cell starts at 0."
    arrs = ", ".join(a.arr for a in A)
    self_arrs = ", ".join(f"self.{a.arr}" for a in A)

    py = []
    if "max" in aggs:
        py.append('NEG = float("-inf")  # an empty cell in the max array')
    if "min" in aggs:
        py.append('POS = float("inf")  # an empty cell in the min array')
    py += ["", ""] + wrap_comment(text.replace("{NONE}", "None"), "#") + [f"class {cls}:"]
    py.append("    __slots__ = (" + ", ".join(f'"{s}"' for s in ["X", "Y", "Z", "SY", "SZ"] + [a.arr for a in A]) + ")")
    py += ["", f"    # O(X*Y*Z) -- X by Y by Z, every cell {'empty' if mm else '0'}; needs X >= 1, Y >= 1 and Z >= 1, else ValueError", "    def __init__(self, X, Y, Z):"]
    b = py_size_check(cls) + ["self.X = X", "self.Y = Y", "self.Z = Z", "self.SY = 2 * Y  # y-nodes per x-node", "self.SZ = 2 * Z  # z-nodes per y-node"]
    for a in A:
        b.append(f"self.{a.arr} = [{a.py_id if mm else 0}] * (8 * X * Y * Z)")
    py += indent(b, 2) + [""]

    def merges(dst, lo, hi, n):
        out = []
        for a in A:
            out += a.py_merge(f"{a.arr}[{dst}]", f"{a.arr}[{lo}]", f"{a.arr}[{hi}]")
        return indent(out, n)

    py += ["    # cell (x, y, z) = v, then every node above it", "    def _set(self, x, y, z, v):"]
    b = ["X, Y, Z, SY, SZ = self.X, self.Y, self.Z, self.SY, self.SZ", f"{arrs} = {self_arrs}", "px = x + X", "py = y + Y",
         "base = (px * SY + py) * SZ  # the cell's own z-tree"]
    for a in A:
        b.append(f"{a.arr}[base + z + Z] = v")
    b += ["pz = (z + Z) >> 1", "while pz:"] + merges("base + pz", "base + 2 * pz", "base + 2 * pz + 1", 1) + ["    pz >>= 1", "py >>= 1",
         "while py:  # the y-nodes above, still in the cell's own x", "    base = (px * SY + py) * SZ", "    lo = (px * SY + 2 * py) * SZ", "    hi = lo + SZ", "    pz = z + Z", "    while pz:"]
    b += merges("base + pz", "lo + pz", "hi + pz", 2) + ["        pz >>= 1", "    py >>= 1", "px >>= 1", "step = SY * SZ", "while px:  # the x-nodes above",
         "    py = y + Y", "    while py:", "        base = (px * SY + py) * SZ", "        lo = (2 * px * SY + py) * SZ", "        hi = lo + step", "        pz = z + Z", "        while pz:"]
    b += merges("base + pz", "lo + pz", "hi + pz", 3) + ["            pz >>= 1", "        py >>= 1", "    px >>= 1"]
    py += indent(b, 2) + [""]
    leaf = "self." + rd.arr + "[((x + self.X) * self.SY + y + self.Y) * self.SZ + z + self.Z]"
    is_empty = {"max": "cur == NEG", "min": "cur == POS"}.get(rd.key)
    if_empty = "; an empty cell becomes v" if mm else ""
    cost = "O(log X * log Y * log Z)"
    py.append(f"    # O(1) -- the value at (x, y, z){', None if the cell is empty' if mm else ''}; {POINT_RULE_PY}")
    py.append("    def pointGet(self, x, y, z):")
    py += indent(py_point_check("pointGet") + ([f"cur = {leaf}", f"return None if {is_empty} else cur"] if mm else [f"return {leaf}"]), 2) + [""]
    py += indent(wrap_comment(f"{cost} -- the cell at (x, y, z) becomes v (it may go down as well as up); {POINT_RULE_PY}", "#"))
    py.append("    def pointAssign(self, x, y, z, v):")
    py += indent(py_point_check("pointAssign") + ["self._set(x, y, z, v)"], 2) + [""]
    py += indent(wrap_comment(f"{cost} -- adds v to the cell at (x, y, z){if_empty}; {POINT_RULE_PY}", "#"))
    py.append("    def pointAdd(self, x, y, z, v):")
    py += indent(py_point_check("pointAdd") + [f"cur = {leaf}", f"self._set(x, y, z, v if {is_empty} else cur + v)" if mm else "self._set(x, y, z, cur + v)"], 2) + [""]
    for name, sym, word in (("pointChmax", ">", "max"), ("pointChmin", "<", "min")):
        py += indent(wrap_comment(f"{cost} -- the cell at (x, y, z) becomes {word}(itself, v){if_empty}; {POINT_RULE_PY}", "#"))
        py.append(f"    def {name}(self, x, y, z, v):")
        py += indent(py_point_check(name) + [f"cur = {leaf}", f"if {is_empty + ' or ' if mm else ''}v {sym} cur:", "    self._set(x, y, z, v)"], 2) + [""]
    for a in A:
        py.append(f"    def _{a.key}Of(self, x1, y1, z1, x2, y2, z2):")

        def zloop(n):
            return indent(["lz = zl", "rz = zr", "while lz < rz:", "    if lz & 1:", *indent(a.py_take("res", f"{a.arr}[base + lz]"), 2), "        lz += 1",
                           "    if rz & 1:", "        rz -= 1", *indent(a.py_take("res", f"{a.arr}[base + rz]"), 2), "    lz >>= 1", "    rz >>= 1"], n)

        def yloop(node, n):
            return indent(["ly = yl", "ry = yr", "while ly < ry:", "    if ly & 1:", f"        base = ({node} * SY + ly) * SZ", *zloop(2), "        ly += 1",
                           "    if ry & 1:", "        ry -= 1", f"        base = ({node} * SY + ry) * SZ", *zloop(2), "    ly >>= 1", "    ry >>= 1"], n)

        b = ["X, Y, Z, SY, SZ = self.X, self.Y, self.Z, self.SY, self.SZ", f"{a.arr} = self.{a.arr}", f"res = {a.py_id}", "yl = y1 + Y", "yr = y2 + Y + 1",
             "zl = z1 + Z", "zr = z2 + Z + 1", "lx = x1 + X", "rx = x2 + X + 1", "while lx < rx:", "    if lx & 1:"] + yloop("lx", 2) + ["        lx += 1", "    if rx & 1:", "        rx -= 1"]
        b += yloop("rx", 2) + ["    lx >>= 1", "    rx >>= 1", f"return {a.py_result('res')}"]
        py += indent(b, 2) + [""]
        what = (f"{a.word} of the set cells in the box x1..x2, y1..y2, z1..z2 ({a.none_words_py} if there are none)" if mm
                else f"{a.word} of the box x1..x2, y1..y2, z1..z2")
        py += indent(wrap_comment(f"{cost} -- {what}; {BOX_RULE_PY}", "#"))
        py.append(f"    def {BOX_OP[a.key]}(self, x1, y1, z1, x2, y2, z2):")
        py += indent(py_box_check(BOX_OP[a.key]) + [f"return self._{a.key}Of(x1, y1, z1, x2, y2, z2)"], 2) + [""]
        py.append(f"    # O(1) -- {a.word} of every set cell ({a.none_words_py} if there are none)" if mm else f"    # O(1) -- {a.word} of the whole grid")
        py.append(f"    def {a.all}(self):")
        root = f"self.{a.arr}[(self.SY + 1) * self.SZ + 1]"
        py += ([f"        res = {root}", f"        return {a.py_result('res')}"] if a.key in ("min", "max") else [f"        return {root}"]) + [""]
        if a.key in ("min", "max"):
            for n, s in CORNERS:
                box = "0, 0, 0, x, y, z" if s == "<=" else "x, y, z, self.X - 1, self.Y - 1, self.Z - 1"
                py += indent(wrap_comment(f"{cost} -- {a.word} of the set cells with all three coordinates {s} x, y, z (None if there are none); {POINT_RULE_PY}", "#"))
                py.append(f"    def {a.key}{n}(self, x, y, z):")
                py += indent(py_point_check(f"{a.key}{n}") + [f"return self._{a.key}Of({box})"], 2) + [""]
    while py[-1] == "":
        py.pop()

    none_cpp = " / ".join(AGGS[k].none_cpp for k in aggs if k in ("min", "max"))
    cpp = wrap_comment(text.replace("{NONE}", none_cpp), "//")
    cpp.append("// T is any integer type (int, long long, ...)" + ("; sums are kept in S (long long for a smaller T)." if "sum" in aggs else "."))
    cpp += ["template <typename T>", f"struct {cls} {{"]
    if "sum" in aggs:
        cpp.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;")
    if "max" in aggs:
        cpp.append("    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no set cell gives")
    if "min" in aggs:
        cpp.append("    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set cell gives")
    cpp.append("    int X, Y, Z, SY, SZ;  // SY = 2Y y-nodes per x-node, SZ = 2Z z-nodes per y-node")
    for a in A:
        cpp.append(f"    vector<{a.cpp_type}> {a.arr};")
    cpp += ["", f"    // O(X*Y*Z) -- X by Y by Z, every cell {'empty' if mm else '0'}; needs X >= 1, Y >= 1 and Z >= 1, else throws invalid_argument",
            f"    {cls}(int X, int Y, int Z) : X(X), Y(Y), Z(Z), SY(2 * Y), SZ(2 * Z) {{",
            f'        if (X < 1 || Y < 1 || Z < 1) throw invalid_argument("{cls}: needs X >= 1, Y >= 1 and Z >= 1");']
    for a in A:
        cpp.append(f"        {a.arr}.assign((size_t)8 * X * Y * Z, {a.cpp_id if mm else a.cpp_type + '(0)'});")
    cpp += ["    }", "", "    size_t at(int px, int py, int pz) const { return ((size_t)px * SY + py) * SZ + pz; }", ""]
    cpp += ["    // cell (x, y, z) = v, then every node above it", "    void setCell(int x, int y, int z, T v) {"]
    b = ["for (int px = x + X; px >= 1; px >>= 1)", "    for (int py = y + Y; py >= 1; py >>= 1)", "        for (int pz = z + Z; pz >= 1; pz >>= 1) {", "            size_t i = at(px, py, pz);"]
    for a in A:
        b += [f"            if (px < X) {a.arr}[i] = {a.cpp_comb(f'{a.arr}[at(2 * px, py, pz)]', f'{a.arr}[at(2 * px + 1, py, pz)]')};",
              f"            else if (py < Y) {a.arr}[i] = {a.cpp_comb(f'{a.arr}[at(px, 2 * py, pz)]', f'{a.arr}[at(px, 2 * py + 1, pz)]')};",
              f"            else if (pz < Z) {a.arr}[i] = {a.cpp_comb(f'{a.arr}[at(px, py, 2 * pz)]', f'{a.arr}[at(px, py, 2 * pz + 1)]')};",
              f"            else {a.arr}[i] = v;"]
    b.append("        }")
    cpp += indent(b, 2) + ["    }", ""]
    leaf_cpp = f"{rd.arr}[at(x + X, y + Y, z + Z)]"
    is_empty_cpp = {"max": "cur == NO_MAX", "min": "cur == NO_MIN"}.get(rd.key)
    cpp += indent(wrap_comment(f"O(1) -- the value at (x, y, z){', ' + rd.none_words_cpp + ' if the cell is empty' if mm else ''}; {POINT_RULE_CPP}", "//"))
    cpp.append("    T pointGet(int x, int y, int z) const {")
    cpp += indent(cpp_point_check("pointGet") + [f"return T({leaf_cpp});"], 2) + ["    }", ""]
    cpp += indent(wrap_comment(f"{cost} -- the cell at (x, y, z) becomes v (it may go down as well as up); {POINT_RULE_CPP}", "//"))
    cpp.append("    void pointAssign(int x, int y, int z, T v) {")
    cpp += indent(cpp_point_check("pointAssign") + ["setCell(x, y, z, v);"], 2) + ["    }", ""]
    cpp += indent(wrap_comment(f"{cost} -- adds v to the cell at (x, y, z){if_empty}; {POINT_RULE_CPP}", "//"))
    cpp.append("    void pointAdd(int x, int y, int z, T v) {")
    cpp += indent(cpp_point_check("pointAdd") + [f"T cur = T({leaf_cpp});", f"setCell(x, y, z, {is_empty_cpp} ? v : T(cur + v));" if mm else "setCell(x, y, z, T(cur + v));"], 2) + ["    }", ""]
    for name, sym, word in (("pointChmax", ">", "max"), ("pointChmin", "<", "min")):
        cpp += indent(wrap_comment(f"{cost} -- the cell at (x, y, z) becomes {word}(itself, v){if_empty}; {POINT_RULE_CPP}", "//"))
        cpp.append(f"    void {name}(int x, int y, int z, T v) {{")
        cpp += indent(cpp_point_check(name) + [f"T cur = T({leaf_cpp});", f"if ({is_empty_cpp + ' || ' if mm else ''}v {sym} cur) setCell(x, y, z, v);"], 2) + ["    }", ""]
    for a in A:
        t = a.cpp_type
        cpp += [f"    {t} {a.key}OverZ(int px, int py, int z1, int z2) const {{", f"        {t} res = {a.cpp_id};",
                "        for (int lz = z1 + Z, rz = z2 + Z + 1; lz < rz; lz >>= 1, rz >>= 1) {",
                f"            if (lz & 1) {a.cpp_take('res', f'{a.arr}[at(px, py, lz++)]')}", f"            if (rz & 1) {a.cpp_take('res', f'{a.arr}[at(px, py, --rz)]')}",
                "        }", "        return res;", "    }", "",
                f"    {t} {a.key}OverYZ(int px, int y1, int z1, int y2, int z2) const {{", f"        {t} res = {a.cpp_id};",
                "        for (int ly = y1 + Y, ry = y2 + Y + 1; ly < ry; ly >>= 1, ry >>= 1) {",
                f"            if (ly & 1) {a.cpp_take('res', f'{a.key}OverZ(px, ly++, z1, z2)')}", f"            if (ry & 1) {a.cpp_take('res', f'{a.key}OverZ(px, --ry, z1, z2)')}",
                "        }", "        return res;", "    }", "",
                f"    {t} {a.key}Of(int x1, int y1, int z1, int x2, int y2, int z2) const {{", f"        {t} res = {a.cpp_id};",
                "        for (int lx = x1 + X, rx = x2 + X + 1; lx < rx; lx >>= 1, rx >>= 1) {",
                f"            if (lx & 1) {a.cpp_take('res', f'{a.key}OverYZ(lx++, y1, z1, y2, z2)')}", f"            if (rx & 1) {a.cpp_take('res', f'{a.key}OverYZ(--rx, y1, z1, y2, z2)')}",
                "        }", "        return res;", "    }", ""]
        what = (f"{a.word} of the set cells in the box x1..x2, y1..y2, z1..z2 ({a.none_words_cpp} if there are none)" if mm
                else f"{a.word} of the box x1..x2, y1..y2, z1..z2")
        cpp += indent(wrap_comment(f"{cost} -- {what}; {BOX_RULE_CPP}", "//"))
        cpp.append(f"    {t} {BOX_OP[a.key]}(int x1, int y1, int z1, int x2, int y2, int z2) const {{")
        cpp += indent(cpp_box_check(BOX_OP[a.key]) + [f"return {a.key}Of(x1, y1, z1, x2, y2, z2);"], 2) + ["    }", ""]
        cpp.append(f"    // O(1) -- {a.word} of every set cell ({a.none_words_cpp} if there are none)" if mm else f"    // O(1) -- {a.word} of the whole grid")
        cpp += [f"    {t} {a.all}() const {{", f"        return {a.arr}[at(1, 1, 1)];", "    }", ""]
        if a.key in ("min", "max"):
            for n, s in CORNERS:
                box = "0, 0, 0, x, y, z" if s == "<=" else "x, y, z, X - 1, Y - 1, Z - 1"
                cpp += indent(wrap_comment(f"{cost} -- {a.word} of the set cells with all three coordinates {s} x, y, z ({a.none_words_cpp} if there are none); {POINT_RULE_CPP}", "//"))
                cpp.append(f"    T {a.key}{n}(int x, int y, int z) const {{")
                cpp += indent(cpp_point_check(f"{a.key}{n}") + [f"return {a.key}Of({box});"], 2) + ["    }", ""]
    while cpp[-1] == "":
        cpp.pop()
    cpp.append("};")
    emit("3d-seg-tree-" + "-".join(aggs), ops, "seg-tree", costs, "X*Y*Z", memory, py, cpp, [("empty-cells", "yes")] if mm else [])


# ------------------------------------------------------------------------------------------------ Fenwick, sum
def bit_sum():
    cls = "Fenwick3D"
    ops = ["pointGet", "pointAssign", "pointAdd", "pointChmax", "pointChmin", "boxSum", "sumAll"]
    costs = {op: "log(X)*log(Y)*log(Z)" for op in ops}
    costs.update({"pointGet": "1", "sumAll": "1"})
    memory = {"layout": "none", "node": "sm[1*X*Y*Z]", "other": "vals[1*X*Y*Z]", "note": "the Fenwick tree is (X + 1) by (Y + 1) by (Z + 1), flat, 1-based"}
    doc = ("3D Fenwick tree (sum): point updates and any-box sums on an X x Y x Z grid, O(log X * log Y * log Z) each, with an "
           "eighth of a 3D segment tree's memory. A box is eight prefix queries added and subtracted. Every cell starts at 0. "
           "Coordinates are 0-based and boxes are inclusive: x1..x2, y1..y2, z1..z2.")
    cost = "O(log X * log Y * log Z)"
    py = ["", ""] + wrap_comment(doc, "#") + [f"class {cls}:", '    __slots__ = ("X", "Y", "Z", "SY", "SZ", "sm", "vals", "total")', "",
                                                "    # O(X*Y*Z) -- X by Y by Z, every cell 0; needs X >= 1, Y >= 1 and Z >= 1, else ValueError", "    def __init__(self, X, Y, Z):"]
    py += indent(py_size_check(cls) + ["self.X = X", "self.Y = Y", "self.Z = Z", "self.SY = Y + 1", "self.SZ = Z + 1", "self.sm = [0] * ((X + 1) * (Y + 1) * (Z + 1))",
                                       "self.vals = [0] * (X * Y * Z)", "self.total = 0"], 2)
    py += ["", "    # cell (x, y, z) becomes v", "    def _set(self, x, y, z, v):"]
    py += indent(["X, Y, Z, SY, SZ, sm = self.X, self.Y, self.Z, self.SY, self.SZ, self.sm", "at = (x * Y + y) * Z + z", "d = v - self.vals[at]", "self.vals[at] = v",
                  "self.total += d", "i = x + 1", "while i <= X:", "    j = y + 1", "    while j <= Y:", "        base = (i * SY + j) * SZ", "        k = z + 1",
                  "        while k <= Z:", "            sm[base + k] += d", "            k += k & -k", "        j += j & -j", "    i += i & -i"], 2)
    py += ["", "    # sum of the cells with all three coordinates below x, y, z", "    def _prefix(self, x, y, z):"]
    py += indent(["SY, SZ, sm, res = self.SY, self.SZ, self.sm, 0", "i = x", "while i > 0:", "    j = y", "    while j > 0:", "        base = (i * SY + j) * SZ", "        k = z",
                  "        while k > 0:", "            res += sm[base + k]", "            k &= k - 1", "        j &= j - 1", "    i &= i - 1", "return res"], 2) + [""]
    leaf = "self.vals[(x * self.Y + y) * self.Z + z]"
    py.append(f"    # O(1) -- the value at (x, y, z); {POINT_RULE_PY}")
    py.append("    def pointGet(self, x, y, z):")
    py += indent(py_point_check("pointGet") + [f"return {leaf}"], 2) + [""]
    for name, text, lines in (
        ("pointAssign", "the cell at (x, y, z) becomes v", ["self._set(x, y, z, v)"]),
        ("pointAdd", "adds v to the cell at (x, y, z)", [f"self._set(x, y, z, {leaf} + v)"]),
        ("pointChmax", "the cell at (x, y, z) becomes max(itself, v)", [f"if v > {leaf}:", "    self._set(x, y, z, v)"]),
        ("pointChmin", "the cell at (x, y, z) becomes min(itself, v)", [f"if v < {leaf}:", "    self._set(x, y, z, v)"]),
    ):
        py += indent(wrap_comment(f"{cost} -- {text}; {POINT_RULE_PY}", "#"))
        py.append(f"    def {name}(self, x, y, z, v):")
        py += indent(py_point_check(name) + lines, 2) + [""]
    py += indent(wrap_comment(f"{cost} -- sum of the box x1..x2, y1..y2, z1..z2; {BOX_RULE_PY}", "#"))
    py.append("    def boxSum(self, x1, y1, z1, x2, y2, z2):")
    py += indent(py_box_check("boxSum") + ["p = self._prefix", "x2 += 1", "y2 += 1", "z2 += 1",
                                           "return (p(x2, y2, z2) - p(x1, y2, z2) - p(x2, y1, z2) - p(x2, y2, z1)",
                                           "        + p(x1, y1, z2) + p(x1, y2, z1) + p(x2, y1, z1) - p(x1, y1, z1))"], 2)
    py += ["", "    # O(1) -- sum of the whole grid", "    def sumAll(self):", "        return self.total"]

    cpp = wrap_comment(doc, "//") + ["// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T).", "template <typename T>", f"struct {cls} {{",
                                      "    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;", "    int X, Y, Z, SY, SZ;", "    vector<S> sm;", "    vector<T> vals;", "    S total = 0;", "",
                                      "    // O(X*Y*Z) -- X by Y by Z, every cell 0; needs X >= 1, Y >= 1 and Z >= 1, else throws invalid_argument",
                                      f"    {cls}(int X, int Y, int Z) : X(X), Y(Y), Z(Z), SY(Y + 1), SZ(Z + 1) {{",
                                      f'        if (X < 1 || Y < 1 || Z < 1) throw invalid_argument("{cls}: needs X >= 1, Y >= 1 and Z >= 1");',
                                      "        sm.assign((size_t)(X + 1) * SY * SZ, 0);", "        vals.assign((size_t)X * Y * Z, T(0));", "    }", "",
                                      "    size_t cell(int x, int y, int z) const { return ((size_t)x * Y + y) * Z + z; }", "",
                                      "    // cell (x, y, z) becomes v", "    void setCell(int x, int y, int z, T v) {"]
    cpp += indent(["S d = S(v) - vals[cell(x, y, z)];", "vals[cell(x, y, z)] = v;", "total += d;", "for (int i = x + 1; i <= X; i += i & -i)", "    for (int j = y + 1; j <= Y; j += j & -j)",
                   "        for (int k = z + 1; k <= Z; k += k & -k) sm[((size_t)i * SY + j) * SZ + k] += d;"], 2)
    cpp += ["    }", "", "    // sum of the cells with all three coordinates below x, y, z", "    S prefix(int x, int y, int z) const {"]
    cpp += indent(["S res = 0;", "for (int i = x; i > 0; i &= i - 1)", "    for (int j = y; j > 0; j &= j - 1)", "        for (int k = z; k > 0; k &= k - 1) res += sm[((size_t)i * SY + j) * SZ + k];", "return res;"], 2)
    cpp += ["    }", "", f"    // O(1) -- the value at (x, y, z); {POINT_RULE_CPP}", "    T pointGet(int x, int y, int z) const {"]
    cpp += indent(cpp_point_check("pointGet") + ["return vals[cell(x, y, z)];"], 2) + ["    }", ""]
    for name, text, body in (
        ("pointAssign", "the cell at (x, y, z) becomes v", "setCell(x, y, z, v);"),
        ("pointAdd", "adds v to the cell at (x, y, z)", "setCell(x, y, z, T(vals[cell(x, y, z)] + v));"),
        ("pointChmax", "the cell at (x, y, z) becomes max(itself, v)", "if (v > vals[cell(x, y, z)]) setCell(x, y, z, v);"),
        ("pointChmin", "the cell at (x, y, z) becomes min(itself, v)", "if (v < vals[cell(x, y, z)]) setCell(x, y, z, v);"),
    ):
        cpp += indent(wrap_comment(f"{cost} -- {text}; {POINT_RULE_CPP}", "//"))
        cpp.append(f"    void {name}(int x, int y, int z, T v) {{")
        cpp += indent(cpp_point_check(name) + [body], 2) + ["    }", ""]
    cpp += indent(wrap_comment(f"{cost} -- sum of the box x1..x2, y1..y2, z1..z2; {BOX_RULE_CPP}", "//"))
    cpp.append("    S boxSum(int x1, int y1, int z1, int x2, int y2, int z2) const {")
    cpp += indent(cpp_box_check("boxSum") + ["x2++, y2++, z2++;", "return prefix(x2, y2, z2) - prefix(x1, y2, z2) - prefix(x2, y1, z2) - prefix(x2, y2, z1)",
                                             "     + prefix(x1, y1, z2) + prefix(x1, y2, z1) + prefix(x2, y1, z1) - prefix(x1, y1, z1);"], 2)
    cpp += ["    }", "", "    // O(1) -- sum of the whole grid", "    S sumAll() const {", "        return total;", "    }", "};"]
    emit("3d-bit-sum", ops, "BIT", costs, "X*Y*Z", memory, py, cpp)


# ------------------------------------------------------------------------------------------------ Fenwick, corner max / min
def corner_bit(kind, corners):
    a = AGGS[kind]
    cls = f"Corner{a.cap}Fenwick3D"
    better = ">" if kind == "max" else "<"
    upd = "pointChmax" if kind == "max" else "pointChmin"
    names = [c[0] for c in corners]
    ident_py = "NEG" if kind == "max" else "POS"
    none = a.none_cpp
    ops = [upd, a.all] + [f"{kind}{n}" for n in names]
    costs = {op: "log(X)*log(Y)*log(Z)" for op in ops}
    costs[a.all] = "1"
    memory = {"layout": "none", "node": " ".join(f"t{n}[1*X*Y*Z]" for n in names),
              "note": "one Fenwick tree per corner direction, (X + 1) by (Y + 1) by (Z + 1), flat; the >= direction is the same tree with every axis mirrored"}
    doc = (f"3D corner {kind} with a Fenwick tree: {upd} at a cell and the {kind} over every cell whose three coordinates are all <= "
           f"(or all >=) the given ones, O(log X * log Y * log Z) each, with an eighth of a 3D segment tree's memory per "
           f"direction. This works because values only move one way: a cell can only go {'up' if kind == 'max' else 'down'}; for a "
           f"cell that can move both ways, or for boxes that aren't corners, use the 3D segment tree. Every cell starts "
           f"empty and queries only see set cells. Coordinates are 0-based.")
    cost = "O(log X * log Y * log Z)"
    py = [f'{ident_py} = float("{"-inf" if kind == "max" else "inf"}")  # an empty cell', "", ""] + wrap_comment(doc + f" A {kind} over no set cell is None.", "#")
    py += [f"class {cls}:", "    __slots__ = (" + ", ".join(f'"{s}"' for s in ["X", "Y", "Z", "SY", "SZ", "top"] + [f"t{n}" for n in names]) + ")", "",
           "    # O(X*Y*Z) -- X by Y by Z, every cell empty; needs X >= 1, Y >= 1 and Z >= 1, else ValueError", "    def __init__(self, X, Y, Z):"]
    b = py_size_check(cls) + ["self.X = X", "self.Y = Y", "self.Z = Z", "self.SY = Y + 1", "self.SZ = Z + 1", f"self.top = {ident_py}"]
    for n in names:
        b.append(f"self.t{n} = [{ident_py}] * ((X + 1) * (Y + 1) * (Z + 1))")
    py += indent(b, 2) + [""]
    py += indent(wrap_comment(f"{cost} -- the cell at (x, y, z) becomes {kind}(itself, v); an empty cell becomes v; {POINT_RULE_PY}", "#"))
    py.append(f"    def {upd}(self, x, y, z, v):")
    b = py_point_check(upd) + ["X, Y, Z, SY, SZ = self.X, self.Y, self.Z, self.SY, self.SZ", f"if v {better} self.top:", "    self.top = v"]
    for n, s in corners:
        i0, j0, k0 = ("x + 1", "y + 1", "z + 1") if s == "<=" else ("X - x", "Y - y", "Z - z")
        b += [f"t = self.t{n}", f"i = {i0}", "while i <= X:", f"    j = {j0}", "    while j <= Y:", "        base = (i * SY + j) * SZ", f"        k = {k0}", "        while k <= Z:",
              f"            if v {better} t[base + k]:", "                t[base + k] = v", "            k += k & -k", "        j += j & -j", "    i += i & -i"]
    py += indent(b, 2) + [""]
    for n, s in corners:
        i0, j0, k0 = ("x + 1", "y + 1", "z + 1") if s == "<=" else ("self.X - x", "self.Y - y", "self.Z - z")
        py += indent(wrap_comment(f"{cost} -- {kind} of the set cells with all three coordinates {s} x, y, z (None if there are none); {POINT_RULE_PY}", "#"))
        py.append(f"    def {kind}{n}(self, x, y, z):")
        py += indent(py_point_check(f"{kind}{n}") + [f"SY, SZ, t, res = self.SY, self.SZ, self.t{n}, {ident_py}", f"j0 = {j0}", f"k0 = {k0}", f"i = {i0}", "while i > 0:", "    j = j0",
                                                     "    while j > 0:", "        base = (i * SY + j) * SZ", "        k = k0", "        while k > 0:", "            cand = t[base + k]",
                                                     f"            if cand {better} res:", "                res = cand", "            k &= k - 1", "        j &= j - 1", "    i &= i - 1",
                                                     f"return None if res == {ident_py} else res"], 2) + [""]
    py += [f"    # O(1) -- {kind} of every set cell (None if there are none)", f"    def {a.all}(self):", f"        return None if self.top == {ident_py} else self.top"]

    cpp = wrap_comment(doc + f" A {kind} over no set cell is {none}.", "//")
    cpp += ["// T is any integer type (int, long long, ...).", "template <typename T>", f"struct {cls} {{",
            f"    static constexpr T {none} = numeric_limits<T>::{'min' if kind == 'max' else 'max'}();  // what a {kind} over no set cell gives",
            "    int X, Y, Z, SY, SZ;", f"    T top = {none};", f"    vector<T> {', '.join('t' + n for n in names)};", "",
            "    // O(X*Y*Z) -- X by Y by Z, every cell empty; needs X >= 1, Y >= 1 and Z >= 1, else throws invalid_argument",
            f"    {cls}(int X, int Y, int Z) : X(X), Y(Y), Z(Z), SY(Y + 1), SZ(Z + 1) {{",
            f'        if (X < 1 || Y < 1 || Z < 1) throw invalid_argument("{cls}: needs X >= 1, Y >= 1 and Z >= 1");']
    for n in names:
        cpp.append(f"        t{n}.assign((size_t)(X + 1) * SY * SZ, {none});")
    cpp += ["    }", ""]
    cpp += indent(wrap_comment(f"{cost} -- the cell at (x, y, z) becomes {kind}(itself, v); an empty cell becomes v; {POINT_RULE_CPP}", "//"))
    cpp.append(f"    void {upd}(int x, int y, int z, T v) {{")
    b = cpp_point_check(upd) + [f"top = {kind}(top, v);"]
    for n, s in corners:
        i0, j0, k0 = ("x + 1", "y + 1", "z + 1") if s == "<=" else ("X - x", "Y - y", "Z - z")
        b += [f"for (int i = {i0}; i <= X; i += i & -i)", f"    for (int j = {j0}; j <= Y; j += j & -j)", f"        for (int k = {k0}; k <= Z; k += k & -k) {{",
              "            size_t at = ((size_t)i * SY + j) * SZ + k;", f"            t{n}[at] = {kind}(t{n}[at], v);", "        }"]
    cpp += indent(b, 2) + ["    }", ""]
    for n, s in corners:
        i0, j0, k0 = ("x + 1", "y + 1", "z + 1") if s == "<=" else ("X - x", "Y - y", "Z - z")
        cpp += indent(wrap_comment(f"{cost} -- {kind} of the set cells with all three coordinates {s} x, y, z ({none} if there are none); {POINT_RULE_CPP}", "//"))
        cpp.append(f"    T {kind}{n}(int x, int y, int z) const {{")
        cpp += indent(cpp_point_check(f"{kind}{n}") + [f"T res = {none};", f"for (int i = {i0}; i > 0; i &= i - 1)", f"    for (int j = {j0}; j > 0; j &= j - 1)",
                                                       f"        for (int k = {k0}; k > 0; k &= k - 1) res = {kind}(res, t{n}[((size_t)i * SY + j) * SZ + k]);", "return res;"], 2) + ["    }", ""]
    cpp += [f"    // O(1) -- {kind} of every set cell ({none} if there are none)", f"    T {a.all}() const {{", "        return top;", "    }", "};"]
    emit(f"3d-bit-corner-{kind}-" + "-".join(n.lower() for n in names), ops, "BIT", costs, "X*Y*Z", memory, py, cpp, [("empty-cells", "yes")])


def main():
    n = 0
    for aggs in subsets(["sum", "min", "max"]):
        seg_tree(aggs)
        n += 1
    bit_sum()
    n += 1
    for kind in ("max", "min"):
        for mask in range(1, 4):
            corner_bit(kind, [c for i, c in enumerate(CORNERS) if mask >> i & 1])
            n += 1
    print(f"3d: {n} folders")


if __name__ == "__main__":
    main()
