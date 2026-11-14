"""Writes the single-log subtree-xor templates: tree-queries/subtree-xor-apply-fenwick-{node,edge}, each template.{py,cpp}.

Subtree xor updates together with a path xor query, in O(log n) each (a wrapped range template takes O(log^2 n) for the
path). A path's xor is taken from the xors root..v: path(a, b) = above(a) ^ above(b) (^ the lca's own value, for nodes),
so the question is what a subtree xor does to above(v). Xoring x into the subtree of r reaches the values from r down,
and root..v holds depth(v) - depth(r) + 1 of them: x shows in above(v) when that count is odd, which is when v and r
are both at even or both at odd depth. So the update is "xor over r's stretch of positions", kept in one of two
Fenwick trees by r's depth parity, and above(v) reads the one for v's own parity. One value changing by x changes
above(u) for every u below it: a stretch xor in a third tree. A subtree's xor needs the stretch updates by position
parity (as in gen_tree_path_add.py) and the one-value changes at their own positions.

    python3 gen_tree_subtree_xor.py           # write
    python3 gen_tree_subtree_xor.py --check   # exit 1 if a file on disk differs from what this would write
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

PY = '''\
class Tree:
@CTOR_NOTE@
    def __init__(self, @CTOR@):
@LAYOUT@@VALUES@
@ARRAYS_NOTE@
        first, rootXor = [0] * (n + 1), [0] * (hi + 1)
        for i, v in enumerate(order):
            first[i + 1] = first[i] ^ base[v]
            rootXor[v] = base[v] ^ (rootXor[par[v]] if v != root else 0)
        self.base, self.first, self.rootXor = base, first, rootXor
@TREES_NOTE@
        self.diffs = ([0] * (n + 1), [0] * (n + 1))
        self.up = ([0] * (n + 1), [0] * (n + 1))
        self.below, self.own = [0] * (n + 1), [0] * (n + 1)

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

    # the value kept at node v is xored with x (it alone): every path root..u with u at or below v sees it
    def _bump(self, v, x):
        self.base[v] ^= x
        p = self.pos[v]
        self._flip(self.own, p, x)
        self._flip(self.below, p, x)
        self._flip(self.below, p + self.sz[v], x)

    # every value at positions l..r is xored with x; top: the depth of the shallowest of them (nothing for l > r)
    def _spread(self, l, r, top, x):
        if l > r:
            return
        self._flip(self.diffs[l & 1], l, x)
        self._flip(self.diffs[(r + 1) & 1], r + 1, x)
        # a path from the root sees x once for each of them it holds: an odd number when its end is at top's parity
        self._flip(self.up[top & 1], l, x)
        self._flip(self.up[top & 1], r + 1, x)

    # the value kept at node v
    def _value(self, v):
        p = self.pos[v]
        return self.base[v] ^ self._xor(self.diffs[0], p) ^ self._xor(self.diffs[1], p)

    # what the stretch xors gave the values at positions 0..k, xored together (0 when k is -1): a stretch that starts
    # at j covers an odd number of them when j and k are both even or both odd
    def _spreadUpTo(self, k):
        return self._xor(self.diffs[k & 1], k)

    # the xor of the values kept on the path root..v
    def _fromRoot(self, v):
        p = self.pos[v]
        return self.rootXor[v] ^ self._xor(self.below, p) ^ self._xor(self.up[self.dep[v] & 1], p)
'''
CPP = '''\
template <typename T>
struct Tree {
@MEMBERS@
    using U = unsigned long long;  // (xor is done on the bits: a negative value keeps its sign through it)
@ARRAYS_NOTE@
    HotVector<U> base, first, rootXor;
@TREES_NOTE@
    HotVector<U> diffs[2], up[2], below, own;

@CTOR_NOTE@
@CTOR@ {
@LAYOUT@
@VALUES@        first.assign(n + 1, 0), rootXor.assign(hi + 1, 0);
        for (int i = 0; i < n; i++) {
            int v = order[i];
            first[i + 1] = first[i] ^ base[v];
            rootXor[v] = base[v] ^ (v == root ? U(0) : rootXor[par[v]]);
        }
        own.assign(n + 1, 0), below = diffs[0] = diffs[1] = up[0] = up[1] = own;
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

    // the value kept at node v is xored with x (it alone): every path root..u with u at or below v sees it
    LEETCODE_NO_SANITIZE void bump(int v, U x) {
        base[v] ^= x;
        flip(own, pos[v], x);
        flip(below, pos[v], x), flip(below, pos[v] + sz[v], x);
    }

    // every value at positions l..r is xored with x; top: the depth of the shallowest of them (nothing for l > r)
    LEETCODE_NO_SANITIZE void spread(int l, int r, int top, U x) {
        if (l > r) return;
        flip(diffs[l & 1], l, x), flip(diffs[(r + 1) & 1], r + 1, x);
        // a path from the root sees x once for each of them it holds: an odd number when its end is at top's parity
        flip(up[top & 1], l, x), flip(up[top & 1], r + 1, x);
    }

    // the value kept at node v
    LEETCODE_NO_SANITIZE U valueOf(int v) const { return base[v] ^ xorOf(diffs[0], pos[v]) ^ xorOf(diffs[1], pos[v]); }

    // what the stretch xors gave the values at positions 0..k, xored together (0 when k is -1): a stretch that starts
    // at j covers an odd number of them when j and k are both even or both odd
    LEETCODE_NO_SANITIZE U spreadUpTo(int k) const { return xorOf(diffs[k & 1], k); }

    // the xor of the values kept on the path root..v
    LEETCODE_NO_SANITIZE U fromRoot(int v) const {
        return rootXor[v] ^ xorOf(below, pos[v]) ^ xorOf(up[dep[v] & 1], pos[v]);
    }
'''


def make(edge):
    t = "edge" if edge else "node"
    folder = f"subtree-xor-apply-fenwick-{t}"
    vals, val_word, x = ("edge weights", "weight", "w") if edge else ("node values", "val", "x")
    at = "a - b" if edge else "node"
    nodes = ("a", "b") if edge else ("node",)
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

    def here(name):
        if edge:
            return f'        v = self._edge("{t}{name}", a, b)\n', f'        int v = edgeAt("{t}{name}", a, b);\n'
        return G.py_check(t + name, nodes), G.cpp_check(t + name, nodes)

    v = "v" if edge else "node"
    p, c = here("Get")
    add_op("Get", [], [], "T", f"{val_word}({at}){either}", p + f"        return self._value({v})\n",
           c + f"        return (T)(long long)valueOf({v});\n")
    p, c = here("Assign")
    add_op("Assign", [x], ["T"], "void", f"{val_word}({at}) = {x}{either}",
           p + f"        self._bump({v}, {x} ^ self._value({v}))\n", c + f"        bump({v}, bitsOf({x}) ^ valueOf({v}));\n")
    p, c = here("Add")
    add_op("Add", [x], ["T"], "void", f"{val_word}({at}) += {x}{either}",
           p + f"        now = self._value({v})\n        self._bump({v}, (now + {x}) ^ now)\n",
           c + f"        U now = valueOf({v});\n        bump({v}, (now + bitsOf({x})) ^ now);\n")
    for name, sign in (("Chmax", ">"), ("Chmin", "<")):
        p, c = here(name)
        add_op(name, [x], ["T"], "void", f"{val_word}({at}) = {name[2:].lower()}({val_word}, {x}){either}",
               p + f"        now = self._value({v})\n        if {x} {sign} now:\n            self._bump({v}, {x} ^ now)\n",
               c + f"        T now = (T)(long long)valueOf({v});\n        if ({x} {sign} now) bump({v}, bitsOf({x}) ^ bitsOf(now));\n")

    skip = " + 1" if edge else ""
    add_op("SubtreeXORApply", [x], ["T"], "void", f"{val_word} ^= {x} for every {t} in node's subtree",
           G.py_check(t + "SubtreeXORApply", ("node",)) + "        l = self.pos[node]\n"
           + f"        self._spread(l{skip}, l + self.sz[node] - 1, self.dep[node]{skip}, {x})\n",
           G.cpp_check(t + "SubtreeXORApply", ("node",))
           + f"        spread(pos[node]{skip}, pos[node] + sz[node] - 1, dep[node]{skip}, bitsOf({x}));\n", where=("node",))
    none = "; 0 when node is a leaf (no edges)" if edge else ""
    lo_p, lo_s = ("l + 1", "l") if edge else ("l", "l - 1")
    add_op("SubtreeXOR", [], [], "T", f"XOR of the {vals} in node's subtree{none}",
           G.py_check(t + "SubtreeXOR", ("node",)) + "        l = self.pos[node]\n        r = l + self.sz[node] - 1\n"
           + f"        return (self.first[r + 1] ^ self.first[{lo_p}] ^ self._xor(self.own, r) ^ self._xor(self.own, {lo_s})\n"
           + f"                ^ self._spreadUpTo(r) ^ self._spreadUpTo({lo_s}))\n",
           G.cpp_check(t + "SubtreeXOR", ("node",)) + "        int l = pos[node], r = l + sz[node] - 1;\n"
           + f"        return (T)(long long)(first[r + 1] ^ first[{lo_p}] ^ xorOf(own, r) ^ xorOf(own, {lo_s}) ^ spreadUpTo(r) ^\n"
           + f"                              spreadUpTo({lo_s}));\n", where=("node",))
    none = "; 0 when a == b (no edges)" if edge else ""
    if edge:
        py_path = "        return self._fromRoot(a) ^ self._fromRoot(b)  # (what lies above the lca is in both: it cancels)\n"
        cpp_path = "        return (T)(long long)(fromRoot(a) ^ fromRoot(b));  // (what lies above the lca is in both: it cancels)\n"
    else:
        py_path = ("        # (the lca and what lies above it are in both: they cancel, so the lca's value is put back)\n"
                   "        return self._fromRoot(a) ^ self._fromRoot(b) ^ self._value(self._lca(a, b))\n")
        cpp_path = ("        // (the lca and what lies above it are in both: they cancel, so the lca's value is put back)\n"
                    "        return (T)(long long)(fromRoot(a) ^ fromRoot(b) ^ valueOf(lcaOf(a, b)));\n")
    add_op("PathXOR", [], [], "T", f"XOR of the {vals} on the path a..b{none}",
           G.py_check(t + "PathXOR", ("a", "b")) + py_path, G.cpp_check(t + "PathXOR", ("a", "b")) + cpp_path, where=("a", "b"))

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
            "  node: diffs[2*N] up[2*N] below[1*N] own[1*N]",
            "  tags: none",
            f"  other: base[1*N] first[1*N] rootXor[1*N] {G.LAYOUT_ARRAYS}",
        ]
        return "".join(f"{cm} {line}\n" for line in lines)

    one = "edge" if edge else "node"
    how = ("How it works: one heavy-light pass gives every node a position, so that each subtree is one stretch of positions "
           "(pos[node] .. pos[node] + sz[node] - 1). A path's xor comes from the xors root..v: the part above the lca is in "
           "both root..a and root..b and cancels" + ("" if edge else ", and the lca's own value is put back") + ". A "
           f"subtree xor of x reaches every {one} from the subtree's top down, and root..v holds some number of those: x "
           "shows in root..v when that number is odd, which is when v's depth is even or odd like the top's. So a subtree "
           "update is \"xor over a stretch of positions\", written to one of two Fenwick trees by the top's depth parity, "
           "and root..v reads the tree for v's own parity. One value changing changes root..u for every u below it: a "
           "stretch xor in a third tree. For one value and for a subtree's xor, the stretch updates are also kept by "
           "position parity, and the one-value changes at their own positions.")
    info = type("R", (), {"extra_names": [], "cls": ""})
    if edge:
        doc_py = G.fill_doc(G.PY_DOC_EDGE, "#", info, "edges, root", "", "edge")
        doc_cpp = G.fill_doc(G.CPP_DOC_EDGE, "//", info, "edges, root", "", "edge")
        py_ctor, cpp_ctor = "edges, root", "const vector<vector<E>>& edges, int root"
        py_values = ("        for e in edges:\n"
                     "            if len(e) != 3:\n"
                     '                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")\n'
                     "        base = [0] * (hi + 1)\n"
                     "        for e in edges:\n"
                     "            base[e[0] if par[e[0]] == e[1] else e[1]] = e[2]\n")
        cpp_values = ("        for (const auto& e : edges)\n"
                      '            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");\n'
                      "        base.assign(hi + 1, 0);\n"
                      "        for (const auto& e : edges) {\n"
                      "            int a = (int)e[0], b = (int)e[1];\n"
                      "            base[par[a] == b ? a : b] = bitsOf((T)e[2]);\n"
                      "        }\n")
        kept = "the weight of the edge above v (the root has none)"
    else:
        doc_py = G.fill_doc(G.PY_DOC, "#", info, "edges, root, vals", "")
        doc_cpp = G.fill_doc(G.CPP_DOC, "//", info, "edges, root, vals", "")
        py_ctor, cpp_ctor = "edges, root, vals", "const vector<vector<E>>& edges, int root, const vector<T>& vals"
        py_values = G.PY_VALS + "        base = list(vals)\n"
        cpp_values = ("        if ((int)vals.size() != hi + 1)\n"
                      '            throw invalid_argument("Tree: vals[node] is node\'s value, so nodes " + nodes + " need vals.size() = " +\n'
                      "                                   to_string(hi + 1) + \", got \" + to_string(vals.size()));\n"
                      "        base.assign(hi + 1, 0);\n"
                      "        for (int v = lo; v <= hi; v++) base[v] = bitsOf(vals[v]);\n")
        kept = "v's value"
    bad = "an edge has no weight" if edge else "vals has the wrong length"
    arrays = (f"base[v]: {kept}, apart from the subtree updates that cover it. first[i]: the starting values at positions "
              "below i, xored together. rootXor[v]: the starting values on the path root..v, xored together.")
    trees = ("Fenwick trees over the positions (1-based), kept with xor. diffs[0], diffs[1]: where a subtree update starts and "
             "stops, at even and at odd positions. up[0], up[1]: the same starts and stops, by whether the subtree's top is at "
             "even or odd depth. below: where a one-value change starts and stops reaching the paths from the root. own: the "
             "one-value changes, each at its own position.")
    py_marks = {
        "@CTOR_NOTE@": note("#", "O(n) -- builds the layout and the xors of the starting values; raises ValueError when the "
                            f"edges are not one tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@ARRAYS_NOTE@": note("#", arrays, 8), "@TREES_NOTE@": note("#", trees, 8),
        "@CTOR@": py_ctor, "@LAYOUT@": shape.py_layout_body(), "@VALUES@": py_values,
    }
    cpp_marks = {
        "@CTOR_NOTE@": note("//", "O(n) -- builds the layout and the xors of the starting values; throws invalid_argument when "
                            f"the edges are not one tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@ARRAYS_NOTE@": note("//", arrays, 4), "@TREES_NOTE@": note("//", trees, 4),
        "@CTOR@": f"    template <typename E = int> Tree({cpp_ctor}) : root(root)", "@LAYOUT@": shape.cpp_layout_body(),
        "@VALUES@": cpp_values, "@MEMBERS@": shape.cpp_members().rstrip("\n"),
    }

    def doc_with(doc, cm):
        return doc[:doc.index(f"{cm} How it works")] + G.wrap(cm, how)

    def fill(text, marks):
        for k, val in marks.items():
            text = text.replace(k, val)
        return text

    py = (header("#", "py") + "\nfrom bisect import bisect_left\n\n\n" + doc_with(doc_py, "#") + fill(PY, py_marks)
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
            print(f"FAIL  tree-queries/{rel}: differs from what gen_tree_subtree_xor.py writes (rerun it)")
        print(f"{len(stale)} stale subtree-xor files" if stale else "single-log subtree xor templates are fresh")
        sys.exit(1 if stale else 0)
    print(f"{len(sources())} subtree-xor files, {len(stale)} written")


if __name__ == "__main__":
    main()
