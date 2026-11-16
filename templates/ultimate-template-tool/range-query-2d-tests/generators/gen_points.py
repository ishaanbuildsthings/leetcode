"""Points known up front: the constructor is given every (x, y) that will ever be updated, any integers (negative is
fine), and compresses them. Memory is N log N in flat arrays, costs are log^2 N.

    python3 gen_points.py          # writes range-queries-2d/points-.../template.{py,cpp}

  points-seg-tree-<aggregates>         point updates, any rectangle: a tree over the distinct x's whose every node is a
                                       tree over just the y's that fall under it
  points-bit-sum, -xor, -sum-xor       the same shape with Fenwick trees (lighter), for sum / xor
  points-bit-corner-<max|min>-...      point chmax (chmin) with max (min) over a corner, one Fenwick tree per direction
"""
from lib2d import AGGS, AGG_ORDER, cost_note, cpp_throw, header, indent, py_raise, subsets, wrap_comment, write

CORNERS = [("LteLte", "<=", "<="), ("LteGte", "<=", ">="), ("GteLte", ">=", "<="), ("GteGte", ">=", ">=")]
POINT_RULE_PY = "needs (x, y) to be one of the points given, else IndexError"
POINT_RULE_CPP = "needs (x, y) to be one of the points given, else throws out_of_range"
RECT_RULE_PY = "needs x1 <= x2 and y1 <= y2, else IndexError"
RECT_RULE_CPP = "needs x1 <= x2 and y1 <= y2, else throws out_of_range"
CTOR_PY = ("O(N log N) -- points: every (x, y) that will ever be updated, as pairs of integers (negative is fine, repeats are "
           "fine); needs at least one, else ValueError")
CTOR_CPP = ("O(N log N) -- points: every (x, y) that will ever be updated (negative is fine, repeats are fine); needs at least "
            "one, else throws invalid_argument")


def emit(folder, ops, dstype, costs, build, memory, py, cpp, extra=()):
    args = (ops, dstype, costs, build, memory, "points", list(extra))
    write(folder, header(folder, "py", *args) + py, header(folder, "cpp", *args) + cpp)


def py_rect_check(name):
    return ["if x1 > x2 or y1 > y2:"] + indent(py_raise(
        "IndexError", f"{name}: needs x1 <= x2 and y1 <= y2, got x1 = {{x1}}, y1 = {{y1}}, x2 = {{x2}}, y2 = {{y2}}", 3))


def cpp_rect_check(name):
    return cpp_throw("x1 > x2 || y1 > y2", "out_of_range", f"{name}: needs x1 <= x2 and y1 <= y2", 2)


PY_INDEX = [
    "    # where (x, y) is in the sorted points",
    "    def _index(self, x, y, name):",
    "        pts = self.pts",
    "        i = bisect_left(pts, (x, y))",
    "        if i == len(pts) or pts[i] != (x, y):",
    '            raise IndexError(f"{name}: ({x}, {y}) is not one of the points given to the constructor")',
    "        return i",
    "",
]
CPP_INDEX = [
    "    // where (x, y) is in the sorted points",
    "    int indexOf(long long x, long long y, const char* name) const {",
    "        auto it = lower_bound(pts.begin(), pts.end(), make_pair(x, y));",
    "        if (it == pts.end() || *it != make_pair(x, y))",
    '            throw out_of_range(string(name) + ": (x, y) is not one of the points given to the constructor");',
    "        return (int)(it - pts.begin());",
    "    }",
    "",
]


# ------------------------------------------------------------------------------------------------ seg tree of seg trees
def seg_ops(aggs):
    ops = ["pointGet", "pointAssign", "pointAdd", "pointChmax", "pointChmin"]
    for k in aggs:
        ops += [AGGS[k].rect, AGGS[k].all]
        if k in ("min", "max"):
            ops += [f"{k}{n}" for n, _, _ in CORNERS]
    return ops


def seg_tree(aggs):
    cls = "PointsSegTree2D"
    A = [AGGS[k] for k in aggs]
    mm = "min" in aggs or "max" in aggs
    g = cost_note(aggs)
    ops = seg_ops(aggs)
    costs = {}
    for op in ops:
        if op.endswith("All"):
            costs[op] = "1"
        elif op == "pointGet":
            costs[op] = "log(N)"
        elif op.startswith("point"):
            costs[op] = "log^2(N)*log(U) ?" if g else "log^2(N)"
        elif op == "rectGcd":
            costs[op] = "log^2(N)+log(U) ?"
        else:
            costs[op] = "log^2(N)"
    memory = {
        "layout": "2n-iterative",
        "node": " ".join(f"{a.arr}[2*N*log(N)]" for a in A),
        "other": "ys[1*N*log(N)] pts[2*N] vals[1*N] xs[1*N] off[2*N] cnt[2*N]",
        "note": "every point's y is listed in each of the O(log N) x-nodes above it; an x-node's column tree is twice its list",
    }
    words = ", ".join(a.word for a in A)
    text = (f"2D segment tree over points known up front ({words}): point updates and any-rectangle queries in O(log^2 N), "
            f"with N log N memory whatever the coordinates are (any integers, negative is fine). The constructor takes "
            f"every (x, y) that will ever be updated. A bottom-up tree over the distinct x's; every node of it keeps the "
            f"sorted y's of the points under it and a bottom-up tree over just those. Rectangles are inclusive, x1..x2 by "
            f"y1..y2, and their corners can be any integers, given or not.")
    if mm:
        empty = ["a min / max over no set point is {NONE}"]
        if any(k in aggs for k in ("sum", "gcd", "xor", "or")):
            empty.append("a " + " / ".join(AGGS[k].word for k in aggs if k in ("sum", "gcd", "xor", "or")) + " over none is 0")
        if "and" in aggs:
            empty.append("an AND over none is -1 (every bit set)")
        text += f" Every point starts empty and queries only see points that have been set: {'; '.join(empty)}."
    else:
        text += " Every point given starts at 0."
    doc_py = text.replace("{NONE}", "None")
    doc_cpp = text.replace("{NONE}", " / ".join(AGGS[k].none_cpp for k in aggs if k in ("min", "max")))

    # ---- Python
    py = ["from bisect import bisect_left, bisect_right"]
    if "gcd" in aggs:
        py.append("from math import gcd")
    py.append("")
    if mm:
        py += ['NEG = float("-inf")  # an empty point in a max array; also "no lower bound" on a coordinate',
               'POS = float("inf")  # an empty point in a min array; also "no upper bound" on a coordinate', ""]
    py += [""] + wrap_comment(doc_py, "#") + [f"class {cls}:"]
    slots = ["n", "pts", "vals", "xs", "ys", "off", "cnt"] + [a.arr for a in A]
    py.append("    __slots__ = (" + ", ".join(f'"{s}"' for s in slots) + ")")
    py += [""] + indent(wrap_comment(CTOR_PY, "#")) + ["    def __init__(self, points):"]
    b = [
        "if not points:",
        f'    raise ValueError("{cls}: needs at least one point")',
        "pts = self.pts = sorted(set(map(tuple, points)))",
        f"self.vals = [{'None' if mm else '0'}] * len(pts)",
        "xs = self.xs = sorted({x for x, _ in pts})",
        "n = self.n = len(xs)",
        "lists = [[] for _ in range(2 * n)]  # per x-node: the distinct y's under it, ascending",
        "for x, y in sorted(pts, key=lambda p: p[1]):",
        "    p = bisect_left(xs, x) + n",
        "    while p:",
        "        lst = lists[p]",
        "        if not lst or lst[-1] != y:",
        "            lst.append(y)",
        "        p >>= 1",
        "off = self.off = [0] * (2 * n)",
        "cnt = self.cnt = [0] * (2 * n)",
        "ys = self.ys = []",
        "for p in range(1, 2 * n):",
        "    off[p] = len(ys)",
        "    cnt[p] = len(lists[p])",
        "    ys += lists[p]",
    ]
    for a in A:
        b.append(f"self.{a.arr} = [{a.py_id if mm else 0}] * (2 * len(ys))  # x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])")
    py += indent(b, 2) + [""] + PY_INDEX
    arrs = ", ".join(a.arr for a in A)
    self_arrs = ", ".join(f"self.{a.arr}" for a in A)
    py += ["    # point (x, y) = v, then every node above it", "    def _set(self, x, y, v):"]
    b = ["xs, ys, off, cnt = self.xs, self.ys, self.off, self.cnt", f"{arrs} = {self_arrs}", "p = bisect_left(xs, x) + self.n"]
    for a in A:
        b.append(f"v{a.cap} = v  # this aggregate over the points with this y under x-node p")
    b += ["while True:", "    o = off[p]", "    c = cnt[p]", "    base = 2 * o", "    k = bisect_left(ys, y, o, o + c) - o + c"]
    for a in A:
        b.append(f"    {a.arr}[base + k] = v{a.cap}")
    b += ["    k >>= 1", "    while k:"]
    for a in A:
        b += indent(a.py_merge(f"{a.arr}[base + k]", f"{a.arr}[base + 2 * k]", f"{a.arr}[base + 2 * k + 1]"), 2)
    b += ["        k >>= 1", "    if p == 1:", "        break", "    s = p ^ 1  # the other half of the parent: does it have this y too?",
          "    o = off[s]", "    c = cnt[s]", "    j = bisect_left(ys, y, o, o + c)", "    if j < o + c and ys[j] == y:", "        j += o + c"]
    for a in A:
        b += indent(a.py_take(f"v{a.cap}", f"{a.arr}[j]"), 2)
    b += ["    p >>= 1"]
    py += indent(b, 2) + [""]

    def py_inner(a, node):
        return [
            f"o = off[{node}]",
            f"c = cnt[{node}]",
            "base = 2 * o",
            "lo = bisect_left(ys, y1, o, o + c) - o + c",
            "hi = bisect_right(ys, y2, o, o + c) - o + c",
            "while lo < hi:",
            "    if lo & 1:",
            *indent(a.py_take("res", f"{a.arr}[base + lo]"), 2),
            "        lo += 1",
            "    if hi & 1:",
            "        hi -= 1",
            *indent(a.py_take("res", f"{a.arr}[base + hi]"), 2),
            "    lo >>= 1",
            "    hi >>= 1",
        ]

    is_empty = "cur is None"
    py.append(f"    # O(log N) -- the value at (x, y){', None if it was never set' if mm else ''}; {POINT_RULE_PY}")
    py += ["    def pointGet(self, x, y):", '        return self.vals[self._index(x, y, "pointGet")]', ""]
    upd = "O(log^2 N)" + (" gcds" if "gcd" in aggs else "")
    if_empty = "; an empty point becomes v" if mm else ""
    py += indent(wrap_comment(f"{upd} -- the point (x, y) becomes v (it may go down as well as up); {POINT_RULE_PY}", "#"))
    py += ["    def pointAssign(self, x, y, v):", '        self.vals[self._index(x, y, "pointAssign")] = v', "        self._set(x, y, v)", ""]
    py += indent(wrap_comment(f"{upd} -- adds v to the point (x, y){if_empty}; {POINT_RULE_PY}", "#"))
    py += ["    def pointAdd(self, x, y, v):", '        i = self._index(x, y, "pointAdd")', "        cur = self.vals[i]"]
    py += indent(["if cur is not None:", "    v += cur"] if mm else ["v += cur"], 2)
    py += ["        self.vals[i] = v", "        self._set(x, y, v)", ""]
    for name, sym, word in (("pointChmax", ">", "max"), ("pointChmin", "<", "min")):
        py += indent(wrap_comment(f"{upd} -- the point (x, y) becomes {word}(itself, v){if_empty}; {POINT_RULE_PY}", "#"))
        py += [f"    def {name}(self, x, y, v):", f'        i = self._index(x, y, "{name}")', "        cur = self.vals[i]",
               f"        if {is_empty + ' or ' if mm else ''}v {sym} cur:", "            self.vals[i] = v", "            self._set(x, y, v)", ""]
    for a in A:
        py.append(f"    def _{a.key}Of(self, x1, y1, x2, y2):")
        b = ["xs, ys, off, cnt = self.xs, self.ys, self.off, self.cnt", f"{a.arr} = self.{a.arr}", f"res = {a.py_id}",
             "l = bisect_left(xs, x1) + self.n", "r = bisect_right(xs, x2) + self.n", "while l < r:", "    if l & 1:"]
        b += indent(py_inner(a, "l"), 2) + ["        l += 1", "    if r & 1:", "        r -= 1"] + indent(py_inner(a, "r"), 2)
        b += ["    l >>= 1", "    r >>= 1", f"return {a.py_result('res')}"]
        py += indent(b, 2) + [""]
        cost = "O(log^2 N + log U)" if a.key == "gcd" else "O(log^2 N)"
        what = (f"{a.word} of the set points with x1 <= x <= x2 and y1 <= y <= y2 ({a.none_words_py} if there are none)" if mm
                else f"{a.word} of the points with x1 <= x <= x2 and y1 <= y <= y2 ({a.none_words_py} if no point is there)")
        py += indent(wrap_comment(f"{cost} -- {what}; {RECT_RULE_PY}", "#"))
        py.append(f"    def {a.rect}(self, x1, y1, x2, y2):")
        py += indent(py_rect_check(a.rect) + [f"return self._{a.key}Of(x1, y1, x2, y2)"], 2) + [""]
        py.append(f"    # O(1) -- {a.word} of every {'set ' if mm else ''}point" + (f" ({a.none_words_py} if there are none)" if mm else ""))
        py.append(f"    def {a.all}(self):")
        root = f"self.{a.arr}[2 * self.off[1] + 1]"
        if a.key in ("min", "max"):
            py += [f"        res = {root}", f"        return {a.py_result('res')}", ""]
        else:
            py += [f"        return abs({root})" if a.key == "gcd" else f"        return {root}", ""]
        if a.key in ("min", "max"):
            for n, xsn, ysn in CORNERS:
                bx = ("NEG", "x") if xsn == "<=" else ("x", "POS")
                by = ("NEG", "y") if ysn == "<=" else ("y", "POS")
                py += indent(wrap_comment(f"O(log^2 N) -- {a.word} of the set points with x {xsn} the given x and y {ysn} the given y "
                                          f"(None if there are none); any integers", "#"))
                py += [f"    def {a.key}{n}(self, x, y):", f"        return self._{a.key}Of({bx[0]}, {by[0]}, {bx[1]}, {by[1]})", ""]
    while py[-1] == "":
        py.pop()

    # ---- C++
    cpp = wrap_comment(doc_cpp, "//")
    cpp.append("// T is any integer type (int, long long, ...)" + ("; sums are kept in S (long long for a smaller T)." if "sum" in aggs else ".")
               + " Coordinates are long long.")
    cpp += ["template <typename T>", f"struct {cls} {{", "    using ll = long long;"]
    if "sum" in aggs:
        cpp.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;")
    if "max" in aggs:
        cpp.append("    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no set point gives")
    if "min" in aggs:
        cpp.append("    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set point gives")
    if mm:
        cpp += ["    static constexpr ll LOW = numeric_limits<ll>::min(), HIGH = numeric_limits<ll>::max();  // no bound on a coordinate"]
    cpp += ["    int n;", "    vector<pair<ll, ll>> pts;", "    vector<T> vals;"]
    if mm:
        cpp.append("    vector<char> isSet;")
    cpp += ["    vector<ll> xs, ys;", "    vector<int> off, cnt;"]
    for a in A:
        cpp.append(f"    vector<{a.cpp_type}> {a.arr};  // x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])")
    cpp.append("")
    if "gcd" in aggs:
        cpp += ["    static T gcdOf(T a, T b) { return std::gcd(a, b); }", ""]
    cpp += indent(wrap_comment(CTOR_CPP, "//"))
    cpp += [f"    explicit {cls}(vector<pair<ll, ll>> points) : pts(std::move(points)) {{"]
    b = [
        f'if (pts.empty()) throw invalid_argument("{cls}: needs at least one point");',
        "sort(pts.begin(), pts.end());",
        "pts.erase(unique(pts.begin(), pts.end()), pts.end());",
        "vals.assign(pts.size(), T(0));",
    ]
    if mm:
        b.append("isSet.assign(pts.size(), 0);")
    b += [
        "for (auto& p : pts)",
        "    if (xs.empty() || xs.back() != p.first) xs.push_back(p.first);",
        "n = (int)xs.size();",
        "vector<int> byY(pts.size());",
        "iota(byY.begin(), byY.end(), 0);",
        "sort(byY.begin(), byY.end(), [&](int a, int b) { return pts[a].second < pts[b].second; });",
        "vector<vector<ll>> lists(2 * n);  // per x-node: the distinct y's under it, ascending",
        "for (int i : byY) {",
        "    ll y = pts[i].second;",
        "    for (int p = (int)(lower_bound(xs.begin(), xs.end(), pts[i].first) - xs.begin()) + n; p >= 1; p >>= 1)",
        "        if (lists[p].empty() || lists[p].back() != y) lists[p].push_back(y);",
        "}",
        "off.assign(2 * n, 0);",
        "cnt.assign(2 * n, 0);",
        "for (int p = 1; p < 2 * n; p++) {",
        "    off[p] = (int)ys.size();",
        "    cnt[p] = (int)lists[p].size();",
        "    ys.insert(ys.end(), lists[p].begin(), lists[p].end());",
        "}",
    ]
    for a in A:
        b.append(f"{a.arr}.assign(2 * ys.size(), {a.cpp_id if mm else a.cpp_type + '(0)'});")
    cpp += indent(b, 2) + ["    }", ""] + CPP_INDEX
    cpp += ["    // point (x, y) = v, then every node above it", "    void setPoint(ll x, ll y, T v) {"]
    b = ["int p = (int)(lower_bound(xs.begin(), xs.end(), x) - xs.begin()) + n;"]
    for a in A:
        b.append(f"{a.cpp_type} v{a.cap} = v;  // this aggregate over the points with this y under x-node p")
    b += ["while (true) {", "    const ll* first = ys.data() + off[p];", "    int base = 2 * off[p], k = (int)(lower_bound(first, first + cnt[p], y) - first) + cnt[p];"]
    for a in A:
        b.append(f"    {a.arr}[base + k] = v{a.cap};")
    b.append("    for (k >>= 1; k >= 1; k >>= 1) {")
    for a in A:
        b.append(f"        {a.arr}[base + k] = {a.cpp_comb(f'{a.arr}[base + 2 * k]', f'{a.arr}[base + 2 * k + 1]')};")
    b += ["    }", "    if (p == 1) break;", "    int s = p ^ 1;  // the other half of the parent: does it have this y too?",
          "    first = ys.data() + off[s];", "    int j = (int)(lower_bound(first, first + cnt[s], y) - first);", "    if (j < cnt[s] && first[j] == y) {",
          "        j += 2 * off[s] + cnt[s];"]
    for a in A:
        b.append("        " + a.cpp_take(f"v{a.cap}", f"{a.arr}[j]"))
    b += ["    }", "    p >>= 1;", "}"]
    cpp += indent(b, 2) + ["    }", ""]
    none_point = {True: None}.get(False)
    rd_none = "NO_MAX" if "max" in aggs else "NO_MIN" if "min" in aggs else None
    cpp += indent(wrap_comment(f"O(log N) -- the value at (x, y){', ' + rd_none + ' if it was never set' if mm else ''}; {POINT_RULE_CPP}", "//"))
    cpp += ["    T pointGet(ll x, ll y) const {", '        int i = indexOf(x, y, "pointGet");',
            f"        return isSet[i] ? vals[i] : {rd_none};" if mm else "        return vals[i];", "    }", ""]
    cpp += indent(wrap_comment(f"{upd} -- the point (x, y) becomes v (it may go down as well as up); {POINT_RULE_CPP}", "//"))
    cpp += ["    void pointAssign(ll x, ll y, T v) {", '        int i = indexOf(x, y, "pointAssign");', "        vals[i] = v;"]
    if mm:
        cpp.append("        isSet[i] = 1;")
    cpp += ["        setPoint(x, y, v);", "    }", ""]
    cpp += indent(wrap_comment(f"{upd} -- adds v to the point (x, y){if_empty}; {POINT_RULE_CPP}", "//"))
    cpp += ["    void pointAdd(ll x, ll y, T v) {", '        int i = indexOf(x, y, "pointAdd");']
    if mm:
        cpp += ["        vals[i] = isSet[i] ? T(vals[i] + v) : v;", "        isSet[i] = 1;"]
    else:
        cpp += ["        vals[i] = T(vals[i] + v);"]
    cpp += ["        setPoint(x, y, vals[i]);", "    }", ""]
    for name, sym, word in (("pointChmax", ">", "max"), ("pointChmin", "<", "min")):
        cpp += indent(wrap_comment(f"{upd} -- the point (x, y) becomes {word}(itself, v){if_empty}; {POINT_RULE_CPP}", "//"))
        cpp += [f"    void {name}(ll x, ll y, T v) {{", f'        int i = indexOf(x, y, "{name}");',
                f"        if ({'isSet[i] && ' if mm else ''}!(v {sym} vals[i])) return;", "        vals[i] = v;"]
        if mm:
            cpp.append("        isSet[i] = 1;")
        cpp += ["        setPoint(x, y, v);", "    }", ""]

    def cpp_inner(a, node):
        return [
            f"const ll* first = ys.data() + off[{node}];",
            f"int base = 2 * off[{node}], c = cnt[{node}];",
            "int lo = (int)(lower_bound(first, first + c, y1) - first) + c;",
            "int hi = (int)(upper_bound(first, first + c, y2) - first) + c;",
            "for (; lo < hi; lo >>= 1, hi >>= 1) {",
            f"    if (lo & 1) {a.cpp_take('res', f'{a.arr}[base + lo++]')}",
            f"    if (hi & 1) {a.cpp_take('res', f'{a.arr}[base + --hi]')}",
            "}",
        ]

    for a in A:
        cpp.append(f"    {a.cpp_type} {a.key}Of(ll x1, ll y1, ll x2, ll y2) const {{")
        b = [f"{a.cpp_type} res = {a.cpp_id};", "int l = (int)(lower_bound(xs.begin(), xs.end(), x1) - xs.begin()) + n;",
             "int r = (int)(upper_bound(xs.begin(), xs.end(), x2) - xs.begin()) + n;", "for (; l < r; l >>= 1, r >>= 1) {", "    if (l & 1) {"]
        b += indent(cpp_inner(a, "l"), 2) + ["        l++;", "    }", "    if (r & 1) {", "        --r;"] + indent(cpp_inner(a, "r"), 2) + ["    }", "}", "return res;"]
        cpp += indent(b, 2) + ["    }", ""]
        cost = "O(log^2 N + log U)" if a.key == "gcd" else "O(log^2 N)"
        what = (f"{a.word} of the set points with x1 <= x <= x2 and y1 <= y <= y2 ({a.none_words_cpp} if there are none)" if mm
                else f"{a.word} of the points with x1 <= x <= x2 and y1 <= y <= y2 ({a.none_words_cpp} if no point is there)")
        cpp += indent(wrap_comment(f"{cost} -- {what}; {RECT_RULE_CPP}", "//"))
        cpp.append(f"    {a.cpp_type} {a.rect}(ll x1, ll y1, ll x2, ll y2) const {{")
        cpp += indent(cpp_rect_check(a.rect) + [f"return {a.key}Of(x1, y1, x2, y2);"], 2) + ["    }", ""]
        cpp.append(f"    // O(1) -- {a.word} of every {'set ' if mm else ''}point" + (f" ({a.none_words_cpp} if there are none)" if mm else ""))
        cpp.append(f"    {a.cpp_type} {a.all}() const {{")
        root = f"{a.arr}[2 * off[1] + 1]"
        cpp += [f"        return gcdOf({root}, T(0));" if a.key == "gcd" else f"        return {root};", "    }", ""]
        if a.key in ("min", "max"):
            for n, xsn, ysn in CORNERS:
                bx = ("LOW", "x") if xsn == "<=" else ("x", "HIGH")
                by = ("LOW", "y") if ysn == "<=" else ("y", "HIGH")
                cpp += indent(wrap_comment(f"O(log^2 N) -- {a.word} of the set points with x {xsn} the given x and y {ysn} the given y "
                                           f"({a.none_words_cpp} if there are none); any integers", "//"))
                cpp += [f"    T {a.key}{n}(ll x, ll y) const {{", f"        return {a.key}Of({bx[0]}, {by[0]}, {bx[1]}, {by[1]});", "    }", ""]
    while cpp[-1] == "":
        cpp.pop()
    cpp.append("};")
    emit("points-seg-tree-" + "-".join(aggs), ops, "seg-tree", costs, "N*log(N)", memory, py, cpp, [("empty-cells", "yes")] if mm else [])


# ------------------------------------------------------------------------------------------------ Fenwick of Fenwicks
PY_BIT_BUILD = [
    "xs = self.xs = sorted({x for x, _ in pts})",
    "n = self.n = len(xs)",
    "lists = [[] for _ in range(n + 1)]  # per Fenwick x-node: the distinct y's it covers, ascending",
    "for x, y in sorted(pts, key=lambda p: p[1]):",
    "    i = bisect_left(xs, x) + 1",
    "    while i <= n:",
    "        lst = lists[i]",
    "        if not lst or lst[-1] != y:",
    "            lst.append(y)",
    "        i += i & -i",
    "off = self.off = [0] * (n + 1)",
    "cnt = self.cnt = [0] * (n + 1)",
    "ys = self.ys = []",
    "for i in range(1, n + 1):",
    "    off[i] = len(ys)",
    "    cnt[i] = len(lists[i])",
    "    ys += lists[i]",
]
CPP_BIT_BUILD = [
    "for (auto& p : pts)",
    "    if (xs.empty() || xs.back() != p.first) xs.push_back(p.first);",
    "n = (int)xs.size();",
    "vector<int> byY(pts.size());",
    "iota(byY.begin(), byY.end(), 0);",
    "sort(byY.begin(), byY.end(), [&](int a, int b) { return pts[a].second < pts[b].second; });",
    "vector<vector<ll>> lists(n + 1);  // per Fenwick x-node: the distinct y's it covers, ascending",
    "for (int i : byY) {",
    "    ll y = pts[i].second;",
    "    int k = (int)(lower_bound(xs.begin(), xs.end(), pts[i].first) - xs.begin()) + 1;",
    "    for (; k <= n; k += k & -k)",
    "        if (lists[k].empty() || lists[k].back() != y) lists[k].push_back(y);",
    "}",
    "off.assign(n + 1, 0);",
    "cnt.assign(n + 1, 0);",
    "for (int i = 1; i <= n; i++) {",
    "    off[i] = (int)ys.size();",
    "    cnt[i] = (int)lists[i].size();",
    "    ys.insert(ys.end(), lists[i].begin(), lists[i].end());",
    "}",
]


def bit_sum(aggs):
    cls = "PointsFenwick2D"
    A = [AGGS[k] for k in aggs]
    sym = {"sum": "+", "xor": "^"}
    words = " and ".join(a.word for a in A)
    ops = ["pointGet", "pointAssign", "pointAdd", "pointChmax", "pointChmin"] + [x for a in A for x in (a.rect, a.all)]
    costs = {op: "log^2(N)" for op in ops}
    costs.update({"pointGet": "log(N)", **{a.all: "1" for a in A}})
    memory = {"layout": "none", "node": " ".join(f"{a.arr}[1*N*log(N)]" for a in A),
              "other": "ys[1*N*log(N)] pts[2*N] vals[1*N] xs[1*N] off[1*N] cnt[1*N]",
              "note": "every point's y is listed in each of the O(log N) Fenwick x-nodes covering it; an x-node's own Fenwick tree is as long as its list"}
    doc = (f"2D Fenwick tree over points known up front ({words}): point updates and any-rectangle {words} in O(log^2 N), "
           f"with N log N memory whatever the coordinates are (any integers, negative is fine). The constructor takes every "
           f"(x, y) that will ever be updated; every point starts at 0. A Fenwick tree over the distinct x's; every node of "
           f"it keeps the sorted y's of the points it covers and a Fenwick tree over just those. Half the memory of the "
           f"segment tree version and a smaller constant, for {words} only. Rectangles are inclusive, x1..x2 by y1..y2, and "
           f"their corners can be any integers, given or not.")
    py = ["from bisect import bisect_left, bisect_right", "", ""] + wrap_comment(doc, "#") + [f"class {cls}:"]
    slots = ["n", "pts", "vals", "xs", "ys", "off", "cnt"] + [a.arr for a in A] + [f"total{a.cap}" for a in A]
    py.append("    __slots__ = (" + ", ".join(f'"{s}"' for s in slots) + ")")
    py += [""] + indent(wrap_comment(CTOR_PY, "#")) + ["    def __init__(self, points):"]
    b = ["if not points:", f'    raise ValueError("{cls}: needs at least one point")', "pts = self.pts = sorted(set(map(tuple, points)))",
         "self.vals = [0] * len(pts)"] + PY_BIT_BUILD
    for a in A:
        b += [f"self.{a.arr} = [0] * len(ys)  # x-node i's own Fenwick tree is [off[i], off[i] + cnt[i]), 1-based inside", f"self.total{a.cap} = 0"]
    py += indent(b, 2) + [""] + PY_INDEX
    py += ["    # point number i, at (x, y), becomes v", "    def _set(self, i, x, y, v):"]
    b = ["old = self.vals[i]", "self.vals[i] = v", "xs, ys, off, cnt, n = self.xs, self.ys, self.off, self.cnt, self.n"]
    for a in A:
        s = sym[a.key]
        b += [f"d = {'v - old' if a.key == 'sum' else 'v ^ old'}", f"self.total{a.cap} {s}= d", f"t = self.{a.arr}", "i = bisect_left(xs, x) + 1", "while i <= n:",
              "    o = off[i]", "    c = cnt[i]", "    k = bisect_left(ys, y, o, o + c) - o + 1", "    o -= 1", "    while k <= c:", f"        t[o + k] {s}= d",
              "        k += k & -k", "    i += i & -i"]
    py += indent(b, 2) + [""]
    for a in A:
        s = sym[a.key]
        py += [f"    # {a.word} of the points with x <= the given x and y <= the given y", f"    def _prefix{a.cap}(self, x, y):"]
        py += indent(["xs, ys, off, cnt, t = self.xs, self.ys, self.off, self.cnt, self." + a.arr, "res = 0", "i = bisect_right(xs, x)", "while i > 0:",
                      "    o = off[i]", "    k = bisect_right(ys, y, o, o + cnt[i]) - o", "    o -= 1", "    while k > 0:", f"        res {s}= t[o + k]",
                      "        k &= k - 1", "    i &= i - 1", "return res"], 2) + [""]
    py.append(f"    # O(log N) -- the value at (x, y); {POINT_RULE_PY}")
    py += ["    def pointGet(self, x, y):", '        return self.vals[self._index(x, y, "pointGet")]', ""]
    for name, text, lines in (
        ("pointAssign", "the point (x, y) becomes v", ["self._set(i, x, y, v)"]),
        ("pointAdd", "adds v to the point (x, y)", ["self._set(i, x, y, self.vals[i] + v)"]),
        ("pointChmax", "the point (x, y) becomes max(itself, v)", ["if v > self.vals[i]:", "    self._set(i, x, y, v)"]),
        ("pointChmin", "the point (x, y) becomes min(itself, v)", ["if v < self.vals[i]:", "    self._set(i, x, y, v)"]),
    ):
        py += indent(wrap_comment(f"O(log^2 N) -- {text}; {POINT_RULE_PY}", "#"))
        py += [f"    def {name}(self, x, y, v):", f'        i = self._index(x, y, "{name}")'] + indent(lines, 2) + [""]
    for a in A:
        s = sym[a.key]
        m = "-" if a.key == "sum" else "^"
        py += indent(wrap_comment(f"O(log^2 N) -- {a.word} of the points with x1 <= x <= x2 and y1 <= y <= y2 (0 if no point is there); {RECT_RULE_PY}", "#"))
        py.append(f"    def {a.rect}(self, x1, y1, x2, y2):")
        py += indent(py_rect_check(a.rect) + [f"p = self._prefix{a.cap}", f"return p(x2, y2) {m} p(x1 - 1, y2) {m} p(x2, y1 - 1) {s} p(x1 - 1, y1 - 1)"], 2)
        py += ["", f"    # O(1) -- {a.word} of every point", f"    def {a.all}(self):", f"        return self.total{a.cap}", ""]
    while py[-1] == "":
        py.pop()

    cpp = wrap_comment(doc, "//")
    cpp.append("// T is any integer type (int, long long, ...)" + ("; sums are kept in S (long long for a smaller T)." if "sum" in aggs else ".")
               + " Coordinates are long long.")
    cpp += ["template <typename T>", f"struct {cls} {{", "    using ll = long long;"]
    if "sum" in aggs:
        cpp.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;")
    cpp += ["    int n;", "    vector<pair<ll, ll>> pts;", "    vector<T> vals;", "    vector<ll> xs, ys;", "    vector<int> off, cnt;"]
    for a in A:
        cpp += [f"    vector<{a.cpp_type}> {a.arr};  // x-node i's own Fenwick tree is [off[i], off[i] + cnt[i]), 1-based inside", f"    {a.cpp_type} total{a.cap} = 0;"]
    cpp += [""] + indent(wrap_comment(CTOR_CPP, "//")) + [f"    explicit {cls}(vector<pair<ll, ll>> points) : pts(std::move(points)) {{"]
    b = [f'if (pts.empty()) throw invalid_argument("{cls}: needs at least one point");', "sort(pts.begin(), pts.end());",
         "pts.erase(unique(pts.begin(), pts.end()), pts.end());", "vals.assign(pts.size(), T(0));"] + CPP_BIT_BUILD
    for a in A:
        b.append(f"{a.arr}.assign(ys.size(), 0);")
    cpp += indent(b, 2) + ["    }", ""] + CPP_INDEX
    cpp += ["    // point number i, at (x, y), becomes v", "    void setPoint(int i, ll x, ll y, T v) {"]
    b = ["T old = vals[i];", "vals[i] = v;", "int xi = (int)(lower_bound(xs.begin(), xs.end(), x) - xs.begin()) + 1;"]
    for a in A:
        s = sym[a.key]
        b += [f"{a.cpp_type} d{a.cap} = {f'{a.cpp_type}(v) - old' if a.key == 'sum' else 'v ^ old'};", f"total{a.cap} {s}= d{a.cap};",
              "for (int k = xi; k <= n; k += k & -k) {", "    const ll* first = ys.data() + off[k];",
              f"    {a.cpp_type}* t = {a.arr}.data() + off[k] - 1;",
              f"    for (int j = (int)(lower_bound(first, first + cnt[k], y) - first) + 1; j <= cnt[k]; j += j & -j) t[j] {s}= d{a.cap};", "}"]
    cpp += indent(b, 2) + ["    }", ""]
    for a in A:
        s = sym[a.key]
        cpp += [f"    // {a.word} of the points with x <= the given x and y <= the given y", f"    {a.cpp_type} prefix{a.cap}(ll x, ll y) const {{"]
        cpp += indent([f"{a.cpp_type} res = 0;", "for (int k = (int)(upper_bound(xs.begin(), xs.end(), x) - xs.begin()); k > 0; k &= k - 1) {",
                       "    const ll* first = ys.data() + off[k];", f"    const {a.cpp_type}* t = {a.arr}.data() + off[k] - 1;",
                       f"    for (int j = (int)(upper_bound(first, first + cnt[k], y) - first); j > 0; j &= j - 1) res {s}= t[j];", "}", "return res;"], 2)
        cpp += ["    }", ""]
    cpp.append(f"    // O(log N) -- the value at (x, y); {POINT_RULE_CPP}")
    cpp += ["    T pointGet(ll x, ll y) const {", '        return vals[indexOf(x, y, "pointGet")];', "    }", ""]
    for name, text, body in (
        ("pointAssign", "the point (x, y) becomes v", "setPoint(i, x, y, v);"),
        ("pointAdd", "adds v to the point (x, y)", "setPoint(i, x, y, T(vals[i] + v));"),
        ("pointChmax", "the point (x, y) becomes max(itself, v)", "if (v > vals[i]) setPoint(i, x, y, v);"),
        ("pointChmin", "the point (x, y) becomes min(itself, v)", "if (v < vals[i]) setPoint(i, x, y, v);"),
    ):
        cpp += indent(wrap_comment(f"O(log^2 N) -- {text}; {POINT_RULE_CPP}", "//"))
        cpp += [f"    void {name}(ll x, ll y, T v) {{", f'        int i = indexOf(x, y, "{name}");', "        " + body, "    }", ""]
    for a in A:
        s = sym[a.key]
        m = "-" if a.key == "sum" else "^"
        p = f"prefix{a.cap}"
        cpp += indent(wrap_comment(f"O(log^2 N) -- {a.word} of the points with x1 <= x <= x2 and y1 <= y <= y2 (0 if no point is there); {RECT_RULE_CPP}", "//"))
        cpp.append(f"    {a.cpp_type} {a.rect}(ll x1, ll y1, ll x2, ll y2) const {{")
        cpp += indent(cpp_rect_check(a.rect) + [f"return {p}(x2, y2) {m} {p}(x1 - 1, y2) {m} {p}(x2, y1 - 1) {s} {p}(x1 - 1, y1 - 1);"], 2)
        cpp += ["    }", "", f"    // O(1) -- {a.word} of every point", f"    {a.cpp_type} {a.all}() const {{", f"        return total{a.cap};", "    }", ""]
    while cpp[-1] == "":
        cpp.pop()
    cpp.append("};")
    emit("points-bit-" + "-".join(aggs), ops, "BIT", costs, "N*log(N)", memory, py, cpp)


def corner_bit(kind, corners):
    a = AGGS[kind]
    cls = f"PointsCorner{a.cap}Fenwick2D"
    helper = f"_Prefix{a.cap}Fenwick"
    better = ">" if kind == "max" else "<"
    upd = "pointChmax" if kind == "max" else "pointChmin"
    names = [c[0] for c in corners]
    ident_py = "NEG" if kind == "max" else "POS"
    none = a.none_cpp
    ops = [upd, a.all] + [f"{kind}{n}" for n in names]
    costs = {op: "log^2(N)" for op in ops}
    costs[a.all] = "1"
    k = len(names)
    memory = {"layout": "none", "node": f"tree[{k}*N*log(N)]", "other": f"ys[{k}*N*log(N)] xs[{k}*N] off[{k}*N] cnt[{k}*N] pts[2*N]",
              "note": "one Fenwick-of-Fenwicks per corner direction asked for (a >= direction is the same structure on negated coordinates)"}
    doc = (f"Corner {kind} over points known up front, with Fenwick trees: {upd} at a point and the {kind} over a corner of the "
           f"plane (every point with x <= or >= a given x, and y <= or >= a given y) in O(log^2 N), with N log N memory per "
           f"direction whatever the coordinates are (any integers, negative is fine). The constructor takes every (x, y) "
           f"that will ever be updated. This works because values only move one way: a point can only go "
           f"{'up' if kind == 'max' else 'down'}, so a tree entry never has to forget a value; for a point that can move both "
           f"ways, or for rectangles that aren't corners, use the segment tree version. Every point starts empty and "
           f"queries only see points that have been set.")
    py = ["from bisect import bisect_left, bisect_right", "", f'{ident_py} = float("{"-inf" if kind == "max" else "inf"}")  # a point never set', "", "",
          f"# {kind} over the points with x <= a given x and y <= a given y, values only going {'up' if kind == 'max' else 'down'}",
          f"class {helper}:", '    __slots__ = ("n", "xs", "ys", "off", "cnt", "tree")', "", "    def __init__(self, pts):"]
    py += indent(PY_BIT_BUILD + [f"self.tree = [{ident_py}] * len(ys)"], 2) + ["", "    def improve(self, x, y, v):"]
    py += indent(["xs, ys, off, cnt, t, n = self.xs, self.ys, self.off, self.cnt, self.tree, self.n", "i = bisect_left(xs, x) + 1", "while i <= n:", "    o = off[i]",
                  "    c = cnt[i]", "    k = bisect_left(ys, y, o, o + c) - o + 1", "    o -= 1", "    while k <= c:", f"        if v {better} t[o + k]:",
                  "            t[o + k] = v", "        k += k & -k", "    i += i & -i"], 2) + ["", "    def best(self, x, y):"]
    py += indent(["xs, ys, off, cnt, t = self.xs, self.ys, self.off, self.cnt, self.tree", f"res = {ident_py}", "i = bisect_right(xs, x)", "while i > 0:",
                  "    o = off[i]", "    k = bisect_right(ys, y, o, o + cnt[i]) - o", "    o -= 1", "    while k > 0:", "        z = t[o + k]",
                  f"        if z {better} res:", "            res = z", "        k &= k - 1", "    i &= i - 1", "return res"], 2) + ["", ""]
    py += wrap_comment(doc + f" A {kind} over no set point is None.", "#") + [f"class {cls}:"]
    py.append("    __slots__ = (" + ", ".join(f'"{s}"' for s in ["pts", "top"] + [f"t{n}" for n in names]) + ")")
    py += [""] + indent(wrap_comment(CTOR_PY, "#")) + ["    def __init__(self, points):"]
    b = ["if not points:", f'    raise ValueError("{cls}: needs at least one point")', "pts = self.pts = sorted(set(map(tuple, points)))", f"self.top = {ident_py}"]
    for n, xsn, ysn in corners:
        sx, sy = ("" if xsn == "<=" else "-"), ("" if ysn == "<=" else "-")
        b.append(f"self.t{n} = {helper}(" + ("pts" if not sx and not sy else f"sorted(({sx}x, {sy}y) for x, y in pts)") + ")")
    py += indent(b, 2) + [""]
    py += indent(wrap_comment(f"O(log^2 N) -- the point (x, y) becomes {kind}(itself, v); an empty point becomes v; {POINT_RULE_PY}", "#"))
    py += [f"    def {upd}(self, x, y, v):", "        pts = self.pts", "        i = bisect_left(pts, (x, y))", "        if i == len(pts) or pts[i] != (x, y):",
           f'            raise IndexError(f"{upd}: ({{x}}, {{y}}) is not one of the points given to the constructor")',
           f"        if v {better} self.top:", "            self.top = v"]
    for n, xsn, ysn in corners:
        py.append(f"        self.t{n}.improve({'x' if xsn == '<=' else '-x'}, {'y' if ysn == '<=' else '-y'}, v)")
    py.append("")
    for n, xsn, ysn in corners:
        py += indent(wrap_comment(f"O(log^2 N) -- {kind} of the set points with x {xsn} the given x and y {ysn} the given y (None if there are none); "
                                  f"any integers", "#"))
        py += [f"    def {kind}{n}(self, x, y):", f"        res = self.t{n}.best({'x' if xsn == '<=' else '-x'}, {'y' if ysn == '<=' else '-y'})",
               f"        return None if res == {ident_py} else res", ""]
    py += [f"    # O(1) -- {kind} of every set point (None if there are none)", f"    def {a.all}(self):",
           f"        return None if self.top == {ident_py} else self.top"]

    cpp = wrap_comment(doc + f" A {kind} over no set point is {none}.", "//")
    cpp += ["// T is any integer type (int, long long, ...). Coordinates are long long.", "template <typename T>", f"struct {cls} {{", "    using ll = long long;",
            f"    static constexpr T {none} = numeric_limits<T>::{'min' if kind == 'max' else 'max'}();  // what a {kind} over no set point gives", "",
            f"    // {kind} over the points with x <= a given x and y <= a given y, values only going {'up' if kind == 'max' else 'down'}",
            "    struct Prefix {", "        int n = 0;", "        vector<ll> xs, ys;", "        vector<int> off, cnt;", "        vector<T> tree;", "",
            "        void build(vector<pair<ll, ll>> pts) {", "            sort(pts.begin(), pts.end());"]
    cpp += indent(CPP_BIT_BUILD + [f"tree.assign(ys.size(), {none});"], 3)
    cpp += ["        }", "", "        void improve(ll x, ll y, T v) {",
            "            for (int k = (int)(lower_bound(xs.begin(), xs.end(), x) - xs.begin()) + 1; k <= n; k += k & -k) {",
            "                const ll* first = ys.data() + off[k];", "                T* t = tree.data() + off[k] - 1;",
            "                for (int j = (int)(lower_bound(first, first + cnt[k], y) - first) + 1; j <= cnt[k]; j += j & -j)",
            f"                    t[j] = {kind}(t[j], v);", "            }", "        }", "", "        T best(ll x, ll y) const {", f"            T res = {none};",
            "            for (int k = (int)(upper_bound(xs.begin(), xs.end(), x) - xs.begin()); k > 0; k &= k - 1) {",
            "                const ll* first = ys.data() + off[k];", "                const T* t = tree.data() + off[k] - 1;",
            f"                for (int j = (int)(upper_bound(first, first + cnt[k], y) - first); j > 0; j &= j - 1) res = {kind}(res, t[j]);",
            "            }", "            return res;", "        }", "    };", "", "    vector<pair<ll, ll>> pts;", f"    T top = {none};",
            f"    Prefix {', '.join('t' + n for n in names)};", ""]
    cpp += indent(wrap_comment(CTOR_CPP, "//")) + [f"    explicit {cls}(vector<pair<ll, ll>> points) : pts(std::move(points)) {{"]
    b = [f'if (pts.empty()) throw invalid_argument("{cls}: needs at least one point");', "sort(pts.begin(), pts.end());",
         "pts.erase(unique(pts.begin(), pts.end()), pts.end());"]
    for n, xsn, ysn in corners:
        if xsn == "<=" and ysn == "<=":
            b.append(f"t{n}.build(pts);")
        else:
            b += ["{", "    auto flipped = pts;", f"    for (auto& p : flipped) p = {{{'p.first' if xsn == '<=' else '-p.first'}, {'p.second' if ysn == '<=' else '-p.second'}}};",
                  f"    t{n}.build(std::move(flipped));", "}"]
    cpp += indent(b, 2) + ["    }", ""]
    cpp += indent(wrap_comment(f"O(log^2 N) -- the point (x, y) becomes {kind}(itself, v); an empty point becomes v; {POINT_RULE_CPP}", "//"))
    cpp += [f"    void {upd}(ll x, ll y, T v) {{", f'        if (!binary_search(pts.begin(), pts.end(), make_pair(x, y)))',
            f'            throw out_of_range("{upd}: (x, y) is not one of the points given to the constructor");', f"        top = {kind}(top, v);"]
    for n, xsn, ysn in corners:
        cpp.append(f"        t{n}.improve({'x' if xsn == '<=' else '-x'}, {'y' if ysn == '<=' else '-y'}, v);")
    cpp += ["    }", ""]
    for n, xsn, ysn in corners:
        cpp += indent(wrap_comment(f"O(log^2 N) -- {kind} of the set points with x {xsn} the given x and y {ysn} the given y ({none} if there are none); "
                                   f"any integers", "//"))
        cpp += [f"    T {kind}{n}(ll x, ll y) const {{", f"        return t{n}.best({'x' if xsn == '<=' else '-x'}, {'y' if ysn == '<=' else '-y'});", "    }", ""]
    cpp += [f"    // O(1) -- {kind} of every set point ({none} if there are none)", f"    T {a.all}() const {{", "        return top;", "    }", "};"]
    emit(f"points-bit-corner-{kind}-" + "-".join(n.lower() for n in names), ops, "BIT", costs, "N*log(N)", memory, py, cpp, [("empty-cells", "yes")])


def main():
    n = 0
    for aggs in subsets(AGG_ORDER):
        seg_tree(aggs)
        n += 1
    for aggs in (["sum"], ["xor"], ["sum", "xor"]):
        bit_sum(aggs)
        n += 1
    for kind in ("max", "min"):
        for mask in range(1, 16):
            corner_bit(kind, [c for i, c in enumerate(CORNERS) if mask >> i & 1])
            n += 1
    print(f"points: {n} folders")


if __name__ == "__main__":
    main()
