"""Writes the fixed-value path templates with O(1) queries: tree-queries/path-static-node and path-static-edge, each
template.{py,cpp}.

With no updates, a sum, a xor and a hash along the path from the root to a node are prefix arrays, and a path a..b is
two or three reads of them once the lca is known. The lca is O(1) with the shape template's table (a sparse table over
the positions, n log n memory: gen_tree_shape.py's "table" variant), so every query here is O(1).

    sum   nodes: sumTo[a] + sumTo[b] - sumTo[lca] - sumTo[parent(lca)]      edges: sumTo[a] + sumTo[b] - 2 * sumTo[lca]
    xor   nodes: xorTo[a] ^ xorTo[b] ^ val[lca]                             edges: xorTo[a] ^ xorTo[b]
    hash  the way up (a -> lca) from up[]: the sum of hash(value) * base^depth along root..v, so a difference of two
          is the hash of the stretch between them times base^(depth of its top), taken off with an inverse power;
          the way down (lca -> b) from down[]: the hash of root..v read downwards

(The wrapped sparse-table and prefix-sum folders already give path min / max / gcd / and / or / sum without updates in
O(log n): a table over the layout would cost the same log, so they have no template here.)

    python3 gen_tree_static.py           # write
    python3 gen_tree_static.py --check   # exit 1 if a file on disk differs from what this would write
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_tree as G  # noqa: E402
import gen_tree_shape as shape  # noqa: E402
from gen_tree_bitset import note  # noqa: E402

DIR = G.DIR
KIND = "root-prefix"
LAYOUT_ARRAYS = f"{shape.LAYOUT_ARRAYS} {shape.OTHER_ARRAYS[1]}"

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
@ARRAYS_NOTE@
        deepest = max(dep[v] for v in order)
        pw, ipw = [1] * (deepest + 2), [1] * (deepest + 2)
        inverse = pow(_HB, _HP - 2, _HP)
        for d in range(1, deepest + 2):
            pw[d] = pw[d - 1] * _HB % _HP
            ipw[d] = ipw[d - 1] * inverse % _HP
        sumTo, xorTo, down, up = [0] * (hi + 1), [0] * (hi + 1), [0] * (hi + 1), [0] * (hi + 1)
        sumAt, xorAt = [0] * (n + 1), [0] * (n + 1)
        for i, v in enumerate(order):
            x = val[v]
            sumAt[i + 1] = sumAt[i] + x
            xorAt[i + 1] = xorAt[i] ^ x
            if v == root:
@ROOT@
            p = par[v]
            h = (x + _HO) % _HP
            sumTo[v] = sumTo[p] + x
            xorTo[v] = xorTo[p] ^ x
            down[v] = (down[p] * _HB + h) % _HP
            up[v] = (up[p] + h * pw[dep[v]]) % _HP
        self.val, self.sumTo, self.xorTo, self.sumAt, self.xorAt = val, sumTo, xorTo, sumAt, xorAt
        self.down, self.up, self.pw, self.ipw = down, up, pw, ipw

    # the hash of the @VALS@ read walking a -> b
    def _hash(self, a, b):
        dep, down = self.dep, self.down
        c = self._lca(a, b)
        d = dep[c]
@HEAD@
        m = dep[b] - d  # how many values the way down from the lca holds
        return ((head - down[c]) * self.pw[m] + down[b]) % _HP
'''

CPP = '''\
template <typename T>
struct Tree {
@MEMBERS@
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;  // what sums are kept in
    using U64 = unsigned long long;
@ARRAYS_NOTE@
    HotVector<T> val, xorTo, xorAt;
    HotVector<S> sumTo, sumAt;
    HotVector<U64> down, up, pw, ipw;

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
    // the hash of one value: v + an offset random per run, so no common value is 0 (a 0 in front would vanish)
    static U64 hval(T v) {
        static U64 off = 1 + rnd() % (HP - 1);
        long long r = (long long)v % (long long)HP;
        return hadd(r < 0 ? (U64)(r + (long long)HP) : (U64)r, off);
    }

@CTOR_NOTE@
    template <typename E = int> Tree(@CTOR@) : root(root) {
@LAYOUT@
@VALUES@        int deepest = 0;
        for (int i = 0; i < n; i++) deepest = max(deepest, dep[order[i]]);
        U64 inverse = 1, base = HB();
        for (U64 e = HP - 2, b = base; e > 0; e >>= 1, b = hmul(b, b))  // base^(HP - 2) is 1 / base
            if (e & 1) inverse = hmul(inverse, b);
        pw.assign(deepest + 2, 1), ipw.assign(deepest + 2, 1);
        for (int d = 1; d < deepest + 2; d++) pw[d] = hmul(pw[d - 1], base), ipw[d] = hmul(ipw[d - 1], inverse);
        sumTo.assign(hi + 1, 0), xorTo.assign(hi + 1, 0), down.assign(hi + 1, 0), up.assign(hi + 1, 0);
        sumAt.assign(n + 1, 0), xorAt.assign(n + 1, 0);
        for (int i = 0; i < n; i++) {
            int v = order[i], p = par[v];
            T x = val[v];
            sumAt[i + 1] = sumAt[i] + x, xorAt[i + 1] = xorAt[i] ^ x;
            if (v == root) {
@ROOT@
            }
            U64 h = hval(x);
            sumTo[v] = sumTo[p] + x, xorTo[v] = xorTo[p] ^ x;
            down[v] = hadd(hmul(down[p], base), h), up[v] = hadd(up[p], hmul(h, pw[dep[v]]));
        }
    }

    // the hash of the @VALS@ read walking a -> b
    LEETCODE_NO_SANITIZE U64 hashOf(int a, int b) const {
        int c = lcaOf(a, b), d = dep[c];
@HEAD@
        int m = dep[b] - d;  // how many values the way down from the lca holds
        return hadd(hmul(hsub(head, down[c]), pw[m]), down[b]);
    }
'''


def make(edge):
    t = "edge" if edge else "node"
    folder = f"path-static-{t}"
    vals, val_word = ("edge weights", "weight") if edge else ("node values", "val")
    at = "a - b" if edge else "node"
    nodes = ("a", "b") if edge else ("node",)
    costs, py_ops, cpp_ops = {}, [], []

    def add_op(name, ret, doc, py_body, cpp_body, where):
        full = t + name
        costs[full] = "1"
        py_ops.append(G.comment("#", "1", doc) + f"    def {full}(self, {', '.join(where)}):\n" + G.py_check(full, where) + py_body)
        decl = ", ".join(f"int {v}" for v in where)
        cpp_ops.append(G.comment("//", "1", doc) + f"    LEETCODE_NO_SANITIZE {ret} {full}({decl}) const {{\n"
                       + G.cpp_check(full, where) + cpp_body + "    }\n")

    # ---- one value
    if edge:
        full = "edgeGet"
        costs[full] = "1"
        py_ops.append("    # O(1) -- weight(a - b); a and b are the edge's two ends, in either order\n"
                      f"    def {full}(self, a, b):\n" + G.py_check(full, ("a", "b"))
                      + "        if self.par[a] == b:\n            return self.val[a]\n"
                      "        if self.par[b] == a:\n            return self.val[b]\n"
                      f'        raise IndexError(f"{full}: needs an edge between a and b, got {{a}} and {{b}}")\n')
        cpp_ops.append("    // O(1) -- weight(a - b); a and b are the edge's two ends, in either order\n"
                       f"    LEETCODE_NO_SANITIZE T {full}(int a, int b) const {{\n" + G.cpp_check(full, ("a", "b"))
                       + "        if (par[a] == b) return val[a];\n        if (par[b] == a) return val[b];\n"
                       f'        throw out_of_range("{full}: needs an edge between a and b");\n    }}\n')
    else:
        add_op("Get", "T", "val(node)", "        return self.val[node]\n", "        return val[node];\n", ("node",))

    # ---- a path
    none0 = "; 0 when a == b (no edges)" if edge else ""
    if edge:
        add_op("PathSum", "S", f"sum of the {vals} on the path a..b{none0}",
               "        sumTo = self.sumTo\n        return sumTo[a] + sumTo[b] - 2 * sumTo[self._lca(a, b)]\n",
               "        return sumTo[a] + sumTo[b] - 2 * sumTo[lcaOf(a, b)];\n", ("a", "b"))
        add_op("PathXOR", "T", f"xor of the {vals} on the path a..b{none0}",
               "        return self.xorTo[a] ^ self.xorTo[b]\n", "        return xorTo[a] ^ xorTo[b];\n", ("a", "b"))
    else:
        add_op("PathSum", "S", f"sum of the {vals} on the path a..b",
               "        sumTo = self.sumTo\n        c = self._lca(a, b)\n"
               "        return sumTo[a] + sumTo[b] - sumTo[c] - (sumTo[self.par[c]] if c != self.root else 0)\n",
               "        int c = lcaOf(a, b);\n"
               "        return sumTo[a] + sumTo[b] - sumTo[c] - (c == root ? S(0) : sumTo[par[c]]);\n", ("a", "b"))
        add_op("PathXOR", "T", f"xor of the {vals} on the path a..b",
               "        return self.xorTo[a] ^ self.xorTo[b] ^ self.val[self._lca(a, b)]\n",
               "        return xorTo[a] ^ xorTo[b] ^ val[lcaOf(a, b)];\n", ("a", "b"))
    same = " (two paths with no edges are equal)" if edge else ""
    size = "self._dist({}, {})"
    add_op("PathHash", "unsigned long long",
           f"hash of the {vals} read a -> b (mod 2^61 - 1, random base): equal sequences hash equal{none0}",
           "        return self._hash(a, b)\n", "        return hashOf(a, b);\n", ("a", "b"))
    add_op("PathHashReversed", "unsigned long long", f"hash of the {vals} read b -> a (equal to {t}PathHash(b, a)){none0}",
           "        return self._hash(b, a)\n", "        return hashOf(b, a);\n", ("a", "b"))
    add_op("PathIsPalindrome", "bool", f"do the {vals} read the same a -> b and b -> a?" + (" (True when a == b: no edges)" if edge else ""),
           "        return self._hash(a, b) == self._hash(b, a)\n", "        return hashOf(a, b) == hashOf(b, a);\n", ("a", "b"))
    add_op("PathsEqual", "bool", f"do the {vals} read a -> b equal those read c -> d?{same}",
           f"        return {size.format('a', 'b')} == {size.format('c', 'd')} and self._hash(a, b) == self._hash(c, d)\n",
           "        return distOf(a, b) == distOf(c, d) && hashOf(a, b) == hashOf(c, d);\n", ("a", "b", "c", "d"))

    # ---- a subtree: one stretch of positions (an edge template leaves out the edge above node)
    skip = " + 1" if edge else ""
    none0 = "; 0 when node is a leaf (no edges)" if edge else ""
    for name, arr, op, ret in (("Sum", "sumAt", "-", "S"), ("XOR", "xorAt", "^", "T")):
        add_op(f"Subtree{name}", ret, f"{name.lower()} of the {vals} in node's subtree{none0}",
               f"        l = self.pos[node]\n        return self.{arr}[l + self.sz[node]] {op} self.{arr}[l{skip}]\n",
               f"        return {arr}[pos[node] + sz[node]] {op} {arr}[pos[node]{skip}];\n", ("node",))

    costs_all = dict(costs)
    costs_all.update({op: shape.COSTS[op][1] for op in G.SHAPE_OPS})

    def header(cm, ext):
        lines = [
            "Template by https://github.com/ishaanbuildsthings",
            f"{G.URL}/{folder}/template.{ext}",
            "@operations: " + " ".join(sorted(costs_all)),
            f"@data-structure-type: {KIND}",
            "@complexities:",
            *[f"  {op}: {costs_all[op]}" for op in sorted(costs_all)],
            "  build: N*log(N)",
            "@memory:",
            "  layout: none",
            "  node: sumTo[1*N] xorTo[1*N] sumAt[1*N] xorAt[1*N] down[1*N] up[1*N]",
            "  tags: none",
            f"  other: val[1*N] pw[1*N] ipw[1*N] {LAYOUT_ARRAYS}",
            "  note: the n log n part is the lca table (what makes every query O(1)); pw / ipw are as long as the tree is deep",
        ]
        return "".join(f"{cm} {line}\n" for line in lines)

    one = "edge" if edge else "node"
    how = ("How it works: the values never change, so a sum, a xor and a hash along the path from the root to a node are "
           "kept for every node, and a path a..b is two or three reads of them around the lca of a and b. The lca is O(1): "
           "one heavy-light pass gives every node a position, and a sparse table over the positions finds it (between two "
           "nodes' positions, the parent that sits earliest is their lca). A subtree is one stretch of positions "
           "(pos[node] .. pos[node] + sz[node] - 1), so prefix arrays over the positions give its sum and xor. For the "
           f"hash, up[v] is the sum of hash({one}) * base^depth along root..v: the difference of two of them is the hash of "
           "the stretch between, read upwards, times base^(the depth of its top), which an inverse power of the base takes "
           "off. down[v] is the hash of root..v read downwards. The way up to the lca and the way down from it are then "
           "joined like any two hashes.")
    info = type("R", (), {"extra_names": [], "cls": ""})
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
        py_root = "                continue  # (no edge above the root: its sums stay 0)"
        cpp_root = "                continue;  // (no edge above the root: its sums stay 0)"
        py_head = ("        # the way up: the edges below the lca, the shallowest one level under it\n"
                   "        head = (self.up[a] - self.up[c]) * self.ipw[d + 1] % _HP")
        cpp_head = ("        // the way up: the edges below the lca, the shallowest one level under it\n"
                    "        U64 head = hmul(hsub(up[a], up[c]), ipw[d + 1]);")
        kept = "val[v]: the weight of the edge above v (the root has none)"
    else:
        doc_py = G.fill_doc(G.PY_DOC, "#", info, "edges, root, vals", "")
        doc_cpp = G.fill_doc(G.CPP_DOC, "//", info, "edges, root, vals", "")
        py_ctor, cpp_ctor = "edges, root, vals", "const vector<vector<E>>& edges, int root, const vector<T>& vals"
        py_values = G.PY_VALS + "        val = list(vals)\n"
        cpp_values = ("        if ((int)vals.size() != hi + 1)\n"
                      '            throw invalid_argument("Tree: vals[node] is node\'s value, so nodes " + nodes + " need vals.size() = " +\n'
                      "                                   to_string(hi + 1) + \", got \" + to_string(vals.size()));\n"
                      "        val.assign(vals.begin(), vals.end());\n")
        py_root = ("                sumTo[v], xorTo[v] = x, x\n"
                   "                down[v] = up[v] = (x + _HO) % _HP\n"
                   "                continue")
        cpp_root = ("                sumTo[v] = x, xorTo[v] = x, down[v] = up[v] = hval(x);\n"
                    "                continue;")
        py_head = ("        # the way up: a .. lca, the lca being its top\n"
                   "        above = self.up[self.par[c]] if c != self.root else 0\n"
                   "        head = (self.up[a] - above) * self.ipw[d] % _HP")
        cpp_head = ("        // the way up: a .. lca, the lca being its top\n"
                    "        U64 head = hmul(hsub(up[a], c == root ? 0 : up[par[c]]), ipw[d]);")
        kept = "val[v]: v's value"
    bad = "an edge has no weight" if edge else "vals has the wrong length"
    arrays = (f"{kept}. Along the path root..v: sumTo[v] and xorTo[v] (the sum and the xor of its {vals}), down[v] (their hash "
              "read downwards) and up[v] (the sum of hash(value) * base^depth). Over the positions: sumAt[i] and xorAt[i], "
              "the sum and the xor of the values at positions below i. pw[d] = base^d and ipw[d] = 1 / base^d.")
    marks = {"@VALS@": vals}
    py_marks = {
        "@CTOR_NOTE@": note("#", "O(n log n) -- builds the layout, the lca table and the sums from the root; raises ValueError "
                            f"when the edges are not one tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@ARRAYS_NOTE@": note("#", arrays, 8), "@CTOR@": py_ctor, "@LAYOUT@": shape.py_layout_body(True),
        "@VALUES@": py_values, "@ROOT@": py_root, "@HEAD@": py_head,
    }
    cpp_marks = {
        "@CTOR_NOTE@": note("//", "O(n log n) -- builds the layout, the lca table and the sums from the root; throws "
                            f"invalid_argument when the edges are not one tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@ARRAYS_NOTE@": note("//", arrays, 4), "@CTOR@": cpp_ctor, "@LAYOUT@": shape.cpp_layout_body(True),
        "@VALUES@": cpp_values, "@ROOT@": cpp_root, "@HEAD@": cpp_head, "@MEMBERS@": shape.cpp_members(True).rstrip("\n"),
    }

    def doc_with(doc, cm):
        cut = doc.index(f"{cm} How it works")
        return doc[:cut] + G.wrap(cm, how)

    def fill(text, extra):
        for k, v in {**marks, **extra}.items():
            text = text.replace(k, v)
        return text

    py = (header("#", "py") + "\n" + PY_TOP + doc_with(doc_py, "#") + fill(PY, py_marks)
          + "\n" + "\n".join(py_ops) + "\n" + shape.py_shape_methods(True))
    cpp = (header("//", "cpp") + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n" + shape.FAST_NOTE
           + shape.PRELUDE + doc_with(doc_cpp, "//") + fill(CPP, cpp_marks)
           + "\n" + "\n".join(cpp_ops) + "\n" + shape.cpp_shape_methods(True).rstrip("\n") + "\n};\n")
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
            print(f"FAIL  tree-queries/{rel}: differs from what gen_tree_static.py writes (rerun it)")
        print(f"{len(stale)} stale fixed-value path files" if stale else "fixed-value path templates are fresh")
        sys.exit(1 if stale else 0)
    print(f"{len(sources())} fixed-value path files, {len(stale)} written")


if __name__ == "__main__":
    main()
