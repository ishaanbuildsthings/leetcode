"""Writes the single-log path hashing templates: tree-queries/path-hash-fenwick-node and path-hash-fenwick-edge, each
template.{py,cpp}.

A wrapped range template (gen_tree.py) hashes a path in O(log^2 n): O(log n) chain pieces, a range hash each. With
one-value updates and subtree adds there is a single-log way, the one path-static-* uses with fixed values, kept in
Fenwick trees instead of prefix arrays. With h(w) = the hash of w's value and B the base, two sums along root..v:

    up(v)   = the sum of h(w) * B^depth(w)        a difference of two is a stretch read upwards, times B^(its top's depth)
    low(v)  = the sum of h(w) * B^-depth(w)       low(v) * B^depth(v) is the hash of root..v read downwards

A value sits at its node's position and is taken back just past that node's subtree, so a prefix up to pos[v] is the sum
along root..v: one value changing is two point writes in each tree.

Adding x to a whole subtree (top node t, every node u below it gets h + x): up(u) grows by
x * (B^(depth(u) + 1) - B^depth(t)) / (B - 1), a geometric sum. The part with depth(t) is the same for every u in the
subtree, so it goes into the tree like a value; the part with depth(u) is (the total added to u) * B / (B - 1) *
B^depth(u), and the total added to u is one more Fenwick tree (which the values need anyway). low(u) the same way.

    python3 gen_tree_hash_fenwick.py           # write
    python3 gen_tree_hash_fenwick.py --check   # exit 1 if a file on disk differs from what this would write
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_tree as G  # noqa: E402
import gen_tree_shape as shape  # noqa: E402
from gen_tree_bitset import note  # noqa: E402

DIR = G.DIR
KIND = "euler-fenwick"

PY_TOP = '''\
import random
from bisect import bisect_left

_HP = (1 << 61) - 1  # hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


'''

PY = '''\
class Tree:
@CTOR_NOTE@
    def __init__(self, @CTOR@):
@LAYOUT@@VALUES@
        deepest = dep[bfs[-1]]
        pw, ipw = [1] * (deepest + 2), [1] * (deepest + 2)
        inverse = pow(_HB, _HP - 2, _HP)
        for d in range(1, deepest + 2):
            pw[d] = pw[d - 1] * _HB % _HP
            ipw[d] = ipw[d - 1] * inverse % _HP
@TREES_NOTE@
        up, low = [0] * (n + 2), [0] * (n + 2)
        for v in bfs:
@SKIP_ROOT@            h = (val[v] + _HO) % _HP
            i = pos[v] + 1
            j = i + sz[v]
            x = h * pw[dep[v]] % _HP
            up[i] += x
            up[j] -= x
            x = h * ipw[dep[v]] % _HP
            low[i] += x
            low[j] -= x
        for i in range(1, n + 1):
            up[i] %= _HP
            low[i] %= _HP
            j = i + (i & -i)
            if j <= n:
                up[j] += up[i]
                low[j] += low[i]
        self.val, self.up, self.low, self.added, self.pw, self.ipw = val, up, low, [0] * (n + 2), pw, ipw
        # 1 / (B - 1) and B / (B - 1): what a geometric sum of powers of the base is divided by (see SubtreeAdd)
        self.geo = pow(_HB - 1, _HP - 2, _HP)
        self.geoB = self.geo * _HB % _HP

    # add x at every position i..j-1 of a tree read by prefixes: x goes in at i and is taken back at j
    def _spread(self, tree, i, j, x, mod):
        n = self.n
        while i <= n:
            tree[i] += x
            if mod:
                tree[i] %= mod
            i += i & -i
        while j <= n:
            tree[j] -= x
            if mod:
                tree[j] %= mod
            j += j & -j

    # the sum of positions 1..i of a tree
    def _upTo(self, tree, i):
        res = 0
        while i > 0:
            res += tree[i]
            i -= i & -i
        return res

    # the value kept at node v right now (what it was given, plus every subtree add that reached it)
    def _value(self, v):
        return self.val[v] + self._upTo(self.added, self.pos[v] + 1)

    # the value kept at node v changes by d
    def _change(self, v, d):
        i = self.pos[v] + 1
        j = i + self.sz[v]
        k = self.dep[v]
        self.val[v] += d
        d %= _HP
        self._spread(self.up, i, j, d * self.pw[k] % _HP, _HP)
        self._spread(self.low, i, j, d * self.ipw[k] % _HP, _HP)

    # the sum of hash(value) * base^depth over the @VALS@ on the path root..v
    def _upSum(self, v):
        i = self.pos[v] + 1
        return (self._upTo(self.up, i) + self._upTo(self.added, i) % _HP * self.geoB % _HP * self.pw[self.dep[v]]) % _HP

    # the hash of the @VALS@ on the path root..v, read downwards
    def _downHash(self, v):
        i = self.pos[v] + 1
        k = self.dep[v]
        low = (self._upTo(self.low, i) - self._upTo(self.added, i) % _HP * self.geo % _HP * self.ipw[k]) % _HP
        return low * self.pw[k] % _HP

    # the hash of the @VALS@ read walking a -> b
    def _hash(self, a, b):
        dep = self.dep
        c = self._lca(a, b)
        d = dep[c]
@HEAD@
        m = dep[b] - d  # how many values the way down from the lca holds
        return ((head - self._downHash(c)) * self.pw[m] + self._downHash(b)) % _HP
'''

CPP = '''\
template <typename T>
struct Tree {
@MEMBERS@
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;  // what sums are kept in
    using U64 = unsigned long long;
    HotVector<T> val;  // @VAL_NOTE@
@TREES_NOTE@
    HotVector<U64> up, low, pw, ipw;
    HotVector<S> added;
    U64 geo, geoB;  // 1 / (B - 1) and B / (B - 1): what a geometric sum of powers of the base is divided by

    // hashes are mod the prime 2^61 - 1, with a base picked at random each run (so no test can be built against it)
    static U64 rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
    static constexpr U64 HP = (1ULL << 61) - 1;
    static U64 HB() {
        static U64 b = (1ULL << 40) + rnd() % (HP - (1ULL << 41));
        return b;
    }
    LEETCODE_NO_SANITIZE static U64 hmul(U64 a, U64 b) {
        unsigned __int128 c = (unsigned __int128)a * b;
        U64 r = (U64)(c & HP) + (U64)(c >> 61);
        r = (r & HP) + (r >> 61);
        return r >= HP ? r - HP : r;
    }
    LEETCODE_NO_SANITIZE static U64 hadd(U64 a, U64 b) { return a + b >= HP ? a + b - HP : a + b; }
    LEETCODE_NO_SANITIZE static U64 hsub(U64 a, U64 b) { return a >= b ? a - b : a + HP - b; }
    LEETCODE_NO_SANITIZE static U64 hpow(U64 b, U64 e) {
        U64 r = 1;
        for (; e > 0; e >>= 1, b = hmul(b, b))
            if (e & 1) r = hmul(r, b);
        return r;
    }
    // a number (a value, or a change to one) mod the prime, in [0, HP)
    LEETCODE_NO_SANITIZE static U64 hnorm(S d) {
        long long r = (long long)(d % (S)HP);
        return r < 0 ? (U64)(r + (long long)HP) : (U64)r;
    }
    // the hash of one value: v + an offset random per run, so no common value is 0 (a 0 in front would vanish)
    static U64 hval(T v) {
        static U64 off = 1 + rnd() % (HP - 1);
        return hadd(hnorm((S)v), off);
    }

@CTOR_NOTE@
    template <typename E = int> Tree(@CTOR@) : root(root) {
@LAYOUT@
@VALUES@        int deepest = dep[bfs[n - 1]];
        U64 base = HB(), inverse = hpow(base, HP - 2);  // base^(HP - 2) is 1 / base
        pw.assign(deepest + 2, 1), ipw.assign(deepest + 2, 1);
        for (int d = 1; d < deepest + 2; d++) pw[d] = hmul(pw[d - 1], base), ipw[d] = hmul(ipw[d - 1], inverse);
        geo = hpow(base - 1, HP - 2), geoB = hmul(geo, base);
        up.assign(n + 2, 0), low.assign(n + 2, 0), added.assign(n + 2, 0);
        for (int k = 0; k < n; k++) {
            int v = bfs[k], i = pos[v] + 1, j = i + sz[v];
@SKIP_ROOT@            U64 h = hval(val[v]), x = hmul(h, pw[dep[v]]), y = hmul(h, ipw[dep[v]]);
            up[i] = hadd(up[i], x), up[j] = hsub(up[j], x);
            low[i] = hadd(low[i], y), low[j] = hsub(low[j], y);
        }
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) up[j] = hadd(up[j], up[i]), low[j] = hadd(low[j], low[i]);
        }
    }

    // add x at every position i..j-1 of a tree read by prefixes: x goes in at i and is taken back at j
    LEETCODE_NO_SANITIZE void spread(HotVector<U64>& tree, int i, int j, U64 x) {
        for (; i <= n; i += i & -i) tree[i] = hadd(tree[i], x);
        for (; j <= n; j += j & -j) tree[j] = hsub(tree[j], x);
    }

    // the sum of positions 1..i of a tree
    LEETCODE_NO_SANITIZE U64 upTo(const HotVector<U64>& tree, int i) const {
        U64 res = 0;
        for (; i > 0; i -= i & -i) res = hadd(res, tree[i]);
        return res;
    }

    // the total every subtree add has given the node at position i - 1
    LEETCODE_NO_SANITIZE S addedTo(int i) const {
        S res = 0;
        for (; i > 0; i -= i & -i) res += added[i];
        return res;
    }

    // the value kept at node v right now (what it was given, plus every subtree add that reached it)
    LEETCODE_NO_SANITIZE T valueOf(int v) const { return (T)((S)val[v] + addedTo(pos[v] + 1)); }

    // the value kept at node v changes by d
    LEETCODE_NO_SANITIZE void change(int v, S d) {
        int i = pos[v] + 1, j = i + sz[v], k = dep[v];
        val[v] = (T)((S)val[v] + d);
        U64 x = hnorm(d);
        spread(up, i, j, hmul(x, pw[k]));
        spread(low, i, j, hmul(x, ipw[k]));
    }

    // the sum of hash(value) * base^depth over the @VALS@ on the path root..v
    LEETCODE_NO_SANITIZE U64 upSum(int v) const {
        int i = pos[v] + 1;
        return hadd(upTo(up, i), hmul(hmul(hnorm(addedTo(i)), geoB), pw[dep[v]]));
    }

    // the hash of the @VALS@ on the path root..v, read downwards
    LEETCODE_NO_SANITIZE U64 downHash(int v) const {
        int i = pos[v] + 1, k = dep[v];
        return hmul(hsub(upTo(low, i), hmul(hmul(hnorm(addedTo(i)), geo), ipw[k])), pw[k]);
    }

    // the hash of the @VALS@ read walking a -> b
    LEETCODE_NO_SANITIZE U64 hashOf(int a, int b) const {
        int c = lcaOf(a, b), d = dep[c];
@HEAD@
        int m = dep[b] - d;  // how many values the way down from the lca holds
        return hadd(hmul(hsub(head, downHash(c)), pw[m]), downHash(b));
    }
'''


def make(edge):
    t = "edge" if edge else "node"
    folder = f"path-hash-fenwick-{t}"
    vals, val_word, x = ("edge weights", "weight", "w") if edge else ("node values", "val", "x")
    at = "a - b" if edge else "node"
    nodes = ("a", "b") if edge else ("node",)
    costs, py_ops, cpp_ops = {}, [], []

    def add_op(name, args, types, ret, doc, py_body, cpp_body, where=nodes, const=False):
        full = t + name
        costs[full] = "log(N)"
        py_ops.append(G.comment("#", "log(N)", doc) + f"    def {full}(self, {', '.join(list(where) + args)}):\n" + py_body)
        decl = ", ".join([f"int {v}" for v in where] + [f"{ty} {a}" for ty, a in zip(types, args)])
        cpp_ops.append(G.comment("//", "log(N)", doc)
                       + f"    LEETCODE_NO_SANITIZE {ret} {full}({decl}){' const' if const else ''} {{\n" + cpp_body + "    }\n")

    # ---- one node / one edge: where it is kept (an edge: under its lower end)
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

    def here(name):  # the node a one-node / one-edge op acts on, checked
        if edge:
            return f'        v = self._edge("{t}{name}", a, b)\n', f'        int v = edgeAt("{t}{name}", a, b);\n'
        return G.py_check(t + name, nodes) + "        v = node\n", G.cpp_check(t + name, nodes) + "        int v = node;\n"

    p, c = here("Get")
    add_op("Get", [], [], "T", f"{val_word}({at}){either}", p + "        return self._value(v)\n", c + "        return valueOf(v);\n",
           const=True)
    p, c = here("Assign")
    add_op("Assign", [x], ["T"], "void", f"{val_word}({at}) = {x}{either}",
           p + f"        self._change(v, {x} - self._value(v))\n", c + f"        change(v, (S){x} - (S)valueOf(v));\n")
    p, c = here("Add")
    add_op("Add", [x], ["T"], "void", f"{val_word}({at}) += {x}{either}",
           p + f"        self._change(v, {x})\n", c + f"        change(v, (S){x});\n")
    for name, sign in (("Chmax", ">"), ("Chmin", "<")):
        p, c = here(name)
        add_op(name, [x], ["T"], "void", f"{val_word}({at}) = {name[2:].lower()}({val_word}, {x}){either}",
               p + f"        now = self._value(v)\n        if {x} {sign} now:\n            self._change(v, {x} - now)\n",
               c + f"        T now = valueOf(v);\n        if ({x} {sign} now) change(v, (S){x} - (S)now);\n")

    # ---- a subtree add: one stretch of positions (an edge template leaves out the edge above node)
    first, top = ("self.pos[node] + 2", "self.dep[node] + 1") if edge else ("self.pos[node] + 1", "self.dep[node]")
    cfirst, ctop = ("pos[node] + 2", "dep[node] + 1") if edge else ("pos[node] + 1", "dep[node]")
    leaf = " (nothing when node is a leaf: no edges)" if edge else ""
    add_op("SubtreeAdd", [x], ["T"], "void", f"{val_word} += {x} for every {'edge' if edge else 'node'} in node's subtree{leaf}",
           G.py_check(f"{t}SubtreeAdd", ("node",))
           + f"        i = {first}\n        j = self.pos[node] + 1 + self.sz[node]\n"
           + ("        if i >= j:\n            return\n" if edge else "")
           + f"        top = {top}  # the depth of the shallowest value changed\n"
           f"        self._spread(self.added, i, j, {x}, 0)\n"
           f"        m = {x} % _HP\n"
           "        # each sum grows by a geometric sum of powers; here, the part that is the same all over the subtree\n"
           "        self._spread(self.up, i, j, -m * self.geo % _HP * self.pw[top] % _HP, _HP)\n"
           "        self._spread(self.low, i, j, m * self.geoB % _HP * self.ipw[top] % _HP, _HP)\n",
           G.cpp_check(f"{t}SubtreeAdd", ("node",))
           + f"        int i = {cfirst}, j = pos[node] + 1 + sz[node];\n"
           + ("        if (i >= j) return;\n" if edge else "")
           + f"        int top = {ctop};  // the depth of the shallowest value changed\n"
           f"        for (int k = i; k <= n; k += k & -k) added[k] += (S){x};\n"
           f"        for (int k = j; k <= n; k += k & -k) added[k] -= (S){x};\n"
           f"        U64 m = hnorm((S){x});\n"
           "        // each sum grows by a geometric sum of powers; here, the part that is the same all over the subtree\n"
           "        spread(up, i, j, hsub(0, hmul(hmul(m, geo), pw[top])));\n"
           "        spread(low, i, j, hmul(hmul(m, geoB), ipw[top]));\n", where=("node",))

    # ---- a path
    none0 = "; 0 when a == b (no edges)" if edge else ""
    same = " (two paths with no edges are equal)" if edge else ""

    def path_op(name, ret, doc, py_body, cpp_body, where=("a", "b")):
        add_op(name, [], [], ret, doc, G.py_check(t + name, where) + py_body, G.cpp_check(t + name, where) + cpp_body,
               where=where, const=True)

    path_op("PathHash", "unsigned long long",
            f"hash of the {vals} read a -> b (mod 2^61 - 1, random base): equal sequences hash equal{none0}",
            "        return self._hash(a, b)\n", "        return hashOf(a, b);\n")
    path_op("PathHashReversed", "unsigned long long", f"hash of the {vals} read b -> a (equal to {t}PathHash(b, a)){none0}",
            "        return self._hash(b, a)\n", "        return hashOf(b, a);\n")
    path_op("PathIsPalindrome", "bool",
            f"do the {vals} read the same a -> b and b -> a?" + (" (True when a == b: no edges)" if edge else ""),
            "        return self._hash(a, b) == self._hash(b, a)\n", "        return hashOf(a, b) == hashOf(b, a);\n")
    path_op("PathsEqual", "bool", f"do the {vals} read a -> b equal those read c -> d?{same}",
            "        return self._dist(a, b) == self._dist(c, d) and self._hash(a, b) == self._hash(c, d)\n",
            "        return distOf(a, b) == distOf(c, d) && hashOf(a, b) == hashOf(c, d);\n", where=("a", "b", "c", "d"))

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
            "  node: up[1*N] low[1*N] added[1*N]",
            "  tags: none",
            f"  other: val[1*N] pw[1*N] ipw[1*N] {G.LAYOUT_ARRAYS}",
            "  note: three Fenwick trees over the positions; pw / ipw are as long as the tree is deep",
        ]
        return "".join(f"{cm} {line}\n" for line in lines)

    one = "edge" if edge else "node"
    how = ("How it works: one heavy-light pass gives every node a position, so that each subtree is one stretch of positions "
           f"(pos[node] .. pos[node] + sz[node] - 1). Two sums are kept along the path from the root to every node v: the sum "
           f"of hash({one}) * base^depth, and the sum of hash({one}) / base^depth. The difference of two of the first is the "
           "hash of the stretch between, read upwards, times base^(the depth of its top), which an inverse power takes off; "
           "the second times base^depth(v) is the hash of root..v read downwards. A path a -> b is the way up to the lca and "
           "the way down from it, joined like any two hashes. Each term sits at its node's position in a Fenwick tree and is "
           "taken back just past that node's subtree, so a prefix up to pos[v] is the sum along root..v, and one value "
           "changing is two point writes: one log for everything, where chain pieces would take two. A subtree add makes "
           "each sum grow by a geometric sum of powers of the base: the part that is the same all over the subtree goes "
           "into the trees like a value, and the rest is (the total added to that node, a third Fenwick tree) times a power "
           "that depends on the node's depth only. No path updates, and no assign over a subtree.")
    info = type("R", (), {"extra_names": [], "cls": ""})
    trees = ("Three Fenwick trees over positions 1..n, each read by prefixes (a term goes in at its node's position and is "
             f"taken back just past that node's subtree, so the prefix up to pos[v] sums over the path root..v). up: "
             f"hash({one}) * base^depth. low: hash({one}) / base^depth. added: what subtree adds gave, so its prefix up to "
             "pos[v] is the total added to v. pw[d] = base^d and ipw[d] = 1 / base^d.")
    bad = "an edge has no weight" if edge else "vals has the wrong length"
    if edge:
        doc_py = G.fill_doc(G.PY_DOC_EDGE, "#", info, "edges, root", "", "edge")
        doc_cpp = G.fill_doc(G.CPP_DOC_EDGE, "//", info, "edges, root", "", "edge")
        py_ctor, cpp_ctor = "edges, root", "const vector<vector<E>>& edges, int root"
        py_values = ("        for e in edges:\n"
                     "            if len(e) != 3:\n"
                     '                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")\n'
                     "        val = [0] * (hi + 1)  # val[v]: the weight of the edge above v (the root has none)\n"
                     "        for e in edges:\n"
                     "            val[e[0] if par[e[0]] == e[1] else e[1]] = e[2]\n")
        cpp_values = ("        for (const auto& e : edges)\n"
                      '            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");\n'
                      "        val.assign(hi + 1, T(0));\n"
                      "        for (const auto& e : edges) {\n"
                      "            int a = (int)e[0], b = (int)e[1];\n"
                      "            val[par[a] == b ? a : b] = (T)e[2];\n"
                      "        }\n")
        py_skip = "            if v == root:\n                continue  # (no edge above the root)\n"
        cpp_skip = "            if (v == root) continue;  // (no edge above the root)\n"
        py_head = ("        # the way up: the edges below the lca, the shallowest one level under it\n"
                   "        head = (self._upSum(a) - self._upSum(c)) * self.ipw[d + 1] % _HP")
        cpp_head = ("        // the way up: the edges below the lca, the shallowest one level under it\n"
                    "        U64 head = hmul(hsub(upSum(a), upSum(c)), ipw[d + 1]);")
        val_note = "val[v]: the weight given to the edge above v (the root has none), before any subtree add"
    else:
        doc_py = G.fill_doc(G.PY_DOC, "#", info, "edges, root, vals", "")
        doc_cpp = G.fill_doc(G.CPP_DOC, "//", info, "edges, root, vals", "")
        py_ctor, cpp_ctor = "edges, root, vals", "const vector<vector<E>>& edges, int root, const vector<T>& vals"
        py_values = G.PY_VALS + "        val = list(vals)  # what each node was given, before any subtree add\n"
        cpp_values = ("        if ((int)vals.size() != hi + 1)\n"
                      '            throw invalid_argument("Tree: vals[node] is node\'s value, so nodes " + nodes + " need vals.size() = " +\n'
                      "                                   to_string(hi + 1) + \", got \" + to_string(vals.size()));\n"
                      "        val.assign(vals.begin(), vals.end());\n")
        py_skip = cpp_skip = ""
        py_head = ("        # the way up: a .. lca, the lca being its top\n"
                   "        above = self._upSum(self.par[c]) if c != self.root else 0\n"
                   "        head = (self._upSum(a) - above) * self.ipw[d] % _HP")
        cpp_head = ("        // the way up: a .. lca, the lca being its top\n"
                    "        U64 head = hmul(hsub(upSum(a), c == root ? 0 : upSum(par[c])), ipw[d]);")
        val_note = "what each node was given, before any subtree add"
    marks = {"@VALS@": vals}
    py_marks = {
        "@CTOR_NOTE@": note("#", "O(n) -- builds the layout and the Fenwick trees; raises ValueError when the edges are not one "
                            f"tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@TREES_NOTE@": note("#", trees, 8), "@CTOR@": py_ctor, "@LAYOUT@": shape.py_layout_body(),
        "@VALUES@": py_values, "@SKIP_ROOT@": py_skip, "@HEAD@": py_head,
    }
    cpp_marks = {
        "@CTOR_NOTE@": note("//", "O(n) -- builds the layout and the Fenwick trees; throws invalid_argument when the edges are "
                            f"not one tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@TREES_NOTE@": note("//", trees, 4), "@CTOR@": cpp_ctor, "@LAYOUT@": shape.cpp_layout_body(),
        "@VALUES@": cpp_values, "@SKIP_ROOT@": cpp_skip, "@HEAD@": cpp_head, "@MEMBERS@": shape.cpp_members().rstrip("\n"),
        "@VAL_NOTE@": val_note,
    }

    def doc_with(doc, cm):
        cut = doc.index(f"{cm} How it works")
        return doc[:cut] + G.wrap(cm, how)

    def fill(text, extra):
        for k, v in {**marks, **extra}.items():
            text = text.replace(k, v)
        return text

    py = (header("#", "py") + "\n" + PY_TOP + doc_with(doc_py, "#") + fill(PY, py_marks)
          + "\n" + "\n".join(py_ops) + "\n" + shape.py_shape_methods())
    cpp = (header("//", "cpp") + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n" + shape.FAST_NOTE
           + shape.PRELUDE + doc_with(doc_cpp, "//") + fill(CPP, cpp_marks)
           + "\n" + "\n".join(cpp_ops) + "\n" + shape.cpp_shape_methods().rstrip("\n") + "\n};\n")
    return folder, py, cpp


def sources():
    out = {}
    for edge in (False, True):
        folder, py, cpp = make(edge)
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
            print(f"FAIL  tree-queries/{rel}: differs from what gen_tree_hash_fenwick.py writes (rerun it)")
        print(f"{len(stale)} stale single-log path hashing files" if stale else "single-log path hashing templates are fresh")
        sys.exit(1 if stale else 0)
    print(f"{len(sources())} single-log path hashing files, {len(stale)} written")


if __name__ == "__main__":
    main()
