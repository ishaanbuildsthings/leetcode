"""Writes the count-distinct path templates: tree-queries/path-distinct-bitset-{node,edge}, each template.{py,cpp}.

"How many distinct values are on this path?" cannot be put together from the pieces' own answers (a value on two
pieces counts once), and no fast general way is known. What works when the values are few: a segment tree over the
positions whose nodes each hold a bitset, one bit per distinct value under the node (a parent is the OR of its
children). A path is O(log n) chain pieces, each O(log n) nodes: OR their bitsets and count the bits. That is
O(log^2 n * D / 64) for D distinct values, and 2 * n * D / 8 bytes: fine up to a few thousand distinct values.

A value gets its bit the first time it appears (also later, through an assign), so nothing has to be known up front;
C++ needs a cap on how many distinct values can ever appear (to size the bitsets), Python ints grow by themselves.

    python3 gen_tree_bitset.py           # write
    python3 gen_tree_bitset.py --check   # exit 1 if a file on disk differs from what this would write
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import gen_tree as G  # noqa: E402
import gen_tree_shape as shape  # noqa: E402

DIR = G.DIR
KIND = "bitset-seg-tree"

PY = '''\
class Tree:
@CTOR_NOTE@
    def __init__(self, @CTOR@, distinctCap=None):
@LAYOUT@@VALUES@
@BITS_NOTE@
        ids = {}
        bits = [0] * (2 * n)
        for i in range(@FIRST@, n):
            x = val[order[i]]
            b = ids.get(x)
            if b is None:
                b = ids[x] = len(ids)
            bits[n + i] = 1 << b
        for i in range(n - 1, 0, -1):
            bits[i] = bits[2 * i] | bits[2 * i + 1]
        self.val, self.ids, self.bits = val, ids, bits

    # the value kept at node v becomes x
    def _set(self, v, x):
        ids, bits = self.ids, self.bits
        b = ids.get(x)
        if b is None:
            b = ids[x] = len(ids)
        i = self.n + self.pos[v]
        bits[i] = 1 << b
        i >>= 1
        while i:
            bits[i] = bits[2 * i] | bits[2 * i + 1]
            i >>= 1
        self.val[v] = x

    # the bitset of the values at positions l..r
    def _or(self, l, r):
        bits = self.bits
        l += self.n
        r += self.n + 1
        res = 0
        while l < r:
            if l & 1:
                res |= bits[l]
                l += 1
            if r & 1:
                r -= 1
                res |= bits[r]
            l >>= 1
            r >>= 1
        return res

    # the bitset of the @VALS@ on the path a..b: the OR over its chain pieces
    def _pathBits(self, a, b):
        head, par, dep, pos = self.head, self.par, self.dep, self.pos
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res |= self._or(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
@LCA_PIECE@
'''

CPP = '''\
template <typename T>
struct Tree {
@MEMBERS@
    HotVector<T> val;  // @VAL_NOTE@
    unordered_map<T, int> ids;  // each value's bit, handed out as values first appear
    int cap, words;  // how many distinct values the bitsets have room for; how many 64-bit words that is
@BITS_NOTE@
    HotVector<unsigned long long> bits;
    mutable HotVector<unsigned long long> acc;  // the bitset a query ORs its nodes into

@CTOR_NOTE@
@CTOR@ {
@LAYOUT@
@VALUES@        for (int i = @FIRST@; i < n; i++) ids.emplace(val[order[i]], (int)ids.size());
        cap = distinctCap > 0 ? distinctCap : max(1, (int)ids.size());
        if ((int)ids.size() > cap)
            throw invalid_argument("Tree: the values hold " + to_string(ids.size()) +
                                   " distinct ones, more than distinctCap = " + to_string(cap));
        words = (cap + 63) / 64;
        bits.assign((size_t)2 * n * words, 0), acc.assign(words, 0);
        for (int i = @FIRST@; i < n; i++) {
            int b = ids[val[order[i]]];
            bits[(size_t)(n + i) * words + (b >> 6)] |= 1ULL << (b & 63);
        }
        for (int i = n - 1; i > 0; i--) pull(i);
    }

    // seg node i's bitset = the OR of its two children's
    LEETCODE_NO_SANITIZE void pull(int i) {
        unsigned long long *p = &bits[(size_t)i * words], *l = &bits[(size_t)2 * i * words], *r = l + words;
        for (int w = 0; w < words; w++) p[w] = l[w] | r[w];
    }

    // the bit of value x: a new one the first time x appears (throws length_error once distinctCap values have one)
    int idOf(T x) {
        auto it = ids.find(x);
        if (it != ids.end()) return it->second;
        if ((int)ids.size() >= cap)
            throw length_error("Tree: more than distinctCap = " + to_string(cap) +
                               " distinct values (pass a bigger distinctCap)");
        int b = (int)ids.size();
        ids.emplace(x, b);
        return b;
    }

    // the value kept at node v becomes x
    void setValue(int v, T x) {
        int b = idOf(x);
        int i = n + pos[v];
        unsigned long long* p = &bits[(size_t)i * words];
        for (int w = 0; w < words; w++) p[w] = 0;
        p[b >> 6] = 1ULL << (b & 63);
        for (i >>= 1; i > 0; i >>= 1) pull(i);
        val[v] = x;
    }

    // ORs the bitsets of the values at positions l..r into acc
    LEETCODE_NO_SANITIZE void orInto(int l, int r) const {
        unsigned long long* out = &acc[0];
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) {
                const unsigned long long* p = &bits[(size_t)l++ * words];
                for (int w = 0; w < words; w++) out[w] |= p[w];
            }
            if (r & 1) {
                const unsigned long long* p = &bits[(size_t)--r * words];
                for (int w = 0; w < words; w++) out[w] |= p[w];
            }
        }
    }

    // how many bits acc has set, emptying it for the next query
    LEETCODE_NO_SANITIZE int takeCount() const {
        int count = 0;
        for (int w = 0; w < words; w++) count += __builtin_popcountll(acc[w]), acc[w] = 0;
        return count;
    }

    // how many distinct @VALS@ are on the path a..b: the OR over its chain pieces
    LEETCODE_NO_SANITIZE int pathCount(int a, int b) const {
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            orInto(pos[head[a]], pos[a]);
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
@LCA_PIECE@
        return takeCount();
    }
'''


def note(cm, text, pad):
    """a comment block at this indent, wrapped the way the repo's formatter would."""
    lines, cur = [], " " * pad + cm
    for w in text.split(" "):
        if len(cur) + 1 + len(w) > 120:
            lines.append(cur)
            cur = " " * pad + cm
        cur += " " + w
    return "\n".join(lines + [cur])


def make(edge):
    t = "edge" if edge else "node"
    folder = f"path-distinct-bitset-{t}"
    vals, val_word, x = ("edge weights", "weight", "w") if edge else ("node values", "val", "x")
    at = "a - b" if edge else "node"
    nodes = ("a", "b") if edge else ("node",)
    costs, py_ops, cpp_ops = {}, [], []

    def add_op(name, args, types, ret, cost, doc, py_body, cpp_body, where=nodes, const=False):
        full = t + name
        costs[full] = cost
        py_ops.append(G.comment("#", cost, doc) + f"    def {full}(self, {', '.join(list(where) + args)}):\n" + py_body)
        decl = ", ".join([f"int {v}" for v in where] + [f"{ty} {a}" for ty, a in zip(types, args)])
        mark = "LEETCODE_NO_SANITIZE " if const else ""  # (an update reaches the id map: left to the sanitizers)
        cpp_ops.append(G.comment("//", cost, doc) + f"    {mark}{ret} {full}({decl}){' const' if const else ''} {{\n" + cpp_body
                       + "    }\n")

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
        return G.py_check(t + name, nodes) + "        v = node\n", G.cpp_check(t + name, nodes) + "        int v = node;\n"

    upd = "log(N)*D/64"
    p, c = here("Get")
    add_op("Get", [], [], "T", "1", f"{val_word}({at}){either}", p + "        return self.val[v]\n", c + "        return val[v];\n",
           const=True)
    p, c = here("Assign")
    add_op("Assign", [x], ["T"], "void", upd, f"{val_word}({at}) = {x}{either}", p + f"        self._set(v, {x})\n",
           c + f"        setValue(v, {x});\n")
    p, c = here("Add")
    add_op("Add", [x], ["T"], "void", upd, f"{val_word}({at}) += {x}{either}", p + f"        self._set(v, self.val[v] + {x})\n",
           c + f"        setValue(v, val[v] + {x});\n")
    for name, sign in (("Chmax", ">"), ("Chmin", "<")):
        p, c = here(name)
        add_op(name, [x], ["T"], "void", upd, f"{val_word}({at}) = {name[2:].lower()}({val_word}, {x}){either}",
               p + f"        if {x} {sign} self.val[v]:\n            self._set(v, {x})\n",
               c + f"        if ({x} {sign} val[v]) setValue(v, {x});\n")

    # ---- a path
    path_cost, sub_cost = "log^2(N)*D/64", "log(N)*D/64"
    size_py = "self._dist(a, b)" + ("" if edge else " + 1")
    size_cpp = "distOf(a, b)" + ("" if edge else " + 1")
    none0, none1 = ("; 0 when a == b (no edges)", "; True when a == b (no edges)") if edge else ("", "")
    add_op("PathCountDistinct", [], [], "int", path_cost, f"number of distinct {vals} on the path a..b{none0}",
           G.py_check(f"{t}PathCountDistinct", ("a", "b")) + '        return bin(self._pathBits(a, b)).count("1")\n',
           G.cpp_check(f"{t}PathCountDistinct", ("a", "b")) + "        return pathCount(a, b);\n", where=("a", "b"), const=True)
    add_op("PathAllDistinct", [], [], "bool", path_cost, f"are all the {vals} on the path a..b distinct?{none1}",
           G.py_check(f"{t}PathAllDistinct", ("a", "b")) + f'        return bin(self._pathBits(a, b)).count("1") == {size_py}\n',
           G.cpp_check(f"{t}PathAllDistinct", ("a", "b")) + f"        return pathCount(a, b) == {size_cpp};\n",
           where=("a", "b"), const=True)

    # ---- a subtree: one stretch of positions (an edge template leaves out the edge above node)
    none0, none1 = ("; 0 when node is a leaf (no edges)", "; True when node is a leaf (no edges)") if edge else ("", "")
    skip, size_py, size_cpp = (" + 1", "self.sz[node] - 1", "sz[node] - 1") if edge else ("", "self.sz[node]", "sz[node]")
    why = "        # the edges below node: the positions after its own (none for a leaf: an empty stretch)\n" if edge else ""
    sub_py = (f"        l = self.pos[node]\n" + why
              + f'        many = bin(self._or(l{skip}, l + self.sz[node] - 1)).count("1")\n')
    sub_cpp = (why.replace("#", "//") + f"        orInto(pos[node]{skip}, pos[node] + sz[node] - 1);\n"
               "        int many = takeCount();\n")
    add_op("SubtreeCountDistinct", [], [], "int", sub_cost, f"number of distinct {vals} in node's subtree{none0}",
           G.py_check(f"{t}SubtreeCountDistinct", ("node",)) + sub_py.replace("many = ", "return "),
           G.cpp_check(f"{t}SubtreeCountDistinct", ("node",)) + sub_cpp.replace("int many = ", "return "),
           where=("node",), const=True)
    add_op("SubtreeAllDistinct", [], [], "bool", sub_cost, f"are all the {vals} in node's subtree distinct?{none1}",
           G.py_check(f"{t}SubtreeAllDistinct", ("node",)) + sub_py + f"        return many == {size_py}\n",
           G.cpp_check(f"{t}SubtreeAllDistinct", ("node",)) + sub_cpp + f"        return many == {size_cpp};\n",
           where=("node",), const=True)

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
            "  build: N*D/64",
            "@memory:",
            "  layout: none",
            "  node: bits[2*N*D/64]",
            "  tags: none",
            f"  other: val[1*N] {G.LAYOUT_ARRAYS}",
            "  note: D = how many distinct values the bitsets have room for (C++: distinctCap); a bitset is D / 64 words",
        ]
        return "".join(f"{cm} {line}\n" for line in lines)

    how = ("How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one "
           "stretch of positions (pos[node] .. pos[node] + sz[node] - 1). A segment tree over the positions keeps a bitset "
           f"per node, one bit per distinct {'weight' if edge else 'value'} under it. A path a..b is O(log n) chain pieces, "
           "each O(log n) tree nodes: their bitsets ORed together have one bit per distinct value on the path. With D "
           "distinct values a bitset is D / 64 words, so this is for up to a few thousand distinct values (memory is "
           "2 * n * D / 8 bytes). A value gets its bit the first time it appears, also later through an assign.")
    cap_note = {"#": "distinctCap: not needed in Python (its ints grow): accepted so both languages are called the same way.",
                "//": "distinctCap: how many distinct values can ever appear, the ones here now and every one assigned later "
                      "(they size the bitsets). Leave it out when no new value will be assigned."}
    info = type("R", (), {"extra_names": [], "cls": ""})
    marks = {"@VALS@": vals, "@BAD_INPUT@": "an edge has no weight" if edge else "vals has the wrong length",
             "@FIRST@": "1" if edge else "0"}
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
        val_note = "val[v]: the weight of the edge above v (the root has none)"
        py_lca = ("        if l < r:  # (the lca's own position is the edge above it)\n"
                  "            res |= self._or(l + 1, r)\n        return res")
        cpp_lca = "        if (l < r) orInto(l + 1, r);  // (the lca's own position is the edge above it)"
    else:
        doc_py = G.fill_doc(G.PY_DOC, "#", info, "edges, root, vals", "")
        doc_cpp = G.fill_doc(G.CPP_DOC, "//", info, "edges, root, vals", "")
        py_ctor, cpp_ctor = "edges, root, vals", "const vector<vector<E>>& edges, int root, const vector<T>& vals"
        py_values = G.PY_VALS + "        val = list(vals)\n"
        cpp_values = ("        if ((int)vals.size() != hi + 1)\n"
                      '            throw invalid_argument("Tree: vals[node] is node\'s value, so nodes " + nodes + " need vals.size() = " +\n'
                      "                                   to_string(hi + 1) + \", got \" + to_string(vals.size()));\n"
                      "        val.assign(vals.begin(), vals.end());\n")
        val_note = "the node values"
        py_lca = "        return res | self._or(l, r)"
        cpp_lca = "        orInto(l, r);"

    bad = marks["@BAD_INPUT@"]
    py_marks = {
        "@CTOR_NOTE@": note("#", "O(n * D / 64) -- builds the layout and the bitset tree; raises ValueError when the edges are "
                            f"not one tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@BITS_NOTE@": note("#", "bits: a segment tree over the positions (its leaves n .. 2n - 1), each node an int used as a "
                            "bitset with one bit per distinct value under it; a parent is the OR of its two children. ids: "
                            "each value's bit, handed out as values first appear.", 8),
    }
    sig = f"    template <typename E = int> Tree({cpp_ctor}, int distinctCap = 0) : root(root)"
    if len(sig) > 118:
        sig = (f"    template <typename E = int> Tree({cpp_ctor},\n" + " " * 36 + "int distinctCap = 0)\n"
               "        : root(root)")
    cpp_marks = {
        "@CTOR_NOTE@": note("//", "O(n * D / 64) -- builds the layout and the bitset tree; throws invalid_argument when the "
                            f"edges are not one tree on nodes 0..n-1 or 1..n, {bad}, or the values hold more than "
                            "distinctCap distinct ones", 4),
        "@BITS_NOTE@": note("//", "bits: a segment tree over the positions (its leaves n .. 2n - 1), `words` words a node: a "
                            "bitset with one bit per distinct value under the node; a parent is the OR of its two children",
                            4),
        "@CTOR@": sig,
    }

    def doc_with(doc, cm):
        cut = doc.index(f"{cm} How it works")
        return doc[:cut] + G.wrap(cm, cap_note[cm]) + f"{cm}\n" + G.wrap(cm, how)

    def fill(text, extra):
        for k, v in {**marks, **extra}.items():
            text = text.replace(k, v)
        return text

    py = (header("#", "py") + "\nfrom bisect import bisect_left\n\n\n" + doc_with(doc_py, "#")
          + fill(PY, {**py_marks, "@CTOR@": py_ctor, "@LAYOUT@": shape.py_layout_body(), "@VALUES@": py_values, "@LCA_PIECE@": py_lca})
          + "\n" + "\n".join(py_ops) + "\n" + shape.py_shape_methods())
    cpp = (header("//", "cpp") + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n" + shape.FAST_NOTE
           + shape.PRELUDE + doc_with(doc_cpp, "//")
           + fill(CPP, {**cpp_marks, "@LAYOUT@": shape.cpp_layout_body(), "@VALUES@": cpp_values, "@LCA_PIECE@": cpp_lca,
                        "@MEMBERS@": shape.cpp_members().rstrip("\n"), "@VAL_NOTE@": val_note})
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
            print(f"FAIL  tree-queries/{rel}: differs from what gen_tree_bitset.py writes (rerun it)")
        print(f"{len(stale)} stale count-distinct path files" if stale else "count-distinct path templates are fresh")
        sys.exit(1 if stale else 0)
    print(f"{len(sources())} count-distinct path files, {len(stale)} written")


if __name__ == "__main__":
    main()
