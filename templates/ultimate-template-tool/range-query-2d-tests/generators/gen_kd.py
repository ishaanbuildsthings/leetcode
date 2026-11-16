"""Points known up front, rectangle updates with any query: the k-d tree with lazy tags.

    python3 gen_kd.py              # writes range-queries-2d/points-kd-tree-<aggregates>/template.{py,cpp}

Rectangle add and rectangle assign with rectangle sum / min / max, which no tree of trees can do (a tag can't be pushed
down an outer tree). The price is O(sqrt N) per rectangle op instead of O(log^2 N); memory is linear.
"""
from lib2d import AGGS, cpp_throw, header, indent, py_raise, subsets, wrap_comment, write

CORNERS = [("LteLte", "<=", "<="), ("LteGte", "<=", ">="), ("GteLte", ">=", "<="), ("GteGte", ">=", ">=")]
POINT_RULE_PY = "needs (x, y) to be one of the points given, else IndexError"
POINT_RULE_CPP = "needs (x, y) to be one of the points given, else throws out_of_range"
RECT_RULE_PY = "needs x1 <= x2 and y1 <= y2, else IndexError"
RECT_RULE_CPP = "needs x1 <= x2 and y1 <= y2, else throws out_of_range"


def py_rect_check(name):
    return ["if x1 > x2 or y1 > y2:"] + indent(py_raise(
        "IndexError", f"{name}: needs x1 <= x2 and y1 <= y2, got x1 = {{x1}}, y1 = {{y1}}, x2 = {{x2}}, y2 = {{y2}}", 3))


def cpp_rect_check(name):
    return cpp_throw("x1 > x2 || y1 > y2", "out_of_range", f"{name}: needs x1 <= x2 and y1 <= y2", 2)


def kd_tree(aggs):
    cls = "KdTree2D"
    A = [AGGS[k] for k in aggs]
    has = {k: k in aggs for k in ("sum", "min", "max")}
    rd = A[0]  # a single point's node holds its value in every array
    ops = ["pointGet", "pointAssign", "pointAdd", "pointChmax", "pointChmin", "rectAdd", "rectAssign"]
    for a in A:
        ops += [a.rect, a.all]
        if a.key in ("min", "max"):
            ops += [f"{a.key}{n}" for n, _, _ in CORNERS]
    costs = {}
    for op in ops:
        costs[op] = "1" if op.endswith("All") else "log(N)" if op.startswith("point") else "sqrt(N)"
    memory = {
        "layout": "none",
        "node": " ".join(f"{a.arr}[2*N]" for a in A),
        "tags": "addTag[2*N] setTag[2*N]",
        "other": "xMin[2*N] xMax[2*N] yMin[2*N] yMax[2*N] pts[2*N] pos[1*N]",
        "note": "a binary tree over the points in k-d order (2N - 1 nodes), each node with its points' bounding box",
    }
    words = ", ".join(a.word for a in A)
    doc = (f"K-d tree with lazy tags ({words}): rectangle add and rectangle assign together with rectangle {words}, over points "
           f"known up front (any integers, negative is fine). O(sqrt N) per rectangle op, O(log N) per point op, linear "
           f"memory. A tree of trees can't do rectangle updates with these queries (a tag can't be pushed down its outer "
           f"tree); this can, because it is one tree: the points are split in half by x, each half by y, and so on, every "
           f"node keeps the bounding box of its points, and a rectangle op only opens the nodes whose box the rectangle's "
           f"border crosses (about sqrt N of them). The constructor takes every (x, y) that will ever be used; every point "
           f"starts at 0. Rectangles are inclusive, x1..x2 by y1..y2, and their corners can be any integers; a rectangle "
           f"update touches the given points inside it.")

    # ------------------------------------------------------------------ Python
    py = ["from bisect import bisect_left", ""]
    if has["max"]:
        py.append('NEG = float("-inf")  # the max of no points; also "no lower bound" on a coordinate')
    if has["min"]:
        py.append('POS = float("inf")  # the min of no points; also "no upper bound" on a coordinate')
    if has["max"] != has["min"]:
        py.append('POS = float("inf")  # "no upper bound" on a coordinate' if has["max"] else 'NEG = float("-inf")  # "no lower bound" on a coordinate')
    py += ["", ""] + wrap_comment(doc + (" A min / max over a rectangle with no given point in it is None." if has["min"] or has["max"] else ""), "#")
    py.append(f"class {cls}:")
    slots = ["n", "pts", "pos", "xMin", "xMax", "yMin", "yMax", "addTag", "setTag"] + [a.arr for a in A]
    py.append("    __slots__ = (" + ", ".join(f'"{s}"' for s in slots) + ")")
    py += [""] + indent(wrap_comment("O(N log N) -- points: every (x, y) that will ever be used, as pairs of integers (negative is fine, repeats "
                                     "are fine); needs at least one, else ValueError", "#")) + ["    def __init__(self, points):"]
    b = [
        "if not points:",
        f'    raise ValueError("{cls}: needs at least one point")',
        "pts = self.pts = sorted(set(map(tuple, points)))",
        "n = self.n = len(pts)",
        "size = 2 * n",
        "xMin = self.xMin = [0] * size",
        "xMax = self.xMax = [0] * size",
        "yMin = self.yMin = [0] * size",
        "yMax = self.yMax = [0] * size",
        "pos = self.pos = [0] * n  # pos[i]: where point i (in sorted order) sits in k-d order",
        "self.addTag = [0] * size",
        "self.setTag = [None] * size",
    ]
    for a in A:
        b.append(f"self.{a.arr} = [0] * size")
    b += [
        "side = [False] * n",
        "# a node is a stretch l..r of the k-d order; node (l, r) is numbered (l + r) | (l != r), its halves l..mid, mid+1..r.",
        "# Each node gets its points sorted by (x, y) and by (y, x); splitting keeps both orders, so the build is N log N",
        "todo = [(0, n - 1, list(range(n)), sorted(range(n), key=lambda i: (pts[i][1], pts[i][0])), 0)]",
        "while todo:",
        "    l, r, byX, byY, axis = todo.pop()",
        "    node = (l + r) | (l != r)",
        "    xMin[node] = pts[byX[0]][0]",
        "    xMax[node] = pts[byX[-1]][0]",
        "    yMin[node] = pts[byY[0]][1]",
        "    yMax[node] = pts[byY[-1]][1]",
        "    if l == r:",
        "        pos[byX[0]] = l",
        "        continue",
        "    mid = (l + r) >> 1",
        "    half = mid - l + 1",
        "    first = byX[:half] if axis == 0 else byY[:half]",
        "    for i in first:",
        "        side[i] = True",
        "    if axis == 0:",
        "        todo.append((mid + 1, r, byX[half:], [i for i in byY if not side[i]], 1))",
        "        todo.append((l, mid, first, [i for i in byY if side[i]], 1))",
        "    else:",
        "        todo.append((mid + 1, r, [i for i in byX if not side[i]], byY[half:], 0))",
        "        todo.append((l, mid, [i for i in byX if side[i]], first, 0))",
        "    for i in first:",
        "        side[i] = False",
    ]
    py += indent(b, 2) + [""]
    arrs = ", ".join(a.arr for a in A)
    self_arrs = ", ".join(f"self.{a.arr}" for a in A)

    def py_apply_assign(node, cnt, val):
        out = [f"setTag[{node}] = {val}", f"addTag[{node}] = 0"]
        for a in A:
            out.append(f"{a.arr}[{node}] = {val} * {cnt}" if a.key == "sum" else f"{a.arr}[{node}] = {val}")
        return out

    def py_apply_add(node, cnt, val):
        out = [f"if setTag[{node}] is None:", f"    addTag[{node}] += {val}", "else:", f"    setTag[{node}] += {val}"]
        for a in A:
            out.append(f"{a.arr}[{node}] += {val} * {cnt}" if a.key == "sum" else f"{a.arr}[{node}] += {val}")
        return out

    py += ["    # hands node (l, r)'s waiting assign / add to its two halves", "    def _push(self, node, l, r):"]
    b = ["setTag, addTag = self.setTag, self.addTag", "sv = setTag[node]", "av = addTag[node]", "if sv is None and not av:", "    return",
         f"{arrs} = {self_arrs}", "mid = (l + r) >> 1", "for a, b in ((l, mid), (mid + 1, r)):", "    child = (a + b) | (a != b)", "    cnt = b - a + 1", "    if sv is not None:"]
    b += indent(py_apply_assign("child", "cnt", "sv"), 2) + ["    else:"] + indent(py_apply_add("child", "cnt", "av"), 2)
    b += ["setTag[node] = None", "addTag[node] = 0"]
    py += indent(b, 2) + [""]

    def py_pull(node, left, right):
        out = []
        for a in A:
            out += a.py_merge(f"{a.arr}[{node}]", f"{a.arr}[{left}]", f"{a.arr}[{right}]")
        return out

    py += ["    # every given point inside the rectangle: assign v (isAssign) or add v", "    def _update(self, x1, y1, x2, y2, isAssign, v):"]
    b = ["xMin, xMax, yMin, yMax, setTag, addTag = self.xMin, self.xMax, self.yMin, self.yMax, self.setTag, self.addTag", f"{arrs} = {self_arrs}", "push = self._push", "",
         "def go(l, r):", "    node = (l + r) | (l != r)", "    if xMin[node] > x2 or xMax[node] < x1 or yMin[node] > y2 or yMax[node] < y1:", "        return",
         "    if x1 <= xMin[node] and xMax[node] <= x2 and y1 <= yMin[node] and yMax[node] <= y2:", "        cnt = r - l + 1", "        if isAssign:"]
    b += indent(py_apply_assign("node", "cnt", "v"), 3) + ["        else:"] + indent(py_apply_add("node", "cnt", "v"), 3)
    b += ["        return", "    push(node, l, r)", "    mid = (l + r) >> 1", "    go(l, mid)", "    go(mid + 1, r)", "    left = (l + mid) | (l != mid)", "    right = (mid + 1 + r) | (mid + 1 != r)"]
    b += indent(py_pull("node", "left", "right")) + ["", "go(0, self.n - 1)"]
    py += indent(b, 2) + [""]
    res_names = [f"res{a.cap}" for a in A]
    py += ["    # the aggregates over the given points inside the rectangle, and how many points that is", "    def _query(self, x1, y1, x2, y2):"]
    b = ["xMin, xMax, yMin, yMax = self.xMin, self.xMax, self.yMin, self.yMax", f"{arrs} = {self_arrs}", "push = self._push"]
    for a in A:
        b.append(f"res{a.cap} = {a.py_id}")
    b += ["count = 0", "stack = [(0, self.n - 1)]", "while stack:", "    l, r = stack.pop()", "    node = (l + r) | (l != r)",
          "    if xMin[node] > x2 or xMax[node] < x1 or yMin[node] > y2 or yMax[node] < y1:", "        continue",
          "    if x1 <= xMin[node] and xMax[node] <= x2 and y1 <= yMin[node] and yMax[node] <= y2:", "        count += r - l + 1"]
    for a in A:
        b += indent(a.py_take(f"res{a.cap}", f"{a.arr}[node]"), 2)
    b += ["        continue", "    push(node, l, r)", "    mid = (l + r) >> 1", "    stack.append((l, mid))", "    stack.append((mid + 1, r))", f"return {', '.join(res_names)}, count"]
    py += indent(b, 2) + [""]
    py += ["    # where point (x, y) sits in k-d order, with every tag above it handed down first", "    def _open(self, x, y, name):"]
    py += indent(["pts = self.pts", "i = bisect_left(pts, (x, y))", "if i == len(pts) or pts[i] != (x, y):",
                  '    raise IndexError(f"{name}: ({x}, {y}) is not one of the points given to the constructor")', "p = self.pos[i]", "push = self._push", "l = 0", "r = self.n - 1",
                  "while l < r:", "    push((l + r) | 1, l, r)", "    mid = (l + r) >> 1", "    if p <= mid:", "        r = mid", "    else:", "        l = mid + 1", "return p"], 2) + [""]
    py += ["    # the point at k-d position p becomes v, then every node above it", "    def _setLeaf(self, p, v):"]
    b = [f"{arrs} = {self_arrs}"] + [f"{a.arr}[2 * p] = v" for a in A]
    b += ["path = []", "l = 0", "r = self.n - 1", "while l < r:", "    path.append((l, r))", "    mid = (l + r) >> 1", "    if p <= mid:", "        r = mid", "    else:", "        l = mid + 1",
          "for l, r in reversed(path):", "    mid = (l + r) >> 1", "    node = (l + r) | 1", "    left = (l + mid) | (l != mid)", "    right = (mid + 1 + r) | (mid + 1 != r)"]
    b += indent(py_pull("node", "left", "right"))
    py += indent(b, 2) + [""]
    py.append(f"    # O(log N) -- the value at (x, y); {POINT_RULE_PY}")
    py += ["    def pointGet(self, x, y):", f'        return self.{rd.arr}[2 * self._open(x, y, "pointGet")]', ""]
    for name, text, lines in (
        ("pointAssign", "the point (x, y) becomes v", ["self._setLeaf(p, v)"]),
        ("pointAdd", "adds v to the point (x, y)", [f"self._setLeaf(p, self.{rd.arr}[2 * p] + v)"]),
        ("pointChmax", "the point (x, y) becomes max(itself, v)", [f"if v > self.{rd.arr}[2 * p]:", "    self._setLeaf(p, v)"]),
        ("pointChmin", "the point (x, y) becomes min(itself, v)", [f"if v < self.{rd.arr}[2 * p]:", "    self._setLeaf(p, v)"]),
    ):
        py += indent(wrap_comment(f"O(log N) -- {text}; {POINT_RULE_PY}", "#"))
        py += [f"    def {name}(self, x, y, v):", f'        p = self._open(x, y, "{name}")'] + indent(lines, 2) + [""]
    for name, text, flag in (("rectAdd", "adds v to every given point", "False"), ("rectAssign", "every given point becomes v, for the points", "True")):
        py += indent(wrap_comment(f"O(sqrt N) -- {text} with x1 <= x <= x2 and y1 <= y <= y2; {RECT_RULE_PY}", "#"))
        py.append(f"    def {name}(self, x1, y1, x2, y2, v):")
        py += indent(py_rect_check(name) + [f"self._update(x1, y1, x2, y2, {flag}, v)"], 2) + [""]
    for idx, a in enumerate(A):
        none = "None" if a.key in ("min", "max") else "0"
        py += indent(wrap_comment(f"O(sqrt N) -- {a.word} of the given points with x1 <= x <= x2 and y1 <= y <= y2 ({none} if no point is there); {RECT_RULE_PY}", "#"))
        py.append(f"    def {a.rect}(self, x1, y1, x2, y2):")
        body = ["res = self._query(x1, y1, x2, y2)"]
        body.append(f"return res[{idx}] if res[-1] else None" if a.key in ("min", "max") else f"return res[{idx}]")
        py += indent(py_rect_check(a.rect) + body, 2) + [""]
        py += [f"    # O(1) -- {a.word} of every point", f"    def {a.all}(self):", f"        return self.{a.arr}[(self.n - 1) | (self.n > 1)]", ""]
        if a.key in ("min", "max"):
            for n, xsn, ysn in CORNERS:
                bx = ("NEG", "x") if xsn == "<=" else ("x", "POS")
                by = ("NEG", "y") if ysn == "<=" else ("y", "POS")
                py += indent(wrap_comment(f"O(sqrt N) -- {a.word} of the given points with x {xsn} the given x and y {ysn} the given y (None if there are none); "
                                          f"any integers", "#"))
                py += [f"    def {a.key}{n}(self, x, y):", f"        res = self._query({bx[0]}, {by[0]}, {bx[1]}, {by[1]})", f"        return res[{idx}] if res[-1] else None", ""]
    while py[-1] == "":
        py.pop()

    # ------------------------------------------------------------------ C++
    none_cpp = " / ".join(a.none_cpp for a in A if a.key in ("min", "max"))
    cpp = wrap_comment(doc + (f" A min / max over a rectangle with no given point in it is {none_cpp}." if none_cpp else ""), "//")
    cpp.append("// T is any integer type (int, long long, ...)" + ("; sums are kept in S (long long for a smaller T)." if has["sum"] else ".") + " Coordinates are long long.")
    cpp += ["template <typename T>", f"struct {cls} {{", "    using ll = long long;"]
    if has["sum"]:
        cpp.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;")
    if has["max"]:
        cpp.append("    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no point gives")
    if has["min"]:
        cpp.append("    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no point gives")
    cpp += ["    static constexpr ll LOW = numeric_limits<ll>::min(), HIGH = numeric_limits<ll>::max();  // no bound on a coordinate", "    int n;", "    vector<pair<ll, ll>> pts;",
            "    vector<int> pos;  // pos[i]: where point i (in sorted order) sits in k-d order", "    vector<ll> xMin, xMax, yMin, yMax;", "    vector<T> addTag, setTag;", "    vector<char> hasSet;",
            "    unsigned long long seed = 1;  // for the random pivots of the build"]
    for a in A:
        cpp.append(f"    vector<{a.cpp_type}> {a.arr};")
    cpp += [""] + indent(wrap_comment("O(N log N) -- points: every (x, y) that will ever be used (negative is fine, repeats are fine); needs at least one, else throws "
                                      "invalid_argument", "//"))
    cpp += [f"    explicit {cls}(vector<pair<ll, ll>> points) : pts(std::move(points)) {{"]
    b = [f'if (pts.empty()) throw invalid_argument("{cls}: needs at least one point");', "sort(pts.begin(), pts.end());", "pts.erase(unique(pts.begin(), pts.end()), pts.end());",
         "n = (int)pts.size();", "size_t size = 2 * (size_t)n;", "xMin.assign(size, 0), xMax.assign(size, 0), yMin.assign(size, 0), yMax.assign(size, 0);", "pos.assign(n, 0);",
         "addTag.assign(size, T(0)), setTag.assign(size, T(0)), hasSet.assign(size, 0);"]
    for a in A:
        b.append(f"{a.arr}.assign(size, 0);")
    b += ["seed = chrono::steady_clock::now().time_since_epoch().count() | 1;", "vector<int> order(n);", "iota(order.begin(), order.end(), 0);",
          "buildNode(order.data(), 0, n - 1, 0);"]
    cpp += indent(b, 2) + ["    }", "", "    static int id(int l, int r) { return (l + r) | (l != r); }  // the number of the node for the stretch l..r of the k-d order", "",
                           "    // is point a before point b, by x then y (axis 0) or by y then x (axis 1)",
                           "    bool before(int a, int b, int axis) const {",
                           "        ll ka = axis ? pts[a].second : pts[a].first, kb = axis ? pts[b].second : pts[b].first;",
                           "        if (ka != kb) return ka < kb;",
                           "        return axis ? pts[a].first < pts[b].first : pts[a].second < pts[b].second;",
                           "    }",
                           "",
                           "    // rearranges order[l..r] so the point that belongs at position mid is there, with everything before it in front:",
                           "    // quickselect around random pivots (random so that no input can make it slow), expected O(r - l)",
                           "    void splitAt(int* order, int l, int r, int mid, int axis) {",
                           "        while (l < r) {",
                           "            seed ^= seed << 13, seed ^= seed >> 7, seed ^= seed << 17;",
                           "            int pivot = order[l + (int)(seed % (unsigned long long)(r - l + 1))], i = l, j = r;",
                           "            while (i <= j) {",
                           "                while (before(order[i], pivot, axis)) i++;",
                           "                while (before(pivot, order[j], axis)) j--;",
                           "                if (i <= j) {",
                           "                    int held = order[i];",
                           "                    order[i++] = order[j], order[j--] = held;",
                           "                }",
                           "            }",
                           "            if (mid <= j) r = j;",
                           "            else if (mid >= i) l = i;",
                           "            else return;",
                           "        }",
                           "    }",
                           "",
                           "    // order[l..r] holds this node's points: split them in half by x (axis 0) or by y, ties by the other coordinate",
                           "    void buildNode(int* order, int l, int r, int axis) {"]
    cpp += indent([
        "int node = id(l, r);",
        "ll loX = HIGH, hiX = LOW, loY = HIGH, hiY = LOW;",
        "for (int i = l; i <= r; i++) {",
        "    ll x = pts[order[i]].first, y = pts[order[i]].second;",
        "    if (x < loX) loX = x;",
        "    if (x > hiX) hiX = x;",
        "    if (y < loY) loY = y;",
        "    if (y > hiY) hiY = y;",
        "}",
        "xMin[node] = loX, xMax[node] = hiX, yMin[node] = loY, yMax[node] = hiY;",
        "if (l == r) {",
        "    pos[order[l]] = l;",
        "    return;",
        "}",
        "int mid = (l + r) >> 1;",
        "splitAt(order, l, r, mid, axis);",
        "buildNode(order, l, mid, axis ^ 1);",
        "buildNode(order, mid + 1, r, axis ^ 1);",
    ], 2) + ["    }", ""]
    cnt_param = "int cnt" if has["sum"] else "int"  # (how many points the node has: only a sum needs it)
    cpp += [f"    void applyAssign(int node, {cnt_param}, T v) {{", "        hasSet[node] = 1, setTag[node] = v, addTag[node] = 0;"]
    for a in A:
        cpp.append(f"        {a.arr}[node] = {'S(v) * cnt' if a.key == 'sum' else 'v'};")
    cpp += ["    }", "", f"    void applyAdd(int node, {cnt_param}, T v) {{", "        if (hasSet[node]) setTag[node] += v;", "        else addTag[node] += v;"]
    for a in A:
        cpp.append(f"        {a.arr}[node] += {'S(v) * cnt' if a.key == 'sum' else 'v'};")
    cpp += ["    }", "", "    // hands node (l, r)'s waiting assign / add to its two halves", "    void push(int node, int l, int r) {",
            "        if (!hasSet[node] && addTag[node] == 0) return;", "        int mid = (l + r) >> 1;",
            "        if (hasSet[node]) applyAssign(id(l, mid), mid - l + 1, setTag[node]), applyAssign(id(mid + 1, r), r - mid, setTag[node]);",
            "        else applyAdd(id(l, mid), mid - l + 1, addTag[node]), applyAdd(id(mid + 1, r), r - mid, addTag[node]);",
            "        hasSet[node] = 0, addTag[node] = 0;", "    }", "", "    void pull(int node, int l, int r) {", "        int mid = (l + r) >> 1, left = id(l, mid), right = id(mid + 1, r);"]
    for a in A:
        cpp.append(f"        {a.arr}[node] = {a.cpp_comb(f'{a.arr}[left]', f'{a.arr}[right]')};")
    cpp += ["    }", "", "    bool outside(int node, ll x1, ll y1, ll x2, ll y2) const {", "        return xMin[node] > x2 || xMax[node] < x1 || yMin[node] > y2 || yMax[node] < y1;", "    }", "",
            "    bool inside(int node, ll x1, ll y1, ll x2, ll y2) const {", "        return x1 <= xMin[node] && xMax[node] <= x2 && y1 <= yMin[node] && yMax[node] <= y2;", "    }", "",
            "    // every given point inside the rectangle: assign v (isAssign) or add v", "    void update(int l, int r, ll x1, ll y1, ll x2, ll y2, bool isAssign, T v) {",
            "        int node = id(l, r);", "        if (outside(node, x1, y1, x2, y2)) return;", "        if (inside(node, x1, y1, x2, y2)) {",
            "            if (isAssign) applyAssign(node, r - l + 1, v);", "            else applyAdd(node, r - l + 1, v);", "            return;", "        }", "        push(node, l, r);",
            "        int mid = (l + r) >> 1;", "        update(l, mid, x1, y1, x2, y2, isAssign, v);", "        update(mid + 1, r, x1, y1, x2, y2, isAssign, v);", "        pull(node, l, r);", "    }", ""]
    for a in A:
        t = a.cpp_type
        cpp += [f"    void {a.key}Over(int l, int r, ll x1, ll y1, ll x2, ll y2, {t}& res) {{", "        int node = id(l, r);", "        if (outside(node, x1, y1, x2, y2)) return;",
                "        if (inside(node, x1, y1, x2, y2)) {", "            " + a.cpp_take("res", f"{a.arr}[node]"), "            return;", "        }", "        push(node, l, r);",
                "        int mid = (l + r) >> 1;", f"        {a.key}Over(l, mid, x1, y1, x2, y2, res);", f"        {a.key}Over(mid + 1, r, x1, y1, x2, y2, res);", "    }", "",
                f"    {t} {a.key}Of(ll x1, ll y1, ll x2, ll y2) {{", f"        {t} res = {a.cpp_id};", f"        {a.key}Over(0, n - 1, x1, y1, x2, y2, res);", "        return res;", "    }", ""]
    cpp += ["    // where point (x, y) sits in k-d order, with every tag above it handed down first", "    int open(ll x, ll y, const char* name) {",
            "        auto it = lower_bound(pts.begin(), pts.end(), make_pair(x, y));", "        if (it == pts.end() || *it != make_pair(x, y))",
            '            throw out_of_range(string(name) + ": (x, y) is not one of the points given to the constructor");', "        int p = pos[it - pts.begin()];",
            "        for (int l = 0, r = n - 1; l < r;) {", "            push(id(l, r), l, r);", "            int mid = (l + r) >> 1;", "            if (p <= mid) r = mid;", "            else l = mid + 1;", "        }",
            "        return p;", "    }", "", "    // the point at k-d position p becomes v, then every node above it", "    void setLeaf(int l, int r, int p, T v) {", "        if (l == r) {"]
    for a in A:
        cpp.append(f"            {a.arr}[id(l, r)] = v;")
    cpp += ["            return;", "        }", "        int mid = (l + r) >> 1;", "        if (p <= mid) setLeaf(l, mid, p, v);", "        else setLeaf(mid + 1, r, p, v);", "        pull(id(l, r), l, r);", "    }", ""]
    cpp.append(f"    // O(log N) -- the value at (x, y); {POINT_RULE_CPP}")
    cpp += ["    T pointGet(ll x, ll y) {", f'        return T({rd.arr}[2 * open(x, y, "pointGet")]);', "    }", ""]
    for name, text, body in (
        ("pointAssign", "the point (x, y) becomes v", "setLeaf(0, n - 1, p, v);"),
        ("pointAdd", "adds v to the point (x, y)", f"setLeaf(0, n - 1, p, T({rd.arr}[2 * p] + v));"),
        ("pointChmax", "the point (x, y) becomes max(itself, v)", f"if (v > T({rd.arr}[2 * p])) setLeaf(0, n - 1, p, v);"),
        ("pointChmin", "the point (x, y) becomes min(itself, v)", f"if (v < T({rd.arr}[2 * p])) setLeaf(0, n - 1, p, v);"),
    ):
        cpp += indent(wrap_comment(f"O(log N) -- {text}; {POINT_RULE_CPP}", "//"))
        cpp += [f"    void {name}(ll x, ll y, T v) {{", f'        int p = open(x, y, "{name}");', "        " + body, "    }", ""]
    for name, text, flag in (("rectAdd", "adds v to every given point", "false"), ("rectAssign", "every given point becomes v, for the points", "true")):
        cpp += indent(wrap_comment(f"O(sqrt N) -- {text} with x1 <= x <= x2 and y1 <= y <= y2; {RECT_RULE_CPP}", "//"))
        cpp.append(f"    void {name}(ll x1, ll y1, ll x2, ll y2, T v) {{")
        cpp += indent(cpp_rect_check(name) + [f"update(0, n - 1, x1, y1, x2, y2, {flag}, v);"], 2) + ["    }", ""]
    for a in A:
        t = a.cpp_type
        none = a.none_cpp if a.key in ("min", "max") else "0"
        cpp += indent(wrap_comment(f"O(sqrt N) -- {a.word} of the given points with x1 <= x <= x2 and y1 <= y <= y2 ({none} if no point is there); {RECT_RULE_CPP}", "//"))
        cpp.append(f"    {t} {a.rect}(ll x1, ll y1, ll x2, ll y2) {{")
        cpp += indent(cpp_rect_check(a.rect) + [f"return {a.key}Of(x1, y1, x2, y2);"], 2) + ["    }", ""]
        cpp += [f"    // O(1) -- {a.word} of every point", f"    {t} {a.all}() const {{", f"        return {a.arr}[id(0, n - 1)];", "    }", ""]
        if a.key in ("min", "max"):
            for n, xsn, ysn in CORNERS:
                bx = ("LOW", "x") if xsn == "<=" else ("x", "HIGH")
                by = ("LOW", "y") if ysn == "<=" else ("y", "HIGH")
                cpp += indent(wrap_comment(f"O(sqrt N) -- {a.word} of the given points with x {xsn} the given x and y {ysn} the given y ({a.none_cpp} if there are none); "
                                           f"any integers", "//"))
                cpp += [f"    T {a.key}{n}(ll x, ll y) {{", f"        return {a.key}Of({bx[0]}, {by[0]}, {bx[1]}, {by[1]});", "    }", ""]
    while cpp[-1] == "":
        cpp.pop()
    cpp.append("};")
    args = (ops, "kd-tree", costs, "N*log(N)", memory, "points", [])
    folder = "points-kd-tree-" + "-".join(aggs)
    write(folder, header(folder, "py", *args) + py, header(folder, "cpp", *args) + cpp)


def main():
    for aggs in subsets(["sum", "min", "max"]):
        kd_tree(aggs)
    print("kd tree: 7 folders")


if __name__ == "__main__":
    main()
