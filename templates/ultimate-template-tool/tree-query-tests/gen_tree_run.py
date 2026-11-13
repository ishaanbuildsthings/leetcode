"""Writes the longest-equal-run path templates: tree-queries/path-run-{node,edge}, each template.{py,cpp}.

"The longest run of equal adjacent values along the path a -> b" needs more from a chain piece than the range
templates' longestEqualRun gives: how the piece starts and ends (its first and last value, and how many equal values
it starts and ends with), so that a run can carry on from one piece into the next, and the piece read backwards when
the walk goes up it. So these templates keep their own segment tree over the heavy-light positions. A tree node holds
that summary for the values under it, two summaries join in O(1), and a summary read backwards is the same numbers
swapped. Assign and add over a path or a subtree are lazy (an assign makes the whole node one run; an add moves its
two end values and leaves its runs alone).

    python3 gen_tree_run.py           # write
    python3 gen_tree_run.py --check   # exit 1 if a file on disk differs from what this would write
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_tree as G  # noqa: E402
import gen_tree_shape as shape  # noqa: E402
from gen_tree_bitset import note  # noqa: E402

DIR = G.DIR
KIND = "run-seg-tree"

PY = '''\
class Tree:
@CTOR_NOTE@
    def __init__(self, @CTOR@):
@LAYOUT@@VALUES@
@RUN_NOTE@
        run = [None] * n + [(@START@[v], @START@[v], 1, 1, 1, 1) for v in order]
        join = self._join
        for i in range(n - 1, 0, -1):
            run[i] = join(run[2 * i], run[2 * i + 1])
        self.run, self.hasSet, self.setTo, self.add = run, [False] * n, [0] * n, [0] * n

    # two stretches read one after the other (None: an empty stretch)
    @staticmethod
    def _join(A, B):
        if A is None:
            return B
        if B is None:
            return A
        fa, la, pa, sa, ba, na = A
        fb, lb, pb, sb, bb, nb = B
        best = ba if ba > bb else bb
        if la != fb:
            return (fa, lb, pa, sb, best, na + nb)
        mid = sa + pb  # (the run that crosses from A into B)
        return (fa, lb, pa + pb if pa == na else pa, sb + sa if sb == nb else sb, mid if mid > best else best, na + nb)

    # the same stretch read backwards
    @staticmethod
    def _flip(A):
        return (A[1], A[0], A[3], A[2], A[4], A[5])

    # seg node i takes an update: every value under it becomes x (assign), or grows by x
    def _apply(self, i, assign, x):
        f, l, p, s, b, m = self.run[i]
        if assign:
            self.run[i] = (x, x, m, m, m, m)
            if i < self.n:
                self.hasSet[i], self.setTo[i], self.add[i] = True, x, 0
        else:
            self.run[i] = (f + x, l + x, p, s, b, m)
            if i < self.n:
                if self.hasSet[i]:
                    self.setTo[i] += x
                else:
                    self.add[i] += x

    # hands every update waiting above leaf p down to the two children, top first
    def _push(self, p):
        hasSet, setTo, add, apply = self.hasSet, self.setTo, self.add, self._apply
        for s in range(p.bit_length() - 1, 0, -1):
            i = p >> s
            if hasSet[i]:
                apply(2 * i, True, setTo[i])
                apply(2 * i + 1, True, setTo[i])
                hasSet[i] = False
            elif add[i]:
                apply(2 * i, False, add[i])
                apply(2 * i + 1, False, add[i])
                add[i] = 0

    # recomputes the seg nodes above leaf p (one with an update waiting is right as it is)
    def _pull(self, p):
        run, hasSet, add, join = self.run, self.hasSet, self.add, self._join
        p >>= 1
        while p:
            if not hasSet[p] and not add[p]:
                run[p] = join(run[2 * p], run[2 * p + 1])
            p >>= 1

    # the values at positions l..r all become x (assign), or all grow by x (nothing for an empty stretch, l > r)
    def _update(self, l, r, assign, x):
        if l > r:
            return
        apply = self._apply
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        i, j = l, r + 1
        while i < j:
            if i & 1:
                apply(i, assign, x)
                i += 1
            if j & 1:
                j -= 1
                apply(j, assign, x)
            i >>= 1
            j >>= 1
        self._pull(l)
        self._pull(r)

    # the value at position p
    def _valueAt(self, p):
        self._push(p + self.n)
        return self.run[p + self.n][0]

    # the values at positions l..r, read in position order (None for an empty stretch, l > r)
    def _runOf(self, l, r):
        if l > r:
            return None
        run, join = self.run, self._join
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        r += 1
        left = right = None
        while l < r:
            if l & 1:
                left = join(left, run[l])
                l += 1
            if r & 1:
                r -= 1
                right = join(run[r], right)
            l >>= 1
            r >>= 1
        return join(left, right)

    # the path a..b as stretches of positions (l, r), one for each chain piece, in no particular order
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

    # the @VALS@ read walking a -> b@NONE@
    def _pathRun(self, a, b):
        head, par, dep, pos = self.head, self.par, self.dep, self.pos
        join, flip, runOf = self._join, self._flip, self._runOf
        res = None
@WALK@        return res
'''

CPP = '''\
template <typename T>
struct Tree {
@MEMBERS@
@RUN_NOTE@
    struct Run {
        T first, last;
        int pre, suf, best, len;
    };
    HotVector<Run> run;  // a segment tree over the positions (its leaves n .. 2n - 1): the values under each node
    // waiting at a seg node to be handed to its two children: an assign (hasSet[i], to the value setTo[i]) or an add
    HotVector<char> hasSet;
    HotVector<T> setTo, add;

@CTOR_NOTE@
    template <typename E = int> Tree(@CTOR@) : root(root) {
@LAYOUT@
@VALUES@        run.assign(2 * n, Run{T(), T(), 1, 1, 1, 1});
        for (int i = @FIRST@; i < n; i++) run[n + i].first = run[n + i].last = @START@[order[i]];
        for (int i = n - 1; i > 0; i--) run[i] = join(run[2 * i], run[2 * i + 1]);
        hasSet.assign(n, 0), setTo.assign(n, T()), add.assign(n, T());
    }

    // two stretches read one after the other
    LEETCODE_NO_SANITIZE static Run join(const Run& a, const Run& b) {
        if (a.len == 0) return b;
        if (b.len == 0) return a;
        Run res{a.first, b.last, a.pre, b.suf, a.best > b.best ? a.best : b.best, a.len + b.len};
        if (a.last == b.first) {
            if (a.pre == a.len) res.pre = a.len + b.pre;
            if (b.suf == b.len) res.suf = b.len + a.suf;
            if (a.suf + b.pre > res.best) res.best = a.suf + b.pre;  // (the run that crosses from a into b)
        }
        return res;
    }

    // the same stretch read backwards
    LEETCODE_NO_SANITIZE static Run flipped(const Run& a) { return Run{a.last, a.first, a.suf, a.pre, a.best, a.len}; }

    // seg node i takes an update: every value under it becomes x (assign), or grows by x
    LEETCODE_NO_SANITIZE void apply(int i, bool assign, T x) {
        Run& t = run[i];
        if (assign) {
            t.first = t.last = x, t.pre = t.suf = t.best = t.len;
            if (i < n) hasSet[i] = 1, setTo[i] = x, add[i] = 0;
        } else {
            t.first += x, t.last += x;
            if (i < n) {
                if (hasSet[i]) setTo[i] += x;
                else add[i] += x;
            }
        }
    }

    // hands every update waiting above leaf p down to the two children, top first
    LEETCODE_NO_SANITIZE void push(int p) {
        for (int s = 31 - __builtin_clz(p); s > 0; s--) {
            int i = p >> s;
            if (hasSet[i]) {
                apply(2 * i, true, setTo[i]), apply(2 * i + 1, true, setTo[i]);
                hasSet[i] = 0;
            } else if (add[i] != 0) {
                apply(2 * i, false, add[i]), apply(2 * i + 1, false, add[i]);
                add[i] = 0;
            }
        }
    }

    // recomputes the seg nodes above leaf p (one with an update waiting is right as it is)
    LEETCODE_NO_SANITIZE void pullAbove(int p) {
        for (p >>= 1; p > 0; p >>= 1)
            if (!hasSet[p] && add[p] == 0) run[p] = join(run[2 * p], run[2 * p + 1]);
    }

    // the values at positions l..r all become x (assign), or all grow by x (nothing for an empty stretch, l > r)
    LEETCODE_NO_SANITIZE void update(int l, int r, bool assign, T x) {
        if (l > r) return;
        l += n, r += n;
        push(l), push(r);
        for (int i = l, j = r + 1; i < j; i >>= 1, j >>= 1) {
            if (i & 1) apply(i++, assign, x);
            if (j & 1) apply(--j, assign, x);
        }
        pullAbove(l), pullAbove(r);
    }

    // the value at position p
    LEETCODE_NO_SANITIZE T valueAt(int p) {
        push(p + n);
        return run[p + n].first;
    }

    // the values at positions l..r, read in position order (len 0 for an empty stretch, l > r)
    LEETCODE_NO_SANITIZE Run runOf(int l, int r) {
        Run left{T(), T(), 0, 0, 0, 0}, right = left;
        if (l > r) return left;
        l += n, r += n;
        push(l), push(r);
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) left = join(left, run[l++]);
            if (r & 1) right = join(run[--r], right);
        }
        return join(left, right);
    }

    // the path a..b as stretches of positions ls[i]..rs[i], one for each chain piece, in no particular order; returns
    // how many there are
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

    // the @VALS@ read walking a -> b@NONE@
    LEETCODE_NO_SANITIZE Run pathRun(int a, int b) {
        Run res{T(), T(), 0, 0, 0, 0};
@WALK@        return res;
    }
'''


def make(edge):
    t = "edge" if edge else "node"
    folder = f"path-run-{t}"
    vals, val_word, x = ("edge weights", "weight", "w") if edge else ("node values", "val", "x")
    at = "a - b" if edge else "node"
    nodes = ("a", "b") if edge else ("node",)
    costs, py_ops, cpp_ops = {}, [], []

    def add_op(name, args, types, ret, cost, doc, py_body, cpp_body, where=nodes):
        full = t + name
        costs[full] = cost
        py_ops.append(G.comment("#", cost, doc) + f"    def {full}(self, {', '.join(list(where) + args)}):\n" + py_body)
        decl = ", ".join([f"int {v}" for v in where] + [f"{ty} {a}" for ty, a in zip(types, args)])
        cpp_ops.append(G.comment("//", cost, doc) + f"    LEETCODE_NO_SANITIZE {ret} {full}({decl}) {{\n" + cpp_body + "    }\n")

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

    one, path_cost, sub_cost = "log(N)", "log^2(N)", "log(N)"
    p, c = here("Get")
    add_op("Get", [], [], "T", one, f"{val_word}({at}){either}", p + "        return self._valueAt(p)\n",
           c + "        return valueAt(p);\n")
    for name, sign, flag in (("Assign", "=", "True"), ("Add", "+=", "False")):
        p, c = here(name)
        add_op(name, [x], ["T"], "void", one, f"{val_word}({at}) {sign} {x}{either}", p + f"        self._update(p, p, {flag}, {x})\n",
               c + f"        update(p, p, {flag.lower()}, {x});\n")
    for name, sign in (("Chmax", ">"), ("Chmin", "<")):
        p, c = here(name)
        add_op(name, [x], ["T"], "void", one, f"{val_word}({at}) = {name[2:].lower()}({val_word}, {x}){either}",
               p + f"        if {x} {sign} self._valueAt(p):\n            self._update(p, p, True, {x})\n",
               c + f"        if ({x} {sign} valueAt(p)) update(p, p, true, {x});\n")

    # ---- a path
    for name, sign, flag in (("Assign", "=", "True"), ("Add", "+=", "False")):
        add_op("Path" + name, [x], ["T"], "void", path_cost, f"{val_word} {sign} {x} for every {t} on the path a..b",
               G.py_check(f"{t}Path{name}", ("a", "b"))
               + f"        for l, r in self._pieces(a, b):\n            self._update(l, r, {flag}, {x})\n",
               G.cpp_check(f"{t}Path{name}", ("a", "b")) + "        int ls[64], rs[64], m = pieces(a, b, ls, rs);\n"
               f"        for (int i = 0; i < m; i++) update(ls[i], rs[i], {flag.lower()}, {x});\n", where=("a", "b"))
    none = "; 0 when a == b (no edges)" if edge else ""
    add_op("PathLongestEqualRun", [], [], "int", path_cost,
           f"length of the longest run of equal adjacent {vals} along the path a..b{none}",
           G.py_check(f"{t}PathLongestEqualRun", ("a", "b"))
           + ("        res = self._pathRun(a, b)\n        return res[4] if res else 0\n" if edge else
              "        return self._pathRun(a, b)[4]\n"),
           G.cpp_check(f"{t}PathLongestEqualRun", ("a", "b")) + "        return pathRun(a, b).best;\n", where=("a", "b"))

    # ---- a subtree: one stretch of positions (an edge template leaves out the edge above node)
    skip = " + 1" if edge else ""
    why = "        # the edges below node: the positions after its own (none for a leaf: an empty stretch)\n" if edge else ""
    for name, sign, flag in (("Assign", "=", "True"), ("Add", "+=", "False")):
        add_op("Subtree" + name, [x], ["T"], "void", sub_cost, f"{val_word} {sign} {x} for every {t} in node's subtree",
               G.py_check(f"{t}Subtree{name}", ("node",)) + "        l = self.pos[node]\n" + why
               + f"        self._update(l{skip}, l + self.sz[node] - 1, {flag}, {x})\n",
               G.cpp_check(f"{t}Subtree{name}", ("node",)) + why.replace("#", "//")
               + f"        update(pos[node]{skip}, pos[node] + sz[node] - 1, {flag.lower()}, {x});\n", where=("node",))

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
            "  node: run[12*N]",
            "  tags: hasSet[1*N] setTo[1*N] add[1*N]",
            f"  other: {G.LAYOUT_ARRAYS}",
            "  note: run holds six numbers for each of the 2N tree nodes (first and last value, the runs at its two ends, its "
            "longest run, its size)",
        ]
        return "".join(f"{cm} {line}\n" for line in lines)

    how = ("How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one "
           "stretch of positions (pos[node] .. pos[node] + sz[node] - 1). A segment tree over the positions keeps, for the "
           f"{'weights' if edge else 'values'} under each of its nodes: the first and the last one, how many equal ones it "
           "starts and ends with, its longest run and its size. Two such summaries join in O(1) (a run can carry on from "
           "one into the next), and a stretch read backwards is the same numbers swapped. A path a -> b is O(log n) chain "
           "pieces: the ones on a's side are read backwards (the walk goes up them), the ones on b's side forwards. An "
           "assign turns a whole tree node into one run and an add moves its two end values, so both wait at the O(log n) "
           "tree nodes that cover a stretch until something below one of them is needed.")
    info = type("R", (), {"extra_names": [], "cls": ""})
    run_words = ("first / last value, how many equal values it starts / ends with, its longest run of equal adjacent "
                 "values, how many values it has")
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
    bad = "an edge has no weight" if edge else "vals has the wrong length"
    marks = {"@VALS@": vals, "@FIRST@": "1" if edge else "0", "@START@": "above" if edge else "vals"}
    py_marks = {
        "@CTOR_NOTE@": note("#", "O(n) -- builds the layout and the run tree; raises ValueError when the edges are not one tree "
                            f"on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@RUN_NOTE@": note("#", "run: a segment tree over the positions (its leaves n .. 2n - 1). run[i] sums up the values "
                           f"under seg node i, read in position order, as a tuple: {run_words}. Waiting at seg node i to be "
                           "handed to its two children: an assign (hasSet[i], to the value setTo[i]) or an add (add[i]).", 8),
        "@CTOR@": py_ctor, "@LAYOUT@": shape.py_layout_body(), "@VALUES@": py_values, "@LCA_PIECE@": py_lca,
        "@NONE@": " (None when a == b: no edges)" if edge else "",
        "@WALK@": G.walk(G.PY_WALK, "res = join(res, flip(runOf(l, r)))", "res = join(res, runOf(l, r))", edge),
    }
    cpp_marks = {
        "@CTOR_NOTE@": note("//", "O(n) -- builds the layout and the run tree; throws invalid_argument when the edges are not "
                            f"one tree on nodes 0..n-1 or 1..n, or {bad}", 4),
        "@RUN_NOTE@": note("//", f"what a stretch of values looks like from outside: its {run_words} (0: an empty stretch)", 4),
        "@CTOR@": cpp_ctor, "@LAYOUT@": shape.cpp_layout_body(), "@VALUES@": cpp_values, "@LCA_PIECE@": cpp_lca,
        "@NONE@": " (len 0 when a == b: no edges)" if edge else "",
        "@WALK@": G.walk(G.CPP_WALK, "res = join(res, flipped(runOf(l, r)));", "res = join(res, runOf(l, r));", edge),
        "@MEMBERS@": shape.cpp_members().rstrip("\n"),
    }

    def doc_with(doc, cm):
        cut = doc.index(f"{cm} How it works")
        return doc[:cut] + G.wrap(cm, how)

    def fill(text, extra):
        for k, v in {**marks, **extra}.items():
            text = text.replace(k, v)
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
            print(f"FAIL  tree-queries/{rel}: differs from what gen_tree_run.py writes (rerun it)")
        print(f"{len(stale)} stale longest-run path files" if stale else "longest-run path templates are fresh")
        sys.exit(1 if stale else 0)
    print(f"{len(sources())} longest-run path files, {len(stale)} written")


if __name__ == "__main__":
    main()
