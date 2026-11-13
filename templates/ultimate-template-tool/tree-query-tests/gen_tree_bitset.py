"""Writes the count-distinct path templates: tree-queries/path-distinct-bitset-{node,edge}, each template.{py,cpp}.

"How many distinct values are on this path?" cannot be put together from the pieces' own answers (a value on two
pieces counts once), and no fast general way is known. What works when the values are few: a segment tree over the
positions whose nodes each hold a bitset, one bit per distinct value under the node (a parent is the OR of its
children). A path is O(log n) chain pieces, each O(log n) nodes: OR their bitsets and count the bits. That is
O(log^2 n * D / 64) for D distinct values, and 2 * n * D / 8 bytes: fine up to a few thousand distinct values.

A value gets its bit the first time it appears (also later, through an assign), so nothing has to be known up front:
Python ints grow by themselves, and C++ makes every bitset half as wide again when a new value finds all the bits taken.
Assigning one value to a whole path or subtree is lazy: the tag of a tree node is the bit everything under it became.

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
    def __init__(self, @CTOR@):
@LAYOUT@@VALUES@
@BITS_NOTE@
        ids, values = {}, []
        bits, tag = [0] * (2 * n), [-1] * (2 * n)
        for i in range(@FIRST@, n):
            x = @START@[order[i]]
            b = ids.get(x)
            if b is None:
                b = ids[x] = len(values)
                values.append(x)
            bits[n + i], tag[n + i] = 1 << b, b
        for i in range(n - 1, 0, -1):
            bits[i] = bits[2 * i] | bits[2 * i + 1]
        self.ids, self.values, self.bits, self.tag = ids, values, bits, tag

    # hands every assign waiting above leaf p down to the two children, top first
    def _push(self, p):
        bits, tag = self.bits, self.tag
        for s in range(p.bit_length() - 1, 0, -1):
            i = p >> s
            b = tag[i]
            if b >= 0:
                bits[2 * i] = bits[2 * i + 1] = 1 << b
                tag[2 * i] = tag[2 * i + 1] = b
                tag[i] = -1

    # recomputes the seg nodes above leaf p (one with an assign waiting is right as it is)
    def _pull(self, p):
        bits, tag = self.bits, self.tag
        p >>= 1
        while p:
            if tag[p] < 0:
                bits[p] = bits[2 * p] | bits[2 * p + 1]
            p >>= 1

    # the values at positions l..r all become x (nothing for an empty stretch, l > r)
    def _assign(self, l, r, x):
        if l > r:
            return
        b = self.ids.get(x)
        if b is None:
            b = self.ids[x] = len(self.values)
            self.values.append(x)
        bits, tag = self.bits, self.tag
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        i, j = l, r + 1
        while i < j:
            if i & 1:
                bits[i], tag[i] = 1 << b, b
                i += 1
            if j & 1:
                j -= 1
                bits[j], tag[j] = 1 << b, b
            i >>= 1
            j >>= 1
        self._pull(l)
        self._pull(r)

    # the bit of the value at position p: the topmost assign still waiting above its leaf, else the leaf's own
    def _bitAt(self, p):
        tag = self.tag
        p += self.n
        for s in range(p.bit_length() - 1, 0, -1):
            if tag[p >> s] >= 0:
                return tag[p >> s]
        return tag[p]

    # the bitset of the values at positions l..r (0 for an empty stretch, l > r)
    def _or(self, l, r):
        if l > r:
            return 0
        bits = self.bits
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        r += 1
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

    # the path a..b as stretches of positions (l, r), one for each chain piece
    def _pieces(self, a, b):
        head, par, dep, pos = self.head, self.par, self.dep, self.pos
        out = []
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            out.append((pos[head[a]], pos[a]))
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
@LCA_PIECE@
        return out

    # the bitset of the @VALS@ on the path a..b
    def _pathBits(self, a, b):
        res = 0
        for l, r in self._pieces(a, b):
            res |= self._or(l, r)
        return res
'''

CPP = '''\
template <typename T>
struct Tree {
@MEMBERS@
    unordered_map<T, int> ids;  // each value's bit, handed out as values first appear
    HotVector<T> values;  // values[b]: the value whose bit is b
    int words;  // how many 64-bit words a bitset is: room for 64 * words distinct values (widen makes more)
@BITS_NOTE@
    HotVector<unsigned long long> bits;
@TAG_NOTE@
    HotVector<int> tag;
    HotVector<unsigned long long> acc;  // the bitset a query ORs its nodes into

@CTOR_NOTE@
@CTOR@ {
@LAYOUT@
@VALUES@        for (int i = @FIRST@; i < n; i++) ids.emplace(@START@[order[i]], (int)ids.size());
        words = max(1, ((int)ids.size() + 63) / 64);
        values.assign(ids.size(), T());
        for (const auto& kept : ids) values[kept.second] = kept.first;
        bits.assign((size_t)2 * n * words, 0), tag.assign(2 * n, -1), acc.assign(words, 0);
        for (int i = @FIRST@; i < n; i++) apply(n + i, ids[@START@[order[i]]]);
        for (int i = n - 1; i > 0; i--) pull(i);
    }

    // seg node i's bitset = the OR of its two children's
    LEETCODE_NO_SANITIZE void pull(int i) {
        unsigned long long *p = &bits[(size_t)i * words], *l = &bits[(size_t)2 * i * words], *r = l + words;
        for (int w = 0; w < words; w++) p[w] = l[w] | r[w];
    }

    // every value under seg node i becomes the one with bit b
    LEETCODE_NO_SANITIZE void apply(int i, int b) {
        unsigned long long* p = &bits[(size_t)i * words];
        for (int w = 0; w < words; w++) p[w] = 0;
        p[b >> 6] = 1ULL << (b & 63);
        tag[i] = b;
    }

    // hands every assign waiting above leaf p down to the two children, top first
    LEETCODE_NO_SANITIZE void push(int p) {
        for (int s = 31 - __builtin_clz(p); s > 0; s--) {
            int i = p >> s, b = tag[i];
            if (b >= 0) {
                apply(2 * i, b), apply(2 * i + 1, b);
                tag[i] = -1;
            }
        }
    }

    // recomputes the seg nodes above leaf p (one with an assign waiting is right as it is)
    LEETCODE_NO_SANITIZE void pullAbove(int p) {
        for (p >>= 1; p > 0; p >>= 1)
            if (tag[p] < 0) pull(p);
    }

    // the bit of value x: a new one the first time x appears (widening the bitsets first when every bit is taken)
    int idOf(T x) {
        auto it = ids.find(x);
        if (it != ids.end()) return it->second;
        int b = (int)ids.size();
        if (b == 64 * words) widen();
        ids.emplace(x, b);
        values.push_back(x);
        return b;
    }

    // makes every bitset half as wide again (at least one word wider): each seg node's words move to their new place
    // and the new words start empty. O(n * D / 64); all the widenings a tree ever does cost less than five builds
    LEETCODE_NO_SANITIZE void widen() {
        int wider = words + (words > 1 ? words / 2 : 1);
        HotVector<unsigned long long> grown((size_t)2 * n * wider, 0);
        for (int i = 1; i < 2 * n; i++) {
            const unsigned long long* from = &bits[(size_t)i * words];
            unsigned long long* to = &grown[(size_t)i * wider];
            for (int w = 0; w < words; w++) to[w] = from[w];
        }
        bits.swap(grown);
        acc.assign(wider, 0);
        words = wider;
    }

    // the values at positions l..r all become x (nothing for an empty stretch, l > r)
    void assignRange(int l, int r, T x) {
        if (l > r) return;
        int b = idOf(x);
        l += n, r += n;
        push(l), push(r);
        for (int i = l, j = r + 1; i < j; i >>= 1, j >>= 1) {
            if (i & 1) apply(i++, b);
            if (j & 1) apply(--j, b);
        }
        pullAbove(l), pullAbove(r);
    }

    // the bit of the value at position p: the topmost assign still waiting above its leaf, else the leaf's own
    LEETCODE_NO_SANITIZE int bitAt(int p) const {
        p += n;
        for (int s = 31 - __builtin_clz(p); s > 0; s--)
            if (tag[p >> s] >= 0) return tag[p >> s];
        return tag[p];
    }

    // ORs the bitsets of the values at positions l..r into acc (nothing for an empty stretch, l > r)
    LEETCODE_NO_SANITIZE void orInto(int l, int r) {
        if (l > r) return;
        l += n, r += n;
        push(l), push(r);
        unsigned long long* out = &acc[0];
        for (r++; l < r; l >>= 1, r >>= 1) {
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
    LEETCODE_NO_SANITIZE int takeCount() {
        int count = 0;
        for (int w = 0; w < words; w++) count += __builtin_popcountll(acc[w]), acc[w] = 0;
        return count;
    }

    // the path a..b as stretches of positions ls[i]..rs[i], one for each chain piece; returns how many there are
    LEETCODE_NO_SANITIZE int pieces(int a, int b, int* ls, int* rs) const {
        int m = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            ls[m] = pos[head[a]], rs[m++] = pos[a];
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
@LCA_PIECE@
        return m;
    }

    // how many distinct @VALS@ are on the path a..b
    LEETCODE_NO_SANITIZE int pathCount(int a, int b) {
        int ls[64], rs[64], m = pieces(a, b, ls, rs);
        for (int i = 0; i < m; i++) orInto(ls[i], rs[i]);
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

    def add_op(name, args, types, ret, cost, doc, py_body, cpp_body, where=nodes, mark=True, const=False):
        full = t + name
        costs[full] = cost
        py_ops.append(G.comment("#", cost, doc) + f"    def {full}(self, {', '.join(list(where) + args)}):\n" + py_body)
        decl = ", ".join([f"int {v}" for v in where] + [f"{ty} {a}" for ty, a in zip(types, args)])
        hot = "LEETCODE_NO_SANITIZE " if mark else ""  # (an update reaches the id map: left to the sanitizers)
        cpp_ops.append(G.comment("//", cost, doc) + f"    {hot}{ret} {full}({decl}){' const' if const else ''} {{\n" + cpp_body
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
            return f'        p = self.pos[self._edge("{t}{name}", a, b)]\n', f'        int p = pos[edgeAt("{t}{name}", a, b)];\n'
        return G.py_check(t + name, nodes) + "        p = self.pos[node]\n", G.cpp_check(t + name, nodes) + "        int p = pos[node];\n"

    # (an op that can bring a value never seen before may widen the C++ bitsets: amortized)
    upd = "log(N)*D/64 amortized"
    p, c = here("Get")
    add_op("Get", [], [], "T", "log(N)", f"{val_word}({at}){either}", p + "        return self.values[self._bitAt(p)]\n",
           c + "        return values[bitAt(p)];\n", const=True)
    p, c = here("Assign")
    add_op("Assign", [x], ["T"], "void", upd, f"{val_word}({at}) = {x}{either}", p + f"        self._assign(p, p, {x})\n",
           c + f"        assignRange(p, p, {x});\n", mark=False)
    p, c = here("Add")
    add_op("Add", [x], ["T"], "void", upd, f"{val_word}({at}) += {x}{either}",
           p + f"        self._assign(p, p, self.values[self._bitAt(p)] + {x})\n",
           c + f"        assignRange(p, p, values[bitAt(p)] + {x});\n", mark=False)
    for name, sign in (("Chmax", ">"), ("Chmin", "<")):
        p, c = here(name)
        add_op(name, [x], ["T"], "void", upd, f"{val_word}({at}) = {name[2:].lower()}({val_word}, {x}){either}",
               p + f"        if {x} {sign} self.values[self._bitAt(p)]:\n            self._assign(p, p, {x})\n",
               c + f"        if ({x} {sign} values[bitAt(p)]) assignRange(p, p, {x});\n", mark=False)

    # ---- a path
    path_cost, sub_cost = "log^2(N)*D/64", "log(N)*D/64"
    every = f"{val_word} = {x} for every {t}"
    add_op("PathAssign", [x], ["T"], "void", path_cost + " amortized", f"{every} on the path a..b",
           G.py_check(f"{t}PathAssign", ("a", "b"))
           + f"        for l, r in self._pieces(a, b):\n            self._assign(l, r, {x})\n",
           G.cpp_check(f"{t}PathAssign", ("a", "b")) + "        int ls[64], rs[64], m = pieces(a, b, ls, rs);\n"
           f"        for (int i = 0; i < m; i++) assignRange(ls[i], rs[i], {x});\n", where=("a", "b"), mark=False)
    size_py = "self._dist(a, b)" + ("" if edge else " + 1")
    size_cpp = "distOf(a, b)" + ("" if edge else " + 1")
    none0, none1 = ("; 0 when a == b (no edges)", "; True when a == b (no edges)") if edge else ("", "")
    add_op("PathCountDistinct", [], [], "int", path_cost, f"number of distinct {vals} on the path a..b{none0}",
           G.py_check(f"{t}PathCountDistinct", ("a", "b")) + '        return bin(self._pathBits(a, b)).count("1")\n',
           G.cpp_check(f"{t}PathCountDistinct", ("a", "b")) + "        return pathCount(a, b);\n", where=("a", "b"))
    add_op("PathAllDistinct", [], [], "bool", path_cost, f"are all the {vals} on the path a..b distinct?{none1}",
           G.py_check(f"{t}PathAllDistinct", ("a", "b")) + f'        return bin(self._pathBits(a, b)).count("1") == {size_py}\n',
           G.cpp_check(f"{t}PathAllDistinct", ("a", "b")) + f"        return pathCount(a, b) == {size_cpp};\n",
           where=("a", "b"))

    # ---- a subtree: one stretch of positions (an edge template leaves out the edge above node)
    none0, none1 = ("; 0 when node is a leaf (no edges)", "; True when node is a leaf (no edges)") if edge else ("", "")
    skip, size_py, size_cpp = (" + 1", "self.sz[node] - 1", "sz[node] - 1") if edge else ("", "self.sz[node]", "sz[node]")
    why = "        # the edges below node: the positions after its own (none for a leaf: an empty stretch)\n" if edge else ""
    add_op("SubtreeAssign", [x], ["T"], "void", sub_cost + " amortized", f"{every} in node's subtree",
           G.py_check(f"{t}SubtreeAssign", ("node",)) + "        l = self.pos[node]\n" + why
           + f"        self._assign(l{skip}, l + self.sz[node] - 1, {x})\n",
           G.cpp_check(f"{t}SubtreeAssign", ("node",)) + why.replace("#", "//")
           + f"        assignRange(pos[node]{skip}, pos[node] + sz[node] - 1, {x});\n", where=("node",), mark=False)
    sub_py = (f"        l = self.pos[node]\n" + why
              + f'        many = bin(self._or(l{skip}, l + self.sz[node] - 1)).count("1")\n')
    sub_cpp = (why.replace("#", "//") + f"        orInto(pos[node]{skip}, pos[node] + sz[node] - 1);\n"
               "        int many = takeCount();\n")
    add_op("SubtreeCountDistinct", [], [], "int", sub_cost, f"number of distinct {vals} in node's subtree{none0}",
           G.py_check(f"{t}SubtreeCountDistinct", ("node",)) + sub_py.replace("many = ", "return "),
           G.cpp_check(f"{t}SubtreeCountDistinct", ("node",)) + sub_cpp.replace("int many = ", "return "),
           where=("node",))
    add_op("SubtreeAllDistinct", [], [], "bool", sub_cost, f"are all the {vals} in node's subtree distinct?{none1}",
           G.py_check(f"{t}SubtreeAllDistinct", ("node",)) + sub_py + f"        return many == {size_py}\n",
           G.cpp_check(f"{t}SubtreeAllDistinct", ("node",)) + sub_cpp + f"        return many == {size_cpp};\n",
           where=("node",))

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
            "  tags: tag[2*N]",
            f"  other: {G.LAYOUT_ARRAYS}",
            "  note: D = how many distinct values ever appeared (a value keeps its bit once it has one); a bitset is "
            "D / 64 words. C++ widens every bitset by half when a new value finds all the bits taken (the amortized "
            "costs: one widening is N*D/64, all of them together less than five builds), so its bitsets can be up to "
            "1.5x that wide, and 2.5x while one widening runs",
        ]
        return "".join(f"{cm} {line}\n" for line in lines)

    how = ("How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one "
           "stretch of positions (pos[node] .. pos[node] + sz[node] - 1). A segment tree over the positions keeps a bitset "
           f"per node, one bit per distinct {'weight' if edge else 'value'} under it. A path a..b is O(log n) chain pieces, "
           "each O(log n) tree nodes: their bitsets ORed together have one bit per distinct value on the path. With D "
           "distinct values a bitset is D / 64 words, so this is for up to a few thousand distinct values (memory is "
           "2 * n * D / 8 bytes). A value gets its bit the first time it appears, also later through an assign, and keeps "
           "it. An assign over a path or a subtree is kept at the O(log n) tree nodes that cover each stretch and handed "
           "down only when something below one of them is needed.")
    # (C++ only: a Python int grows by itself)
    widen_note = (" The bitsets start just wide enough for the values there at the start. When a value never seen before "
                  "finds every bit taken, all of them are made half as wide again: that one call costs O(n * D / 64), "
                  "and all the widenings a tree ever does cost less than five builds. While it widens, the old and the "
                  "new bitsets exist side by side, so a tree whose values keep coming peaks at up to 2.5 times the "
                  "memory above; one whose values are all there at the start never widens.")
    info = type("R", (), {"extra_names": [], "cls": ""})
    marks = {"@VALS@": vals, "@BAD_INPUT@": "an edge has no weight" if edge else "vals has the wrong length",
             "@FIRST@": "1" if edge else "0", "@START@": "above" if edge else "vals"}
    tag_note = ("tag[i]: for a leaf, the bit of its value; for a node above, the bit every value under it was assigned and "
                "its children have not been told yet (-1: none)")
    if edge:
        doc_py = G.fill_doc(G.PY_DOC_EDGE, "#", info, "edges, root", "", "edge")
        doc_cpp = G.fill_doc(G.CPP_DOC_EDGE, "//", info, "edges, root", "", "edge")
        py_ctor, cpp_ctor = "edges, root", "const vector<vector<E>>& edges, int root"
        py_values = ("        for e in edges:\n"
                     "            if len(e) != 3:\n"
                     '                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")\n'
                     "        above = [0] * (hi + 1)  # above[v]: the weight of the edge above v (the root has none)\n"
                     "        for e in edges:\n"
                     "            above[e[0] if par[e[0]] == e[1] else e[1]] = e[2]\n")
        cpp_values = ("        for (const auto& e : edges)\n"
                      '            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");\n'
                      "        vector<T> above(hi + 1, T(0));  // above[v]: the weight of the edge above v (the root has none)\n"
                      "        for (const auto& e : edges) {\n"
                      "            int a = (int)e[0], b = (int)e[1];\n"
                      "            above[par[a] == b ? a : b] = (T)e[2];\n"
                      "        }\n")
        py_lca = ("        if l < r:  # (the lca's own position is the edge above it)\n"
                  "            out.append((l + 1, r))")
        cpp_lca = "        if (l < r) ls[m] = l + 1, rs[m++] = r;  // (the lca's own position is the edge above it)"
    else:
        doc_py = G.fill_doc(G.PY_DOC, "#", info, "edges, root, vals", "")
        doc_cpp = G.fill_doc(G.CPP_DOC, "//", info, "edges, root, vals", "")
        py_ctor, cpp_ctor = "edges, root, vals", "const vector<vector<E>>& edges, int root, const vector<T>& vals"
        py_values = G.PY_VALS
        cpp_values = ("        if ((int)vals.size() != hi + 1)\n"
                      '            throw invalid_argument("Tree: vals[node] is node\'s value, so nodes " + nodes + " need vals.size() = " +\n'
                      "                                   to_string(hi + 1) + \", got \" + to_string(vals.size()));\n")
        py_lca = "        out.append((l, r))"
        cpp_lca = "        ls[m] = l, rs[m++] = r;"

    bad = marks["@BAD_INPUT@"]
    py_marks = {
        "@CTOR_NOTE@": note("#", "O(n * D / 64) -- builds the layout and the bitset tree; raises ValueError when the edges are "
                            f"not one tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@BITS_NOTE@": note("#", "bits: a segment tree over the positions (its leaves n .. 2n - 1), each node an int used as a "
                            "bitset with one bit per distinct value under it; a parent is the OR of its two children. ids: "
                            "each value's bit, handed out as values first appear; values[b]: the value whose bit is b. "
                            + tag_note + ".", 8),
    }
    sig = f"    template <typename E = int> Tree({cpp_ctor}) : root(root)"
    if len(sig) > 118:
        sig = f"    template <typename E = int> Tree({cpp_ctor})\n        : root(root)"
    cpp_marks = {
        "@CTOR_NOTE@": note("//", "O(n * D / 64) -- builds the layout and the bitset tree; throws invalid_argument when the "
                            f"edges are not one tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@BITS_NOTE@": note("//", "bits: a segment tree over the positions (its leaves n .. 2n - 1), `words` words a node: a "
                            "bitset with one bit per distinct value under the node; a parent is the OR of its two children",
                            4),
        "@TAG_NOTE@": note("//", tag_note, 4),
        "@CTOR@": sig,
    }

    def doc_with(doc, cm):
        cut = doc.index(f"{cm} How it works")
        return doc[:cut] + G.wrap(cm, how + (widen_note if cm == "//" else ""))

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
                        "@MEMBERS@": shape.cpp_members().rstrip("\n")})
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
