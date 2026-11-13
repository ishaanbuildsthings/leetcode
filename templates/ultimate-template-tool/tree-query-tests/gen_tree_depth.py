"""Writes the add-by-depth subtree templates: tree-queries/subtree-depth-add-fenwick-{node,edge} and
subtree-depth-add-mod-fenwick-{node,edge}, each template.{py,cpp}.

SubtreeAddByDepth(node, start, step) gives every value in node's subtree start + step * (how far below node it is).
Seen from one value u that is A + B * depth(u), with A = start - step * depth(node) and B = step the same for the
whole subtree, and a subtree is one stretch of positions. So every update is "add A + B * depth over a stretch", and
five Fenwick trees over the positions answer everything in O(log n):

    ca, cb   difference trees: a prefix sum is the A (the B) that applies at a position        -> one value
    sa, sb   their partners for sums over a stretch of positions (sb weighs B by the depths)   -> a subtree's sum
    up       what the updates added to the path root..v, apart from the part that grows with
             depth(v): that part is A * depth(v) + B * (0 + 1 + ... + depth(v))                -> a path's sum

The MOD folders do the same arithmetic mod a fixed MOD (values kept in [0, MOD)).

    python3 gen_tree_depth.py           # write
    python3 gen_tree_depth.py --check   # exit 1 if a file on disk differs from what this would write
"""
import os
import re
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
        first, depSum, rootSum = [0] * (n + 1), [0] * (n + 1), [0] * (hi + 1)
        for i, v in enumerate(order):
            first[i + 1] = @RED(first[i] + base[v])@
            depSum[i + 1] = @RED(depSum[i] + dep[v])@
            rootSum[v] = @RED(base[v] + (rootSum[par[v]] if v != root else 0))@
        self.base, self.first, self.depSum, self.rootSum = base, first, depSum, rootSum

@TREES_NOTE@
        self.ca, self.cb, self.sa, self.sb, self.up = ([0] * (n + 1) for _ in range(5))@KEEP_MOD@

    # one Fenwick step in all five trees: from position p on, ca += a, cb += b, sa += c, sb += d, up += e (nothing when
    # p is past the last position)
    def _mark(self, p, a, b, c, d, e):
        ca, cb, sa, sb, up, n = self.ca, self.cb, self.sa, self.sb, self.up, self.n@GET_MOD@
        p += 1
        while p <= n:
            ca[p] = @RED(ca[p] + a)@
            cb[p] = @RED(cb[p] + b)@
            sa[p] = @RED(sa[p] + c)@
            sb[p] = @RED(sb[p] + d)@
            up[p] = @RED(up[p] + e)@
            p += p & -p

    # the five trees' prefix sums through position p: (ca, cb, sa, sb, up)
    def _read(self, p):
        ca, cb, sa, sb, up = self.ca, self.cb, self.sa, self.sb, self.up
        a = b = c = d = e = 0
        p += 1
        while p > 0:
            a += ca[p]
            b += cb[p]
            c += sa[p]
            d += sb[p]
            e += up[p]
            p -= p & -p
        return a, b, c, d, e

    # every value at positions l..r gets A + B * (its depth) added; top: the depth of the shallowest of them (nothing
    # for an empty stretch, l > r)
    def _spread(self, l, r, top, A, B):
        if l > r:
            return
        depSum = self.depSum
        # what a path from the root gains, apart from its depth terms
        C = A * (1 - top) - B * (top * (top - 1) // 2)
        self._mark(l, A, B, A * l, B * depSum[l], C)
        self._mark(r + 1, -A, -B, -A * (r + 1), -B * depSum[r + 1], -C)

    # the value kept at node v grows by x (it alone)
    def _bump(self, v, x):
        self.base[v] = @RED(self.base[v] + x)@
        p = self.pos[v]
        self._mark(p, 0, 0, -x, 0, x)
        self._mark(p + self.sz[v], 0, 0, 0, 0, -x)

    # the value kept at node v
    def _value(self, v):
        a, b, _, _, _ = self._read(self.pos[v])
        return @RED(self.base[v] + a + b * self.dep[v])@

    # the sum of the values at positions 0..k (0 when k is -1)
    def _upTo(self, k):
        a, b, c, d, _ = self._read(k)
        return @RED(self.first[k + 1] + (k + 1) * a - c + self.depSum[k + 1] * b - d)@

    # the sum of the values kept on the path root..v
    def _fromRoot(self, v):
        a, b, _, _, e = self._read(self.pos[v])
        d = self.dep[v]
        return @RED(self.rootSum[v] + e + a * d + b * (d * (d + 1) // 2))@
'''

CPP = '''\
template <typename T>
struct Tree {
@MEMBERS@
@TYPES@
@ARRAYS_NOTE@
    HotVector<C> base, first, depSum, rootSum;
@TREES_NOTE@
    HotVector<C> ca, cb, sa, sb, up;

@CTOR_NOTE@
@CTOR@ {
@LAYOUT@
@VALUES@        first.assign(n + 1, 0), depSum.assign(n + 1, 0), rootSum.assign(hi + 1, 0);
        for (int i = 0; i < n; i++) {
            int v = order[i];
            first[i + 1] = fit((W)first[i] + (W)base[v]);
            depSum[i + 1] = fit((W)depSum[i] + (W)dep[v]);
            rootSum[v] = fit((W)base[v] + (v == root ? W(0) : (W)rootSum[par[v]]));
        }
        ca.assign(n + 1, 0), cb = sa = sb = up = ca;
    }

@FIT@

    // 0 + 1 + ... + d
    LEETCODE_NO_SANITIZE @TRI@

    // one Fenwick step in all five trees: from position p on, ca += a, cb += b, sa += c, sb += d, up += e (nothing when
    // p is past the last position)
    LEETCODE_NO_SANITIZE void mark(int p, W a, W b, W c, W d, W e) {
        C fa = fit(a), fb = fit(b), fc = fit(c), fd = fit(d), fe = fit(e);
        for (p++; p <= n; p += p & -p) @PUT@
    }

    // the five trees' prefix sums through one position
    struct Read {
        W a, b, sumA, sumB, up;
    };
    LEETCODE_NO_SANITIZE Read read(int p) const {
        W a = 0, b = 0, c = 0, d = 0, e = 0;
        for (p++; p > 0; p -= p & -p) a += ca[p], b += cb[p], c += sa[p], d += sb[p], e += up[p];
        return Read{@READ@};
    }

    // every value at positions l..r gets A + B * (its depth) added; top: the depth of the shallowest of them (nothing
    // for an empty stretch, l > r)
    LEETCODE_NO_SANITIZE void spread(int l, int r, int top, W A, W B) {
        if (l > r) return;
        // what a path from the root gains, apart from its depth terms
        W gain = A * (W)(long long)(1 - top) - B * tri(top - 1);
        mark(l, A, B, A * (W)l, B * (W)depSum[l], gain);
        mark(r + 1, 0 - A, 0 - B, 0 - A * (W)(r + 1), 0 - B * (W)depSum[r + 1], 0 - gain);
    }

    // the value kept at node v grows by x (it alone)
    LEETCODE_NO_SANITIZE void bump(int v, W x) {
        base[v] = fit((W)base[v] + x);
        mark(pos[v], 0, 0, 0 - x, 0, x);
        mark(pos[v] + sz[v], 0, 0, 0, 0, 0 - x);
    }

    // the value kept at node v
    LEETCODE_NO_SANITIZE C valueOf(int v) const {
        Read s = read(pos[v]);
        return fit((W)base[v] + s.a + s.b * (W)dep[v]);
    }

    // the sum of the values at positions 0..k (0 when k is -1)
    LEETCODE_NO_SANITIZE C upTo(int k) const {
        Read s = read(k);
        return fit((W)first[k + 1] + (W)(k + 1) * s.a - s.sumA + (W)depSum[k + 1] * s.b - s.sumB);
    }

    // the sum of the values kept on the path root..v
    LEETCODE_NO_SANITIZE C fromRoot(int v) const {
        Read s = read(pos[v]);
        return fit((W)rootSum[v] + s.up + s.a * (W)dep[v] + s.b * tri(dep[v]));
    }
'''


def red(text, mod, name="self.mod"):
    """Fills @RED(expr)@ (Python only): the expression as it is, or reduced mod MOD in a MOD template. name: how the
    code around it reaches the modulus (a local in the constructor and in _mark, the attribute everywhere else)."""
    out, at = [], 0
    while True:
        i = text.find("@RED(", at)
        if i < 0:
            return "".join(out) + text[at:]
        j = text.index(")@", i)
        expr = text[i + 5:j]
        whole = expr if expr.isidentifier() else f"({expr})"
        out.append(text[at:i] + (f"{whole} % {name}" if mod else expr))
        at = j + 2


def make(edge, mod):
    t = "edge" if edge else "node"
    folder = f"subtree-depth-add-{'mod-' if mod else ''}fenwick-{t}"
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
    all_mod = ", all mod MOD" if mod else ""

    def here(name):
        if edge:
            return f'        v = self._edge("{t}{name}", a, b)\n', f'        int v = edgeAt("{t}{name}", a, b);\n'
        return G.py_check(t + name, nodes), G.cpp_check(t + name, nodes)

    v = "v" if edge else "node"

    # ---- one value
    p, c = here("Get")
    add_op("Get", [], [], "T", f"{val_word}({at}){in_mod}{either}", p + f"        return self._value({v})\n",
           c + f"        return (T)(long long)valueOf({v});\n")
    p, c = here("Assign")
    add_op("Assign", [x], ["T"], "void", f"{val_word}({at}) = {x}{' % MOD' if mod else ''}{either}",
           p + f"        self._bump({v}, {x} - self._value({v}))\n",
           c + f"        bump({v}, wide({x}) - (W)valueOf({v}));\n")
    p, c = here("Add")
    add_op("Add", [x], ["T"], "void", f"{val_word}({at}) = ({val_word} + {x}) % MOD{either}" if mod else f"{val_word}({at}) += {x}{either}",
           p + f"        self._bump({v}, {x})\n", c + f"        bump({v}, wide({x}));\n")
    if not mod:
        for name, sign in (("Chmax", ">"), ("Chmin", "<")):
            p, c = here(name)
            add_op(name, [x], ["T"], "void", f"{val_word}({at}) = {name[2:].lower()}({val_word}, {x}){either}",
                   p + f"        now = self._value({v})\n        if {x} {sign} now:\n            self._bump({v}, {x} - now)\n",
                   c + f"        T now = (T)(long long)valueOf({v});\n        if ({x} {sign} now) bump({v}, wide({x}) - wide(now));\n")

    # ---- a subtree: one stretch of positions (an edge template leaves out the edge above node, so its stretch starts
    # one position later and one level deeper)
    skip = " + 1" if edge else ""
    why = "        # the edges below node: the positions after its own, the shallowest one level below node\n" if edge else ""
    stretch_py = "        l = self.pos[node]\n" + why
    stretch_cpp = why.replace("#", "//") + f"        int l = pos[node]{skip}, r = pos[node] + sz[node] - 1, top = dep[node]{skip};\n"
    add_op(f"SubtreeAdd{M}", [x], ["T"], "void",
           (f"{val_word} = ({val_word} + {x}) % MOD" if mod else f"{val_word} += {x}") + f" for every {t} in node's subtree",
           G.py_check(f"{t}SubtreeAdd{M}", ("node",)) + stretch_py
           + f"        self._spread(l{skip}, l + self.sz[node] - 1, self.dep[node]{skip}, {x}, 0)\n",
           G.cpp_check(f"{t}SubtreeAdd{M}", ("node",)) + stretch_cpp + f"        spread(l, r, top, (W)fit(wide({x})), 0);\n",
           where=("node",))
    if edge:
        doc = ("every edge in node's subtree gets start + step * k added, k = how many edges lie between node and the edge's "
               f"upper end (0 for the edges just below node){all_mod}")
    else:
        doc = f"every node u in node's subtree gets start + step * (depth(u) - depth(node)) added{all_mod}"
    add_op(f"SubtreeAddByDepth{M}", ["start", "step"], ["T", "T"], "void", doc,
           G.py_check(f"{t}SubtreeAddByDepth{M}", ("node",)) + stretch_py
           + f"        top = self.dep[node]{skip}\n"
           + f"        self._spread(l{skip}, l + self.sz[node] - 1, top, start - step * top, step)\n",
           G.cpp_check(f"{t}SubtreeAddByDepth{M}", ("node",)) + stretch_cpp
           + "        spread(l, r, top, (W)fit(wide(start) - wide(step) * (W)top), (W)fit(wide(step)));\n", where=("node",))
    none = "; 0 when node is a leaf (no edges)" if edge else ""
    tail = ", mod MOD" if mod else ""
    add_op(f"SubtreeSum{M}", [], [], "T", f"sum of the {vals} in node's subtree{tail}{none}",
           G.py_check(f"{t}SubtreeSum{M}", ("node",)) + "        l = self.pos[node]\n"
           + red(f"        return @RED(self._upTo(l + self.sz[node] - 1) - self._upTo(l{'' if edge else ' - 1'}))@\n", mod),
           G.cpp_check(f"{t}SubtreeSum{M}", ("node",))
           + f"        return (T)(long long)fit((W)upTo(pos[node] + sz[node] - 1) - (W)upTo(pos[node]{'' if edge else ' - 1'}));\n",
           where=("node",))

    # ---- a path: the sums from the root to its two ends, without what lies above the lca
    none = "; 0 when a == b (no edges)" if edge else ""
    if edge:
        py_path = red("        return @RED(self._fromRoot(a) + self._fromRoot(b) - 2 * self._fromRoot(self._lca(a, b)))@\n", mod)
        cpp_path = "        return (T)(long long)fit((W)fromRoot(a) + (W)fromRoot(b) - (W)2 * (W)fromRoot(lcaOf(a, b)));\n"
    else:
        py_path = ("        c = self._lca(a, b)\n"
                   "        res = self._fromRoot(a) + self._fromRoot(b) - self._fromRoot(c)\n"
                   "        if c != self.root:\n            res -= self._fromRoot(self.par[c])\n"
                   + red("        return @RED(res)@\n", mod))
        cpp_path = ("        int c = lcaOf(a, b);\n"
                    "        W res = (W)fromRoot(a) + (W)fromRoot(b) - (W)fromRoot(c);\n"
                    "        if (c != root) res -= (W)fromRoot(par[c]);\n"
                    "        return (T)(long long)fit(res);\n")
    add_op(f"PathSum{M}", [], [], "T", f"sum of the {vals} on the path a..b{tail}{none}",
           G.py_check(f"{t}PathSum{M}", ("a", "b")) + py_path, G.cpp_check(f"{t}PathSum{M}", ("a", "b")) + cpp_path,
           where=("a", "b"))

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
            "  node: ca[1*N] cb[1*N] sa[1*N] sb[1*N] up[1*N]",
            "  tags: none",
            f"  other: base[1*N] first[1*N] depSum[1*N] rootSum[1*N] {G.LAYOUT_ARRAYS}",
        ]
        return "".join(f"{cm} {line}\n" for line in lines)

    one = "edge" if edge else "node"
    how = ("How it works: one heavy-light pass gives every node a position, so that each subtree is one stretch of positions "
           f"(pos[node] .. pos[node] + sz[node] - 1). Adding by depth gives the {one} at depth d the amount A + B * d, with "
           "the same A and B for the whole subtree (B = step, and A = start minus step times the depth where the subtree "
           "starts). So every update is \"add A + B * depth over a stretch of positions\", and five Fenwick trees over the "
           "positions keep them. ca and cb are difference trees: a prefix sum is the A (the B) that applies at a position, "
           "which gives one value. sa and sb are their partners for a sum over a stretch (sb weighs each B by the depths it "
           "covers), which gives a subtree's sum. up keeps what the updates added to the path from the root down to a node, "
           "apart from the part that follows from that node's own depth d: A * d + B * (0 + 1 + ... + d). With it the sum on "
           "root..v is one read, and a path a..b is root..a plus root..b minus what lies above their lca.")
    wrap_note = {"#": "", "//": (
        "The arithmetic is done mod 2^64 (unsigned), because a product on the way can pass 64 bits though the answer fits: "
        "the answers are exact whenever they fit the value type." if not mod else
        "MOD can be anything below 2^62: products are taken in 128 bits.")}
    info = type("R", (), {"extra_names": ["mod"] if mod else [], "cls": ""})
    sig_names = ("edges, root" if edge else "edges, root, vals") + (", mod" if mod else "")
    example = ", mod" if mod else ""
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
                      "            base[par[a] == b ? a : b] = fit(wide((T)e[2]));\n"
                      "        }\n")
        kept = "the weight of the edge above v (the root has none)"
    else:
        doc_py = G.fill_doc(G.PY_DOC, "#", info, sig_names, example)
        doc_cpp = G.fill_doc(G.CPP_DOC, "//", info, sig_names, example)
        py_ctor, cpp_ctor = "edges, root, vals", "const vector<vector<E>>& edges, int root, const vector<T>& vals"
        py_values = G.PY_VALS + ("        base = [x % mod for x in vals]\n" if mod else "        base = list(vals)\n")
        cpp_values = ("        if ((int)vals.size() != hi + 1)\n"
                      '            throw invalid_argument("Tree: vals[node] is node\'s value, so nodes " + nodes + " need vals.size() = " +\n'
                      "                                   to_string(hi + 1) + \", got \" + to_string(vals.size()));\n"
                      "        base.assign(hi + 1, 0);\n"
                      "        for (int v = lo; v <= hi; v++) base[v] = fit(wide(vals[v]));\n")
        kept = "v's value"
    bad = "an edge has no weight" if edge else "vals has the wrong length"
    arrays = (f"base[v]: {kept} at the start, plus what was added to it alone. first[i]: the starting values at positions "
              "below i, summed. depSum[i]: the depths at positions below i, summed. rootSum[v]: the starting values on the "
              "path root..v, summed.")
    trees = ("Five Fenwick trees over the positions (1-based), filled by the updates, each \"add A + B * depth over a "
             "stretch\": ca, cb (a prefix sum is the A, the B that applies at a position), sa, sb (with them, the sum over "
             "a stretch) and up (what the updates gave the path from the root, apart from its depth terms).")
    py_marks = {
        "@CTOR_NOTE@": note("#", "O(n) -- builds the layout and the sums of the starting values; raises ValueError when the "
                            f"edges are not one tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@ARRAYS_NOTE@": note("#", arrays, 8), "@TREES_NOTE@": note("#", trees, 8),
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
               "    LEETCODE_NO_SANITIZE static W wide(T x) { return (W)(long long)x; }\n\n"
               "    // cell = (cell + x) % MOD, for two numbers already in [0, MOD)\n"
               "    LEETCODE_NO_SANITIZE void put(C& cell, C x) const {\n"
               "        cell += x;\n"
               "        if (cell >= modulus) cell -= modulus;\n"
               "    }")
        tri = "W tri(W d) const { return d * (d + 1) / 2 % modulus; }"
        put = "put(ca[p], fa), put(cb[p], fb), put(sa[p], fc), put(sb[p], fd), put(up[p], fe);"
        read = "fit(a), fit(b), fit(c), fit(d), fit(e)"
    else:
        types = ("    // every number is kept mod 2^64: a product on the way can pass 64 bits though the answer fits, and unsigned\n"
                 "    // arithmetic wraps without harm, so an answer is exact whenever it fits the value type\n"
                 "    using C = unsigned long long;\n"
                 "    using W = unsigned long long;")
        fit = ("    // (the MOD version of this template reduces here; this one keeps every number as it is, mod 2^64)\n"
               "    LEETCODE_NO_SANITIZE static C fit(W x) { return x; }\n"
               "    LEETCODE_NO_SANITIZE static W wide(T x) { return (W)(long long)x; }")
        tri = "static W tri(W d) { return d * (d + 1) / 2; }"
        put = "ca[p] += fa, cb[p] += fb, sa[p] += fc, sb[p] += fd, up[p] += fe;"
        read = "a, b, c, d, e"
    cpp_marks = {
        "@CTOR_NOTE@": note("//", "O(n) -- builds the layout and the sums of the starting values; throws invalid_argument when "
                            f"the edges are not one tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@ARRAYS_NOTE@": note("//", arrays, 4), "@TREES_NOTE@": note("//", trees, 4),
        "@CTOR@": sig + init, "@LAYOUT@": shape.cpp_layout_body(), "@VALUES@": cpp_values,
        "@MEMBERS@": shape.cpp_members().rstrip("\n"), "@TYPES@": types, "@FIT@": fit, "@TRI@": tri, "@PUT@": put,
        "@READ@": read,
    }

    def doc_with(doc, cm):
        cut = doc.index(f"{cm} How it works")
        extra = f"{cm}\n" + G.wrap(cm, wrap_note[cm]) if wrap_note[cm] else ""
        return doc[:cut] + G.wrap(cm, how) + extra

    def fill(text, marks):
        for k, v in marks.items():
            text = text.replace(k, v)
        return text

    cut = PY.index("    # the five trees' prefix sums")  # (before it: the constructor and _mark, which hold mod in a local)
    body = red(fill(PY[:cut], py_marks), mod, "mod") + red(fill(PY[cut:], py_marks), mod)
    if not mod:  # ("x = x + y" reads better as "x += y")
        body = re.sub(r"^(\s+)(\S+) = \2 \+ (.+)$", r"\1\2 += \3", body, flags=re.M)
    py = (header("#", "py") + "\nfrom bisect import bisect_left\n\n\n" + doc_with(doc_py, "#") + body
          + "\n" + "\n".join(py_ops) + "\n" + shape.py_shape_methods())
    cpp = (header("//", "cpp") + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n" + shape.FAST_NOTE
           + shape.PRELUDE + doc_with(doc_cpp, "//") + fill(CPP, cpp_marks)
           + "\n" + "\n".join(cpp_ops) + "\n" + shape.cpp_shape_methods().rstrip("\n") + "\n};\n")
    return folder, py, cpp


def sources():
    out = {}
    for mod in (False, True):
        for edge in (False, True):
            folder, py, cpp = make(edge, mod)
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
            print(f"FAIL  tree-queries/{rel}: differs from what gen_tree_depth.py writes (rerun it)")
        print(f"{len(stale)} stale add-by-depth files" if stale else "add-by-depth subtree templates are fresh")
        sys.exit(1 if stale else 0)
    print(f"{len(sources())} add-by-depth files, {len(stale)} written")


if __name__ == "__main__":
    main()
