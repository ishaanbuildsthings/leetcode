"""Sparse (dynamic) versions of the lazy trees outside the generated family: sparse.py + sparse.cpp per folder.

    python3 sparse_lazy_custom.py

One engine, one small spec per template: the spec gives the node aggregate, the tag, how a tag changes an
aggregate of k slots, how tags compose, and how aggregates merge; the engine writes the same recursive dynamic
tree as sparse_lazy.py (updates push, queries carry the ancestors' tags down and create nothing, node 0 is the
shared all-zeros block). C++: one shared node pool per type. Python: lists of nodes, an aggregate per node, a
tag per node (None: none).
"""
import os

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
PLAIN = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
MOD_POINT = ["pointAdd", "pointAssign", "pointGet"]
POOL_NOTE = ("C++: one shared node pool (node 0 = all zeros), call resetPool() between test cases; Python: lists of "
             "nodes")


def header(cm, ops, comp, mem, note):
    lines = [f"{cm} @operations: {' '.join(ops)}", f"{cm} @data-structure-type: lazy-seg-tree", f"{cm} @complexities:"]
    lines += [f"{cm}   {o}: {comp.get(o, 'log(U)')}" for o in ops] + [f"{cm}   build: 1"]
    node, tags, other = mem
    lines += [f"{cm} @memory:", f"{cm}   layout: sparse", f"{cm}   node: {node}", f"{cm}   tags: {tags}",
              f"{cm}   other: {other}", f"{cm}   note: {note}"]
    return "\n".join(lines) + "\n"


# ================================================================================================ C++

def decl(name, body):  # "struct Name { fields };  // comment", keeping a trailing comment out of the braces
    fields, _, comment = body.partition("//")
    return f"struct {name} {{ {fields.strip()} }};" + (f"  // {comment.strip()}" if comment else "")


def cpp(s):
    name, c = s["name"], s["cpp"]
    mod = s.get("mod", False)
    updates = "".join(
        f"\n    // O(logU) -- {d} for i in [l, r]\n    void {m}(long long l, long long r, {sig}) {{\n"
        f"        if (l <= r) update(root, lo, hi, l, r, {t});\n    }}\n" for m, sig, d, t in c["updates"])
    queries = "".join(
        f"\n    // O(logU) -- {d}\n    {rt} {m}(long long l, long long r) const {{\n"
        f"        Agg res = query(root, lo, hi, l, r, ID);\n        return {e};\n    }}\n" for m, rt, d, e in c["queries"])
    merge = c.get("merge")
    pull = f'''
    void pull(int x) {{ pool[x].v = merge(pool[pool[x].l].v, pool[pool[x].r].v); }}

    {"" if mod else "static "}Agg merge(const Agg& a, const Agg& b){" const" if mod else ""} {{ {merge} }}
''' if merge else ""
    ms = "M" if not mod else ""
    if s["point"] == "plain":
        points = '''
    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
'''
    else:
        points = '''
    // O(logU) -- a[i] += delta (mod p)
    void pointAdd(long long i, T delta) { pointAssign(i, norm(W(pointGet(i)) + delta)); }
'''
    del ms
    intro = "\n".join("// " + line if line else "//" for line in s["desc"])
    return f'''
{intro}
// Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Updates push a node's
// tag into its children (creating them) before recursing past it; queries never push: they carry the
// ancestors' tags down and apply them to what they return, so they create no nodes. Sparse: nodes exist only
// where updates reached, in one pool shared by every {name}<T>; node 0 is the shared all-zeros block.
// T: int, long long, ...
template <typename T>
struct {name} {{
{c.get("types", "")}    {decl("Agg", c["agg"])}
    {decl("Tag", c["tag"])}
    static constexpr Tag ID = {c["ident"]};
    struct Node {{ Agg v; Tag t; int l, r; }};
    static inline vector<Node> pool{{Node{{Agg{{}}, ID, 0, 0}}}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root;{chr(10) + "    T mod;" if mod else ""}

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    {name}(long long lo, long long hi{", T mod = 1000000007" if mod else ""}) : lo(lo), hi(hi){", mod(mod)" if mod else ""} {{ root = make(); }}

    // O(1) -- forget every node of every {name}<T>; call between test cases, then build new trees
    static void resetPool() {{ pool.resize(1); }}

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) {{ pool.reserve(nodes); }}

    static int make() {{
        pool.push_back(Node{{Agg{{}}, ID, 0, 0}});
        return (int)pool.size() - 1;
    }}

    // child of x, creating it (as a block of zeros) if missing
    static int kid(int x, bool right) {{
        int y = right ? pool[x].r : pool[x].l;
        if (!y) {{
            y = make();
            (right ? pool[x].r : pool[x].l) = y;
        }}
        return y;
    }}
{c.get("helpers", "")}
    static bool isId(const Tag& t) {{ return {c["is_id"]}; }}

    // tag o, then tag t
    {"" if mod else "static "}Tag compose(const Tag& o, const Tag& t){" const" if mod else ""} {{ {c["compose"]} }}

    // the aggregate of k slots after tag t
    {"" if mod else "static "}Agg applyTag(Agg v, long long k, const Tag& t){" const" if mod else ""} {{
{c["apply"]}
        return v;
    }}

    // node x (k slots) takes tag t: its aggregate now, its children later
    void applyNode(int x, long long k, const Tag& t) {{
        pool[x].v = applyTag(pool[x].v, k, t);
        pool[x].t = compose(pool[x].t, t);
    }}

    // move x's tag (x covers [a, b]) into its children, creating them
    void push(int x, long long a, long long b) {{
        if (isId(pool[x].t)) return;
        Tag t = pool[x].t;
        long long m = a + (b - a) / 2;
        applyNode(kid(x, false), m - a + 1, t);
        applyNode(kid(x, true), b - m, t);
        pool[x].t = ID;
    }}
{pull}
    void update(int x, long long a, long long b, long long l, long long r, const Tag& t) {{
        if (l <= a && b <= r) {{ applyNode(x, b - a + 1, t); return; }}
        push(x, a, b);
        long long m = a + (b - a) / 2;
        if (l <= m) update(kid(x, false), a, m, l, r, t);
        if (r > m) update(kid(x, true), m + 1, b, l, r, t);{chr(10) + "        pull(x);" if merge else ""}
    }}

    // aggregate of a[max(l, a)..min(r, b)] under node x (covering [a, b]), with t, the ancestors' pending tags, on top
    Agg query(int x, long long a, long long b, long long l, long long r, const Tag& t) const {{
        if (!x) return applyTag(Agg{{}}, std::min(r, b) - std::max(l, a) + 1, t);
        if (l <= a && b <= r) return applyTag(pool[x].v, b - a + 1, t);
        Tag down = compose(pool[x].t, t);
        long long m = a + (b - a) / 2;
        if (r <= m) return query(pool[x].l, a, m, l, r, down);
        {"if (l > m) " if merge else ""}return query(pool[x].r, m + 1, b, l, r, down);{chr(10) + "        return merge(query(pool[x].l, a, m, l, r, down), query(pool[x].r, m + 1, b, l, r, down));" if merge else ""}
    }}
{updates}{queries}
    // O(logU) -- a[i]{c.get("get_note", "")}
    T pointGet(long long i) const {{
        Agg res = query(root, lo, hi, i, i, ID);
        return {c["get"]};
    }}

    // O(logU) -- a[i] = v{c.get("assign_note", "")}
    void pointAssign(long long i, T v) {{
        int path[130], d = 0, y = root;
        long long a = lo, b = hi;
        while (a < b) {{
            push(y, a, b);
            path[d++] = y;
            long long m = a + (b - a) / 2;
            if (i <= m) y = kid(y, false), b = m;
            else y = kid(y, true), a = m + 1;
        }}
        pool[y].v = {c["leaf"]};{chr(10) + "        while (d--) pull(path[d]);" if merge else chr(10) + "        (void)path;"}
    }}
{points}}};
'''


# ================================================================================================ Python

def py(s):
    name, p = s["name"], s["py"]
    mod = s.get("mod", False)
    merge = p.get("merge")
    updates = "".join(f'''
    # O(logU) -- {d} for i in [l, r]
    def {m}(self, l, r, {args}):{p.get("pre", {}).get(m, "")}
        if l <= r:
            self._update(1, self.lo, self.hi, l, r, {t})
''' for m, args, d, t in p["updates"])
    queries = "".join(f'''
    # O(logU) -- {d}
    def {m}(self, l, r):
        res = self._query(1, self.lo, self.hi, l, r, None)
        return {e}
''' for m, d, e in p["queries"])
    if s["point"] == "plain":
        points = '''
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
    else:
        points = '''
    # O(logU) -- a[i] += delta (mod p)
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)
'''
    pull = f'''
    def _pull(self, x):
        v = self.v
        v[x] = self._merge(v[self.L[x]], v[self.R[x]])

    {"" if mod else "@staticmethod" + chr(10) + "    "}def _merge({"self, " if mod else ""}a, b):
{p["merge"]}
''' if merge else ""
    intro = "\n".join("# " + line if line else "#" for line in s["desc"])
    return f'''{p.get("helpers", "")}
{intro}
# Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Updates push a node's tag
# into its children (creating them) before recursing past it; queries never push: they carry the ancestors' tags
# down and apply them to what they return, so they create no nodes. Sparse: lists of nodes; node 0 is the shared
# all-zeros block, node 1 the root; a tag of None means no tag.

ZERO = {p["zero"]}  # the aggregate of any block of zeros


class {name}:
    __slots__ = ("lo", "hi", "L", "R", "v", "tg"{', "mod"' if mod else ""})

    # O(1)
    def __init__(self, lo, hi{", mod=1000000007" if mod else ""}):
        self.lo, self.hi = lo, hi
        self.L, self.R = [0, 0], [0, 0]
        self.v = [ZERO, ZERO]
        self.tg = [None, None]{chr(10) + "        self.mod = mod" if mod else ""}

    def _kid(self, x, right):  # child of x, created as a block of zeros if missing
        kids = self.R if right else self.L
        y = kids[x]
        if not y:
            y = len(self.L)
            self.L.append(0)
            self.R.append(0)
            self.v.append(ZERO)
            self.tg.append(None)
            kids[x] = y
        return y

    # the aggregate v of k slots after tag t
    {"" if mod else "@staticmethod" + chr(10) + "    "}def _tagged({"self, " if mod else ""}v, k, t):
{p["apply"]}

    # tag o, then tag t
    {"" if mod else "@staticmethod" + chr(10) + "    "}def _compose({"self, " if mod else ""}o, t):
{p["compose"]}

    # node x (k slots) takes tag t: its aggregate now, its children later
    def _apply(self, x, k, t):
        self.v[x] = self._tagged(self.v[x], k, t)
        o = self.tg[x]
        self.tg[x] = t if o is None else self._compose(o, t)

    # move x's tag (x covers [a, b]) into its children, creating them
    def _push(self, x, a, b):
        t = self.tg[x]
        if t is not None:
            m = (a + b) // 2
            self._apply(self._kid(x, 0), m - a + 1, t)
            self._apply(self._kid(x, 1), b - m, t)
            self.tg[x] = None
{pull}
    def _update(self, x, a, b, l, r, t):
        if l <= a and b <= r:
            self._apply(x, b - a + 1, t)
            return
        self._push(x, a, b)
        m = (a + b) // 2
        if l <= m:
            self._update(self._kid(x, 0), a, m, l, r, t)
        if r > m:
            self._update(self._kid(x, 1), m + 1, b, l, r, t){chr(10) + "        self._pull(x)" if merge else ""}

    # aggregate of a[max(l, a)..min(r, b)] under node x (covering [a, b]), with the ancestors' tag t on top
    def _query(self, x, a, b, l, r, t):
        if not x:
            return ZERO if t is None else self._tagged(ZERO, (r if r < b else b) - (l if l > a else a) + 1, t)
        if l <= a and b <= r:
            return self.v[x] if t is None else self._tagged(self.v[x], b - a + 1, t)
        o = self.tg[x]
        d = o if t is None else (t if o is None else self._compose(o, t))
        m = (a + b) // 2
        if r <= m:
            return self._query(self.L[x], a, m, l, r, d)
        {"if l > m:" + chr(10) + "            " if merge else ""}return self._query(self.R[x], m + 1, b, l, r, d){chr(10) + "        return self._merge(self._query(self.L[x], a, m, l, r, d), self._query(self.R[x], m + 1, b, l, r, d))" if merge else ""}
{updates}{queries}
    # O(logU) -- a[i]{p.get("get_note", "")}
    def pointGet(self, i):
        res = self._query(1, self.lo, self.hi, i, i, None)
        return {p["get"]}

    # O(logU) -- a[i] = val{p.get("assign_note", "")}
    def pointAssign(self, i, val):
        path = []
        x, a, b = 1, self.lo, self.hi
        while a < b:
            self._push(x, a, b)
            path.append(x)
            m = (a + b) // 2
            if i <= m:
                x, b = self._kid(x, 0), m
            else:
                x, a = self._kid(x, 1), m + 1
        self.v[x] = {p["leaf"]}{chr(10) + "        for y in reversed(path):" + chr(10) + "            self._pull(y)" if merge else ""}
{points}'''


def write(s):
    ops = sorted(s["ops"])
    folder = "-".join(ops)
    path = os.path.join(DIR, folder)
    assert os.path.isdir(path), folder
    note = s["note"] + POOL_NOTE
    open(os.path.join(path, "sparse.py"), "w").write(header("#", ops, s.get("comp", {}), s["mem"], note) + py(s))
    open(os.path.join(path, "sparse.cpp"), "w").write(header("//", ops, s.get("comp", {}), s["mem"], note) + cpp(s))
    print("wrote", folder)


VISIT = "per update, the nodes it visits (at most 4 per level, counting the children a push creates); queries create nothing. "

# ------------------------------------------------------------------------------------------------ clamp, point get only

PY_CLAMP_HELP = '''
INF = float("inf")
NEG = float("-inf")
'''
write({
    "name": "SparseClampTree", "ops": PLAIN + ["rangeAdd", "rangeAssign", "rangeChmax", "rangeChmin"], "point": "plain",
    "desc": ["Range add / assign / chmin / chmax + point ops. A tag is the map x -> min(hi, max(lo, x + add)); these",
             "maps compose into the same form (assign v is hi = lo = v). Only leaves' values matter, so nothing is pulled."],
    "mem": ("v[4*log(U)]", "hi[4*log(U)] lo[4*log(U)] add[4*log(U)]", "links[8*log(U)]"),
    "note": VISIT + "a leaf's value is v (internal nodes keep no aggregate). ",
    "cpp": {
        "types": "    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();\n",
        "agg": "T v;", "tag": "T hi, lo, c;  // x -> min(hi, max(lo, x + c))", "ident": "Tag{INF, NEG, 0}",
        "is_id": "t.hi == INF && t.lo == NEG && t.c == 0",
        "compose": "T h = std::min(t.hi, std::max(t.lo, o.hi == INF ? INF : o.hi + t.c));\n"
                   "        T l = std::min(std::max(t.lo, o.lo == NEG ? NEG : o.lo + t.c), h);\n        return Tag{h, l, o.c + t.c};",
        "apply": "        (void)k;\n        v.v = std::min(t.hi, std::max(t.lo, v.v + t.c));",
        "leaf": "Agg{v}", "get": "res.v",
        "updates": [("rangeAdd", "T v", "a[i] += v", "Tag{INF, NEG, v}"), ("rangeChmin", "T v", "a[i] = min(a[i], v)", "Tag{v, NEG, 0}"),
                    ("rangeChmax", "T v", "a[i] = max(a[i], v)", "Tag{INF, v, 0}"), ("rangeAssign", "T v", "a[i] = v", "Tag{v, v, 0}")],
        "queries": [],
    },
    "py": {
        "helpers": PY_CLAMP_HELP, "zero": "0",
        "apply": "        v += t[2]\n        if v < t[1]:\n            v = t[1]\n        return t[0] if v > t[0] else v",
        "compose": "        h = min(t[0], max(t[1], o[0] + t[2]))\n        return h, min(max(t[1], o[1] + t[2]), h), o[2] + t[2]",
        "leaf": "val", "get": "res",
        "updates": [("rangeAdd", "v", "a[i] += v", "(INF, NEG, v)"), ("rangeChmin", "v", "a[i] = min(a[i], v)", "(v, NEG, 0)"),
                    ("rangeChmax", "v", "a[i] = max(a[i], v)", "(INF, v, 0)"), ("rangeAssign", "v", "a[i] = v", "(v, v, 0)")],
        "queries": [],
    },
})

# ------------------------------------------------------------------------------------------------ and= / or= / xor=, point get only

write({
    "name": "SparseBitOpTree", "ops": PLAIN + ["rangeAndApply", "rangeOrApply", "rangeXorApply"], "point": "plain",
    "desc": ["Range and= / or= / xor= + point ops. Every update is a bit map v -> (v & a) ^ x (and X = (X, 0),",
             "or X = (~X, X), xor X = (all ones, X)), and these maps compose into the same form. Only leaves' values",
             "matter, so nothing is pulled."],
    "mem": ("v[4*log(U)]", "a[4*log(U)] x[4*log(U)]", "links[8*log(U)]"),
    "note": VISIT + "a leaf's value is v (internal nodes keep no aggregate). ",
    "cpp": {
        "agg": "T v;", "tag": "T a, x;  // v -> (v & a) ^ x", "ident": "Tag{T(-1), 0}", "is_id": "t.a == T(-1) && t.x == 0",
        "compose": "return Tag{T(o.a & t.a), T((o.x & t.a) ^ t.x)};",
        "apply": "        (void)k;\n        v.v = (v.v & t.a) ^ t.x;", "leaf": "Agg{v}", "get": "res.v",
        "updates": [("rangeAndApply", "T X", "a[i] &= X", "Tag{X, 0}"), ("rangeOrApply", "T X", "a[i] |= X", "Tag{T(~X), X}"),
                    ("rangeXorApply", "T X", "a[i] ^= X", "Tag{T(-1), X}")],
        "queries": [],
    },
    "py": {
        "zero": "0", "apply": "        return (v & t[0]) ^ t[1]", "compose": "        return o[0] & t[0], (o[1] & t[0]) ^ t[1]",
        "leaf": "val", "get": "res",
        "updates": [("rangeAndApply", "X", "a[i] &= X", "(X, 0)"), ("rangeOrApply", "X", "a[i] |= X", "(~X, X)"),
                    ("rangeXorApply", "X", "a[i] ^= X", "(-1, X)")],
        "queries": [],
    },
})

# ------------------------------------------------------------------------------------------------ bit counts: and= / or= / xor= with sum / and / or

BITS_C = "log(U)*log(U)"
write({
    "name": "SparseBitCountTree",
    "ops": PLAIN + ["rangeAndApply", "rangeAndQuery", "rangeOrApply", "rangeOrQuery", "rangeSum", "rangeXorApply"],
    "point": "plain",
    "comp": {o: BITS_C for o in PLAIN + ["rangeAndApply", "rangeAndQuery", "rangeOrApply", "rangeOrQuery", "rangeSum", "rangeXorApply"]},
    "desc": ["Range and= / or= / xor= with range sum / and / or queries, plus point ops. Values live in [0, 2^BITS).",
             "Each node counts, for every bit, how many of its values have that bit set. Every update is a bit map",
             "v -> (v & a) ^ x, and per bit that is keep, force 0 (count = 0), force 1, or flip (count = length - count),",
             "so every update is an ordinary lazy tag. Sum = sum over bits of count * 2^bit."],
    "mem": ("cnt[4*log(U)*log(U)]", "a[4*log(U)] x[4*log(U)]", "links[8*log(U)]"),
    "note": VISIT + "every node keeps BITS counts (BITS = 20, the second log); ",
    "cpp": {
        "types": "    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n"
                 "    static constexpr int BITS = 20;  // values live in [0, 2^BITS)\n"
                 "    static constexpr T FULL = T((T(1) << BITS) - 1);\n",
        "agg": "array<long long, BITS> c;  // c[b] = how many values below have bit b set",
        "tag": "T a, x;  // v -> (v & a) ^ x", "ident": "Tag{FULL, 0}", "is_id": "t.a == FULL && t.x == 0",
        "compose": "return Tag{T(o.a & t.a), T((o.x & t.a) ^ t.x)};",
        "apply": "        for (int b = 0; b < BITS; b++) {\n            if (!(t.a >> b & 1)) v.c[b] = 0;\n            if (t.x >> b & 1) v.c[b] = k - v.c[b];\n        }",
        "merge": "Agg r; for (int j = 0; j < BITS; j++) r.c[j] = a.c[j] + b.c[j]; return r;",
        "leaf": "[&] { Agg r{}; v &= FULL; for (int b = 0; b < BITS; b++) r.c[b] = v >> b & 1; return r; }()",
        "get": "[&] { T v = 0; for (int b = 0; b < BITS; b++) v |= T(res.c[b]) << b; return v; }()",
        "assign_note": " & FULL", "get_note": "",
        "updates": [("rangeAndApply", "T X", "a[i] &= X", "Tag{T(X & FULL), 0}"),
                    ("rangeOrApply", "T X", "a[i] |= X", "Tag{T(~X & FULL), T(X & FULL)}"),
                    ("rangeXorApply", "T X", "a[i] ^= X", "Tag{FULL, T(X & FULL)}")],
        "queries": [("rangeSum", "S", "a[l] + ... + a[r]", "[&] { S s = 0; for (int b = 0; b < BITS; b++) s += S(res.c[b]) << b; return s; }()"),
                    ("rangeAndQuery", "T", "a[l] & ... & a[r]", "[&] { T v = 0; for (int b = 0; b < BITS; b++) if (res.c[b] == r - l + 1) v |= T(1) << b; return v; }()"),
                    ("rangeOrQuery", "T", "a[l] | ... | a[r]", "[&] { T v = 0; for (int b = 0; b < BITS; b++) if (res.c[b]) v |= T(1) << b; return v; }()")],
    },
    "py": {
        "helpers": "\nBITS = 20  # values live in [0, 2^BITS)\nFULL = (1 << BITS) - 1\n",
        "zero": "(0,) * BITS",
        "apply": "        a, x = t\n        return tuple(((k - c) if x >> b & 1 else c) if a >> b & 1 else (k if x >> b & 1 else 0) for b, c in enumerate(v))",
        "compose": "        return o[0] & t[0], (o[1] & t[0]) ^ t[1]",
        "merge": "        return tuple(map(int.__add__, a, b))",
        "leaf": "tuple(val >> b & 1 for b in range(BITS))", "get": "sum(c << b for b, c in enumerate(res))",
        "assign_note": " & FULL",
        "updates": [("rangeAndApply", "X", "a[i] &= X", "(X & FULL, 0)"), ("rangeOrApply", "X", "a[i] |= X", "(~X & FULL, X & FULL)"),
                    ("rangeXorApply", "X", "a[i] ^= X", "(FULL, X & FULL)")],
        "queries": [("rangeSum", "a[l] + ... + a[r]", "sum(c << b for b, c in enumerate(res))"),
                    ("rangeAndQuery", "a[l] & ... & a[r]", "sum(1 << b for b, c in enumerate(res) if c == r - l + 1)"),
                    ("rangeOrQuery", "a[l] | ... | a[r]", "sum(1 << b for b, c in enumerate(res) if c)")],
    },
})

# ------------------------------------------------------------------------------------------------ assign + gcd

GCD_W = "log(U)*log(U) ?"
write({
    "name": "SparseAssignGcdTree", "ops": PLAIN + ["rangeAssign", "rangeGcd"], "point": "plain",
    "comp": {"pointAdd": GCD_W, "pointAssign": GCD_W, "pointChmax": GCD_W, "pointChmin": GCD_W, "rangeAssign": GCD_W,
             "rangeGcd": "log(U) ?"},
    "desc": ["Range assign + range gcd, plus point ops. Gcds are of |values|. A leaf keeps its value, an internal node",
             "the gcd of |values| below it, and a node assigned v has gcd |v|, so assign is an ordinary lazy tag."],
    "mem": ("g[4*log(U)]", "asg[4*log(U)] hasAsg[4*log(U)]", "links[8*log(U)]"),
    "note": VISIT + "the gcd costs' second log is of the largest value. ",
    "cpp": {
        "agg": "T g;  // a leaf: its value; internal: gcd of |values| below", "tag": "T asg; bool has;",
        "ident": "Tag{0, false}", "is_id": "!t.has", "compose": "return t.has ? t : o;",
        "helpers": "\n    static T absT(T x) { return x < 0 ? -x : x; }\n",
        "apply": "        if (t.has) v.g = k == 1 ? t.asg : absT(t.asg);",
        "merge": "return Agg{std::gcd(absT(a.g), absT(b.g))};",
        "leaf": "Agg{v}", "get": "res.g",
        "updates": [("rangeAssign", "T v", "a[i] = v", "Tag{v, true}")],
        "queries": [("rangeGcd", "T", "gcd of |a[l]|, ..., |a[r]| (0 only if all are 0)", "absT(res.g)")],
    },
    "py": {
        "helpers": "\nfrom math import gcd\n", "zero": "0",
        "apply": "        return t if k == 1 else abs(t)", "compose": "        return t",
        "merge": "        return gcd(a, b)", "leaf": "val", "get": "res",
        "updates": [("rangeAssign", "v", "a[i] = v", "v")],
        "queries": [("rangeGcd", "gcd of |a[l]|, ..., |a[r]| (0 only if all are 0)", "abs(res)")],
    },
})

# ------------------------------------------------------------------------------------------------ max subarray + assign

write({
    "name": "SparseMaxSubarrayAssignTree",
    "ops": PLAIN + ["maxPrefixSum", "maxSubarraySum", "maxSuffixSum", "rangeAssign", "rangeSum"], "point": "plain",
    "desc": ["Range assign with range sum and max prefix / suffix / subarray sum (non-empty pieces), plus point ops.",
             "A node assigned v over k slots is fully known: sum v * k, and its best prefix / suffix / subarray are",
             "v * k if v > 0, else v. A block of zeros summarizes to all zeros. Merging is not commutative."],
    "mem": ("sm[4*log(U)] pre[4*log(U)] suf[4*log(U)] best[4*log(U)]", "asg[4*log(U)] hasAsg[4*log(U)]", "links[8*log(U)]"),
    "note": VISIT,
    "cpp": {
        "types": "    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n",
        "agg": "S sm, pre, suf, best;", "tag": "T asg; bool has;", "ident": "Tag{0, false}", "is_id": "!t.has",
        "compose": "return t.has ? t : o;",
        "apply": "        if (t.has) {\n            v.sm = S(t.asg) * k;\n            v.pre = v.suf = v.best = t.asg > 0 ? v.sm : S(t.asg);\n        }",
        "merge": "return Agg{a.sm + b.sm, max(a.pre, a.sm + b.pre), max(b.suf, b.sm + a.suf), max({a.best, b.best, a.suf + b.pre})};",
        "leaf": "Agg{S(v), S(v), S(v), S(v)}", "get": "T(res.sm)",
        "updates": [("rangeAssign", "T v", "a[i] = v", "Tag{v, true}")],
        "queries": [("rangeSum", "S", "a[l] + ... + a[r]", "res.sm"), ("maxPrefixSum", "S", "best sum of a non-empty prefix of a[l..r]", "res.pre"),
                    ("maxSuffixSum", "S", "best sum of a non-empty suffix of a[l..r]", "res.suf"),
                    ("maxSubarraySum", "S", "best sum of a non-empty subarray of a[l..r]", "res.best")],
    },
    "py": {
        "zero": "(0, 0, 0, 0)",
        "apply": "        s = t * k\n        b = s if t > 0 else t\n        return s, b, b, b", "compose": "        return t",
        "merge": "        return a[0] + b[0], max(a[1], a[0] + b[1]), max(b[2], b[0] + a[2]), max(a[3], b[3], a[2] + b[1])",
        "leaf": "(val, val, val, val)", "get": "res[0]",
        "updates": [("rangeAssign", "v", "a[i] = v", "v")],
        "queries": [("rangeSum", "a[l] + ... + a[r]", "res[0]"), ("maxPrefixSum", "best sum of a non-empty prefix of a[l..r]", "res[1]"),
                    ("maxSuffixSum", "best sum of a non-empty suffix of a[l..r]", "res[2]"),
                    ("maxSubarraySum", "best sum of a non-empty subarray of a[l..r]", "res[3]")],
    },
})

# ------------------------------------------------------------------------------------------------ mod p: affine maps, mult

MOD_TYPES = "    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;\n"
MOD_HELP = "\n    T norm(W x) const { return T((x % mod + mod) % mod); }\n"
AFFINE_CPP_UPD = [("rangeAddMod", "T v", "a[i] = a[i] + v (mod p)", "Tag{1, norm(v)}"),
                  ("rangeMultMod", "T m", "a[i] = a[i] * m (mod p)", "Tag{norm(m), 0}"),
                  ("rangeAssignMod", "T v", "a[i] = v (mod p)", "Tag{0, norm(v)}"),
                  ("rangeAffineMod", "T mult, T add", "a[i] = a[i] * mult + add (mod p)", "Tag{norm(mult), norm(add)}")]
AFFINE_PY_UPD = [("rangeAddMod", "v", "a[i] = a[i] + v (mod p)", "(1, v % self.mod)"),
                 ("rangeMultMod", "m", "a[i] = a[i] * m (mod p)", "(m % self.mod, 0)"),
                 ("rangeAssignMod", "v", "a[i] = v (mod p)", "(0, v % self.mod)"),
                 ("rangeAffineMod", "mult, add", "a[i] = a[i] * mult + add (mod p)", "(mult % self.mod, add % self.mod)")]
for with_sum in (True, False):
    write({
        "name": "SparseAffineSumTree" if with_sum else "SparseAffineTree", "mod": True, "point": "mod",
        "ops": MOD_POINT + ["rangeAddMod", "rangeAffineMod", "rangeAssignMod", "rangeMultMod"] + (["rangeSumMod"] if with_sum else []),
        "desc": ["Range affine maps mod p (add, mult and assign are special cases: x -> 1x + v, mx + 0, 0x + v)"
                 + (" with range sum mod p," if with_sum else ","),
                 "plus point ops. Values are residues in [0, mod). A tag is the map x -> mul * x + add; maps compose into",
                 "the same form" + (", and a node's sum of k slots becomes mul * sum + add * k." if with_sum
                                    else ". Only leaves' values matter, so nothing is pulled.")],
        "mem": ("sm[4*log(U)]", "mul[4*log(U)] add[4*log(U)]", "links[8*log(U)]"),
        "note": VISIT + ("" if with_sum else "a leaf's value is sm (internal nodes keep no aggregate). "),
        "cpp": {
            "types": MOD_TYPES, "agg": "T sm;", "tag": "T mul, add;  // x -> mul * x + add", "ident": "Tag{1, 0}",
            "is_id": "t.mul == 1 && t.add == 0", "helpers": MOD_HELP,
            "compose": "return Tag{T(W(t.mul) * o.mul % mod), T((W(t.mul) * o.add + t.add) % mod)};",
            "apply": "        v.sm = T((W(t.mul) * v.sm + W(t.add) * (k % mod)) % mod);" if with_sum
                     else "        (void)k;\n        v.sm = T((W(t.mul) * v.sm + t.add) % mod);",
            "merge": "return Agg{T((W(a.sm) + b.sm) % mod)};" if with_sum else None,
            "leaf": "Agg{norm(v)}", "get": "res.sm", "get_note": ", in [0, mod)", "assign_note": " (mod p)",
            "updates": AFFINE_CPP_UPD,
            "queries": [("rangeSumMod", "T", "(a[l] + ... + a[r]) mod p", "res.sm")] if with_sum else [],
        },
        "py": {
            "zero": "0", "apply": "        return (t[0] * v + t[1] * k) % self.mod" if with_sum else "        return (t[0] * v + t[1]) % self.mod",
            "compose": "        return t[0] * o[0] % self.mod, (t[0] * o[1] + t[1]) % self.mod",
            "merge": "        return (a + b) % self.mod" if with_sum else None,
            "leaf": "val % self.mod", "get": "res", "get_note": ", in [0, mod)", "assign_note": " (mod p)",
            "updates": AFFINE_PY_UPD,
            "queries": [("rangeSumMod", "(a[l] + ... + a[r]) mod p", "res")] if with_sum else [],
        },
    })

write({
    "name": "SparseMultSumTree", "mod": True, "point": "mod",
    "ops": MOD_POINT + ["rangeMultMod", "rangeSumMod"],
    "desc": ["Range mult with range sum, all mod p, plus point ops. Values are residues in [0, mod). A tag is a pending",
             "multiplier; a node's sum becomes mul * sum. (Pushed in updates like any tag: never pushing would need a",
             "modular inverse at point writes, and a multiplier can be 0.)"],
    "mem": ("sm[4*log(U)]", "mul[4*log(U)]", "links[8*log(U)]"),
    "note": VISIT,
    "cpp": {
        "types": MOD_TYPES, "agg": "T sm;", "tag": "T mul;", "ident": "Tag{1}", "is_id": "t.mul == 1", "helpers": MOD_HELP,
        "compose": "return Tag{T(W(t.mul) * o.mul % mod)};",
        "apply": "        (void)k;\n        v.sm = T(W(t.mul) * v.sm % mod);",
        "merge": "return Agg{T((W(a.sm) + b.sm) % mod)};",
        "leaf": "Agg{norm(v)}", "get": "res.sm", "get_note": ", in [0, mod)", "assign_note": " (mod p)",
        "updates": [("rangeMultMod", "T m", "a[i] = a[i] * m (mod p)", "Tag{norm(m)}")],
        "queries": [("rangeSumMod", "T", "(a[l] + ... + a[r]) mod p", "res.sm")],
    },
    "py": {
        "zero": "0", "apply": "        return t * v % self.mod", "compose": "        return t * o % self.mod",
        "merge": "        return (a + b) % self.mod", "leaf": "val % self.mod", "get": "res",
        "get_note": ", in [0, mod)", "assign_note": " (mod p)",
        "updates": [("rangeMultMod", "m", "a[i] = a[i] * m (mod p)", "m % self.mod")],
        "queries": [("rangeSumMod", "(a[l] + ... + a[r]) mod p", "res")],
    },
})
