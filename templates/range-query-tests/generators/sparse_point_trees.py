"""Sparse (dynamic) versions of the point-update / range-query segment trees: sparse.py + sparse.cpp per folder.

    python3 sparse_point_trees.py

Every position of [lo, hi] starts at 0 and only the paths that updates touch exist.
  C++:    nodes {aggregate, left, right} in one pool shared by every tree of the type; node 0 is the shared
          "all zeros" block, so a missing child needs no special case. Tree::resetPool() between test cases is
          O(1) and keeps the memory. Point updates walk down (creating the path) then recompute it bottom-up.
  Python: a dict keyed by heap index over a power-of-two cover of [lo, hi]; a missing key is a block of zeros.
          The loops are the same bottom-up loops as the dense templates.
Most aggregates of a block of zeros don't depend on its length; the ones that do (longest equal run, max
alternating sum) build a missing node's value from its length.
"""
import os

from note_lang import write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]


def header(cm, ops, comp, node, note):
    lines = [f"{cm} @operations: {' '.join(ops)}", f"{cm} @data-structure-type: seg-tree", f"{cm} @complexities:"]
    lines += [f"{cm}   {o}: {comp.get(o, 'log(U)')}" for o in ops] + [f"{cm}   build: 1"]
    lines += [f"{cm} @memory:", f"{cm}   layout: sparse", f"{cm}   node: {node}", f"{cm}   tags: none",
              f"{cm}   other: children[2*log(U)]",
              f"{cm}   note: per update, one node per level of the touched path; {note} "
              "C++: one shared node pool (node 0 = all zeros), call resetPool() between test cases; "
              "Python: a dict keyed by heap index, a missing key is a block of zeros"]
    return "\n".join(lines) + "\n"


def write(folder, ops, comp, node, note, py, cpp):
    ops = sorted(ops)
    assert "-".join(ops) == folder.split("__")[0], (folder, ops)
    path = os.path.join(DIR, folder)
    assert os.path.isdir(path), folder
    write_template(os.path.join(path, "sparse.py"), header("#", ops, comp, node, note) + py)
    write_template(os.path.join(path, "sparse.cpp"), header("//", ops, comp, node, note) + cpp)
    print("wrote", folder)


PY_POINT_OPS = '''
    # O(logU) -- a[i]
    def pointGet(self, i):
        return {get}

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

CPP_POINT_OPS = '''
    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
'''

# shared C++ pool plumbing; {name} {agg} {zero} are filled in
CPP_POOL = '''    struct Node {{ {agg} v; int l, r; }};
    static inline vector<Node> pool{{Node{{{zero}, 0, 0}}}};  // node 0: the shared all-zeros block
    long long lo, hi;
    int root = 0;

    // O(1) -- an all-zero array over [lo, hi]; any long long range works
    {name}(long long lo, long long hi) : lo(lo), hi(hi) {{}}

    // O(1) -- forget every node of every {name}; call once per test case, then build new trees
    static void resetPool() {{ pool.resize(1); }}

    // optional: reserve room for this many nodes up front (about log U per update)
    static void reservePool(size_t nodes) {{ pool.reserve(nodes); }}

    static int make() {{
        pool.push_back(Node{{{zero}, 0, 0}});
        return (int)pool.size() - 1;
    }}

    // walk from the root to leaf i, creating missing nodes; fills path[] with the nodes above the leaf and
    // returns the leaf. len[] / starts[] (when given) receive each path node's range.
    int descend(long long i, int* path, int& depth, long long* starts = nullptr, long long* ends = nullptr) {{
        if (!root) root = make();
        int x = root;
        long long a = lo, b = hi;
        depth = 0;
        while (a < b) {{
            if (starts) starts[depth] = a, ends[depth] = b;
            path[depth++] = x;
            long long m = a + (b - a) / 2;
            if (i <= m) {{
                if (!pool[x].l) {{ int y = make(); pool[x].l = y; }}
                x = pool[x].l, b = m;
            }} else {{
                if (!pool[x].r) {{ int y = make(); pool[x].r = y; }}
                x = pool[x].r, a = m + 1;
            }}
        }}
        return x;
    }}

    // O(logU) -- the leaf for i, or 0 if no update has touched it
    int find(long long i) const {{
        int x = root;
        long long a = lo, b = hi;
        while (x && a < b) {{
            long long m = a + (b - a) / 2;
            if (i <= m) x = pool[x].l, b = m;
            else x = pool[x].r, a = m + 1;
        }}
        return x;
    }}
'''


# ------------------------------------------------------------------ commutative scalar folds: sum, max, gcd
def scalar(folder, query_op, name, desc, py_merge, py_identity, cpp_merge, cpp_identity, cpp_agg, comp_extra=None,
           py_imports="", note="", py_leaf="val", cpp_leaf="S(v)"):
    ops = POINT + [query_op]
    comp = {o: "log(U)" for o in ops}
    comp.update(comp_extra or {})
    py = f'''{py_imports}
# {desc}, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# Sparse: a dict keyed by heap index over a power-of-two cover of [lo, hi]; a missing key is a block of zeros,
# so only the log U nodes on each updated path exist. Same bottom-up loops as the dense tree.


class {name}:
    __slots__ = ("lo", "size", "t")

    # O(1)
    def __init__(self, lo, hi):
        self.lo = lo
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; leaf of i is size + (i - lo)
        self.t = {{}}

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        t = self.t
        p = self.size + i - self.lo
        t[p] = {py_leaf}
        p >>= 1
        while p:
            a, b = t.get(2 * p, 0), t.get(2 * p + 1, 0)
            t[p] = {py_merge}
            p >>= 1

    # O(logU) -- fold of a[l..r]
    def {query_op}(self, l, r):
        t, res = self.t, {py_identity}
        l += self.size - self.lo
        r += self.size - self.lo + 1
        while l < r:
            if l & 1:
                a, b = res, t.get(l, 0)
                res = {py_merge}
                l += 1
            if r & 1:
                r -= 1
                a, b = res, t.get(r, 0)
                res = {py_merge}
            l >>= 1
            r >>= 1
        return res
''' + PY_POINT_OPS.format(get="self.t.get(self.size + i - self.lo, 0)")
    cpp = f'''
// {desc}, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
// Sparse: only the nodes on updated paths exist, in one pool shared by every {name}; node 0 is the shared
// all-zeros block, so a missing child needs no special case. Point updates walk down, then recompute the path.
// T: int, long long, ...{"; sums are kept in S (long long for small T)" if "S" in cpp_agg else ""}.
template <typename T>
struct {name} {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
{CPP_POOL.format(name=name, agg=cpp_agg, zero="0")}
    static {cpp_agg} merge({cpp_agg} a, {cpp_agg} b) {{ return {cpp_merge}; }}

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {{
        int path[130], depth;
        int x = descend(i, path, depth);
        pool[x].v = {cpp_leaf};
        while (depth) {{
            int y = path[--depth];
            pool[y].v = merge(pool[pool[y].l].v, pool[pool[y].r].v);
        }}
    }}

    {cpp_agg} query(int x, long long a, long long b, long long l, long long r) const {{
        if (r < a || b < l) return {cpp_identity};
        if (!x || (l <= a && b <= r)) return pool[x].v;  // node 0 holds 0, the value of a block of zeros
        long long m = a + (b - a) / 2;
        return merge(query(pool[x].l, a, m, l, r), query(pool[x].r, m + 1, b, l, r));
    }}

    // O(logU) -- fold of a[l..r]
    {cpp_agg} {query_op}(long long l, long long r) const {{ return query(root, lo, hi, l, r); }}

    // O(logU) -- a[i]
    T pointGet(long long i) const {{ return T(pool[find(i)].v); }}
{CPP_POINT_OPS}}};
'''
    write(folder, ops, comp, f"{'sm' if query_op == 'rangeSum' else 'v'}[1*log(U)]", note, py, cpp)


P = "pointAdd-pointAssign-pointChmax-pointChmin-pointGet"
scalar(P + "-rangeSum__seg-tree", "rangeSum", "SparseSumTree", "Point updates + range sum",
       "a + b", "0", "a + b", "0", "S")
scalar(P + "-rangeMax", "rangeMax", "SparseMaxTree", "Point updates + range max",
       "a if a > b else b", "NEG", "max(a, b)", "numeric_limits<T>::lowest()", "T", py_imports='\nNEG = float("-inf")', cpp_leaf="v")
scalar(P + "-rangeGcd", "rangeGcd", "SparseGcdTree", "Point updates + range gcd (of |values|)",
       "gcd(a, b)", "0", "std::gcd(a < 0 ? -a : a, b < 0 ? -b : b)", "0", "T",
       comp_extra={o: "log(U)*log(U) ?" for o in ("pointAdd", "pointAssign", "pointChmax", "pointChmin")} | {"rangeGcd": "2*log(U) ?"},
       py_imports="\nfrom math import gcd", note="leaves hold the signed values, internal nodes the gcd of |values|;", cpp_leaf="v")


# ------------------------------------------------------------------ order-dependent folds: a summary per node
def summary(folder, name, desc, fields, py_merge, cpp_merge, py_leaf, cpp_leaf, py_zero, cpp_zero, len_dependent,
            queries, py_get, cpp_get, node, note="", py_pre="", cpp_pre=""):
    """fields: [(name, cpp type)]; py_merge / py_zero / py_leaf build a tuple; queries: op -> (py on res, cpp on res)"""
    qops = list(queries)
    ops = POINT + qops
    tup = ", ".join(f for f, _ in fields)
    py_zero_fn = f"    @staticmethod\n    def _zero(k):  # a block of k zeros\n        return {py_zero}\n" if len_dependent else ""
    zero_get = "self._zero(k)" if len_dependent else "ZERO"
    py_queries = "".join(f'''
    # O(logU)
    def {op}(self, l, r):
        res = self._query(l, r)
        return {py}
''' for op, (py, _) in queries.items())
    py = f'''{py_pre}
# {desc}, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# Sparse: a dict keyed by heap index over a power-of-two cover of [lo, hi]; a missing key is a block of zeros.
# Each node keeps the summary ({tup}); merging is not commutative, so a query folds a left and a right
# accumulator, tracking each node's length k (a node at level s covers 2^s slots).
{"" if len_dependent else f"ZERO = {py_zero}  # the summary of any block of zeros"}


class {name}:
    __slots__ = ("lo", "size", "t")

    # O(1)
    def __init__(self, lo, hi):
        self.lo = lo
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; leaf of i is size + (i - lo)
        self.t = {{}}

    @staticmethod
    def _merge(a, b):
{py_merge}
{py_zero_fn}
    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        t = self.t
        p = self.size + i - self.lo
        t[p] = {py_leaf}
        p >>= 1
        k = 1  # length of p's children
        while p:
            a, b = t.get(2 * p), t.get(2 * p + 1)
            t[p] = self._merge({zero_get} if a is None else a, {zero_get} if b is None else b)
            p >>= 1
            k <<= 1

    # O(logU) -- summary of a[l..r]
    def _query(self, l, r):
        t = self.t
        left = right = None
        l += self.size - self.lo
        r += self.size - self.lo + 1
        k = 1
        while l < r:
            if l & 1:
                v = t.get(l)
                v = {zero_get} if v is None else v
                left = v if left is None else self._merge(left, v)
                l += 1
            if r & 1:
                r -= 1
                v = t.get(r)
                v = {zero_get} if v is None else v
                right = v if right is None else self._merge(v, right)
            l >>= 1
            r >>= 1
            k <<= 1
        if left is None:
            return right
        if right is None:
            return left
        return self._merge(left, right)
{py_queries}''' + PY_POINT_OPS.format(get=py_get)
    cpp_queries = "".join(f'''
    // O(logU)
    auto {op}(long long l, long long r) const {{
        Agg res = query(root, lo, hi, l, r);
        return {cpp};
    }}
''' for op, (_, cpp) in queries.items())
    agg_fields = " ".join(f"{t} {f};" for f, t in fields)
    zero_expr = "Agg{}" if len_dependent else cpp_zero
    get_agg = "x ? pool[x].v : zero(len)" if len_dependent else "pool[x].v"
    cpp = f'''
// {desc}, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
// Sparse: only the nodes on updated paths exist, in one pool shared by every {name}; a missing child is a block
// of zeros. Each node keeps the summary ({tup}); merging is not commutative, so queries combine left to right.
// T: int, long long, ...; sums are kept in S (long long for small T).{cpp_pre}
template <typename T>
struct {name} {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // an impossible (first sign, last sign) pair
    struct Agg {{ {agg_fields} }};
{CPP_POOL.format(name=name, agg="Agg", zero=zero_expr)}
    static Agg merge(const Agg& a, const Agg& b) {{ return {cpp_merge}; }}
    static Agg leaf(T v) {{ return {cpp_leaf}; }}
    static Agg zero(long long len) {{ (void)len; return {cpp_zero}; }}  // a block of len zeros
    static Agg agg(int x, long long len) {{ return {get_agg}; }}

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {{
        int path[130], depth;
        long long starts[130], ends[130];
        int x = descend(i, path, depth, starts, ends);
        pool[x].v = leaf(v);
        while (depth) {{
            --depth;
            int y = path[depth];
            long long a = starts[depth], b = ends[depth], m = a + (b - a) / 2;
            pool[y].v = merge(agg(pool[y].l, m - a + 1), agg(pool[y].r, b - m));
        }}
    }}

    // summary of a[max(l, a)..min(r, b)]; [a, b] must overlap [l, r]
    Agg query(int x, long long a, long long b, long long l, long long r) const {{
        if (!x) return zero(min(r, b) - max(l, a) + 1);
        if (l <= a && b <= r) return pool[x].v;
        long long m = a + (b - a) / 2;
        if (r <= m) return query(pool[x].l, a, m, l, r);
        if (l > m) return query(pool[x].r, m + 1, b, l, r);
        return merge(query(pool[x].l, a, m, l, r), query(pool[x].r, m + 1, b, l, r));
    }}
{cpp_queries}
    // O(logU) -- a[i]
    T pointGet(long long i) const {{
        int x = find(i);
        return x ? {cpp_get} : T(0);
    }}
{CPP_POINT_OPS}}};
'''
    comp = {o: "log(U)" for o in ops}
    write(folder, ops, comp, node, note, py, cpp)


PREFIX = [("sm", "S"), ("pre", "S"), ("suf", "S"), ("best", "S")]


def prefix_variant(folder, name, desc, keep):
    fields = [f for f in PREFIX if f[0] in keep]
    idx = {f: i for i, (f, _) in enumerate(fields)}
    pm = []
    for f, _ in fields:
        if f == "sm": pm.append(f"a[{idx['sm']}] + b[{idx['sm']}]")
        if f == "pre": pm.append(f"max(a[{idx['pre']}], a[{idx['sm']}] + b[{idx['pre']}])")
        if f == "suf": pm.append(f"max(b[{idx['suf']}], b[{idx['sm']}] + a[{idx['suf']}])")
        if f == "best": pm.append(f"max(a[{idx['best']}], b[{idx['best']}], a[{idx['suf']}] + b[{idx['pre']}])")
    py_merge = f"        return ({', '.join(pm)})"
    cm = []
    for f, _ in fields:
        if f == "sm": cm.append("a.sm + b.sm")
        if f == "pre": cm.append("max(a.pre, a.sm + b.pre)")
        if f == "suf": cm.append("max(b.suf, b.sm + a.suf)")
        if f == "best": cm.append("max({a.best, b.best, a.suf + b.pre})")
    queries = {"rangeSum": (f"res[{idx['sm']}]", "res.sm")}
    if "pre" in keep: queries["maxPrefixSum"] = (f"res[{idx['pre']}]", "res.pre")
    if "suf" in keep: queries["maxSuffixSum"] = (f"res[{idx['suf']}]", "res.suf")
    if "best" in keep: queries["maxSubarraySum"] = (f"res[{idx['best']}]", "res.best")
    n = len(fields)
    summary(folder, name, desc, fields, py_merge, "Agg{" + ", ".join(cm) + "}",
            f"({', '.join(['val'] * n)})", "Agg{" + ", ".join(["S(v)"] * n) + "}",
            f"({', '.join(['0'] * n)})", "Agg{" + ", ".join(["0"] * n) + "}", False, queries,
            "(lambda v: 0 if v is None else v[0])(self.t.get(self.size + i - self.lo))", "T(pool[x].v.sm)",
            " ".join(f"{f}[1*log(U)]" for f, _ in fields),
            note="pieces are non-empty, so a block of zeros summarizes to all zeros;")


prefix_variant("maxPrefixSum-" + P + "-rangeSum", "SparseMaxPrefixSumTree", "Max prefix sum + range sum with point updates", {"sm", "pre"})
prefix_variant("maxSuffixSum-" + P + "-rangeSum", "SparseMaxSuffixSumTree", "Max suffix sum + range sum with point updates", {"sm", "suf"})
prefix_variant("maxPrefixSum-maxSuffixSum-" + P + "-rangeSum", "SparseMaxPrefixSuffixSumTree",
               "Max prefix / suffix sum + range sum with point updates", {"sm", "pre", "suf"})
prefix_variant("maxPrefixSum-maxSubarraySum-maxSuffixSum-" + P + "-rangeSum", "SparseMaxSubarrayTree",
               "Max subarray / prefix / suffix sum + range sum with point updates", {"sm", "pre", "suf", "best"})

summary("longestEqualRun-" + P, "SparseEqualRunTree", "Longest run of equal adjacent values with point updates",
        [("ln", "long long"), ("pre", "long long"), ("suf", "long long"), ("best", "long long"), ("lv", "T"), ("rv", "T")],
        """        aln, apre, asuf, abest, alv, arv = a
        bln, bpre, bsuf, bbest, blv, brv = b
        join = arv == blv
        pre = apre + bpre if join and apre == aln else apre
        suf = bsuf + asuf if join and bsuf == bln else bsuf
        best = abest if abest > bbest else bbest
        if join and asuf + bpre > best:
            best = asuf + bpre
        return aln + bln, pre, suf, best, alv, brv""",
        "Agg{a.ln + b.ln, (a.rv == b.lv && a.pre == a.ln) ? a.ln + b.pre : a.pre, (a.rv == b.lv && b.suf == b.ln) ? b.ln + a.suf : b.suf, "
        "max({a.best, b.best, a.rv == b.lv ? a.suf + b.pre : 0LL}), a.lv, b.rv}",
        "(1, 1, 1, 1, val, val)", "Agg{1, 1, 1, 1, v, v}", "(k, k, k, k, 0, 0)", "Agg{len, len, len, len, T(0), T(0)}", True,
        {"longestEqualRun": ("res[3]", "res.best")},
        "(lambda v: 0 if v is None else v[4])(self.t.get(self.size + i - self.lo))", "pool[x].v.lv",
        "ln[1*log(U)] pre[1*log(U)] suf[1*log(U)] best[1*log(U)] lv[1*log(U)] rv[1*log(U)]",
        note="a block of k zeros is one run of length k, so missing nodes are summarized from their length;")

summary("maxAltSubseqSum-" + P, "SparseAltSumTree", "Max alternating subsequence sum +a - b + c ... with point updates",
        [("pp", "S"), ("pm", "S"), ("mp", "S"), ("mm", "S")],
        """        app, apm, amp, amm = a
        bpp, bpm, bmp, bmm = b
        return (max(app, bpp, app + bmp, apm + bpp),
                max(apm, bpm, app + bmm, apm + bpm),
                max(amp, bmp, amp + bmp, amm + bpp),
                max(amm, bmm, amp + bmm, amm + bpm))""",
        "Agg{max({a.pp, b.pp, a.pp + b.mp, a.pm + b.pp}), max({a.pm, b.pm, a.pp + b.mm, a.pm + b.pm}), "
        "max({a.mp, b.mp, a.mp + b.mp, a.mm + b.pp}), max({a.mm, b.mm, a.mp + b.mm, a.mm + b.pm})}",
        "(val, NEG, NEG, -val)", "Agg{S(v), NEG, NEG, -S(v)}", "(0, 0 if k > 1 else NEG, 0 if k > 1 else NEG, 0)",
        "Agg{0, len > 1 ? S(0) : NEG, len > 1 ? S(0) : NEG, 0}", True,
        {"maxAltSubseqSum": ("max(res[0], res[1])", "max(res.pp, res.pm)")},
        "(lambda v: 0 if v is None else v[0])(self.t.get(self.size + i - self.lo))", "T(pool[x].v.pp)",
        "pp[1*log(U)] pm[1*log(U)] mp[1*log(U)] mm[1*log(U)]",
        note="pairs (first sign, last sign) of a block of zeros: a single zero can't start + and end -;",
        py_pre='\nNEG = float("-inf")', cpp_pre="")


# ------------------------------------------------------------------ max / min trees with leftmost / rightmost searches
SYM = {"Gte": ">=", "Gt": ">", "Lte": "<=", "Lt": "<"}


def search_tree(kind):
    sides = {"max": ["Gte", "Gt"], "min": ["Lte", "Lt"], "both": ["Gte", "Gt", "Lte", "Lt"]}[kind]
    keeps = {"max": ["mx"], "min": ["mn"], "both": ["mx", "mn"]}[kind]
    names = [f"{side}{c}X" for side in ("leftmost", "rightmost") for c in sides]
    qops = (["rangeMax"] if "mx" in keeps else []) + (["rangeMin"] if "mn" in keeps else [])
    ops = sorted(POINT + names + qops)
    folder = "-".join(ops)
    name = {"max": "SparseMaxSearchTree", "min": "SparseMinSearchTree", "both": "SparseMaxMinSearchTree"}[kind]
    arr_of = lambda c: "mx" if c.startswith("G") else "mn"  # noqa: E731

    # ---------------- Python
    py_fold = ""
    for arr, op, cmp in (("mx", "rangeMax", ">"), ("mn", "rangeMin", "<")):
        if arr not in keeps:
            continue
        py_fold += f'''
    # O(logU) -- {op[5:].lower()} of a[l..r]
    def {op}(self, l, r):
        t, res = self.{arr}, {"NEG" if arr == "mx" else "INF"}
        l += self.size - self.lo
        r += self.size - self.lo + 1
        while l < r:
            if l & 1:
                v = t.get(l, 0)
                if v {cmp} res:
                    res = v
                l += 1
            if r & 1:
                r -= 1
                v = t.get(r, 0)
                if v {cmp} res:
                    res = v
            l >>= 1
            r >>= 1
        return res
'''
    py_walks = ""
    for c in sides:
        sym, arr = SYM[c], arr_of(c)
        py_walks += f'''
    # O(logU) -- first i in [l, r] with a[i] {sym} x, or lo - 1
    def leftmost{c}X(self, l, r, x):
        t, size = self.{arr}, self.size
        p = l - self.lo + size
        while True:
            while not p & 1:  # climb while p is a left child: its parent starts at the same index
                p >>= 1
            if t.get(p, 0) {sym} x:  # the answer is inside p: descend, preferring the left child
                while p < size:
                    p <<= 1
                    if not t.get(p, 0) {sym} x:
                        p += 1
                i = p - size + self.lo
                return i if i <= r else self.lo - 1
            p += 1
            if not p & (p - 1):  # walked off the right edge
                return self.lo - 1

    # O(logU) -- last i in [l, r] with a[i] {sym} x, or lo - 1
    def rightmost{c}X(self, l, r, x):
        t, size = self.{arr}, self.size
        p = r - self.lo + size + 1
        while True:
            p -= 1
            while p > 1 and p & 1:  # climb while p is a right child: its parent ends at the same index
                p >>= 1
            if t.get(p, 0) {sym} x:  # the answer is inside p: descend, preferring the right child
                while p < size:
                    p = 2 * p + 1
                    if not t.get(p, 0) {sym} x:
                        p -= 1
                i = p - size + self.lo
                return i if i >= l else self.lo - 1
            if not p & (p - 1):  # walked off the left edge
                return self.lo - 1
'''
    set_leaf = " = ".join(f"self.{a}[p]" for a in keeps) + " = val"
    recompute = ""
    for a in keeps:
        cmp = ">" if a == "mx" else "<"
        recompute += f"            u, w = self.{a}.get(2 * p, 0), self.{a}.get(2 * p + 1, 0)\n            self.{a}[p] = u if u {cmp} w else w\n"
    py = f'''
NEG = float("-inf")
INF = float("inf")

# Range {" / ".join(q[5:].lower() for q in qops)} and leftmost / rightmost index with a[i] {" / ".join(SYM[c] for c in sides)} x, with point updates, over
# any index range [lo, hi] (huge or negative is fine); every position starts at 0. Searches return lo - 1 when nothing
# qualifies (-1 when lo = 0). Sparse: dicts keyed by heap index over a power-of-two cover of [lo, hi]; a missing key is a block of
# zeros. The searches are the dense tree's iterative walks: climb from the boundary until a node holds a match,
# then descend into it.


class {name}:
    __slots__ = ("lo", "size", {", ".join(f'"{a}"' for a in keeps)})

    # O(1)
    def __init__(self, lo, hi):
        self.lo = lo
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; leaf of i is size + (i - lo)
{"".join(f"        self.{a} = {{}}{chr(10)}" for a in keeps)}
    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        p = self.size + i - self.lo
        {set_leaf}
        p >>= 1
        while p:
{recompute}            p >>= 1
{py_fold}{py_walks}''' + PY_POINT_OPS.format(get=f"self.{keeps[0]}.get(self.size + i - self.lo, 0)")

    # ---------------- C++
    agg = "Agg"
    fields = " ".join(f"T {a};" for a in keeps)
    merge = "Agg{" + ", ".join(f"{'max' if a == 'mx' else 'min'}(a.{a}, b.{a})" for a in keeps) + "}"
    cpp_fold = ""
    for arr, op in (("mx", "rangeMax"), ("mn", "rangeMin")):
        if arr not in keeps:
            continue
        fn = "max" if arr == "mx" else "min"
        cpp_fold += f'''
    T fold{arr}(int x, long long a, long long b, long long l, long long r) const {{
        if (r < a || b < l) return {"numeric_limits<T>::lowest()" if arr == "mx" else "numeric_limits<T>::max()"};
        if (!x || (l <= a && b <= r)) return pool[x].v.{arr};  // node 0 holds 0, the value of a block of zeros
        long long m = a + (b - a) / 2;
        return {fn}(fold{arr}(pool[x].l, a, m, l, r), fold{arr}(pool[x].r, m + 1, b, l, r));
    }}

    // O(logU) -- {fn} of a[l..r]
    T {op}(long long l, long long r) const {{ return fold{arr}(root, lo, hi, l, r); }}
'''
    cpp_walks = ""
    for c in sides:
        sym, arr = SYM[c], arr_of(c)
        # does node x (or the all-zero block, x = 0) contain a value passing "v sym x"? it does iff its max / min passes
        cpp_walks += f'''
    long long left{c}(int x, long long a, long long b, long long l, long long r, T v) const {{
        if (r < a || b < l || !(pool[x].v.{arr} {sym} v)) return lo - 1;
        if (!x) return max(a, l);  // a block of zeros, and 0 passes
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = left{c}(pool[x].l, a, m, l, r, v);
        return res != lo - 1 ? res : left{c}(pool[x].r, m + 1, b, l, r, v);
    }}

    long long right{c}(int x, long long a, long long b, long long l, long long r, T v) const {{
        if (r < a || b < l || !(pool[x].v.{arr} {sym} v)) return lo - 1;
        if (!x) return min(b, r);
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = right{c}(pool[x].r, m + 1, b, l, r, v);
        return res != lo - 1 ? res : right{c}(pool[x].l, a, m, l, r, v);
    }}

    // O(logU) -- first i in [l, r] with a[i] {sym} x, or lo - 1
    long long leftmost{c}X(long long l, long long r, T x) const {{ return left{c}(root, lo, hi, l, r, x); }}

    // O(logU) -- last i in [l, r] with a[i] {sym} x, or lo - 1
    long long rightmost{c}X(long long l, long long r, T x) const {{ return right{c}(root, lo, hi, l, r, x); }}
'''
    cpp = f'''
// Range {" / ".join(q[5:].lower() for q in qops)} and leftmost / rightmost index with a[i] {" / ".join(SYM[c] for c in sides)} x, with point updates, over
// any index range [lo, hi] (huge or negative is fine); every position starts at 0. Searches return lo - 1 when nothing
// qualifies (-1 when lo = 0). Sparse: only the nodes on updated paths exist, in one pool shared by every {name}; node 0 is the
// shared all-zeros block. A search prunes any node whose {"max / min" if kind == "both" else ("max" if kind == "max" else "min")} can't pass, so it visits O(log U) nodes.
// T: int, long long, ...
template <typename T>
struct {name} {{
    struct Agg {{ {fields} }};
{CPP_POOL.format(name=name, agg=agg, zero="Agg{}")}
    static Agg merge(const Agg& a, const Agg& b) {{ return {merge}; }}

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {{
        int path[130], depth;
        int x = descend(i, path, depth);
        pool[x].v = Agg{{{", ".join("v" for _ in keeps)}}};
        while (depth) {{
            int y = path[--depth];
            pool[y].v = merge(pool[pool[y].l].v, pool[pool[y].r].v);
        }}
    }}
{cpp_fold}{cpp_walks}
    // O(logU) -- a[i]
    T pointGet(long long i) const {{ return pool[find(i)].v.{keeps[0]}; }}
{CPP_POINT_OPS}}};
'''
    write(folder, ops, {}, " ".join(f"{a}[1*log(U)]" for a in keeps), "", py, cpp)


for kind in ("max", "min", "both"):
    search_tree(kind)
