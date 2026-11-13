"""Writes the single-log path sum / xor / even-frequency templates: tree-queries/path-{sum,xor,even}-fenwick-{node,edge},
each template.{py,cpp}.

A wrapped range template (gen_tree.py) answers a path sum in O(log^2 n): O(log n) chain pieces, a range sum each. With
only one-node (or one-edge) updates there is a single-log way, because a sum can be taken back: put each value at its
node's position and take it back just past that node's subtree. A prefix up to pos[x] then holds exactly the values on
the path root..x, so

    nodes:  path(a, b) = above(a) + above(b) - 2 * above(lca) + val(lca)
    edges:  path(a, b) = above(a) + above(b) - 2 * above(lca)      (a node carries the edge above it)

with `above` one Fenwick prefix. Xor works the same way (it is its own inverse). A second Fenwick tree with each value
at its own position gives subtree sums.

The even-frequency templates are the xor ones over random keys: each distinct value has a key, an even number of equal
values xors to 0, so "does every value on this path appear an even number of times?" is "do its keys xor to 0?" (a
wrong yes has chance about 2^-62).

    python3 gen_tree_fenwick.py           # write
    python3 gen_tree_fenwick.py --check   # exit 1 if a file on disk differs from what this would write
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "set-tests", "generators"))
import gen_tree as G  # noqa: E402
import gen_tree_shape as shape  # noqa: E402
from format_long_lines import long_lines  # noqa: E402
from gen_sets import check_finished  # noqa: E402

DIR = G.DIR
KIND = "euler-fenwick"

PY = '''\
class Tree:
    # O(n) -- builds the layout and the two Fenwick trees; raises ValueError when the edges are not one tree on nodes
    # 0..n-1 or 1..n, or @BAD_INPUT@
    def __init__(self, @CTOR@):
@LAYOUT@@VALUES@
@TREES_NOTE@        down = [0] * (n + 2)
        sub = [0] * (n + 1)
        for v in bfs:
            x = @X_OF_V@
            i = pos[v] + 1
            down[i] @ADD@ x
            down[i + sz[v]] @SUB@ x
            sub[i] @ADD@ x
        for i in range(1, n + 1):
            j = i + (i & -i)
            if j <= n:
                down[j] @ADD@ down[i]
                sub[j] @ADD@ sub[i]
        self.val, self.down, self.sub = val, down, sub
@STORE_KEYS@
    # the value kept at node v changes by d@XOR_NOTE@
    def _change(self, v, d):
        n, down, sub = self.n, self.down, self.sub
        i = self.pos[v] + 1
        j = i
        while j <= n:
            sub[j] @ADD@ d
            down[j] @ADD@ d
            j += j & -j
        j = i + self.sz[v]
        while j <= n:
            down[j] @SUB@ d
            j += j & -j

    # the @SUM@ of the @VALS@ on the path root..v
    def _above(self, v):
        down = self.down
        i = self.pos[v] + 1
        res = 0
        while i > 0:
            res @ADD@ down[i]
            i -= i & -i
        return res

    # the @SUM@ of the values at positions 1..i of sub
    def _upTo(self, i):
        sub = self.sub
        res = 0
        while i > 0:
            res @ADD@ sub[i]
            i -= i & -i
        return res
'''

CPP = '''\
template <typename T>
struct Tree {
@MEMBERS@
    @S_DECL@
    HotVector<T> val;  // @VAL_NOTE@
@KEY_MEMBERS@@TREES_NOTE@    HotVector<S> down, sub;

    // O(n) -- builds the layout and the two Fenwick trees; throws invalid_argument when the edges are not one tree on
    // nodes 0..n-1 or 1..n, or @BAD_INPUT@
    template <typename E = int> Tree(@CTOR@) : root(root) {
@LAYOUT@
@VALUES@        down.assign(n + 2, 0), sub.assign(n + 1, 0);
        for (int k = 0; k < n; k++) {
            int v = bfs[k], i = pos[v] + 1;
            S x = @X_OF_V@;
            down[i] @ADD@ x, down[i + sz[v]] @SUB@ x, sub[i] @ADD@ x;
        }
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) down[j] @ADD@ down[i], sub[j] @ADD@ sub[i];
        }
    }

    // the value kept at node v changes by d@XOR_NOTE@
    LEETCODE_NO_SANITIZE void change(int v, S d) {
        int i = pos[v] + 1;
        for (int j = i; j <= n; j += j & -j) sub[j] @ADD@ d, down[j] @ADD@ d;
        for (int j = i + sz[v]; j <= n; j += j & -j) down[j] @SUB@ d;
    }

    // the @SUM@ of the @VALS@ on the path root..v
    LEETCODE_NO_SANITIZE S above(int v) const {
        S res = 0;
        for (int i = pos[v] + 1; i > 0; i -= i & -i) res @ADD@ down[i];
        return res;
    }

    // the @SUM@ of the values at positions 1..i of sub
    LEETCODE_NO_SANITIZE S upTo(int i) const {
        S res = 0;
        for (; i > 0; i -= i & -i) res @ADD@ sub[i];
        return res;
    }
'''


def make(edge, mode):
    """mode: "sum", "xor", or "even" (every value an even number of times: the xor of random keys)."""
    t = "edge" if edge else "node"
    xor, even = mode != "sum", mode == "even"
    what = "xor" if xor else "sum"
    folder = f"path-{mode}-fenwick-{t}"
    vals, one, val_word, x = (("edge weights", "edge", "weight", "w") if edge else ("node values", "node", "val", "x"))
    held = f"keys of the {vals}" if even else vals  # what the two trees add up
    add, sub = ("^=", "^=") if xor else ("+=", "-=")
    at_py, at_cpp = ("a - b", "a - b") if edge else ("node", "node")
    nodes = ("a", "b") if edge else ("node",)
    marks = {"@SUM@": what, "@VALS@": held, "@ADD@": add, "@SUB@": sub,
             "@XOR_NOTE@": (" (d = the old value's key xor the new one's)" if even else
                            " (d = the old value xor the new one)" if xor else ""),
             "@BAD_INPUT@": "an edge has no weight" if edge else "vals has the wrong length"}

    def fill(text, cm, pad):
        note = (f"down: its prefix up to pos[x] is the {what} of the {held} on the path root..x (each value sits at its "
                "node's position and is taken back just past that node's subtree). sub: each value at its node's position, "
                "so a subtree is one stretch. Both are Fenwick trees over positions 1..n.")
        text = text.replace("@TREES_NOTE@", "".join(line + "\n" for line in G.wrap(" " * pad + cm, note).split("\n") if line))
        for k, v in marks.items():
            text = text.replace(k, v)
        return text

    costs, py_ops, cpp_ops = {}, [], []

    def add_op(name, args, types, ret, cost, doc, py_body, cpp_body, where=nodes, const=False):
        full = t + name
        costs[full] = cost
        py_ops.append(G.comment("#", cost, doc.format(none="None", raises="IndexError"))
                      + f"    def {full}(self, {', '.join(list(where) + args)}):\n" + py_body)
        decl = ", ".join([f"int {v}" for v in where] + [f"{ty} {a}" for ty, a in zip(types, args)])
        cpp_ops.append(G.comment("//", cost, doc.format(none="nullopt", raises="throws out_of_range"))
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
    add_op("Get", [], [], "T", "1", f"{val_word}({at_py}){either}", p + "        return self.val[v]\n", c + "        return val[v];\n",
           const=True)
    if even:  # a value is in the trees as its key
        delta_py, delta_cpp = "self._key(self.val[v]) ^ self._key({new})", "keyOf(val[v]) ^ keyOf({new})"
        py_ops.append("    # the random key of a value: equal values share it, so an even number of them xors to 0\n"
                      "    def _key(self, x):\n"
                      "        k = self.keys.get(x)\n"
                      "        if k is None:\n"
                      "            k = self.keys[x] = random.getrandbits(62) + 1\n"
                      "        return k\n")
        cpp_ops.append("    // the random key of a value: equal values share it, so an even number of them xors to 0 (the value plus this run's\n"
                       "    // seed, mixed: splitmix64)\n"
                       "    LEETCODE_NO_SANITIZE unsigned long long keyOf(T x) const {\n"
                       "        unsigned long long z = (unsigned long long)x + seed;\n"
                       "        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;\n"
                       "        z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;\n"
                       "        return z ^ (z >> 31);\n    }\n")
    else:
        delta_py = "self.val[v] ^ {new}" if xor else "{new} - self.val[v]"
        delta_cpp = "(S)val[v] ^ (S){new}" if xor else "(S){new} - (S)val[v]"
    p, c = here("Assign")
    add_op("Assign", [x], ["T"], "void", "log(N)", f"{val_word}({at_py}) = {x}{either}",
           p + f"        self._change(v, {delta_py.format(new=x)})\n        self.val[v] = {x}\n",
           c + f"        change(v, {delta_cpp.format(new=x)});\n        val[v] = {x};\n")
    p, c = here("Add")
    add_op("Add", [x], ["T"], "void", "log(N)", f"{val_word}({at_py}) += {x}{either}",
           p + f"        new = self.val[v] + {x}\n        self._change(v, {delta_py.format(new='new')})\n        self.val[v] = new\n",
           c + f"        T now = val[v] + {x};\n        change(v, {delta_cpp.format(new='now')});\n        val[v] = now;\n")
    for name, sign in (("Chmax", ">"), ("Chmin", "<")):
        p, c = here(name)
        add_op(name, [x], ["T"], "void", "log(N)", f"{val_word}({at_py}) = {name[2:].lower()}({val_word}, {x}){either}",
               p + f"        if {x} {sign} self.val[v]:\n            self._change(v, {delta_py.format(new=x)})\n            self.val[v] = {x}\n",
               c + f"        if ({x} {sign} val[v]) {{\n            change(v, {delta_cpp.format(new=x)});\n            val[v] = {x};\n        }}\n")

    # ---- a path: two prefixes down from the root, the part above the lca taken back twice
    big = "AllEvenFrequency" if even else "XOR" if xor else "Sum"
    path_ret, path_doc = "S", f"{what} of the {vals} on the path a..b"
    if even:  # the keys of the path xor to 0
        py_path = "(self._above(a) ^ self._above(b)" + ("" if edge else " ^ self._key(self.val[self._lca(a, b)])") + ") == 0"
        cpp_path = "(above(a) ^ above(b)" + ("" if edge else " ^ keyOf(val[lcaOf(a, b)])") + ") == 0"
        py_body = G.py_check(f"{t}Path{big}", ("a", "b")) + f"        return {py_path}\n"
        cpp_body = G.cpp_check(f"{t}Path{big}", ("a", "b")) + f"        return {cpp_path};\n"
        chance = " (by random keys: a wrong yes has chance about 2^-62)"
        path_ret, path_doc = "bool", f"does every value among the {vals} on the path a..b appear an even number of times?{chance}"
    elif xor:
        py_path = "self._above(a) ^ self._above(b)" + ("" if edge else " ^ self.val[self._lca(a, b)]")
        cpp_path = "above(a) ^ above(b)" + ("" if edge else " ^ (S)val[lcaOf(a, b)]")
        py_body = G.py_check(f"{t}Path{big}", ("a", "b")) + f"        return {py_path}\n"
        cpp_body = G.cpp_check(f"{t}Path{big}", ("a", "b")) + f"        return {cpp_path};\n"
    else:
        py_body = (G.py_check(f"{t}Path{big}", ("a", "b")) + "        c = self._lca(a, b)\n"
                   "        return self._above(a) + self._above(b) - 2 * self._above(c)" + ("" if edge else " + self.val[c]") + "\n")
        cpp_body = (G.cpp_check(f"{t}Path{big}", ("a", "b")) + "        int c = lcaOf(a, b);\n"
                    "        return above(a) + above(b) - 2 * above(c)" + ("" if edge else " + (S)val[c]") + ";\n")
    empty = ("; True when a == b (no edges)" if even else "; 0 when a == b (no edges)") if edge else ""
    add_op("Path" + big, [], [], path_ret, "log(N)", path_doc + empty, py_body, cpp_body, where=("a", "b"), const=True)

    # ---- a subtree: one stretch of sub (an edge template leaves out the edge above node)
    first = "self.pos[node] + 1" if edge else "self.pos[node]"
    cfirst = "pos[node] + 1" if edge else "pos[node]"
    minus = "^" if xor else "-"
    empty = ("; True when node is a leaf (no edges)" if even else "; 0 when node is a leaf (no edges)") if edge else ""
    sub_py = f"self._upTo(self.pos[node] + self.sz[node]) {minus} self._upTo({first})"
    sub_cpp = f"upTo(pos[node] + sz[node]) {minus} upTo({cfirst})"
    sub_doc = f"{what} of the {vals} in node's subtree"
    if even:
        sub_py, sub_cpp = f"({sub_py}) == 0", f"({sub_cpp}) == 0"
        sub_doc = f"does every value among the {vals} in node's subtree appear an even number of times?{chance}"
    add_op("Subtree" + big, [], [], path_ret, "log(N)", sub_doc + empty,
           G.py_check(f"{t}Subtree{big}", ("node",)) + f"        return {sub_py}\n",
           G.cpp_check(f"{t}Subtree{big}", ("node",)) + f"        return {sub_cpp};\n", where=("node",), const=True)

    # ---- the two files
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
            "  node: down[1*N] sub[1*N]",
            "  tags: none",
            f"  other: val[1*N] {G.LAYOUT_ARRAYS}",
        ]
        return "".join(f"{cm} {line}\n" for line in lines)

    how = ("How it works: one heavy-light pass gives every node a position, so that each subtree is one stretch of positions "
           f"(pos[node] .. pos[node] + sz[node] - 1). Each {'weight' if edge else 'value'} sits at "
           f"{'its lower end' if edge else 'its node'}'s position in a Fenwick tree and is taken back just past that node's "
           f"subtree, so a prefix up to pos[x] is the {what} over the path root..x. A path a..b is then two such prefixes "
           f"with the part above the lca taken back{'' if xor else ' twice'}: one log, where chain pieces would take two. "
           "Only one value changes at a time (no path or subtree updates).")
    if even:
        how = ("How it works: every distinct value gets a random key, and an even number of equal values xors to 0. So "
               "the values of a path all appear an even number of times exactly when their keys xor to 0 (a wrong yes has "
               "chance about 2^-62). The keys are kept the way a single-log path xor is: one heavy-light pass gives every "
               f"node a position; each key sits at {'its lower end' if edge else 'its node'}'s position in a Fenwick tree and "
               "is taken back just past that node's subtree, so a prefix up to pos[x] is the xor over the path root..x, and "
               "a path a..b is two such prefixes with the part above the lca taken back. Only one value changes at a time "
               "(no path or subtree updates).")
    info = type("R", (), {"extra_names": [], "cls": ""})
    if edge:
        doc_py = G.fill_doc(G.PY_DOC_EDGE, "#", info, "edges, root", "", "edge")
        doc_cpp = G.fill_doc(G.CPP_DOC_EDGE, "//", info, "edges, root", "", "edge")
        marks["@CTOR@"] = "edges, root"
        py_values = ("        for e in edges:\n"
                     "            if len(e) != 3:\n"
                     '                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")\n'
                     "        val = [0] * (hi + 1)  # val[v]: the weight of the edge above v (the root has none: 0)\n"
                     "        for e in edges:\n"
                     "            val[e[0] if par[e[0]] == e[1] else e[1]] = e[2]\n")
        cpp_values = ("        for (const auto& e : edges)\n"
                      '            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");\n'
                      "        val.assign(hi + 1, T(0));\n"
                      "        for (const auto& e : edges) {\n"
                      "            int a = (int)e[0], b = (int)e[1];\n"
                      "            val[par[a] == b ? a : b] = (T)e[2];\n"
                      "        }\n")
        cpp_ctor = "const vector<vector<E>>& edges, int root"
        val_note = "val[v]: the weight of the edge above v (the root has none: 0)"
    else:
        doc_py = G.fill_doc(G.PY_DOC, "#", info, "edges, root, vals", "")
        doc_cpp = G.fill_doc(G.CPP_DOC, "//", info, "edges, root, vals", "")
        marks["@CTOR@"] = "edges, root, vals"
        py_values = G.PY_VALS + "        val = list(vals)\n"
        cpp_values = ("        if ((int)vals.size() != hi + 1)\n"
                      '            throw invalid_argument("Tree: vals[node] is node\'s value, so nodes " + nodes + " need vals.size() = " +\n'
                      "                                   to_string(hi + 1) + \", got \" + to_string(vals.size()));\n"
                      "        val.assign(vals.begin(), vals.end());\n")
        cpp_ctor = "const vector<vector<E>>& edges, int root, const vector<T>& vals"
        val_note = "the node values"
    doc_py = doc_py[:doc_py.index("# How it works")] + G.wrap("#", how)
    doc_cpp = doc_cpp[:doc_cpp.index("// How it works")] + G.wrap("//", how)

    if even:
        py_values += ("        keys = {}  # a random key per distinct value\n\n"
                      "        def key(x):\n"
                      "            k = keys.get(x)\n"
                      "            if k is None:\n"
                      "                k = keys[x] = random.getrandbits(62) + 1\n"
                      "            return k\n\n")
        cpp_values += "        seed = mt19937_64(chrono::steady_clock::now().time_since_epoch().count())();\n"
    marks["@X_OF_V@"], marks["@STORE_KEYS@"] = ("key(val[v])", "        self.keys = keys\n") if even else ("val[v]", "")
    marks["@LAYOUT@"], marks["@VALUES@"] = shape.py_layout_body(), py_values
    imports = "from bisect import bisect_left\n" + ("import random\n" if even else "")
    py = (header("#", "py") + "\n" + imports + "\n\n" + doc_py + fill(PY, "#", 8) + "\n" + "\n".join(py_ops) + "\n" + shape.py_shape_methods())
    marks["@LAYOUT@"], marks["@VALUES@"], marks["@CTOR@"] = shape.cpp_layout_body(), cpp_values, cpp_ctor
    marks["@MEMBERS@"], marks["@VAL_NOTE@"] = shape.cpp_members().rstrip("\n"), val_note
    marks["@X_OF_V@"] = "keyOf(val[v])" if even else "val[v]"
    marks["@S_DECL@"] = ("using S = unsigned long long;  // what the trees hold: the values' 64-bit keys" if even else
                         "using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;  // what sums are kept in")
    marks["@KEY_MEMBERS@"] = "    unsigned long long seed;  // this run's random seed: a value's key is a mix of value + seed\n" if even else ""
    cpp = (header("//", "cpp") + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n" + shape.FAST_NOTE
           + shape.PRELUDE + doc_cpp + fill(CPP, "//", 4) + "\n" + "\n".join(cpp_ops) + "\n" + shape.cpp_shape_methods().rstrip("\n") + "\n};\n")
    return folder, py, cpp


def sources():
    out = {}
    for mode in ("sum", "xor", "even"):
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
            print(f"FAIL  tree-queries/{rel}: differs from what gen_tree_fenwick.py writes (rerun it)")
        print(f"{len(stale)} stale single-log path files" if stale else "single-log path templates are fresh")
        sys.exit(1 if stale else 0)
    print(f"{len(sources())} single-log path files, {len(stale)} written")


if __name__ == "__main__":
    main()
