"""Shared scaffolding for the sparse Fenwick-style templates (used by sparse_bits.py and sparse_more.py).

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

from note_lang import write_template

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
              "tree in a dict (no child pointers); C++: a dynamic prefix-sum tree in one shared node pool, call resetPool() "
              "between test cases"]
    return "\n".join(lines) + "\n"


def write(ops, mem, note, py, cpp):
    ops = sorted(ops)
    folder = "-".join(ops)
    path = os.path.join(DIR, folder)
    assert os.path.isdir(path), folder
    write_template(os.path.join(path, "sparse.py"), header("#", ops, mem, note) + py)
    write_template(os.path.join(path, "sparse.cpp"), header("//", ops, mem, note) + cpp)
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
