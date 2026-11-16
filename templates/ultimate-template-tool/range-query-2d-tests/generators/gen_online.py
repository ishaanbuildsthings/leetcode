"""Nothing known up front: any (x, y) inside a coordinate range given at the build can be updated at any time.

    python3 gen_online.py          # writes range-queries-2d/online-seg-tree-<aggregates>/template.{py,cpp}

A dynamic segment tree over x (nodes made only where touched) whose every node owns a dynamic segment tree over y.
The heaviest of the modes: O(log^2 U) per op and O(log^2 U) new nodes per update. When the points can be listed up
front, the points-known templates do the same in O(log^2 N) with flat arrays.
"""
from lib2d import AGGS, AGG_ORDER, cost_note, cpp_throw, header, indent, py_raise, read_agg, subsets, wrap_comment, write

CORNERS = [("LteLte", "<=", "<="), ("LteGte", "<=", ">="), ("GteLte", ">=", "<="), ("GteGte", ">=", ">=")]
POINT_RULE_PY = "needs xLo <= x <= xHi and yLo <= y <= yHi, else IndexError"
POINT_RULE_CPP = "needs xLo <= x <= xHi and yLo <= y <= yHi, else throws out_of_range"
RECT_RULE_PY = "needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else IndexError"
RECT_RULE_CPP = "needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range"


def py_point_check(name):
    return ["if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):"] + indent(py_raise(
        "IndexError", f"{name}: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {{x}}, y = {{y}}, xLo = {{self.xLo}}, "
        "xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}", 3))


def py_rect_check(name):
    return ["if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):"] + indent(py_raise(
        "IndexError", f"{name}: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {{x1}}, y1 = {{y1}}, x2 = {{x2}}, "
        "y2 = {y2}, xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}", 3))


def cpp_point_check(name):
    return cpp_throw("x < xLo || x > xHi || y < yLo || y > yHi", "out_of_range", f"{name}: needs xLo <= x <= xHi and yLo <= y <= yHi", 2)


def cpp_rect_check(name):
    return ["if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)",
            f'    throw out_of_range("{name}: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");']


def seg_tree(aggs):
    cls = "DynamicSegTree2D"
    A = [AGGS[k] for k in aggs]
    mm = "min" in aggs or "max" in aggs
    g = cost_note(aggs)
    rd = read_agg(aggs)
    ops = ["pointGet", "pointAssign", "pointAdd", "pointChmax", "pointChmin"]
    for a in A:
        ops += [a.rect, a.all]
        if a.key in ("min", "max"):
            ops += [f"{a.key}{n}" for n, _, _ in CORNERS]
    costs = {}
    for op in ops:
        if op.endswith("All"):
            costs[op] = "1"
        elif op == "pointGet":
            costs[op] = "log(U)"
        elif op.startswith("point"):
            costs[op] = "log^2(U)*log(U) ?" if g else "log^2(U)"
        elif op == "rectGcd":
            costs[op] = "log^2(U)+log(U) ?"
        else:
            costs[op] = "log^2(U)"
    memory = {
        "layout": "sparse",
        "node": " ".join(f"{a.arr}[1*log^2(U)]" for a in A),
        "other": "yLeft[1*log^2(U)] yRight[1*log^2(U)] xLeft[1*log(U)] xRight[1*log(U)] xTree[1*log(U)]",
        "note": "sizes are per update: it makes up to log U x-nodes, and a y-path of up to log U nodes in each x-node above the point",
    }
    words = ", ".join(a.word for a in A)
    text = (f"Dynamic 2D segment tree ({words}): point updates and any-rectangle queries over any coordinate range [xLo, xHi] by "
            f"[yLo, yHi] (as big as +-10^18, negative is fine), with nothing known up front. O(log^2 U) per op, U = the size of "
            f"a coordinate range, and up to log^2 U new nodes per update: the heaviest option. When every point that will be "
            f"updated can be listed before the first call, the points-known templates are much lighter. A segment tree over "
            f"x whose nodes are made only where touched, each owning a segment tree over y made the same way. Rectangles are "
            f"inclusive: x1..x2 by y1..y2.")
    if mm:
        empty = ["a min / max over no set cell is {NONE}"]
        if any(k in aggs for k in ("sum", "gcd", "xor", "or")):
            empty.append("a " + " / ".join(AGGS[k].word for k in aggs if k in ("sum", "gcd", "xor", "or")) + " over none is 0")
        if "and" in aggs:
            empty.append("an AND over none is -1 (every bit set)")
        text += f" Every cell starts empty and queries only see cells that have been set: {'; '.join(empty)}."
    else:
        text += " Every cell starts at 0" + (" (so an AND over a rectangle with a cell nobody set is 0)." if "and" in aggs else ".")
    arrs = ", ".join(a.arr for a in A)
    self_arrs = ", ".join(f"self.{a.arr}" for a in A)
    blank = {a.key: (a.py_id if mm else "0") for a in A}

    # ---- Python
    py = []
    if "gcd" in aggs:
        py += ["from math import gcd", ""]
    if "max" in aggs:
        py.append('NEG = float("-inf")  # an empty cell in the max array')
    if "min" in aggs:
        py.append('POS = float("inf")  # an empty cell in the min array')
    py += ["", ""] + wrap_comment(text.replace("{NONE}", "None"), "#") + [f"class {cls}:"]
    slots = ["xLo", "xHi", "yLo", "yHi", "xLeft", "xRight", "xTree", "yLeft", "yRight"] + [a.arr for a in A]
    py.append("    __slots__ = (" + ", ".join(f'"{s}"' for s in slots) + ")")
    py += ["", f"    # O(1) -- every cell of [xLo, xHi] by [yLo, yHi] {'empty' if mm else '0'}; needs xLo <= xHi and yLo <= yHi, else ValueError",
           "    def __init__(self, xLo, xHi, yLo, yHi):"]
    b = ["if xLo > xHi or yLo > yHi:"] + indent(py_raise(
        "ValueError", f"{cls}: needs xLo <= xHi and yLo <= yHi, got xLo = {{xLo}}, xHi = {{xHi}}, yLo = {{yLo}}, yHi = {{yHi}}", 3))
    b += ["self.xLo = xLo", "self.xHi = xHi", "self.yLo = yLo", "self.yHi = yHi",
          "self.xLeft = [0, 0]  # x-node 0 = nothing there, x-node 1 = the root", "self.xRight = [0, 0]", "self.xTree = [0, 0]  # an x-node's own y-tree (its root)",
          "self.yLeft = [0]  # y-node 0 = nothing there: its aggregates are what an untouched range gives", "self.yRight = [0]"]
    for a in A:
        b.append(f"self.{a.arr} = [{blank[a.key]}]")
    py += indent(b, 2) + [""]
    py += ["    # cell (x, y) = v, then every node above it", "    def _set(self, x, y, v):"]
    b = ["xLeft, xRight, xTree, yLeft, yRight = self.xLeft, self.xRight, self.xTree, self.yLeft, self.yRight", f"{arrs} = {self_arrs}", "yLo, yHi = self.yLo, self.yHi",
         "path = []  # the x-nodes from the root down to the one for x alone", "p = 1", "lo = self.xLo", "hi = self.xHi", "while True:", "    path.append(p)", "    if lo == hi:", "        break",
         "    mid = (lo + hi) >> 1", "    if x <= mid:", "        if not xLeft[p]:", "            xLeft[p] = len(xLeft)", "            xLeft.append(0)", "            xRight.append(0)",
         "            xTree.append(0)", "        p = xLeft[p]", "        hi = mid", "    else:", "        if not xRight[p]:", "            xRight[p] = len(xLeft)", "            xLeft.append(0)",
         "            xRight.append(0)", "            xTree.append(0)", "        p = xRight[p]", "        lo = mid + 1"]
    for a in A:
        b.append(f"v{a.cap} = v  # this aggregate over row y of the x-node being written")
    b += ["below = 0  # the x-node just written (a child of the next one up)", "for i in range(len(path) - 1, -1, -1):", "    p = path[i]", "    if below:",
          "        q = xTree[xRight[p] if xLeft[p] == below else xLeft[p]]  # the other child: what does it hold at y?", "        lo = yLo", "        hi = yHi", "        while q and lo < hi:",
          "            mid = (lo + hi) >> 1", "            if y <= mid:", "                q = yLeft[q]", "                hi = mid", "            else:", "                q = yRight[q]",
          "                lo = mid + 1"]
    for a in A:
        b += indent(a.py_take(f"v{a.cap}", f"{a.arr}[q]"), 2)
    b += ["    below = p", "    q = xTree[p]", "    if not q:", "        q = xTree[p] = len(yLeft)", "        yLeft.append(0)", "        yRight.append(0)"]
    for a in A:
        b.append(f"        {a.arr}.append({blank[a.key]})")
    b += ["    ypath = []", "    lo = yLo", "    hi = yHi", "    while lo < hi:", "        ypath.append(q)", "        mid = (lo + hi) >> 1", "        if y <= mid:", "            if not yLeft[q]:",
          "                yLeft[q] = len(yLeft)", "                yLeft.append(0)", "                yRight.append(0)"]
    for a in A:
        b.append(f"                {a.arr}.append({blank[a.key]})")
    b += ["            q = yLeft[q]", "            hi = mid", "        else:", "            if not yRight[q]:", "                yRight[q] = len(yLeft)", "                yLeft.append(0)",
          "                yRight.append(0)"]
    for a in A:
        b.append(f"                {a.arr}.append({blank[a.key]})")
    b += ["            q = yRight[q]", "            lo = mid + 1"]
    for a in A:
        b.append(f"    {a.arr}[q] = v{a.cap}")
    b += ["    for j in range(len(ypath) - 1, -1, -1):", "        q = ypath[j]", "        a = yLeft[q]", "        b = yRight[q]"]
    for a in A:
        b += indent(a.py_merge(f"{a.arr}[q]", f"{a.arr}[a]", f"{a.arr}[b]"), 2)
    py += indent(b, 2) + [""]
    py += ["    # the value held at exactly (x, y) in this aggregate's array (what an untouched cell gives if nothing is there)", "    def _cell(self, x, y):"]
    py += indent(["xLeft, xRight, yLeft, yRight = self.xLeft, self.xRight, self.yLeft, self.yRight", "p = 1", "lo = self.xLo", "hi = self.xHi", "while p and lo < hi:", "    mid = (lo + hi) >> 1",
                  "    if x <= mid:", "        p = xLeft[p]", "        hi = mid", "    else:", "        p = xRight[p]", "        lo = mid + 1", "q = self.xTree[p]", "lo = self.yLo", "hi = self.yHi",
                  "while q and lo < hi:", "    mid = (lo + hi) >> 1", "    if y <= mid:", "        q = yLeft[q]", "        hi = mid", "    else:", "        q = yRight[q]", "        lo = mid + 1",
                  f"return self.{rd.arr}[q]"], 2) + [""]
    is_empty = {"max": "cur == NEG", "min": "cur == POS"}.get(rd.key)
    if_empty = "; an empty cell becomes v" if mm else ""
    upd = "O(log^2 U)" + (" gcds" if "gcd" in aggs else "")
    py += indent(wrap_comment(f"O(log U) -- the value at (x, y){', None if the cell is empty' if mm else ''}; {POINT_RULE_PY}", "#"))
    py.append("    def pointGet(self, x, y):")
    py += indent(py_point_check("pointGet") + (["cur = self._cell(x, y)", f"return None if {is_empty} else cur"] if mm else ["return self._cell(x, y)"]), 2) + [""]
    py += indent(wrap_comment(f"{upd} -- the cell at (x, y) becomes v (it may go down as well as up); {POINT_RULE_PY}", "#"))
    py.append("    def pointAssign(self, x, y, v):")
    py += indent(py_point_check("pointAssign") + ["self._set(x, y, v)"], 2) + [""]
    py += indent(wrap_comment(f"{upd} -- adds v to the cell at (x, y){if_empty}; {POINT_RULE_PY}", "#"))
    py.append("    def pointAdd(self, x, y, v):")
    py += indent(py_point_check("pointAdd") + ["cur = self._cell(x, y)", f"self._set(x, y, v if {is_empty} else cur + v)" if mm else "self._set(x, y, cur + v)"], 2) + [""]
    for name, sym, word in (("pointChmax", ">", "max"), ("pointChmin", "<", "min")):
        py += indent(wrap_comment(f"{upd} -- the cell at (x, y) becomes {word}(itself, v){if_empty}; {POINT_RULE_PY}", "#"))
        py.append(f"    def {name}(self, x, y, v):")
        py += indent(py_point_check(name) + ["cur = self._cell(x, y)", f"if {is_empty + ' or ' if mm else ''}v {sym} cur:", "    self._set(x, y, v)"], 2) + [""]
    for a in A:
        py.append(f"    def _{a.key}Of(self, x1, y1, x2, y2):")
        b = ["xLeft, xRight, xTree, yLeft, yRight = self.xLeft, self.xRight, self.xTree, self.yLeft, self.yRight", f"{a.arr} = self.{a.arr}", "yLo, yHi = self.yLo, self.yHi",
             f"res = {a.py_id}", "stack = [(1, self.xLo, self.xHi)]", "while stack:", "    p, lo, hi = stack.pop()", "    if p and not (x1 <= lo and hi <= x2):", "        mid = (lo + hi) >> 1",
             "        if x1 <= mid:", "            stack.append((xLeft[p], lo, mid))", "        if x2 > mid:", "            stack.append((xRight[p], mid + 1, hi))", "        continue",
             "    # this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's", "    inner = [(xTree[p], yLo, yHi)]", "    while inner:",
             "        q, lo, hi = inner.pop()", "        if q and not (y1 <= lo and hi <= y2):", "            mid = (lo + hi) >> 1", "            if y1 <= mid:",
             "                inner.append((yLeft[q], lo, mid))", "            if y2 > mid:", "                inner.append((yRight[q], mid + 1, hi))", "            continue"]
        b += indent(a.py_take("res", f"{a.arr}[q]"), 2) + [f"return {a.py_result('res')}"]
        py += indent(b, 2) + [""]
        cost = "O(log^2 U + log U)" if a.key == "gcd" else "O(log^2 U)"
        what = (f"{a.word} of the set cells with x1 <= x <= x2 and y1 <= y <= y2 ({a.none_words_py} if there are none)" if mm
                else f"{a.word} of the cells with x1 <= x <= x2 and y1 <= y <= y2")
        py += indent(wrap_comment(f"{cost} -- {what}; {RECT_RULE_PY}", "#"))
        py.append(f"    def {a.rect}(self, x1, y1, x2, y2):")
        py += indent(py_rect_check(a.rect) + [f"return self._{a.key}Of(x1, y1, x2, y2)"], 2) + [""]
        py.append(f"    # O(1) -- {a.word} of every set cell ({a.none_words_py} if there are none)" if mm else f"    # O(1) -- {a.word} of the whole range")
        py.append(f"    def {a.all}(self):")
        root = f"self.{a.arr}[self.xTree[1]]"
        if a.key in ("min", "max"):
            py += [f"        res = {root}", f"        return {a.py_result('res')}", ""]
        else:
            py += [f"        return abs({root})" if a.key == "gcd" else f"        return {root}", ""]
        if a.key in ("min", "max"):
            for n, xsn, ysn in CORNERS:
                bx = ("self.xLo", "x") if xsn == "<=" else ("x", "self.xHi")
                by = ("self.yLo", "y") if ysn == "<=" else ("y", "self.yHi")
                py += indent(wrap_comment(f"O(log^2 U) -- {a.word} of the set cells with x {xsn} the given x and y {ysn} the given y (None if there are none); "
                                          f"{POINT_RULE_PY}", "#"))
                py.append(f"    def {a.key}{n}(self, x, y):")
                py += indent(py_point_check(f"{a.key}{n}") + [f"return self._{a.key}Of({bx[0]}, {by[0]}, {bx[1]}, {by[1]})"], 2) + [""]
    while py[-1] == "":
        py.pop()

    # ---- C++
    none_cpp = " / ".join(AGGS[k].none_cpp for k in aggs if k in ("min", "max"))
    cpp = wrap_comment(text.replace("{NONE}", none_cpp), "//")
    cpp.append("// T is any integer type (int, long long, ...)" + ("; sums are kept in S (long long for a smaller T)." if "sum" in aggs else ".")
               + " Coordinates are long long, with xHi - xLo and yHi - yLo below 2^63.")
    cpp += ["template <typename T>", f"struct {cls} {{", "    using ll = long long;"]
    if "sum" in aggs:
        cpp.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;")
    if "max" in aggs:
        cpp.append("    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no set cell gives")
    if "min" in aggs:
        cpp.append("    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set cell gives")
    cpp += ["    ll xLo, xHi, yLo, yHi;", "    vector<int> xLeft, xRight, xTree;  // x-node 0 = nothing there, 1 = the root; xTree = an x-node's own y-tree (its root)",
            "    vector<int> yLeft, yRight;  // y-node 0 = nothing there: its aggregates are what an untouched range gives"]
    for a in A:
        cpp.append(f"    vector<{a.cpp_type}> {a.arr};")
    cpp.append("")
    if "gcd" in aggs:
        cpp += ["    static T gcdOf(T a, T b) { return std::gcd(a, b); }", ""]
    cblank = {a.key: (a.cpp_id if mm else a.cpp_type + "(0)") for a in A}
    cpp += [f"    // O(1) -- every cell of [xLo, xHi] by [yLo, yHi] {'empty' if mm else '0'}; needs xLo <= xHi and yLo <= yHi, else throws invalid_argument",
            f"    {cls}(ll xLo, ll xHi, ll yLo, ll yHi)", "        : xLo(xLo), xHi(xHi), yLo(yLo), yHi(yHi), xLeft(2, 0), xRight(2, 0), xTree(2, 0), yLeft(1, 0), yRight(1, 0) {",
            f'        if (xLo > xHi || yLo > yHi) throw invalid_argument("{cls}: needs xLo <= xHi and yLo <= yHi");']
    for a in A:
        cpp.append(f"        {a.arr}.assign(1, {cblank[a.key]});")
    cpp += ["    }", "", "    int newX() {", "        xLeft.push_back(0), xRight.push_back(0), xTree.push_back(0);", "        return (int)xLeft.size() - 1;", "    }", "", "    int newY() {",
            "        yLeft.push_back(0), yRight.push_back(0);"]
    for a in A:
        cpp.append(f"        {a.arr}.push_back({cblank[a.key]});")
    cpp += ["        return (int)yLeft.size() - 1;", "    }", "", "    // the y-node of the tree rooted at q that holds exactly y (0 if nothing was set there)", "    int findY(int q, ll y) const {",
            "        ll lo = yLo, hi = yHi;", "        while (q && lo < hi) {", "            ll mid = lo + (hi - lo) / 2;", "            if (y <= mid) q = yLeft[q], hi = mid;",
            "            else q = yRight[q], lo = mid + 1;", "        }", "        return q;", "    }", "", "    // the y-node holding exactly (x, y) (0 if nothing was set there)", "    int findCell(ll x, ll y) const {",
            "        int p = 1;", "        ll lo = xLo, hi = xHi;", "        while (p && lo < hi) {", "            ll mid = lo + (hi - lo) / 2;", "            if (x <= mid) p = xLeft[p], hi = mid;",
            "            else p = xRight[p], lo = mid + 1;", "        }", "        return findY(xTree[p], y);", "    }", "", "    // cell (x, y) = v, then every node above it", "    void setCell(ll x, ll y, T v) {"]
    b = ["int path[66], depth = 0;  // the x-nodes from the root down to the one for x alone", "int p = 1;", "for (ll lo = xLo, hi = xHi;;) {", "    path[depth++] = p;", "    if (lo == hi) break;",
         "    ll mid = lo + (hi - lo) / 2;", "    if (x <= mid) {", "        if (!xLeft[p]) { int made = newX(); xLeft[p] = made; }", "        p = xLeft[p], hi = mid;", "    } else {",
         "        if (!xRight[p]) { int made = newX(); xRight[p] = made; }", "        p = xRight[p], lo = mid + 1;", "    }", "}"]
    for a in A:
        b.append(f"{a.cpp_type} v{a.cap} = v;  // this aggregate over row y of the x-node being written")
    b += ["int below = 0;  // the x-node just written (a child of the next one up)", "for (int i = depth - 1; i >= 0; i--) {", "    p = path[i];", "    if (below) {",
          "        int other = findY(xTree[xLeft[p] == below ? xRight[p] : xLeft[p]], y);  // the other child: what does it hold at y?"]
    for a in A:
        b.append("        " + a.cpp_take(f"v{a.cap}", f"{a.arr}[other]"))
    b += ["    }", "    below = p;", "    if (!xTree[p]) { int made = newY(); xTree[p] = made; }", "    int q = xTree[p], ypath[66], ydepth = 0;", "    for (ll lo = yLo, hi = yHi; lo < hi;) {",
          "        ypath[ydepth++] = q;", "        ll mid = lo + (hi - lo) / 2;", "        if (y <= mid) {", "            if (!yLeft[q]) { int made = newY(); yLeft[q] = made; }",
          "            q = yLeft[q], hi = mid;", "        } else {", "            if (!yRight[q]) { int made = newY(); yRight[q] = made; }", "            q = yRight[q], lo = mid + 1;", "        }", "    }"]
    for a in A:
        b.append(f"    {a.arr}[q] = v{a.cap};")
    b += ["    for (int j = ydepth - 1; j >= 0; j--) {", "        q = ypath[j];"]
    for a in A:
        b.append(f"        {a.arr}[q] = {a.cpp_comb(f'{a.arr}[yLeft[q]]', f'{a.arr}[yRight[q]]')};")
    b += ["    }", "}"]
    cpp += indent(b, 2) + ["    }", ""]
    is_empty_cpp = {"max": "cur == NO_MAX", "min": "cur == NO_MIN"}.get(rd.key)
    cell = f"T({rd.arr}[findCell(x, y)])"
    cpp += indent(wrap_comment(f"O(log U) -- the value at (x, y){', ' + rd.none_words_cpp + ' if the cell is empty' if mm else ''}; {POINT_RULE_CPP}", "//"))
    cpp.append("    T pointGet(ll x, ll y) const {")
    cpp += indent(cpp_point_check("pointGet") + [f"return {cell};"], 2) + ["    }", ""]
    cpp += indent(wrap_comment(f"{upd} -- the cell at (x, y) becomes v (it may go down as well as up); {POINT_RULE_CPP}", "//"))
    cpp.append("    void pointAssign(ll x, ll y, T v) {")
    cpp += indent(cpp_point_check("pointAssign") + ["setCell(x, y, v);"], 2) + ["    }", ""]
    cpp += indent(wrap_comment(f"{upd} -- adds v to the cell at (x, y){if_empty}; {POINT_RULE_CPP}", "//"))
    cpp.append("    void pointAdd(ll x, ll y, T v) {")
    cpp += indent(cpp_point_check("pointAdd") + [f"T cur = {cell};", f"setCell(x, y, {is_empty_cpp} ? v : T(cur + v));" if mm else "setCell(x, y, T(cur + v));"], 2) + ["    }", ""]
    for name, sym, word in (("pointChmax", ">", "max"), ("pointChmin", "<", "min")):
        cpp += indent(wrap_comment(f"{upd} -- the cell at (x, y) becomes {word}(itself, v){if_empty}; {POINT_RULE_CPP}", "//"))
        cpp.append(f"    void {name}(ll x, ll y, T v) {{")
        cpp += indent(cpp_point_check(name) + [f"T cur = {cell};", f"if ({is_empty_cpp + ' || ' if mm else ''}v {sym} cur) setCell(x, y, v);"], 2) + ["    }", ""]
    for a in A:
        t = a.cpp_type
        cpp += [f"    void {a.key}OverY(int q, ll lo, ll hi, ll y1, ll y2, {t}& res) const {{", "        if (q && !(y1 <= lo && hi <= y2)) {", "            ll mid = lo + (hi - lo) / 2;",
                f"            if (y1 <= mid) {a.key}OverY(yLeft[q], lo, mid, y1, y2, res);", f"            if (y2 > mid) {a.key}OverY(yRight[q], mid + 1, hi, y1, y2, res);", "            return;", "        }",
                "        " + a.cpp_take("res", f"{a.arr}[q]"), "    }", "",
                f"    void {a.key}OverX(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, {t}& res) const {{", "        if (p && !(x1 <= lo && hi <= x2)) {", "            ll mid = lo + (hi - lo) / 2;",
                f"            if (x1 <= mid) {a.key}OverX(xLeft[p], lo, mid, x1, y1, x2, y2, res);", f"            if (x2 > mid) {a.key}OverX(xRight[p], mid + 1, hi, x1, y1, x2, y2, res);", "            return;", "        }",
                "        // this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's",
                f"        {a.key}OverY(xTree[p], yLo, yHi, y1, y2, res);", "    }", "",
                f"    {t} {a.key}Of(ll x1, ll y1, ll x2, ll y2) const {{", f"        {t} res = {a.cpp_id};", f"        {a.key}OverX(1, xLo, xHi, x1, y1, x2, y2, res);", "        return res;", "    }", ""]
        cost = "O(log^2 U + log U)" if a.key == "gcd" else "O(log^2 U)"
        what = (f"{a.word} of the set cells with x1 <= x <= x2 and y1 <= y <= y2 ({a.none_words_cpp} if there are none)" if mm
                else f"{a.word} of the cells with x1 <= x <= x2 and y1 <= y <= y2")
        cpp += indent(wrap_comment(f"{cost} -- {what}; {RECT_RULE_CPP}", "//"))
        cpp.append(f"    {t} {a.rect}(ll x1, ll y1, ll x2, ll y2) const {{")
        cpp += indent(cpp_rect_check(a.rect) + [f"return {a.key}Of(x1, y1, x2, y2);"], 2) + ["    }", ""]
        cpp.append(f"    // O(1) -- {a.word} of every set cell ({a.none_words_cpp} if there are none)" if mm else f"    // O(1) -- {a.word} of the whole range")
        root = f"{a.arr}[xTree[1]]"
        cpp += [f"    {t} {a.all}() const {{", f"        return gcdOf({root}, T(0));" if a.key == "gcd" else f"        return {root};", "    }", ""]
        if a.key in ("min", "max"):
            for n, xsn, ysn in CORNERS:
                bx = ("xLo", "x") if xsn == "<=" else ("x", "xHi")
                by = ("yLo", "y") if ysn == "<=" else ("y", "yHi")
                cpp += indent(wrap_comment(f"O(log^2 U) -- {a.word} of the set cells with x {xsn} the given x and y {ysn} the given y ({a.none_words_cpp} if there are none); "
                                           f"{POINT_RULE_CPP}", "//"))
                cpp.append(f"    T {a.key}{n}(ll x, ll y) const {{")
                cpp += indent(cpp_point_check(f"{a.key}{n}") + [f"return {a.key}Of({bx[0]}, {by[0]}, {bx[1]}, {by[1]});"], 2) + ["    }", ""]
    while cpp[-1] == "":
        cpp.pop()
    cpp.append("};")
    args = (ops, "seg-tree", costs, "1", memory, "online", [("empty-cells", "yes")] if mm else [])
    folder = "online-seg-tree-" + "-".join(aggs)
    write(folder, header(folder, "py", *args) + py, header(folder, "cpp", *args) + cpp)


def main():
    for aggs in subsets(AGG_ORDER):
        seg_tree(aggs)
    print(f"online: {len(subsets(AGG_ORDER))} folders")


if __name__ == "__main__":
    main()
