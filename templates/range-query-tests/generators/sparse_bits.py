"""Sparse (dynamic) versions of the Fenwick-tree templates: sparse.py + sparse.cpp per folder.

    python3 sparse_bits.py

Every position of [lo, hi] starts at 0. Each template keeps a few arrays of point changes (differences, or the
coefficients of a prefix-sum polynomial) and only ever needs their prefix sums.
  Python: a Fenwick tree in a dict (only touched indices exist); several arrays share one dict of lists.
  C++:    a dynamic prefix-sum tree in one pool shared by every tree of the type (resetPool() between test cases);
          a point change adds to the O(logU) nodes on its root path, a prefix sum walks one root path. Unsigned
          arithmetic wraps mod 2^64, so results are exact whenever they fit in long long, even when an
          intermediate (like x^2 for an index x near 10^12) does not.
Formulas run on offsets x = i - lo in [0, n), n = hi - lo + 1, exactly like the dense templates on 0-based indices.
"""
import os

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
PLAIN = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
MOD_POINT = ["pointAdd", "pointAssign", "pointGet"]


def header(cm, ops, mem, note):
    lines = [f"{cm} @operations: {' '.join(ops)}", f"{cm} @data-structure-type: BIT", f"{cm} @complexities:"]
    lines += [f"{cm}   {o}: log(U)" for o in ops] + [f"{cm}   build: 1"]
    node, other = mem
    lines += [f"{cm} @memory:", f"{cm}   layout: sparse", f"{cm}   node: {node}", f"{cm}   tags: none",
              f"{cm}   other: {other}",
              f"{cm}   note: per update, the O(logU) entries above each changed position; {note}. Python: a Fenwick "
              "tree in a dict (no links); C++: a dynamic prefix-sum tree in one shared node pool, call resetPool() "
              "between test cases"]
    return "\n".join(lines) + "\n"


def write(ops, mem, note, py, cpp):
    ops = sorted(ops)
    folder = "-".join(ops)
    path = os.path.join(DIR, folder)
    assert os.path.isdir(path), folder
    open(os.path.join(path, "sparse.py"), "w").write(header("#", ops, mem, note) + py)
    open(os.path.join(path, "sparse.cpp"), "w").write(header("//", ops, mem, note) + cpp)
    print("wrote", folder)


# ---------------------------------------------------------------- Python scaffolding

def py_class(name, desc, fields, kind, body):
    """fields: names of the arrays (1 -> a dict of numbers, more -> a dict of lists). kind: add / mod / xor."""
    k = len(fields)
    mod = kind == "mod"
    slots = '"lo", "hi", "n", "d"' + (', "mod"' if mod else "")
    init_mod = "\n        self.mod = mod" if mod else ""
    if k == 1:
        upd = {"add": "d[x] = d.get(x, 0) + v", "mod": "d[x] = (d.get(x, 0) + v) % mod", "xor": "d[x] = d.get(x, 0) ^ v"}[kind]
        acc = {"add": "s += d.get(x, 0)", "mod": "s += d.get(x, 0)", "xor": "s ^= d.get(x, 0)"}[kind]
        ret = "s % self.mod" if mod else "s"
        core = f'''
    # O(logU) -- {fields[0]}[x] += v at offset x
    def _add(self, x, v):
        d, n{", mod" if mod else ""} = self.d, self.n{", self.mod" if mod else ""}
        x += 1
        while x <= n:
            {upd}
            x += x & -x

    # O(logU) -- {fields[0]}[0] + ... + {fields[0]}[x] (0 for x = -1)
    def _prefix(self, x):
        d = self.d
        s = 0
        x += 1
        while x > 0:
            {acc}
            x &= x - 1
        return {ret}
'''
    else:
        args = ", ".join(f"v{j}" for j in range(k))
        red = "".join(f"\n        v{j} %= mod" for j in range(k)) if mod else ""
        bump = "\n".join(f"                e[{j}] {'= (e[' + str(j) + '] + v' + str(j) + ') % mod' if mod else '+= v' + str(j)}" for j in range(k))
        sums = ", ".join(f"s{j}" for j in range(k))
        add_s = "\n".join(f"                s{j} += e[{j}]" for j in range(k))
        ret = ", ".join(f"s{j} % mod" for j in range(k)) if mod else sums
        core = f'''
    # O(logU) -- ({", ".join(fields)})[x] += ({args}) at offset x
    def _add(self, x, {args}):
        d, n{", mod" if mod else ""} = self.d, self.n{", self.mod" if mod else ""}{red}
        x += 1
        while x <= n:
            e = d.get(x)
            if e is None:
                d[x] = [{args}]
            else:
{bump}
            x += x & -x

    # O(logU) -- prefix sums of ({", ".join(fields)}) over offsets 0..x (zeros for x = -1)
    def _prefix(self, x):
        d = self.d
        {" = ".join(f"s{j}" for j in range(k))} = 0
        x += 1
        while x > 0:
            e = d.get(x)
            if e is not None:
{add_s}
            x &= x - 1
        {"mod = self.mod" + chr(10) + "        " if mod else ""}return {ret}
'''
    return f'''
# {desc}
# Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a Fenwick tree in a
# dict keyed by offset x = i - lo, so only the O(logU) entries above changed positions exist.


class {name}:
    __slots__ = ({slots})

    # O(1)
    def __init__(self, lo, hi{", mod=1000000007" if mod else ""}):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.d = {{}}{init_mod}
{core}{body}'''


# ---------------------------------------------------------------- C++ scaffolding

def cpp_struct(name, desc, k, kind, body, using=""):
    """kind: add (unsigned, wraps), mod (residues), xor, sum (signed; point adds only)."""
    ftype = {"add": "W", "mod": "T", "xor": "T", "sum": "S"}[kind]
    mod = kind == "mod"
    upd = {"add": "f[j] += v[j]", "mod": "f[j] = T((W(f[j]) + v[j]) % mod)", "xor": "f[j] ^= v[j]", "sum": "f[j] += v[j]"}[kind]
    acc = {"add": "s[j] += f[j]", "mod": "s[j] = T((W(s[j]) + f[j]) % mod)", "xor": "s[j] ^= f[j]", "sum": "s[j] += f[j]"}[kind]
    types = {
        "add": "    using W = unsigned long long;  // wraps mod 2^64: results are exact whenever they fit in long long\n",
        "mod": "    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;\n",
        "xor": "",
        "sum": "    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n",
    }[kind]
    return f'''
// {desc}
// Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a dynamic
// prefix-sum tree over offsets x = i - lo in [0, n), in one pool shared by every {name}<T>; node 0 is the
// shared all-zeros block. T: int, long long, ...
template <typename T>
struct {name} {{
{types}{using}    using F = array<{ftype}, {k}>;
    struct Node {{ F f; int l, r; }};  // f: totals of the point changes under the node
    static inline vector<Node> pool{{Node{{}}}};  // node 0: all zeros, its children are itself
    long long lo, hi, n;
    int root = 0;{chr(10) + "    T mod;" if mod else ""}

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    {name}(long long lo, long long hi{", T mod = 1000000007" if mod else ""}) : lo(lo), hi(hi), n(hi - lo + 1){", mod(mod)" if mod else ""} {{}}

    // O(1) -- forget every node of every {name}<T>; call between test cases, then build new trees
    static void resetPool() {{ pool.resize(1); }}

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) {{ pool.reserve(nodes); }}

    static int make() {{
        pool.push_back(Node{{}});
        return (int)pool.size() - 1;
    }}

    // O(logU) -- adds v at offset x: to every node on its root path
    void add(long long x, const F& v) {{
        if (!root) root = make();
        int y = root;
        long long a = 0, b = n - 1;
        while (true) {{
            F& f = pool[y].f;
            for (int j = 0; j < {k}; j++) {upd};
            if (a == b) return;
            long long m = a + (b - a) / 2;
            bool right = x > m;
            int c = right ? pool[y].r : pool[y].l;
            if (!c) {{
                c = make();
                (right ? pool[y].r : pool[y].l) = c;
            }}
            y = c;
            if (right) a = m + 1;
            else b = m;
        }}
    }}

    // O(logU) -- totals of the point changes at offsets 0..x (zeros for x < 0)
    F prefix(long long x) const {{
        F s{{}};
        int y = x < 0 ? 0 : root;
        long long a = 0, b = n - 1;
        while (y) {{
            if (b <= x) {{  // the whole node is inside the prefix
                const F& f = pool[y].f;
                for (int j = 0; j < {k}; j++) {acc};
                break;
            }}
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else {{
                const F& f = pool[pool[y].l].f;
                for (int j = 0; j < {k}; j++) {acc};
                y = pool[y].r, a = m + 1;
            }}
        }}
        return s;
    }}
{body}}};
'''


PY_CH = '''
    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self.{add}(i, i, val - cur)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self.{add}(i, i, val - cur)
'''
CPP_CH = '''
    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) {{ T cur = pointGet(i); if (v > cur) {add}(i, i, v - cur); }}

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) {{ T cur = pointGet(i); if (v < cur) {add}(i, i, v - cur); }}
'''


def point_ops(add, chm=True):
    py = f'''
    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.{add}(i, i, delta)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        self.{add}(i, i, val - self.pointGet(i))
'''
    cpp = f'''
    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) {{ {add}(i, i, delta); }}

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {{ {add}(i, i, v - pointGet(i)); }}
'''
    if chm:
        py += PY_CH.format(add=add)
        cpp += CPP_CH.format(add=add)
    return py, cpp


# ---------------------------------------------------------------- range add, point get

pp, cp = point_ops("rangeAdd")
write(PLAIN + ["rangeAdd"], ("d[2*log(U)]", "links[4*log(U)]"), "a range add changes two differences",
      py_class("SparseRangeAddBIT", "Range add, point get: prefix sums of the difference array d[i] = a[i] - a[i - 1].",
               ["d"], "add", '''
    # O(logU) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        if l > r:
            return
        self._add(l - self.lo, v)
        if r < self.hi:
            self._add(r + 1 - self.lo, -v)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self._prefix(i - self.lo)
''' + pp),
      cpp_struct("SparseRangeAddBIT", "Range add, point get: prefix sums of the difference array d[i] = a[i] - a[i - 1].",
                 1, "add", '''
    // O(logU) -- a[i] += v for i in [l, r]
    void rangeAdd(long long l, long long r, T v) {
        if (l > r) return;
        add(l - lo, F{W(v)});
        if (r < hi) add(r + 1 - lo, F{W(0) - W(v)});
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return T(prefix(i - lo)[0]); }
''' + cp))

# ---------------------------------------------------------------- range xor, point get

write(PLAIN + ["rangeXorApply"], ("d[2*log(U)]", "links[4*log(U)]"), "a range xor changes two xor-differences",
      py_class("SparseRangeXorBIT", "Range xor, point get: prefix xors of the xor-difference array d[i] = a[i] ^ a[i - 1].",
               ["d"], "xor", '''
    # O(logU) -- a[i] ^= x for i in [l, r]
    def rangeXorApply(self, l, r, x):
        if l > r:
            return
        self._add(l - self.lo, x)
        if r < self.hi:
            self._add(r + 1 - self.lo, x)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self._prefix(i - self.lo)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        d = self.pointGet(i) ^ val
        if d:
            self.rangeXorApply(i, i, d)

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self.rangeXorApply(i, i, cur ^ val)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self.rangeXorApply(i, i, cur ^ val)
'''),
      cpp_struct("SparseRangeXorBIT", "Range xor, point get: prefix xors of the xor-difference array d[i] = a[i] ^ a[i - 1].",
                 1, "xor", '''
    // O(logU) -- a[i] ^= x for i in [l, r]
    void rangeXorApply(long long l, long long r, T x) {
        if (l > r) return;
        add(l - lo, F{x});
        if (r < hi) add(r + 1 - lo, F{x});
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return prefix(i - lo)[0]; }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        T d = pointGet(i) ^ v;
        if (d) rangeXorApply(i, i, d);
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { T cur = pointGet(i); if (v > cur) rangeXorApply(i, i, cur ^ v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { T cur = pointGet(i); if (v < cur) rangeXorApply(i, i, cur ^ v); }
'''))

# ---------------------------------------------------------------- range add + range sum: P(x) = A(x) + B(x) * x

ADDSUM_DESC = ("Range add + range sum: adding v on [l, r] changes the prefix sum P(x) = a[lo] + ... + a[x] by\n"
               "{c}   v * (x - l + 1) for x in [l, r], and the whole v * (r - l + 1) past r,\n"
               "{c} so P(x) = A(x) + B(x) * x with A, B prefix sums of two arrays of point changes.")
for mod in (False, True):
    sfx = "Mod" if mod else ""
    name = f"SparseRangeAddSumBIT{sfx}"
    ops = (MOD_POINT + ["rangeAddMod", "rangeSumMod"]) if mod else (PLAIN + ["rangeAdd", "rangeSum"])
    pp, cp = point_ops(f"rangeAdd{sfx}", chm=not mod)
    py_body = f'''
    # O(logU) -- a[i] += v{" (mod p)" if mod else ""} for i in [l, r]
    def rangeAdd{sfx}(self, l, r, v):
        if l > r:
            return
        l -= self.lo
        r -= self.lo
        a = v * (1 - l)
        self._add(l, a, v)
        if r + 1 < self.n:
            self._add(r + 1, v * (r - l + 1) - a, -v)

    # O(logU) -- a[lo] + ... + a[lo + x]{" mod p" if mod else ""} (0 for x = -1)
    def _sum(self, x):
        sa, sb = self._prefix(x)
        return {"(sa + sb * x) % self.mod" if mod else "sa + sb * x"}

    # O(logU) -- a[l] + ... + a[r]{" mod p" if mod else ""}
    def rangeSum{sfx}(self, l, r):
        if l > r:
            return 0
        return {"(self._sum(r - self.lo) - self._sum(l - 1 - self.lo)) % self.mod" if mod else "self._sum(r - self.lo) - self._sum(l - 1 - self.lo)"}

    # O(logU) -- a[i]{", in [0, mod)" if mod else ""}
    def pointGet(self, i):
        return self.rangeSum{sfx}(i, i)
''' + pp
    if mod:
        cpp_body = '''
    T norm(W x) const { return T((x % mod + mod) % mod); }

    // O(logU) -- a[i] += v (mod p) for i in [l, r]
    void rangeAddMod(long long l, long long r, T v) {
        if (l > r) return;
        l -= lo, r -= lo;
        T c = norm(v), a = norm(W(c) * norm(1 - l));
        add(l, F{a, c});
        if (r + 1 < n) add(r + 1, F{norm(W(c) * norm(r - l + 1) - a), norm(-W(c))});
    }

    // O(logU) -- (a[lo] + ... + a[lo + x]) mod p (0 for x = -1)
    T sum(long long x) const {
        F s = prefix(x);
        return norm(s[0] + W(s[1]) * norm(x));
    }

    // O(logU) -- (a[l] + ... + a[r]) mod p
    T rangeSumMod(long long l, long long r) const { return l <= r ? norm(W(sum(r - lo)) - sum(l - 1 - lo)) : T(0); }

    // O(logU) -- a[i], in [0, mod)
    T pointGet(long long i) const { return rangeSumMod(i, i); }
''' + cp
    else:
        cpp_body = '''
    // O(logU) -- a[i] += v for i in [l, r]
    void rangeAdd(long long l, long long r, T v) {
        if (l > r) return;
        l -= lo, r -= lo;
        W c = W(v), a = c * W(1 - l);
        add(l, F{a, c});
        if (r + 1 < n) add(r + 1, F{c * W(r - l + 1) - a, W(0) - c});
    }

    // O(logU) -- a[lo] + ... + a[lo + x] (0 for x = -1)
    W sum(long long x) const {
        F s = prefix(x);
        return s[0] + s[1] * W(x);
    }

    // O(logU) -- a[l] + ... + a[r]
    long long rangeSum(long long l, long long r) const { return l <= r ? (long long)(sum(r - lo) - sum(l - 1 - lo)) : 0; }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return T(rangeSum(i, i)); }
''' + cp
    write(ops, ("A[2*log(U)] B[2*log(U)]", "links[4*log(U)]"), "a range add changes two points of A and B",
          py_class(name, ADDSUM_DESC.format(c="#") + (" All mod p." if mod else ""), ["A", "B"], "mod" if mod else "add",
                   py_body),
          cpp_struct(name, ADDSUM_DESC.format(c="//") + (" All mod p." if mod else ""), 2, "mod" if mod else "add",
                     cpp_body))

# ---------------------------------------------------------------- arithmetic-sequence add, point get: a[x] = C(x) + x * S(x)

AP_DESC = ("Range add of an arithmetic sequence (and plain range add), point get{m}. Adding start + (i - l) * step on\n"
           "{c} [l, r] is adding the line c0 + c1 * x (x = i - lo), so a[x] = C(x) + x * S(x) with C, S prefix sums of\n"
           "{c} two difference arrays.")
for mod in (False, True):
    sfx = "Mod" if mod else ""
    name = f"SparseArithSeqBIT{sfx}"
    ops = (MOD_POINT + ["rangeAddArithSeqMod", "rangeAddMod"]) if mod else (PLAIN + ["rangeAdd", "rangeAddArithSeq"])
    pp, cp = point_ops(f"rangeAdd{sfx}", chm=not mod)
    py_body = f'''
    # O(logU) -- a[l + j] += start + j * step{" (mod p)" if mod else ""} for j in [0, r - l]
    def rangeAddArithSeq{sfx}(self, l, r, start, step):
        if l > r:
            return
        l -= self.lo
        r -= self.lo
        c0 = start - step * l
        self._add(l, c0, step)
        if r + 1 < self.n:
            self._add(r + 1, -c0, -step)

    # O(logU) -- a[i] += v{" (mod p)" if mod else ""} for i in [l, r]
    def rangeAdd{sfx}(self, l, r, v):
        self.rangeAddArithSeq{sfx}(l, r, v, 0)

    # O(logU) -- a[i]{", in [0, mod)" if mod else ""}
    def pointGet(self, i):
        x = i - self.lo
        c, s = self._prefix(x)
        return {"(c + s * x) % self.mod" if mod else "c + s * x"}
''' + pp
    if mod:
        cpp_body = '''
    T norm(W x) const { return T((x % mod + mod) % mod); }

    // O(logU) -- a[l + j] += start + j * step (mod p) for j in [0, r - l]
    void rangeAddArithSeqMod(long long l, long long r, T start, T step) {
        if (l > r) return;
        l -= lo, r -= lo;
        T c1 = norm(step), c0 = norm(W(start) - W(c1) * norm(l));
        add(l, F{c0, c1});
        if (r + 1 < n) add(r + 1, F{norm(-W(c0)), norm(-W(c1))});
    }

    // O(logU) -- a[i] += v (mod p) for i in [l, r]
    void rangeAddMod(long long l, long long r, T v) { rangeAddArithSeqMod(l, r, v, 0); }

    // O(logU) -- a[i], in [0, mod)
    T pointGet(long long i) const {
        F s = prefix(i - lo);
        return norm(s[0] + W(s[1]) * norm(i - lo));
    }
''' + cp
    else:
        cpp_body = '''
    // O(logU) -- a[l + j] += start + j * step for j in [0, r - l]
    void rangeAddArithSeq(long long l, long long r, T start, T step) {
        if (l > r) return;
        l -= lo, r -= lo;
        W c1 = W(step), c0 = W(start) - c1 * W(l);
        add(l, F{c0, c1});
        if (r + 1 < n) add(r + 1, F{W(0) - c0, W(0) - c1});
    }

    // O(logU) -- a[i] += v for i in [l, r]
    void rangeAdd(long long l, long long r, T v) { rangeAddArithSeq(l, r, v, 0); }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        F s = prefix(i - lo);
        return T(s[0] + s[1] * W(i - lo));
    }
''' + cp
    write(ops, ("c[2*log(U)] s[2*log(U)]", "links[4*log(U)]"), "an arithmetic-sequence add changes two points of c and s",
          py_class(name, AP_DESC.format(c="#", m=", all mod p" if mod else ""), ["c", "s"], "mod" if mod else "add", py_body),
          cpp_struct(name, AP_DESC.format(c="//", m=", all mod p" if mod else ""), 2, "mod" if mod else "add", cpp_body))

# ---------------------------------------------------------------- arithmetic-sequence add + range sum: P(x) = A + B x + C tri(x)

APSUM_DESC = ("Range add of an arithmetic sequence (and plain range add) + range sum{m}. Adding c0 + c1 * x (x = i - lo)\n"
              "{c} on [l, r] changes the prefix sum P(x) = a[lo] + ... + a[lo + x] by c0 * (x - l + 1) + c1 * (tri(x) - tri(l - 1))\n"
              "{c} for x in [l, r] (tri(k) = k(k+1)/2), and by the whole added total past r. So P(x) = A(x) + B(x) * x +\n"
              "{c} C(x) * tri(x) with A, B, C prefix sums of point changes; tri keeps every coefficient an integer.")
for mod in (False, True):
    sfx = "Mod" if mod else ""
    name = f"SparseArithSeqSumBIT{sfx}"
    ops = (MOD_POINT + ["rangeAddArithSeqMod", "rangeAddMod", "rangeSumMod"]) if mod else (
        PLAIN + ["rangeAdd", "rangeAddArithSeq", "rangeSum"])
    pp, cp = point_ops(f"rangeAdd{sfx}", chm=not mod)
    py_body = f'''
    # O(logU) -- a[l + j] += start + j * step{" (mod p)" if mod else ""} for j in [0, r - l]
    def rangeAddArithSeq{sfx}(self, l, r, start, step):
        if l > r:
            return
        l -= self.lo
        r -= self.lo
        c0, c1 = start - step * l, step  # adding c0 + c1 * x at offset x
        a = c0 * (1 - l) - c1 * _tri(l - 1)
        self._add(l, a, c0, c1)
        if r + 1 < self.n:
            total = c0 * (r - l + 1) + c1 * (_tri(r) - _tri(l - 1))
            self._add(r + 1, total - a, -c0, -c1)

    # O(logU) -- a[i] += v{" (mod p)" if mod else ""} for i in [l, r]
    def rangeAdd{sfx}(self, l, r, v):
        self.rangeAddArithSeq{sfx}(l, r, v, 0)

    # O(logU) -- a[lo] + ... + a[lo + x]{" mod p" if mod else ""} (0 for x = -1)
    def _sum(self, x):
        sa, sb, sc = self._prefix(x)
        return {"(sa + sb * x + sc * _tri(x)) % self.mod" if mod else "sa + sb * x + sc * _tri(x)"}

    # O(logU) -- a[l] + ... + a[r]{" mod p" if mod else ""}
    def rangeSum{sfx}(self, l, r):
        if l > r:
            return 0
        return {"(self._sum(r - self.lo) - self._sum(l - 1 - self.lo)) % self.mod" if mod else "self._sum(r - self.lo) - self._sum(l - 1 - self.lo)"}

    # O(logU) -- a[i]{", in [0, mod)" if mod else ""}
    def pointGet(self, i):
        return self.rangeSum{sfx}(i, i)
''' + pp
    if mod:
        cpp_body = '''
    T norm(W x) const { return T((x % mod + mod) % mod); }
    T tri(long long k) const { return norm(W((__int128)k * (k + 1) / 2 % mod)); }

    // O(logU) -- a[l + j] += start + j * step (mod p) for j in [0, r - l]
    void rangeAddArithSeqMod(long long l, long long r, T start, T step) {
        if (l > r) return;
        l -= lo, r -= lo;
        T c1 = norm(step), c0 = norm(W(start) - W(c1) * norm(l));  // adding c0 + c1 * x at offset x
        T a = norm(W(c0) * norm(1 - l) - W(c1) * tri(l - 1));
        add(l, F{a, c0, c1});
        if (r + 1 < n) {
            T total = norm(W(c0) * norm(r - l + 1) + W(c1) * norm(W(tri(r)) - tri(l - 1)));
            add(r + 1, F{norm(W(total) - a), norm(-W(c0)), norm(-W(c1))});
        }
    }

    // O(logU) -- a[i] += v (mod p) for i in [l, r]
    void rangeAddMod(long long l, long long r, T v) { rangeAddArithSeqMod(l, r, v, 0); }

    // O(logU) -- (a[lo] + ... + a[lo + x]) mod p (0 for x = -1)
    T sum(long long x) const {
        F s = prefix(x);
        return norm(s[0] + W(s[1]) * norm(x) % mod + W(s[2]) * tri(x) % mod);
    }

    // O(logU) -- (a[l] + ... + a[r]) mod p
    T rangeSumMod(long long l, long long r) const { return l <= r ? norm(W(sum(r - lo)) - sum(l - 1 - lo)) : T(0); }

    // O(logU) -- a[i], in [0, mod)
    T pointGet(long long i) const { return rangeSumMod(i, i); }
''' + cp
    else:
        cpp_body = '''
    // k(k+1)/2 mod 2^64, exact (halve the even factor first); tri(-1) = 0
    static W tri(long long k) {
        W a = W(k), b = W(k + 1);
        return a % 2 == 0 ? (a / 2) * b : a * (b / 2);
    }

    // O(logU) -- a[l + j] += start + j * step for j in [0, r - l]
    void rangeAddArithSeq(long long l, long long r, T start, T step) {
        if (l > r) return;
        l -= lo, r -= lo;
        W c1 = W(step), c0 = W(start) - c1 * W(l);  // adding c0 + c1 * x at offset x
        W a = c0 * W(1 - l) - c1 * tri(l - 1);
        add(l, F{a, c0, c1});
        if (r + 1 < n) {
            W total = c0 * W(r - l + 1) + c1 * (tri(r) - tri(l - 1));
            add(r + 1, F{total - a, W(0) - c0, W(0) - c1});
        }
    }

    // O(logU) -- a[i] += v for i in [l, r]
    void rangeAdd(long long l, long long r, T v) { rangeAddArithSeq(l, r, v, 0); }

    // O(logU) -- a[lo] + ... + a[lo + x] (0 for x = -1)
    W sum(long long x) const {
        F s = prefix(x);
        return s[0] + s[1] * W(x) + s[2] * tri(x);
    }

    // O(logU) -- a[l] + ... + a[r]
    long long rangeSum(long long l, long long r) const { return l <= r ? (long long)(sum(r - lo) - sum(l - 1 - lo)) : 0; }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return T(rangeSum(i, i)); }
''' + cp
    write(ops, ("A[2*log(U)] B[2*log(U)] C[2*log(U)]", "links[4*log(U)]"),
          "an arithmetic-sequence add changes two points of A, B and C",
          "\n\ndef _tri(k):\n    return k * (k + 1) // 2\n" +
          py_class(name, APSUM_DESC.format(c="#", m=", all mod p" if mod else ""), ["A", "B", "C"], "mod" if mod else "add",
                   py_body),
          cpp_struct(name, APSUM_DESC.format(c="//", m=", all mod p" if mod else ""), 3, "mod" if mod else "add", cpp_body))

# ---------------------------------------------------------------- point add + range sum + prefix-sum searches

write(["leftmostPrefixSumGtX", "leftmostPrefixSumGteX", "pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet",
       "rangeSum"], ("tree[1*log(U)]", "links[2*log(U)]"),
      "the prefix-sum searches need every a[i] >= 0; they return lo - 1 (-1 when lo = 0) when nothing qualifies",
      py_class("SparseBIT", "Point add, range sum, and the first index where a running sum from l reaches x.",
               ["tree"], "add", '''
    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self._add(i - self.lo, delta)

    # O(logU) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        if l > r:
            return 0
        return self._prefix(r - self.lo) - self._prefix(l - 1 - self.lo)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self.rangeSum(i, i)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        self._add(i - self.lo, val - self.pointGet(i))

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self._add(i - self.lo, val - cur)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self._add(i - self.lo, val - cur)

    # O(logU) -- smallest offset x with prefix(x) >= target (> target if strict), or n. Binary lifting over the
    # Fenwick tree; needs every a[i] >= 0.
    def _lowerBound(self, target, strict):
        d, n = self.d, self.n
        pos = acc = 0
        step = 1 << (n.bit_length() - 1)
        while step:
            nxt = pos + step
            if nxt <= n:
                v = acc + d.get(nxt, 0)
                if v < target or (strict and v == target):
                    pos, acc = nxt, v
            step >>= 1
        return pos

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] >= x, or lo - 1. Needs every a[i] >= 0.
    def leftmostPrefixSumGteX(self, l, r, x):
        i = max(l, self.lo + self._lowerBound(self._prefix(l - 1 - self.lo) + x, False))
        return i if i <= r else self.lo - 1

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] > x, or lo - 1. Needs every a[i] >= 0.
    def leftmostPrefixSumGtX(self, l, r, x):
        i = max(l, self.lo + self._lowerBound(self._prefix(l - 1 - self.lo) + x, True))
        return i if i <= r else self.lo - 1
'''),
      cpp_struct("SparseBIT", "Point add, range sum, and the first index where a running sum from l reaches x.", 1, "sum", '''
    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { add(i - lo, F{S(delta)}); }

    // O(logU) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) const { return l <= r ? prefix(r - lo)[0] - prefix(l - 1 - lo)[0] : S(0); }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return T(rangeSum(i, i)); }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) { pointAdd(i, v - pointGet(i)); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { T cur = pointGet(i); if (v > cur) pointAdd(i, v - cur); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { T cur = pointGet(i); if (v < cur) pointAdd(i, v - cur); }

    // O(logU) -- smallest offset x with prefix(x) >= target (> target if strict), or n. Needs every a[i] >= 0.
    long long lowerBound(S target, bool strict) const {
        auto reached = [&](S v) { return strict ? v > target : v >= target; };
        if (!reached(pool[root].f[0])) return n;
        int y = root;
        long long a = 0, b = n - 1;
        S acc = 0;
        while (a < b) {  // node 0 is a block of zeros: the answer is its first position
            long long m = a + (b - a) / 2;
            S left = acc + pool[pool[y].l].f[0];
            if (reached(left)) y = pool[y].l, b = m;
            else acc = left, y = pool[y].r, a = m + 1;
        }
        return a;
    }

    // O(logU) -- first i in [l, r] with a[l] + ... + a[i] >= x, or lo - 1. Needs every a[i] >= 0.
    long long leftmostPrefixSumGteX(long long l, long long r, T x) const {
        long long i = max(l, lo + lowerBound(prefix(l - 1 - lo)[0] + x, false));
        return i <= r ? i : lo - 1;
    }

    // O(logU) -- first i in [l, r] with a[l] + ... + a[i] > x, or lo - 1. Needs every a[i] >= 0.
    long long leftmostPrefixSumGtX(long long l, long long r, T x) const {
        long long i = max(l, lo + lowerBound(prefix(l - 1 - lo)[0] + x, true));
        return i <= r ? i : lo - 1;
    }
'''))
