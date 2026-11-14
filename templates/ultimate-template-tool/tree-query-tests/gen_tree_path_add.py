"""Writes the single-log path update templates: tree-queries/path-add-fenwick-{node,edge},
path-add-mod-fenwick-{node,edge} and path-xor-apply-fenwick-{node,edge}, each template.{py,cpp}.

A wrapped range template (gen_tree.py) adds to a path in O(log^2 n): O(log n) chain pieces, a range add each. When the
queries are one value or a subtree (not a path), an add can be marked instead, because it can be taken back: put +x at
both ends of the path and take it back at their lca and at the node above the lca. Then

    the value of a node  =  its starting value + every mark inside its subtree

since a node on the path has exactly one end below it, and a node off the path has none or both ends and the lca. For
edges (an edge is kept at its lower end) the marks are +x at both ends and -2x at the lca. A subtree is one stretch of
positions, so "every mark inside a subtree" is one Fenwick range sum: a path add is O(log n).

A subtree's sum counts a mark at y once for every node between y and the subtree's top, so a second Fenwick tree
weighs each mark by its depth. Subtree adds are kept apart, as plain "add over a stretch of positions" (two more
Fenwick trees), and one value changes through a mark at it taken back at its parent.

Xor works the same way (it is its own inverse): the marks are x at both ends, the lca and the node above it. What a
subtree's xor sees of a mark depends on whether an odd number of nodes lie between it and the top, so the marks are
kept by depth parity, and the stretch updates by position parity.

There is no single-log path sum here: a path update with a path query needs the O(log^2 n) templates.

    python3 gen_tree_path_add.py           # write
    python3 gen_tree_path_add.py --check   # exit 1 if a file on disk differs from what this would write
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_tree as G  # noqa: E402
import gen_tree_shape as shape  # noqa: E402
from gen_tree_bitset import note  # noqa: E402
from gen_tree_depth import red  # noqa: E402

DIR = G.DIR
KIND = "euler-fenwick"

PY_ADD = '''\
class Tree:
@CTOR_NOTE@
    def __init__(self, @CTOR@):
@LAYOUT@@VALUES@
@ARRAYS_NOTE@
        first = [0] * (n + 1)
        for i, v in enumerate(order):
            first[i + 1] = @RED(first[i] + base[v])@
        self.base, self.first = base, first
@TREES_NOTE@
        self.m1, self.m2, self.d1, self.d2 = ([0] * (n + 1) for _ in range(4))@KEEP_MOD@

    # tree[p] += x, tree a Fenwick tree over the positions (nothing when p is past the last position)
    def _add(self, tree, p, x):
        n = self.n@GET_MOD@
        p += 1
        while p <= n:
            tree[p] = @RED(tree[p] + x)@
            p += p & -p

    # the sum of tree's entries at positions 0..k (0 when k is -1)
    def _sum(self, tree, k):
        res = 0
        k += 1
        while k > 0:
            res += tree[k]
            k -= k & -k
        return res

    # a mark of x at node v: every @THING@ from v up to the root has x more inside its subtree
    def _mark(self, v, x):
        p = self.pos[v]
        self._add(self.m1, p, x)
        self._add(self.m2, p, x * self.dep[v])

    # the value kept at node v grows by x (it alone): a mark at v, taken back at its parent
    def _bump(self, v, x):
        self._mark(v, x)
        if v != self.root:
            self._mark(self.par[v], -x)

    # every value at positions l..r grows by x (nothing for an empty stretch, l > r)
    def _spread(self, l, r, x):
        if l > r:
            return
        self._add(self.d1, l, x)
        self._add(self.d1, r + 1, -x)
        self._add(self.d2, l, x * l)
        self._add(self.d2, r + 1, -x * (r + 1))

    # the value kept at node v: its starting value, the marks inside its subtree, the stretch adds that cover it
    def _value(self, v):
        l, m1 = self.pos[v], self.m1
        inside = self._sum(m1, l + self.sz[v] - 1) - self._sum(m1, l - 1)
        return @RED(self.base[v] + inside + self._sum(self.d1, l))@

    # what the stretch adds gave the values at positions 0..k, in all (0 when k is -1)
    def _spreadUpTo(self, k):
        return (k + 1) * self._sum(self.d1, k) - self._sum(self.d2, k)
'''
CPP_ADD = '''\
template <typename T>
struct Tree {
@MEMBERS@
@TYPES@
@ARRAYS_NOTE@
    HotVector<C> base, first;
@TREES_NOTE@
    HotVector<C> m1, m2, d1, d2;

@CTOR_NOTE@
@CTOR@ {
@LAYOUT@
@VALUES@        first.assign(n + 1, 0);
        for (int i = 0; i < n; i++) first[i + 1] = fit((W)first[i] + (W)base[order[i]]);
        m1.assign(n + 1, 0), m2 = d1 = d2 = m1;
    }

@FIT@

    // tree[p] += x, tree a Fenwick tree over the positions (nothing when p is past the last position)
    LEETCODE_NO_SANITIZE void add(HotVector<C>& tree, int p, W x) @CONST@{
        C f = fit(x);
        for (p++; p <= n; p += p & -p) @PUT@
    }

    // the sum of tree's entries at positions 0..k (0 when k is -1)
    LEETCODE_NO_SANITIZE W sum(const HotVector<C>& tree, int k) const {
        W res = 0;
        for (k++; k > 0; k -= k & -k) res += tree[k];
        return res;
    }

    // a mark of x at node v: every @THING@ from v up to the root has x more inside its subtree
    LEETCODE_NO_SANITIZE void mark(int v, W x) {
        add(m1, pos[v], x);
        add(m2, pos[v], x * (W)dep[v]);
    }

    // the value kept at node v grows by x (it alone): a mark at v, taken back at its parent
    LEETCODE_NO_SANITIZE void bump(int v, W x) {
        mark(v, x);
        if (v != root) mark(par[v], 0 - x);
    }

    // every value at positions l..r grows by x (nothing for an empty stretch, l > r)
    LEETCODE_NO_SANITIZE void spread(int l, int r, W x) {
        if (l > r) return;
        add(d1, l, x), add(d1, r + 1, 0 - x);
        add(d2, l, x * (W)l), add(d2, r + 1, 0 - x * (W)(r + 1));
    }

    // the value kept at node v: its starting value, the marks inside its subtree, the stretch adds that cover it
    LEETCODE_NO_SANITIZE C valueOf(int v) const {
        int l = pos[v];
        return fit((W)base[v] + sum(m1, l + sz[v] - 1) - sum(m1, l - 1) + sum(d1, l));
    }

    // what the stretch adds gave the values at positions 0..k, in all (0 when k is -1)
    LEETCODE_NO_SANITIZE W spreadUpTo(int k) const { return (W)(long long)(k + 1) * sum(d1, k) - sum(d2, k); }
'''
PY_XOR = '''\
class Tree:
@CTOR_NOTE@
    def __init__(self, @CTOR@):
@LAYOUT@@VALUES@
@ARRAYS_NOTE@
        first = [0] * (n + 1)
        for i, v in enumerate(order):
            first[i + 1] = first[i] ^ base[v]
        self.base, self.first = base, first
@TREES_NOTE@
        self.marks = ([0] * (n + 1), [0] * (n + 1))
        self.diffs = ([0] * (n + 1), [0] * (n + 1))

    # tree[p] ^= x, tree a Fenwick tree over the positions (nothing when p is past the last position)
    def _flip(self, tree, p, x):
        n = self.n
        p += 1
        while p <= n:
            tree[p] ^= x
            p += p & -p

    # the xor of tree's entries at positions 0..k (0 when k is -1)
    def _xor(self, tree, k):
        res = 0
        k += 1
        while k > 0:
            res ^= tree[k]
            k -= k & -k
        return res

    # a mark of x at node v: every @THING@ from v up to the root has x once more inside its subtree
    def _mark(self, v, x):
        self._flip(self.marks[self.dep[v] & 1], self.pos[v], x)

    # the value kept at node v is xored with x (it alone): a mark at v, taken back at its parent
    def _bump(self, v, x):
        self._mark(v, x)
        if v != self.root:
            self._mark(self.par[v], x)

    # every value at positions l..r is xored with x (nothing for an empty stretch, l > r)
    def _spread(self, l, r, x):
        if l > r:
            return
        self._flip(self.diffs[l & 1], l, x)
        self._flip(self.diffs[(r + 1) & 1], r + 1, x)

    # the value kept at node v: its starting value, the marks inside its subtree, the stretch xors that cover it
    def _value(self, v):
        l = self.pos[v]
        r = l + self.sz[v] - 1
        xor, (m0, m1), (d0, d1) = self._xor, self.marks, self.diffs
        return self.base[v] ^ xor(m0, r) ^ xor(m0, l - 1) ^ xor(m1, r) ^ xor(m1, l - 1) ^ xor(d0, l) ^ xor(d1, l)

    # what the stretch xors gave the values at positions 0..k, xored together (0 when k is -1): a stretch that starts
    # at j covers an odd number of them when j and k are both even or both odd
    def _spreadUpTo(self, k):
        return self._xor(self.diffs[k & 1], k)
'''
CPP_XOR = '''\
template <typename T>
struct Tree {
@MEMBERS@
    using U = unsigned long long;  // (xor is done on the bits: a negative value keeps its sign through it)
@ARRAYS_NOTE@
    HotVector<U> base, first;
@TREES_NOTE@
    HotVector<U> marks[2], diffs[2];

@CTOR_NOTE@
@CTOR@ {
@LAYOUT@
@VALUES@        first.assign(n + 1, 0);
        for (int i = 0; i < n; i++) first[i + 1] = first[i] ^ base[order[i]];
        marks[0].assign(n + 1, 0), marks[1] = diffs[0] = diffs[1] = marks[0];
    }

    LEETCODE_NO_SANITIZE static U bitsOf(T x) { return (U)(long long)x; }

    // tree[p] ^= x, tree a Fenwick tree over the positions (nothing when p is past the last position)
    LEETCODE_NO_SANITIZE void flip(HotVector<U>& tree, int p, U x) const {
        for (p++; p <= n; p += p & -p) tree[p] ^= x;
    }

    // the xor of tree's entries at positions 0..k (0 when k is -1)
    LEETCODE_NO_SANITIZE U xorOf(const HotVector<U>& tree, int k) const {
        U res = 0;
        for (k++; k > 0; k -= k & -k) res ^= tree[k];
        return res;
    }

    // a mark of x at node v: every @THING@ from v up to the root has x once more inside its subtree
    LEETCODE_NO_SANITIZE void mark(int v, U x) { flip(marks[dep[v] & 1], pos[v], x); }

    // the value kept at node v is xored with x (it alone): a mark at v, taken back at its parent
    LEETCODE_NO_SANITIZE void bump(int v, U x) {
        mark(v, x);
        if (v != root) mark(par[v], x);
    }

    // every value at positions l..r is xored with x (nothing for an empty stretch, l > r)
    LEETCODE_NO_SANITIZE void spread(int l, int r, U x) {
        if (l > r) return;
        flip(diffs[l & 1], l, x), flip(diffs[(r + 1) & 1], r + 1, x);
    }

    // the value kept at node v: its starting value, the marks inside its subtree, the stretch xors that cover it
    LEETCODE_NO_SANITIZE U valueOf(int v) const {
        int l = pos[v], r = l + sz[v] - 1;
        return base[v] ^ xorOf(marks[0], r) ^ xorOf(marks[0], l - 1) ^ xorOf(marks[1], r) ^ xorOf(marks[1], l - 1) ^
               xorOf(diffs[0], l) ^ xorOf(diffs[1], l);
    }

    // what the stretch xors gave the values at positions 0..k, xored together (0 when k is -1): a stretch that starts
    // at j covers an odd number of them when j and k are both even or both odd
    LEETCODE_NO_SANITIZE U spreadUpTo(int k) const { return xorOf(diffs[k & 1], k); }
'''


def make(edge, mode):
    """mode: "add", "mod" (add with a fixed MOD) or "xor"."""
    t = "edge" if edge else "node"
    mod, xor = mode == "mod", mode == "xor"
    folder = {"add": "path-add-fenwick-", "mod": "path-add-mod-fenwick-", "xor": "path-xor-apply-fenwick-"}[mode] + t
    vals, val_word, x = ("edge weights", "weight", "w") if edge else ("node values", "val", "x")
    at = "a - b" if edge else "node"
    nodes = ("a", "b") if edge else ("node",)
    M = "Mod" if mod else ""
    costs, py_ops, cpp_ops = {}, [], []

    def add_op(name, args, types, ret, doc, py_body, cpp_body, where=nodes):
        full = t + name
        costs[full] = "log(N)"
        py_ops.append(G.comment("#", "log(N)", doc) + f"    def {full}(self, {', '.join(list(where) + args)}):\n" + py_body)
        decl = ", ".join([f"int {v}" for v in where] + [f"{ty} {a}" for ty, a in zip(types, args)])
        cpp_ops.append(G.comment("//", "log(N)", doc) + f"    LEETCODE_NO_SANITIZE {ret} {full}({decl}) {{\n" + cpp_body + "    }\n")

    if edge:
        py_ops.append("    # the lower end of the edge a - b, the node its weight is kept under (a and b in either order)\n"
                      "    def _edge(self, name, a, b):\n"
                      "        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):\n"
                      "            self._bad(name, a, b)\n"
                      "        if self.par[a] == b:\n            return a\n"
                      "        if self.par[b] == a:\n            return b\n"
                      '        raise IndexError(f"{name}: needs an edge between a and b, got {a} and {b}")\n')
        cpp_ops.append("    // the lower end of the edge a - b, the node its weight is kept under (a and b in either order)\n"
                       "    LEETCODE_NO_SANITIZE int edgeAt(const char* name, int a, int b) const {\n"
                       "        if (a < lo || a > hi || b < lo || b > hi) bad(name);\n"
                       "        if (par[a] == b) return a;\n        if (par[b] == a) return b;\n"
                       '        throw out_of_range(string(name) + ": needs an edge between a and b");\n    }\n')
    either = "; a and b are the edge's two ends, in either order" if edge else ""
    in_mod = " (kept in [0, MOD))" if mod else ""

    def here(name):
        if edge:
            return f'        v = self._edge("{t}{name}", a, b)\n', f'        int v = edgeAt("{t}{name}", a, b);\n'
        return G.py_check(t + name, nodes), G.cpp_check(t + name, nodes)

    v = "v" if edge else "node"
    # how C++ turns an argument into what the trees keep, and a kept value into what it returns
    kept = (lambda e: f"bitsOf({e})") if xor else (lambda e: f"wide({e})")
    out = (lambda e: f"(T)(long long){e}")

    # ---- one value
    p, c = here("Get")
    add_op("Get", [], [], "T", f"{val_word}({at}){in_mod}{either}", p + f"        return self._value({v})\n",
           c + f"        return {out(f'valueOf({v})')};\n")
    p, c = here("Assign")
    if xor:
        add_op("Assign", [x], ["T"], "void", f"{val_word}({at}) = {x}{either}",
               p + f"        self._bump({v}, {x} ^ self._value({v}))\n", c + f"        bump({v}, bitsOf({x}) ^ valueOf({v}));\n")
        p, c = here("Add")
        add_op("Add", [x], ["T"], "void", f"{val_word}({at}) += {x}{either}",
               p + f"        now = self._value({v})\n        self._bump({v}, (now + {x}) ^ now)\n",
               c + f"        U now = valueOf({v});\n        bump({v}, (now + bitsOf({x})) ^ now);\n")
    else:
        add_op("Assign", [x], ["T"], "void", f"{val_word}({at}) = {x}{' % MOD' if mod else ''}{either}",
               p + f"        self._bump({v}, {x} - self._value({v}))\n", c + f"        bump({v}, wide({x}) - (W)valueOf({v}));\n")
        p, c = here("Add")
        add_op("Add", [x], ["T"], "void",
               f"{val_word}({at}) = ({val_word} + {x}) % MOD{either}" if mod else f"{val_word}({at}) += {x}{either}",
               p + f"        self._bump({v}, {x})\n", c + f"        bump({v}, wide({x}));\n")
    if not mod:
        for name, sign in (("Chmax", ">"), ("Chmin", "<")):
            p, c = here(name)
            diff_py = f"{x} ^ now" if xor else f"{x} - now"
            diff_cpp = f"bitsOf({x}) ^ bitsOf(now)" if xor else f"wide({x}) - wide(now)"
            add_op(name, [x], ["T"], "void", f"{val_word}({at}) = {name[2:].lower()}({val_word}, {x}){either}",
                   p + f"        now = self._value({v})\n        if {x} {sign} now:\n            self._bump({v}, {diff_py})\n",
                   c + f"        T now = {out(f'valueOf({v})')};\n        if ({x} {sign} now) bump({v}, {diff_cpp});\n")

    # ---- a path: marks at its two ends, taken back at the lca (and, for nodes, at the node above it)
    if xor:
        name, how_py, how_cpp = "PathXORApply", f"{val_word} ^= {x}", f"U d = bitsOf({x});"
        back_py = ("        self._mark(c, x)\n        if c != self.root:\n            self._mark(self.par[c], x)\n" if not edge else "")
        back_cpp = ("        mark(c, d);\n        if (c != root) mark(par[c], d);\n" if not edge else "")
        lca_py = "        c = self._lca(a, b)\n" if not edge else "        # (an edge is kept at its lower end: the lca's own marks would cancel)\n"
        lca_cpp = "        int c = lcaOf(a, b);\n" if not edge else "        // (an edge is kept at its lower end: the lca's own marks would cancel)\n"
    else:
        name = f"PathAdd{M}"
        how_py = f"{val_word} = ({val_word} + {x}) % MOD" if mod else f"{val_word} += {x}"
        how_cpp = f"W d = (W)fit(wide({x}));"
        if edge:
            back_py = f"        self._mark(c, -2 * {x})  # (an edge is kept at its lower end: the lca's own stays out)\n"
            back_cpp = "        mark(c, 0 - d - d);  // (an edge is kept at its lower end: the lca's own stays out)\n"
        else:
            back_py = f"        self._mark(c, -{x})\n        if c != self.root:\n            self._mark(self.par[c], -{x})\n"
            back_cpp = "        mark(c, 0 - d);\n        if (c != root) mark(par[c], 0 - d);\n"
        lca_py, lca_cpp = "        c = self._lca(a, b)\n", "        int c = lcaOf(a, b);\n"
    nothing = " (nothing when a == b)" if edge else ""
    add_op(name, [x], ["T"], "void", f"{how_py} for every {t} on the path a..b{nothing}",
           G.py_check(t + name, ("a", "b")) + lca_py + f"        self._mark(a, {x})\n        self._mark(b, {x})\n" + back_py,
           G.cpp_check(t + name, ("a", "b")) + f"        {how_cpp}\n" + lca_cpp + "        mark(a, d), mark(b, d);\n" + back_cpp,
           where=("a", "b"))

    # ---- a subtree: one stretch of positions (an edge template leaves out the edge above node: one position later)
    skip = " + 1" if edge else ""
    if xor:
        name, how = "SubtreeXORApply", f"{val_word} ^= {x}"
        amount_py, amount_cpp = x, f"bitsOf({x})"
    else:
        name, how = f"SubtreeAdd{M}", (f"{val_word} = ({val_word} + {x}) % MOD" if mod else f"{val_word} += {x}")
        amount_py, amount_cpp = x, f"(W)fit(wide({x}))"
    add_op(name, [x], ["T"], "void", f"{how} for every {t} in node's subtree",
           G.py_check(t + name, ("node",)) + "        l = self.pos[node]\n"
           + f"        self._spread(l{skip}, l + self.sz[node] - 1, {amount_py})\n",
           G.cpp_check(t + name, ("node",)) + f"        spread(pos[node]{skip}, pos[node] + sz[node] - 1, {amount_cpp});\n",
           where=("node",))
    none = "; 0 when node is a leaf (no edges)" if edge else ""
    lo_first, lo_spread = ("l + 1", "l") if edge else ("l", "l - 1")
    if xor:
        parity = "(self.dep[node] + 1) & 1" if edge else "self.dep[node] & 1"
        parity_cpp = "(dep[node] + 1) & 1" if edge else "dep[node] & 1"
        why = ("a mark at y is seen once for every " + ("edge between y and node" if edge else "node from y up to node")
               + ": an odd number of times when y's depth is " + ("the other kind (even / odd) than" if edge else "even or odd like") + " node's")
        add_op("SubtreeXOR", [], [], "T", f"XOR of the {vals} in node's subtree{none}",
               G.py_check(t + "SubtreeXOR", ("node",)) + "        l = self.pos[node]\n        r = l + self.sz[node] - 1\n"
               + note("#", why, 8) + f"\n        m = self.marks[{parity}]\n"
               + f"        return (self.first[r + 1] ^ self.first[{lo_first}] ^ self._xor(m, r) ^ self._xor(m, l - 1)\n"
               + f"                ^ self._spreadUpTo(r) ^ self._spreadUpTo({lo_spread}))\n",
               G.cpp_check(t + "SubtreeXOR", ("node",)) + "        int l = pos[node], r = l + sz[node] - 1;\n"
               + note("//", why, 8) + f"\n        const HotVector<U>& m = marks[{parity_cpp}];\n"
               + f"        return (T)(long long)(first[r + 1] ^ first[{lo_first}] ^ xorOf(m, r) ^ xorOf(m, l - 1) ^ spreadUpTo(r) ^\n"
               + f"                              spreadUpTo({lo_spread}));\n", where=("node",))
    else:
        tail = ", mod MOD" if mod else ""
        top = "self.dep[node]" if edge else "(self.dep[node] - 1)"
        top_cpp = "dep[node]" if edge else "dep[node] - 1"
        why = ("a mark at y counts once for every " + ("edge between y and node" if edge else "node from y up to node")
               + ": depth(y) - " + ("depth(node)" if edge else "(depth(node) - 1)") + " times")
        add_op(f"SubtreeSum{M}", [], [], "T", f"sum of the {vals} in node's subtree{tail}{none}",
               G.py_check(f"{t}SubtreeSum{M}", ("node",)) + "        l = self.pos[node]\n        r = l + self.sz[node] - 1\n"
               + note("#", why, 8) + "\n"
               + "        count = self._sum(self.m1, r) - self._sum(self.m1, l - 1)\n"
               + "        weighed = self._sum(self.m2, r) - self._sum(self.m2, l - 1)\n"
               + f"        return (self.first[r + 1] - self.first[{lo_first}] + weighed - {top} * count\n"
               + f"                + self._spreadUpTo(r) - self._spreadUpTo({lo_spread})){' % self.mod' if mod else ''}\n",
               G.cpp_check(f"{t}SubtreeSum{M}", ("node",)) + "        int l = pos[node], r = l + sz[node] - 1;\n"
               + note("//", why, 8) + "\n"
               + "        W count = sum(m1, r) - sum(m1, l - 1), weighed = sum(m2, r) - sum(m2, l - 1);\n"
               + f"        return (T)(long long)fit((W)first[r + 1] - (W)first[{lo_first}] + weighed - (W)(long long)({top_cpp}) * count +\n"
               + f"                                 spreadUpTo(r) - spreadUpTo({lo_spread}));\n", where=("node",))

    costs_all = dict(costs)
    costs_all.update({op: shape.COSTS[op][0] for op in G.SHAPE_OPS})

    def header(cm, ext):
        lines = [
            "Template by https://github.com/ishaanbuildsthings",
            f"{G.URL}/{folder}/template.{ext}",
            "@operations: " + " ".join(sorted(costs_all)),
            f"@data-structure-type: {KIND}",
            "@complexities:",
            *[f"  {op}: {costs_all[op]}" for op in sorted(costs_all)],
            "  build: N",
            "@memory:",
            "  layout: none",
            "  node: " + ("marks[2*N] diffs[2*N]" if xor else "m1[1*N] m2[1*N] d1[1*N] d2[1*N]"),
            "  tags: none",
            f"  other: base[1*N] first[1*N] {G.LAYOUT_ARRAYS}",
        ]
        return "".join(f"{cm} {line}\n" for line in lines)

    op_word, back = ("xor", "x again") if xor else ("add", "-x")
    ends = ("x at both ends of the path" + ("" if xor else ", and -2x at their lca") if edge else
            f"x at both ends of the path, and {back} at their lca and at the node above the lca")
    why_edge = (" (an edge is kept at its lower end, so the lca's own position must not gain anything"
                + (": with xor the two ends' marks already cancel there)" if xor else ")")) if edge else ""
    one = "edge" if edge else "node"
    how = ("How it works: one heavy-light pass gives every node a position, so that each subtree is one stretch of positions "
           f"(pos[node] .. pos[node] + sz[node] - 1). A path {op_word} is not spread over the path: it leaves marks, {ends}"
           f"{why_edge}. The value of {'an' if edge else 'a'} {one} is then its starting value "
           + ("xored with" if xor else "plus") + " every mark inside its subtree: "
           f"{'an' if edge else 'a'} {one} on the path has exactly one end below it, and one off the path has no mark below "
           "it or a set that cancels. \"Every mark inside a subtree\" is one Fenwick range " + ("xor" if xor else "sum")
           + ", so a path update is O(log n), where a wrapped range template needs O(log^2 n). "
           + ("For a subtree's xor a mark at y counts once per " + one + " between y and the subtree's top, so only the "
              "marks at the right depth parity are seen: the marks are kept in two trees, by even and odd depth. Subtree "
              "updates are kept apart as \"xor over a stretch of positions\" (two more trees, by even and odd position)."
              if xor else
              "For a subtree's sum a mark at y counts once per " + one + " between y and the subtree's top, so a second "
              "tree keeps each mark times its depth. Subtree adds are kept apart as \"add over a stretch of positions\" "
              "(two more trees).")
           + " One value changes through a mark at it, taken back at its parent. There is no single-log path "
           + ("xor" if xor else "sum") + " here: a path update together with a path query needs the O(log^2 n) templates.")
    wrap_note = {"#": "", "//": "" if xor else (
        "The arithmetic is done mod 2^64 (unsigned), because a product on the way can pass 64 bits though the answer fits: "
        "the answers are exact whenever they fit the value type." if not mod else
        "MOD can be anything below 2^62: products are taken in 128 bits.")}
    info = type("R", (), {"extra_names": ["mod"] if mod else [], "cls": ""})
    sig_names = ("edges, root" if edge else "edges, root, vals") + (", mod" if mod else "")
    example = ", mod" if mod else ""
    start_cpp = (lambda e: f"bitsOf({e})") if xor else (lambda e: f"fit(wide({e}))")
    if edge:
        doc_py = G.fill_doc(G.PY_DOC_EDGE, "#", info, sig_names, example, "edge")
        doc_cpp = G.fill_doc(G.CPP_DOC_EDGE, "//", info, sig_names, example, "edge")
        py_ctor, cpp_ctor = "edges, root", "const vector<vector<E>>& edges, int root"
        py_values = ("        for e in edges:\n"
                     "            if len(e) != 3:\n"
                     '                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")\n'
                     "        base = [0] * (hi + 1)\n"
                     "        for e in edges:\n"
                     + red("            base[e[0] if par[e[0]] == e[1] else e[1]] = @RED(e[2])@\n", mod, "mod"))
        cpp_values = ("        for (const auto& e : edges)\n"
                      '            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");\n'
                      "        base.assign(hi + 1, 0);\n"
                      "        for (const auto& e : edges) {\n"
                      "            int a = (int)e[0], b = (int)e[1];\n"
                      f"            base[par[a] == b ? a : b] = {start_cpp('(T)e[2]')};\n"
                      "        }\n")
        kept_word = "the weight of the edge above v at the start (the root has none)"
    else:
        doc_py = G.fill_doc(G.PY_DOC, "#", info, sig_names, example)
        doc_cpp = G.fill_doc(G.CPP_DOC, "//", info, sig_names, example)
        py_ctor, cpp_ctor = "edges, root, vals", "const vector<vector<E>>& edges, int root, const vector<T>& vals"
        py_values = G.PY_VALS + ("        base = [x % mod for x in vals]\n" if mod else "        base = list(vals)\n")
        cpp_values = ("        if ((int)vals.size() != hi + 1)\n"
                      '            throw invalid_argument("Tree: vals[node] is node\'s value, so nodes " + nodes + " need vals.size() = " +\n'
                      "                                   to_string(hi + 1) + \", got \" + to_string(vals.size()));\n"
                      "        base.assign(hi + 1, 0);\n"
                      f"        for (int v = lo; v <= hi; v++) base[v] = {start_cpp('vals[v]')};\n")
        kept_word = "v's value at the start"
    bad = "an edge has no weight" if edge else "vals has the wrong length"
    arrays = (f"base[v]: {kept_word} (it never changes: every update is kept in the trees). first[i]: the starting values at "
              "positions below i, " + ("xored together." if xor else "summed."))
    if xor:
        trees = ("Fenwick trees over the positions (1-based), kept with xor. marks[0], marks[1]: the marks at nodes of even "
                 "and of odd depth. diffs[0], diffs[1]: where a stretch xor starts and stops, at even and at odd positions.")
    else:
        trees = ("Four Fenwick trees over the positions (1-based). m1: the marks. m2: each mark times its node's depth. d1, "
                 "d2: the stretch adds as differences (d1) and differences times their position (d2), which together give "
                 "the sum over a stretch.")
    thing = "edge" if edge else "node"
    py_marks = {
        "@CTOR_NOTE@": note("#", "O(n) -- builds the layout and the sums of the starting values; raises ValueError when the "
                            f"edges are not one tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@ARRAYS_NOTE@": note("#", arrays, 8), "@TREES_NOTE@": note("#", trees, 8), "@THING@": thing,
        "@CTOR@": py_ctor + (", mod=10**9 + 7" if mod else ""), "@LAYOUT@": shape.py_layout_body(), "@VALUES@": py_values,
        "@KEEP_MOD@": "\n        self.mod = mod" if mod else "", "@GET_MOD@": "\n        mod = self.mod" if mod else "",
    }
    sig = f"    template <typename E = int> Tree({cpp_ctor}{', long long mod = 1000000007' if mod else ''})"
    init = " : root(root)" + (", modulus(mod)" if mod else "")
    if len(sig + init) > 118:
        sig = (f"    template <typename E = int> Tree({cpp_ctor},\n" + " " * 36 + "long long mod = 1000000007)") if mod else sig
        init = "\n        : root(root)" + (", modulus(mod)" if mod else "")
    if mod:
        types = ("    using C = long long;  // a kept number, in [0, MOD)\n"
                 "    using W = __int128;  // wide enough for a product of two of them\n"
                 "    long long modulus;")
        fit = ("    // x mod MOD, in [0, MOD)\n"
               "    LEETCODE_NO_SANITIZE C fit(W x) const {\n"
               "        x %= modulus;\n"
               "        return (C)(x < 0 ? x + modulus : x);\n"
               "    }\n"
               "    LEETCODE_NO_SANITIZE static W wide(T x) { return (W)(long long)x; }")
        put, const = "{\n            tree[p] += f;\n            if (tree[p] >= modulus) tree[p] -= modulus;\n        }", "const "
    else:
        types = ("    // every number is kept mod 2^64: a product on the way can pass 64 bits though the answer fits, and unsigned\n"
                 "    // arithmetic wraps without harm, so an answer is exact whenever it fits the value type\n"
                 "    using C = unsigned long long;\n"
                 "    using W = unsigned long long;")
        fit = ("    // (the MOD version of this template reduces here; this one keeps every number as it is, mod 2^64)\n"
               "    LEETCODE_NO_SANITIZE static C fit(W x) { return x; }\n"
               "    LEETCODE_NO_SANITIZE static W wide(T x) { return (W)(long long)x; }")
        put, const = "tree[p] += f;", "const "
    cpp_marks = {
        "@CTOR_NOTE@": note("//", "O(n) -- builds the layout and the sums of the starting values; throws invalid_argument when "
                            f"the edges are not one tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@ARRAYS_NOTE@": note("//", arrays, 4), "@TREES_NOTE@": note("//", trees, 4), "@THING@": thing,
        "@CTOR@": sig + init, "@LAYOUT@": shape.cpp_layout_body(), "@VALUES@": cpp_values,
        "@MEMBERS@": shape.cpp_members().rstrip("\n"), "@TYPES@": types, "@FIT@": fit, "@PUT@": put, "@CONST@": const,
    }

    def doc_with(doc, cm):
        cut = doc.index(f"{cm} How it works")
        extra = f"{cm}\n" + G.wrap(cm, wrap_note[cm]) if wrap_note[cm] else ""
        return doc[:cut] + G.wrap(cm, how) + extra

    def fill(text, marks):
        for k, val in marks.items():
            text = text.replace(k, val)
        return text

    if xor:
        body = fill(PY_XOR, py_marks)
        cpp_body = fill(CPP_XOR, cpp_marks)
    else:
        cut = PY_ADD.index("    # the sum of tree's entries")  # (before it: the constructor and _add hold mod in a local)
        body = red(fill(PY_ADD[:cut], py_marks), mod, "mod") + red(fill(PY_ADD[cut:], py_marks), mod)
        if not mod:  # ("x = x + y" reads better as "x += y")
            body = re.sub(r"^(\s+)(\S+) = \2 \+ (.+)$", r"\1\2 += \3", body, flags=re.M)
        cpp_body = fill(CPP_ADD, cpp_marks)
    py = (header("#", "py") + "\nfrom bisect import bisect_left\n\n\n" + doc_with(doc_py, "#") + body
          + "\n" + "\n".join(py_ops) + "\n" + shape.py_shape_methods())
    cpp = (header("//", "cpp") + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n" + shape.FAST_NOTE
           + shape.PRELUDE + doc_with(doc_cpp, "//") + cpp_body
           + "\n" + "\n".join(cpp_ops) + "\n" + shape.cpp_shape_methods().rstrip("\n") + "\n};\n")
    return folder, py, cpp


def sources():
    out = {}
    for mode in ("add", "mod", "xor"):
        for edge in (False, True):
            folder, py, cpp = make(edge, mode)
            for name, text in (("template.py", py), ("template.cpp", cpp)):
                out[os.path.join(folder, name)] = shape.tidy(text, f"{folder}/{name}")
    return out


def main():
    check = "--check" in sys.argv
    stale = []
    for rel, text in sources().items():
        path = os.path.join(DIR, rel)
        if os.path.exists(path) and open(path, encoding="utf-8").read() == text:
            continue
        stale.append(rel)
        if not check:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w", encoding="utf-8").write(text)
    if check:
        for rel in stale:
            print(f"FAIL  tree-queries/{rel}: differs from what gen_tree_path_add.py writes (rerun it)")
        print(f"{len(stale)} stale path-update files" if stale else "single-log path update templates are fresh")
        sys.exit(1 if stale else 0)
    print(f"{len(sources())} path-update files, {len(stale)} written")


if __name__ == "__main__":
    main()
