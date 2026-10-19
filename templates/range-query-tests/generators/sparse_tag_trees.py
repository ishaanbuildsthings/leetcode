"""Sparse (dynamic) versions of the range-update + point-query trees: sparse.py + sparse.cpp per folder.

    python3 sparse_tag_trees.py

Every position of [lo, hi] starts at 0 and only nodes that updates reach exist.
  Tag trees (chmax, chmin, and=, or=, floor div, floor sqrt, mult mod): internal nodes hold a pending tag, leaves
    hold values. The tags commute, so range updates never push; pointGet folds the tags on the leaf's path. A point
    write first pushes the tags on its own path down (creating the path's siblings) so they stop applying to it.
  rangeAssign: every node remembers the last assignment covering it and its timestamp; the newest on a path wins.
  rangeMod: a max tree; rangeMod descends only into nodes whose max is >= mod (a missing node is all zeros).
  C++:    nodes in one pool shared by every tree of the type; resetPool() between test cases.
  Python: a dict keyed by heap index over a power-of-two cover of [lo, hi].
"""
import os

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
PLAIN = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
MOD_POINT = ["pointAdd", "pointAssign", "pointGet"]


def header(cm, ops, comp, mem, note):
    lines = [f"{cm} @operations: {' '.join(ops)}", f"{cm} @data-structure-type: seg-tree", f"{cm} @complexities:"]
    lines += [f"{cm}   {o}: {comp.get(o, 'log(U)')}" for o in ops] + [f"{cm}   build: 1"]
    node, tags, other = mem
    lines += [f"{cm} @memory:", f"{cm}   layout: sparse", f"{cm}   node: {node}", f"{cm}   tags: {tags}",
              f"{cm}   other: {other}", f"{cm}   note: {note}"]
    return "\n".join(lines) + "\n"


def write(ops, comp, mem, note, py, cpp):
    ops = sorted(ops)
    folder = "-".join(ops)
    path = os.path.join(DIR, folder)
    assert os.path.isdir(path), folder
    open(os.path.join(path, "sparse.py"), "w").write(header("#", ops, comp, mem, note) + py)
    open(os.path.join(path, "sparse.cpp"), "w").write(header("//", ops, comp, mem, note) + cpp)
    print("wrote", folder)


TAG_MEM = ("none", "tag[4*log(U)]", "links[8*log(U)]")
TAG_NOTE = ("per update, the nodes a range update visits (at most 4 per level; a point write creates its path and "
            "the path's siblings); a node's one field is its pending tag, or at a leaf its value. C++: one shared "
            "node pool, call resetPool() between test cases; Python: a dict keyed by heap index")

CPP_POOL = '''    struct Node {{ T v; int l, r; }};  // internal node: pending tag ({ident} = none); leaf: value
    static inline vector<Node> pool{{Node{{}}}};  // node 0 is never used: a 0 link means "not created yet"
    long long lo, hi;
    int root;{members}

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    {name}(long long lo, long long hi{ctor_args}) : lo(lo), hi(hi){ctor_init} {{ root = make(lo == hi); }}

    // O(1) -- forget every node of every {name}<T>; call between test cases, then build new trees
    static void resetPool() {{ pool.resize(1); }}

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) {{ pool.reserve(nodes); }}

    static int make(bool leaf) {{
        pool.push_back(Node{{leaf ? T(0) : {ident}, 0, 0}});
        return (int)pool.size() - 1;
    }}

    // child of x (creating it if missing); leaf: whether the child is a single position
    static int kid(int x, bool right, bool leaf) {{
        int y = right ? pool[x].r : pool[x].l;
        if (!y) {{
            y = make(leaf);
            (right ? pool[x].r : pool[x].l) = y;
        }}
        return y;
    }}
'''


def tag_tree(ops, name, desc, ident_py, ident_cpp, compose_py, leaf_py, compose_cpp, leaf_cpp, update_op, update_desc,
             update_arg="v", py_pre="", cpp_pre="", cpp_helpers="", guard_py="", guard_cpp="", mod=False, comp=None,
             note=""):
    """compose_*: the tag `a` followed by the tag `v`; leaf_*: the value `a` after the tag `v`. Every tag here
    commutes with the others. update_arg None: the update takes no argument and applies the tag 1."""
    arg_py = f", {update_arg}" if update_arg else ""
    arg_cpp = f", T {update_arg}" if update_arg else ""
    val = update_arg or "1"
    norm_py = " % self.mod" if mod else ""
    py_points = f'''
    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        p = self.size + i - self.lo
        self._push(p)
        self.t[p] = val{norm_py}

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        p = self.size + i - self.lo
        self._push(p)
        t = self.t
        t[p] = (t.get(p, 0) + delta){norm_py}
'''
    if not mod:
        py_points += '''
    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        p = self.size + i - self.lo
        self._push(p)
        t = self.t
        if val > t.get(p, 0):
            t[p] = val

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        p = self.size + i - self.lo
        self._push(p)
        t = self.t
        if val < t.get(p, 0):
            t[p] = val
'''
    py = f'''{py_pre}
# {desc}, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# Internal nodes hold a pending tag, leaves hold values. The tags commute, so a range update just tags its
# O(logU) covering nodes and pointGet folds the tags on the leaf's root path. A point write first pushes the tags
# on its path down, so they stop applying to it. Sparse: a dict keyed by heap index over a power-of-two cover of
# [lo, hi]; a missing internal node has no tag, a missing leaf is 0.


class {name}:
    __slots__ = ("lo", "size", "t"{', "mod"' if mod else ""})

    # O(1)
    def __init__(self, lo, hi{", mod=1000000007" if mod else ""}):
        self.lo = lo
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of i is size + (i - lo)
        self.t = {{}}{chr(10) + "        self.mod = mod" if mod else ""}

    # node x takes tag v (a leaf into its value)
    def _apply(self, x, v):
        t = self.t
        if x >= self.size:
            a = t.get(x, 0)
            t[x] = {leaf_py}
        else:
            a = t.get(x, {ident_py})
            t[x] = {compose_py}

    # O(logU) -- {update_desc} for i in [l, r]
    def {update_op}(self, l, r{arg_py}):{guard_py}
        l += self.size - self.lo
        r += self.size - self.lo + 1
        while l < r:
            if l & 1:
                self._apply(l, {val})
                l += 1
            if r & 1:
                r -= 1
                self._apply(r, {val})
            l >>= 1
            r >>= 1

    # O(logU) -- move the tags on leaf p's root path down, so none of them is pending above p
    def _push(self, p):
        t = self.t
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            v = t.pop(x, None)
            if v is not None and v != {ident_py}:
                self._apply(2 * x, v)
                self._apply(2 * x + 1, v)

    # O(logU) -- a[i]
    def pointGet(self, i):
        t = self.t
        p = self.size + i - self.lo
        x = t.get(p, 0)
        a = {ident_py}  # the tags on the path, composed
        p >>= 1
        while p:
            v = t.get(p)
            if v is not None:
                a = {compose_py}
            p >>= 1
        a, v = x, a
        return {leaf_py}
''' + py_points

    cpp_points = f'''
    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {{
        int p = push(i);
        pool[p].v = {"norm(v)" if mod else "v"};
    }}

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) {{
        int p = push(i);
        pool[p].v = {"norm(W(pool[p].v) + delta)" if mod else "pool[p].v + delta"};
    }}
'''
    if not mod:
        cpp_points += '''
    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) {
        int p = push(i);
        if (v > pool[p].v) pool[p].v = v;
    }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) {
        int p = push(i);
        if (v < pool[p].v) pool[p].v = v;
    }
'''
    pool = CPP_POOL.format(ident=ident_cpp, name=name, members="\n    T mod;" if mod else "",
                           ctor_args=", T mod = 1000000007" if mod else "", ctor_init=", mod(mod)" if mod else "")
    cpp = f'''
// {desc}, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
// Internal nodes hold a pending tag, leaves hold values. The tags commute, so a range update just tags its
// O(logU) covering nodes and pointGet folds the tags on the leaf's root path. A point write first pushes the tags
// on its path down, so they stop applying to it. Sparse: nodes exist only where updates reached, in one pool
// shared by every {name}<T>.{cpp_pre} T: int, long long, ...
template <typename T>
struct {name} {{
{pool}{cpp_helpers}
    T compose(T a, T v) const {{ return {compose_cpp}; }}  // tag a, then tag v
    T leaf(T a, T v) const {{ return {leaf_cpp}; }}  // value a after tag v

    void apply(int x, bool isLeaf, T v) {{ pool[x].v = isLeaf ? leaf(pool[x].v, v) : compose(pool[x].v, v); }}

    void update(int x, long long a, long long b, long long l, long long r, T v) {{
        if (l <= a && b <= r) {{ apply(x, a == b, v); return; }}
        long long m = a + (b - a) / 2;
        if (l <= m) update(kid(x, false, a == m), a, m, l, r, v);
        if (r > m) update(kid(x, true, m + 1 == b), m + 1, b, l, r, v);
    }}

    // O(logU) -- {update_desc} for i in [l, r]
    void {update_op}(long long l, long long r{arg_cpp}) {{{guard_cpp}
        if (l <= r) update(root, lo, hi, l, r, {val if update_arg else "T(1)"});
    }}

    // O(logU) -- move the tags on i's root path down (creating the path's siblings); returns i's leaf
    int push(long long i) {{
        int y = root;
        long long a = lo, b = hi;
        while (a < b) {{
            long long m = a + (b - a) / 2;
            T t = pool[y].v;
            if (t != {ident_cpp}) {{
                apply(kid(y, false, a == m), a == m, t);
                apply(kid(y, true, m + 1 == b), m + 1 == b, t);
                pool[y].v = {ident_cpp};
            }}
            if (i <= m) y = kid(y, false, a == m), b = m;
            else y = kid(y, true, m + 1 == b), a = m + 1;
        }}
        return y;
    }}

    // O(logU) -- a[i]
    T pointGet(long long i) const {{
        T t = {ident_cpp}, x = 0;
        int y = root;
        long long a = lo, b = hi;
        while (y) {{
            if (a == b) {{ x = pool[y].v; break; }}
            t = compose(t, pool[y].v);
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else y = pool[y].r, a = m + 1;
        }}
        return leaf(x, t);
    }}
{cpp_points}}};
'''
    write(ops, comp or {}, TAG_MEM, note + TAG_NOTE, py, cpp)


tag_tree(PLAIN + ["rangeChmax"], "SparseRangeChmaxTree", "Range chmax + point ops", "NEG", "numeric_limits<T>::lowest()",
         "a if a > v else v", "a if a > v else v", "max(a, v)", "max(a, v)", "rangeChmax", "a[i] = max(a[i], v)",
         py_pre='\nNEG = float("-inf")\n')
tag_tree(PLAIN + ["rangeChmin"], "SparseRangeChminTree", "Range chmin + point ops", "INF", "numeric_limits<T>::max()",
         "a if a < v else v", "a if a < v else v", "min(a, v)", "min(a, v)", "rangeChmin", "a[i] = min(a[i], v)",
         py_pre='\nINF = float("inf")\n')
tag_tree(PLAIN + ["rangeAndApply"], "SparseRangeAndTree", "Range and= + point ops", "-1", "T(-1)",
         "a & v", "a & v", "a & v", "a & v", "rangeAndApply", "a[i] &= v")
tag_tree(PLAIN + ["rangeOrApply"], "SparseRangeOrTree", "Range or= + point ops", "0", "T(0)",
         "a | v", "a | v", "a | v", "a | v", "rangeOrApply", "a[i] |= v")
tag_tree(PLAIN + ["rangeFloorDiv"], "SparseRangeFloorDivTree",
         "Range floor-divide + point ops (divisors >= 1, values may be negative)", "1", "T(1)",
         "a * v if a * v < CAP else CAP", "a // v", "mulCap(a, v)", "floorDiv(a, v)", "rangeFloorDiv",
         "a[i] = floor(a[i] / v), v >= 1",
         py_pre="\nCAP = 1 << 62  # a pending divisor past every |value| floors everything to 0 or -1, so cap the product\n",
         cpp_pre="\n// floor(floor(x / a) / b) == floor(x / (a * b)), so pending divisors multiply; products are capped at\n"
                 "// CAP = max(T), past which every |value| < CAP floors to 0 or -1.",
         cpp_helpers='''
    static constexpr T CAP = numeric_limits<T>::max();
    static T floorDiv(T x, T d) { T q = x / d; return (x % d != 0 && x < 0) ? q - 1 : q; }
    static T mulCap(T a, T b) { return a > CAP / b ? CAP : a * b; }
''',
         guard_py="\n        if v == 1:\n            return", guard_cpp="\n        if (v == 1) return;",
         note="a pending divisor is the product of the divisions, capped; ")
tag_tree(PLAIN + ["rangeFloorSqrt"], "SparseRangeFloorSqrtTree", "Range floor-sqrt + point ops (values >= 0)", "0",
         "T(0)", "a + v if a + v < MAX_SQRTS else MAX_SQRTS", "_sqrts(a, v)", "min(a + v, MAX_SQRTS)",
         "sqrtTimes(a, v)", "rangeFloorSqrt", "a[i] = floor(sqrt(a[i]))", update_arg=None,
         py_pre='''
from math import isqrt

MAX_SQRTS = 6  # six floor-sqrts take any value below 2^64 to 0 or 1, which are fixed points


def _sqrts(x, k):  # x after k floor-sqrts
    while k and x > 1:
        x = isqrt(x)
        k -= 1
    return x
''',
         cpp_pre="\n// A pending tag counts floor-sqrts, capped at 6 (six take any value below 2^64 to 0 or 1, fixed points).",
         cpp_helpers='''
    static constexpr T MAX_SQRTS = 6;
    static T isqrt(T x) {
        T r = (T)sqrtl((long double)x);
        while ((__int128)r * r > x) r--;
        while ((__int128)(r + 1) * (r + 1) <= x) r++;
        return r;
    }
    static T sqrtTimes(T v, T k) {
        for (; k > 0 && v > 1; k--) v = isqrt(v);
        return v;
    }
''',
         note="a pending tag counts floor-sqrts (at most 6 isqrts per point op); ")
tag_tree(MOD_POINT + ["rangeMultMod"], "SparseRangeMultModTree", "rangeMultMod + point ops (values in [0, mod))", "1",
         "T(1)", "a * v % self.mod", "a * v % self.mod", "T(W(a) * v % mod)", "T(W(a) * v % mod)", "rangeMultMod",
         "a[i] = a[i] * v (mod p)", mod=True,
         guard_py="\n        v %= self.mod", guard_cpp="\n        v = norm(v);",
         cpp_helpers='''
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    T norm(W x) const { return T((x % mod + mod) % mod); }
''')


# ---------------------------------------------------------------- rangeAssign: timestamps, no pushing anywhere

ASSIGN_PY = '''
# Range assign + point ops over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# No pushing anywhere: assignments are stamped with an increasing counter, every node remembers the newest one
# covering it, and pointGet returns the newest on the leaf's root path. A point write is a newer stamp on the leaf,
# so it is O(1). Sparse: a dict keyed by heap index over a power-of-two cover of [lo, hi] -> (stamp, value).


class SparseRangeAssignTree:
    __slots__ = ("lo", "size", "t", "clock")

    # O(1)
    def __init__(self, lo, hi):
        self.lo = lo
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of i is size + (i - lo)
        self.t = {}
        self.clock = 0

    # O(logU) -- a[i] = val for i in [l, r]
    def rangeAssign(self, l, r, val):
        self.clock += 1
        e = (self.clock, val)
        t = self.t
        l += self.size - self.lo
        r += self.size - self.lo + 1
        while l < r:
            if l & 1:
                t[l] = e
                l += 1
            if r & 1:
                r -= 1
                t[r] = e
            l >>= 1
            r >>= 1

    # O(logU) -- a[i]
    def pointGet(self, i):
        t = self.t
        p = self.size + i - self.lo
        best, res = t.get(p, (0, 0))
        p >>= 1
        while p:
            e = t.get(p)
            if e is not None and e[0] > best:
                best, res = e
            p >>= 1
        return res

    # O(1) -- a[i] = val
    def pointAssign(self, i, val):
        self.clock += 1
        self.t[self.size + i - self.lo] = (self.clock, val)

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
'''

ASSIGN_CPP = '''
// Range assign + point ops over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
// No pushing anywhere: assignments are stamped with an increasing counter, every node remembers the newest one
// covering it, and pointGet returns the newest on the leaf's root path. Sparse: nodes exist only where updates
// reached, in one pool shared by every SparseRangeAssignTree<T>. T: int, long long, ...
template <typename T>
struct SparseRangeAssignTree {
    struct Node { int stamp; T v; int l, r; };  // the newest assignment covering the node (stamp 0: none)
    static inline vector<Node> pool{Node{}};  // node 0 is never used: a 0 link means "not created yet"
    long long lo, hi;
    int root, clock = 0;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeAssignTree(long long lo, long long hi) : lo(lo), hi(hi) { root = make(); }

    // O(1) -- forget every node of every SparseRangeAssignTree<T>; call between test cases, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make() {
        pool.push_back(Node{0, T(0), 0, 0});
        return (int)pool.size() - 1;
    }

    // child of x, creating it if missing
    static int kid(int x, bool right) {
        int y = right ? pool[x].r : pool[x].l;
        if (!y) {
            y = make();
            (right ? pool[x].r : pool[x].l) = y;
        }
        return y;
    }

    void update(int x, long long a, long long b, long long l, long long r, int c, T v) {
        if (l <= a && b <= r) { pool[x].stamp = c, pool[x].v = v; return; }
        long long m = a + (b - a) / 2;
        if (l <= m) update(kid(x, false), a, m, l, r, c, v);
        if (r > m) update(kid(x, true), m + 1, b, l, r, c, v);
    }

    // O(logU) -- a[i] = v for i in [l, r]
    void rangeAssign(long long l, long long r, T v) {
        if (l <= r) update(root, lo, hi, l, r, ++clock, v);
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        int y = root, best = 0;
        T res = 0;
        long long a = lo, b = hi;
        while (y) {
            if (pool[y].stamp > best) best = pool[y].stamp, res = pool[y].v;
            if (a == b) break;
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else y = pool[y].r, a = m + 1;
        }
        return res;
    }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        int y = root;
        long long a = lo, b = hi;
        while (a < b) {
            long long m = a + (b - a) / 2;
            if (i <= m) y = kid(y, false), b = m;
            else y = kid(y, true), a = m + 1;
        }
        pool[y].stamp = ++clock, pool[y].v = v;
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
'''
write(PLAIN + ["rangeAssign"], {}, ("none", "stamp[4*log(U)] val[4*log(U)]", "links[8*log(U)]"),
      "per update, the nodes a range update visits (at most 4 per level), each remembering the newest assignment "
      "covering it; Python stores only the covering nodes (point assign is O(1) there). C++: one shared node pool, "
      "call resetPool() between test cases; Python: a dict keyed by heap index", ASSIGN_PY, ASSIGN_CPP)


# ---------------------------------------------------------------- rangeMod: a max tree that descends

MOD_PY = '''
# Range mod + point ops over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# Requires a[i] >= 0, mod >= 1. Mods don't compose into one tag, so rangeMod descends into every covering node
# whose max is still >= mod; each value that changes at least halves, so the work is amortized. Sparse: a dict
# keyed by heap index over a power-of-two cover of [lo, hi]; a missing node is all zeros, so rangeMod never
# enters one.


class SparseRangeModTree:
    __slots__ = ("lo", "size", "mx")

    # O(1)
    def __init__(self, lo, hi):
        self.lo = lo
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of i is size + (i - lo)
        self.mx = {}  # heap index -> max of the subtree (missing: 0)

    # O(logU) -- recompute the maxes on leaf p's root path
    def _pull(self, p):
        mx = self.mx
        p >>= 1
        while p:
            a = mx.get(2 * p, 0)
            b = mx.get(2 * p + 1, 0)
            mx[p] = a if a > b else b
            p >>= 1

    def _descend(self, top, mod):
        mx, size = self.mx, self.size
        stack, inner = [top], []
        while stack:
            y = stack.pop()
            if mx.get(y, 0) < mod:
                continue
            if y >= size:
                mx[y] %= mod
            else:
                inner.append(y)
                stack.append(2 * y)
                stack.append(2 * y + 1)
        for y in reversed(inner):  # pre-order reversed puts every child before its parent
            a = mx.get(2 * y, 0)
            b = mx.get(2 * y + 1, 0)
            mx[y] = a if a > b else b

    # amortized O(logU logV) -- a[i] %= mod for i in [l, r]
    def rangeMod(self, l, r, mod):
        if l > r:
            return
        l += self.size - self.lo
        r += self.size - self.lo
        lo, hi = l, r + 1
        while lo < hi:
            if lo & 1:
                self._descend(lo, mod)
                lo += 1
            if hi & 1:
                hi -= 1
                self._descend(hi, mod)
            lo >>= 1
            hi >>= 1
        self._pull(l)
        self._pull(r)

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.mx.get(self.size + i - self.lo, 0)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        p = self.size + i - self.lo
        self.mx[p] = val
        self._pull(p)

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
'''

MOD_CPP = '''
// Range mod + point ops over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
// Requires a[i] >= 0, mod >= 1. Mods don't compose into one tag, so rangeMod descends into every node in range
// whose max is still >= mod; each value that changes at least halves, so the work is amortized. Sparse: nodes in
// one pool shared by every SparseRangeModTree<T>; node 0 is the shared all-zeros block, which rangeMod never enters.
// T: int, long long, ...
template <typename T>
struct SparseRangeModTree {
    struct Node { T mx; int l, r; };  // max of the subtree
    static inline vector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root = 0;
    int path[130];

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeModTree(long long lo, long long hi) : lo(lo), hi(hi) {}

    // O(1) -- forget every node of every SparseRangeModTree<T>; call between test cases, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make() {
        pool.push_back(Node{T(0), 0, 0});
        return (int)pool.size() - 1;
    }

    void pull(int x) { pool[x].mx = max(pool[pool[x].l].mx, pool[pool[x].r].mx); }

    void modRec(int x, long long a, long long b, long long l, long long r, T mod) {
        if (pool[x].mx < mod) return;  // includes node 0
        if (a == b) { pool[x].mx %= mod; return; }
        long long m = a + (b - a) / 2;
        if (l <= m) modRec(pool[x].l, a, m, l, r, mod);
        if (r > m) modRec(pool[x].r, m + 1, b, l, r, mod);
        pull(x);
    }

    // amortized O(logU logV) -- a[i] %= mod for i in [l, r]
    void rangeMod(long long l, long long r, T mod) {
        if (l <= r) modRec(root, lo, hi, l, r, mod);
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        int y = root;
        long long a = lo, b = hi;
        while (y && a < b) {
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else y = pool[y].r, a = m + 1;
        }
        return pool[y].mx;
    }

    // O(logU) -- create i's path (path[0] = root), returns its depth
    int descend(long long i) {
        if (!root) root = make();
        int y = root, d = 0;
        path[0] = y;
        long long a = lo, b = hi;
        while (a < b) {
            long long m = a + (b - a) / 2;
            bool right = i > m;
            int c = right ? pool[y].r : pool[y].l;
            if (!c) {
                c = make();
                (right ? pool[y].r : pool[y].l) = c;
            }
            y = path[++d] = c;
            if (right) a = m + 1;
            else b = m;
        }
        return d;
    }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        int d = descend(i);
        pool[path[d]].mx = v;
        while (d--) pull(path[d]);
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
'''
write(PLAIN + ["rangeMod"], {"rangeMod": "log(U)*log(U) amortized"}, ("mx[1*log(U)]", "none", "links[2*log(U)]"),
      "per point write, one node per level of its path (rangeMod creates nothing); rangeMod's second log is of the "
      "largest value. C++: one shared node pool (node 0 = all zeros), call resetPool() between test cases; Python: a "
      "dict keyed by heap index, a missing key is a block of zeros", MOD_PY, MOD_CPP)
