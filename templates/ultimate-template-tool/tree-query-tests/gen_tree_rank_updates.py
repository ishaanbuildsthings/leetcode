"""Writes the by-rank path templates that take updates: tree-queries/path-rank-updates-{node,edge}, each
template.{py,cpp}.

gen_tree_rank.py's templates answer by rank on a path from a persistent tree with a version per node, and their values
are fixed. Here one value can change. The versions still hold the starting values; the changes go into a Fenwick tree
over the positions whose nodes are trees over the value range too (from the same pool of tree nodes): changing the
value at v from old to new counts old one time less and new one time more from pos[v] on, and the opposite from just
past v's subtree on, so the Fenwick trees through pos[u] correct the path root..u for every u under v. A path is then

    nodes:  root..a + root..b - root..lca - root..parent(lca)
    edges:  root..a + root..b - 2 * root..lca

each root path being one version and O(log n) Fenwick trees, and all of them walk down the value range together:
O(log n * log U) a query. The values are not known up front, so the value range [valLo, valHi] is a constructor
argument (as in the range templates), and U is its size.

Memory is the price: an update makes up to 4 * log n * log U new tree nodes (measured: about 500 at n = 2 * 10^5 and
U = 10^9, 10 KB in C++), and none is ever freed.

    python3 gen_tree_rank_updates.py           # write
    python3 gen_tree_rank_updates.py --check   # exit 1 if a file on disk differs from what this would write

The public path ops (names, comments, how each is built from the three walks) are gen_tree_rank.py's.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_tree as G  # noqa: E402
import gen_tree_rank as R  # noqa: E402
import gen_tree_shape as shape  # noqa: E402
from gen_tree_bitset import note  # noqa: E402

DIR = G.DIR
KIND = "persistent-paths"
COST = "log(N)*log(U)"

PY = '''\
class Tree:
@CTOR_NOTE@
    def __init__(self, @CTOR@, valLo, valHi):
@LAYOUT@@VALUES@
@POOL_NOTE@
        span = valHi - valLo + 1
        depth = max(1, (span - 1).bit_length())
        room = n * (depth + 1) + 1
        lc, rc, cnt, tot = [0] * room, [0] * room, [0] * room, [0] * room
        ver = [0] * (hi + 1)
        used = 1
        for v in @NODES@:
            prev = @PREV@
            x = val[v]
            if not valLo <= x <= valHi:
                raise ValueError(f"Tree: every value must lie in [valLo, valHi] = [{valLo}, {valHi}], got {x}")
            i = x - valLo
            cur = ver[v] = used
            a, b = 0, span - 1
            while True:
                cnt[cur] = cnt[prev] + 1
                tot[cur] = tot[prev] + x
                used += 1
                if a == b:
                    break
                mid = (a + b) >> 1
                if i <= mid:
                    rc[cur] = rc[prev]
                    lc[cur] = used
                    prev = lc[prev]
                    b = mid
                else:
                    lc[cur] = lc[prev]
                    rc[cur] = used
                    prev = rc[prev]
                    a = mid + 1
                cur = used
        del lc[used:], rc[used:], cnt[used:], tot[used:]  # (an update appends the nodes it needs)
        self.lc, self.rc, self.cnt, self.tot, self.ver, self.val = lc, rc, cnt, tot, ver, val
        self.top = [0] * (n + 1)  # the Fenwick tree over the positions: top[i] is its i-th tree of changes (0: empty)
        self.valLo, self.valHi, self.span = valLo, valHi, span

    # a new, empty tree node at the end of the pool
    def _node(self):
        self.lc.append(0)
        self.rc.append(0)
        self.cnt.append(0)
        self.tot.append(0)
        return len(self.cnt) - 1

    # from position p on, the Fenwick trees count x d more times (d is 1 or -1); nothing when p is past the last
    # position
    def _change(self, p, x, d):
        lc, rc, cnt, tot, top = self.lc, self.rc, self.cnt, self.tot, self.top
        place, last, n = x - self.valLo, self.span - 1, self.n
        i = p + 1
        while i <= n:
            if not top[i]:
                top[i] = self._node()
            cur = top[i]
            a, b = 0, last
            while True:
                cnt[cur] += d
                tot[cur] += d * x
                if a == b:
                    break
                mid = (a + b) >> 1
                if place <= mid:
                    if not lc[cur]:
                        lc[cur] = self._node()
                    cur = lc[cur]
                    b = mid
                else:
                    if not rc[cur]:
                        rc[cur] = self._node()
                    cur = rc[cur]
                    a = mid + 1
            i += i & -i

    # the value kept at node v becomes x: every path root..u with u in v's subtree loses the old value and gains x
    def _set(self, v, x):
        old = self.val[v]
        if x == old:
            return
        if not self.valLo <= x <= self.valHi:
            raise ValueError(f"Tree: every value must lie in [valLo, valHi] = [{self.valLo}, {self.valHi}], got {x}")
        p = self.pos[v]
        q = p + self.sz[v]
        self._change(p, old, -1)
        self._change(p, x, 1)
        self._change(q, old, 1)
        self._change(q, x, -1)
        self.val[v] = x

    # how many values of the range [valLo, valHi] are < x (after: <= x): the rank x would take
    def _rankOf(self, x, after):
        if x < self.valLo:
            return 0
        if x > self.valHi:
            return self.span
        return x - self.valLo + (1 if after else 0)

    # adds to `trees` the ones that together hold the path root..v: v's version and the Fenwick trees through pos[v]
    def _gather(self, v, trees):
        top = self.top
        trees.append(self.ver[v])
        i = self.pos[v] + 1
        while i > 0:
            if top[i]:
                trees.append(top[i])
            i -= i & -i

@ROOTS_NOTE@
    def _roots(self, a, b):
        c = self._lca(a, b)
        plus, minus = [], []
        self._gather(a, plus)
        self._gather(b, plus)
        self._gather(c, minus)
@ABOVE@
        return plus, minus

    # how many values a path has, and their sum
    def _countOf(self, rs):
        cnt = self.cnt
        return sum(cnt[t] for t in rs[0]) - sum(cnt[t] for t in rs[1])

    def _sumOf(self, rs):
        tot = self.tot
        return sum(tot[t] for t in rs[0]) - sum(tot[t] for t in rs[1])

    # the kth smallest value of a path (1 <= k <= its size): its trees walk down the value range together
    def _kthValue(self, rs, k):
        lc, rc, cnt = self.lc, self.rc, self.cnt
        plus, minus = rs
        lo, hi = 0, self.span - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            left = sum(cnt[lc[t]] for t in plus) - sum(cnt[lc[t]] for t in minus)
            if k <= left:
                plus, minus = [lc[t] for t in plus], [lc[t] for t in minus]
                hi = mid
            else:
                k -= left
                plus, minus = [rc[t] for t in plus], [rc[t] for t in minus]
                lo = mid + 1
        return self.valLo + lo

    # (how many, their sum) of a path's values that are among the r smallest values of the range [valLo, valHi]
    def _valuesBelow(self, rs, r):
        lc, rc, cnt, tot = self.lc, self.rc, self.cnt, self.tot
        plus, minus = rs
        lo, hi = 0, self.span - 1
        if r <= 0:
            return 0, 0
        if r > hi:
            return self._countOf(rs), self._sumOf(rs)
        many = total = 0
        while lo < hi:
            mid = (lo + hi) >> 1
            if r > mid:  # the whole left half is wanted
                many += sum(cnt[lc[t]] for t in plus) - sum(cnt[lc[t]] for t in minus)
                total += sum(tot[lc[t]] for t in plus) - sum(tot[lc[t]] for t in minus)
                plus, minus = [rc[t] for t in plus], [rc[t] for t in minus]
                lo = mid + 1
            else:
                plus, minus = [lc[t] for t in plus], [lc[t] for t in minus]
                hi = mid
        return many, total

    # the sum of a path's k smallest values (0 <= k <= its size)
    def _smallestSum(self, rs, k):
        if k <= 0:
            return 0
        lc, rc, cnt, tot = self.lc, self.rc, self.cnt, self.tot
        plus, minus = rs
        total = 0
        lo, hi = 0, self.span - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            left = sum(cnt[lc[t]] for t in plus) - sum(cnt[lc[t]] for t in minus)
            if k <= left:
                plus, minus = [lc[t] for t in plus], [lc[t] for t in minus]
                hi = mid
            else:
                k -= left
                total += sum(tot[lc[t]] for t in plus) - sum(tot[lc[t]] for t in minus)
                plus, minus = [rc[t] for t in plus], [rc[t] for t in minus]
                lo = mid + 1
        return total + k * (self.valLo + lo)
'''

CPP = '''\
template <typename T>
struct Tree {
@MEMBERS@
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;  // what sums are kept in
    long long valLo, valHi, span;  // every value lies in [valLo, valHi]; span: how many values that is
@POOL_NOTE@
    HotVector<int> lc, rc, cnt;
    HotVector<S> tot;
    HotVector<int> ver;  // ver[v]: the root of v's version
    HotVector<int> top;  // the Fenwick tree over the positions: top[i] is its i-th tree of changes (0: empty)
    HotVector<T> val;  // @VAL_NOTE@
    // the trees whose counts add up to a path: r[0 .. plus) count for it, r[plus .. total) count against it
    struct Roots {
        int r[136];
        int plus, total;
    };

@CTOR_NOTE@
@CTOR@ {
@LAYOUT@
@VALUES@        int depth = 1;
        while ((1LL << depth) < span) depth++;
        size_t room = (size_t)n * (depth + 1) + 1;
        lc.assign(room, 0), rc.assign(room, 0), cnt.assign(room, 0), tot.assign(room, 0);
        ver.assign(hi + 1, 0);
        int used = 1;
        for (int k = @FIRST@; k < n; k++) {
            int v = bfs[k], prev = @PREV@;
            T x = val[v];
            if (x < valLo || x > valHi) throw invalid_argument("Tree: every value must lie in [valLo, valHi]");
            long long i = (long long)x - valLo, a = 0, b = span - 1;
            int cur = ver[v] = used;
            while (true) {
                cnt[cur] = cnt[prev] + 1, tot[cur] = tot[prev] + x;
                used++;
                if (a == b) break;
                long long mid = (a + b) >> 1;
                if (i <= mid) rc[cur] = rc[prev], lc[cur] = used, prev = lc[prev], b = mid;
                else lc[cur] = lc[prev], rc[cur] = used, prev = rc[prev], a = mid + 1;
                cur = used;
            }
        }
        lc.resize(used), rc.resize(used), cnt.resize(used), tot.resize(used);  // (an update appends the nodes it needs)
        top.assign(n + 1, 0);
    }

    // a new, empty tree node at the end of the pool
    int newNode() {
        lc.push_back(0), rc.push_back(0), cnt.push_back(0), tot.push_back(0);
        return (int)cnt.size() - 1;
    }

    // from position p on, the Fenwick trees count x d more times (d is 1 or -1); nothing when p is past the last
    // position
    void change(int p, T x, int d) {
        long long place = (long long)x - valLo;
        for (int i = p + 1; i <= n; i += i & -i) {
            if (!top[i]) top[i] = newNode();
            int cur = top[i];
            long long a = 0, b = span - 1;
            while (true) {
                cnt[cur] += d, tot[cur] += (S)d * x;
                if (a == b) break;
                long long mid = (a + b) >> 1;
                int next = place <= mid ? lc[cur] : rc[cur];
                if (!next) {
                    next = newNode();  // (the pool may have moved: lc / rc are read again below)
                    (place <= mid ? lc[cur] : rc[cur]) = next;
                }
                cur = next;
                if (place <= mid) b = mid;
                else a = mid + 1;
            }
        }
    }

    // the value kept at node v becomes x: every path root..u with u in v's subtree loses the old value and gains x
    void setValue(int v, T x) {
        T old = val[v];
        if (x == old) return;
        if (x < valLo || x > valHi) throw invalid_argument("Tree: every value must lie in [valLo, valHi]");
        int p = pos[v], q = p + sz[v];
        change(p, old, -1), change(p, x, 1);
        change(q, old, 1), change(q, x, -1);
        val[v] = x;
    }

    // how many values of the range [valLo, valHi] are < x (after: <= x): the rank x would take
    LEETCODE_NO_SANITIZE long long rankOf(T x, bool after) const {
        if (x < valLo) return 0;
        if (x > valHi) return span;
        return (long long)x - valLo + (after ? 1 : 0);
    }

    // adds to rs the trees that together hold the path root..v: v's version and the Fenwick trees through pos[v]
    LEETCODE_NO_SANITIZE void gather(int v, Roots& rs) const {
        rs.r[rs.total++] = ver[v];
        for (int i = pos[v] + 1; i > 0; i -= i & -i)
            if (top[i]) rs.r[rs.total++] = top[i];
    }

    // the trees whose counts add up to @PATH@
    LEETCODE_NO_SANITIZE Roots roots(int a, int b) const {
        Roots rs;
        rs.total = 0;
        int c = lcaOf(a, b);
        gather(a, rs), gather(b, rs);
        rs.plus = rs.total;
        gather(c, rs);
@ABOVE@
        return rs;
    }

    // how many values a path has, and their sum
    LEETCODE_NO_SANITIZE int countOf(const Roots& rs) const {
        int res = 0;
        for (int i = 0; i < rs.plus; i++) res += cnt[rs.r[i]];
        for (int i = rs.plus; i < rs.total; i++) res -= cnt[rs.r[i]];
        return res;
    }
    LEETCODE_NO_SANITIZE S sumOf(const Roots& rs) const {
        S res = 0;
        for (int i = 0; i < rs.plus; i++) res += tot[rs.r[i]];
        for (int i = rs.plus; i < rs.total; i++) res -= tot[rs.r[i]];
        return res;
    }

    // the same two for the lower half of the value range the trees are at
    LEETCODE_NO_SANITIZE int leftCount(const Roots& rs) const {
        int res = 0;
        for (int i = 0; i < rs.plus; i++) res += cnt[lc[rs.r[i]]];
        for (int i = rs.plus; i < rs.total; i++) res -= cnt[lc[rs.r[i]]];
        return res;
    }
    LEETCODE_NO_SANITIZE S leftSum(const Roots& rs) const {
        S res = 0;
        for (int i = 0; i < rs.plus; i++) res += tot[lc[rs.r[i]]];
        for (int i = rs.plus; i < rs.total; i++) res -= tot[lc[rs.r[i]]];
        return res;
    }

    // every tree steps into the lower (the upper) half of its value range
    LEETCODE_NO_SANITIZE void goLeft(Roots& rs) const {
        for (int i = 0; i < rs.total; i++) rs.r[i] = lc[rs.r[i]];
    }
    LEETCODE_NO_SANITIZE void goRight(Roots& rs) const {
        for (int i = 0; i < rs.total; i++) rs.r[i] = rc[rs.r[i]];
    }

    // the kth smallest value of a path (1 <= k <= its size): its trees walk down the value range together
    LEETCODE_NO_SANITIZE T kthValue(Roots rs, int k) const {
        long long lo = 0, hi = span - 1;
        while (lo < hi) {
            long long mid = (lo + hi) >> 1;
            int left = leftCount(rs);
            if (k <= left) {
                goLeft(rs);
                hi = mid;
            } else {
                k -= left;
                goRight(rs);
                lo = mid + 1;
            }
        }
        return (T)(valLo + lo);
    }

    // how many of a path's values are among the r smallest values of the range [valLo, valHi]; total: their sum
    LEETCODE_NO_SANITIZE int valuesBelow(Roots rs, long long r, S& total) const {
        long long lo = 0, hi = span - 1;
        int many = 0;
        total = 0;
        if (r <= 0) return 0;
        if (r > hi) {
            total = sumOf(rs);
            return countOf(rs);
        }
        while (lo < hi) {
            long long mid = (lo + hi) >> 1;
            if (r > mid) {  // the whole lower half is wanted
                many += leftCount(rs);
                total += leftSum(rs);
                goRight(rs);
                lo = mid + 1;
            } else {
                goLeft(rs);
                hi = mid;
            }
        }
        return many;
    }

    // the sum of a path's k smallest values (0 <= k <= its size)
    LEETCODE_NO_SANITIZE S smallestSum(Roots rs, int k) const {
        if (k <= 0) return 0;
        S total = 0;
        long long lo = 0, hi = span - 1;
        while (lo < hi) {
            long long mid = (lo + hi) >> 1;
            int left = leftCount(rs);
            if (k <= left) {
                goLeft(rs);
                hi = mid;
            } else {
                k -= left;
                total += leftSum(rs);
                goRight(rs);
                lo = mid + 1;
            }
        }
        return total + (S)k * (S)(valLo + lo);
    }
'''


def fill_py(body):
    """A path op's Python body from gen_tree_rank.py, for a list of trees instead of its three or four versions."""
    t = body.replace("@R@", "rs").replace("@cnt()@", "self._countOf(rs)").replace("@tot()@", "self._sumOf(rs)")
    return re.sub(r"bisect_(left|right)\(self\.srt, (\w+)\)",
                  lambda m: f"self._rankOf({m.group(2)}, {m.group(1) == 'right'})", t)


def fill_cpp(body):
    return body.replace("@R@", "rs").replace("@cnt()@", "countOf(rs)").replace("@tot()@", "sumOf(rs)")


def path_methods(w):
    """(the Python methods, the C++ methods, {op: cost}) of the path queries: gen_tree_rank.py's, over a list of trees."""
    py, cpp, costs = [], [], {}
    for name, args, types, ret, (doc_py, doc_cpp), body_py, body_cpp in R.ops(w):
        full = f"{w.t}Path{name}"
        costs[full] = COST
        body_py, body_cpp = fill_py(body_py), fill_cpp(body_cpp)
        doc_py = doc_py.format(none="None", raises="IndexError")
        doc_cpp = doc_cpp.format(none="nullopt", raises="throws out_of_range")
        py.append(G.comment("#", COST, doc_py) + f"    def {full}(self, {', '.join(['a', 'b'] + args)}):\n"
                  + G.py_check(full, ("a", "b")) + "        rs = self._roots(a, b)\n"
                  + ("        size = self._countOf(rs)\n" if "size" in body_py else "") + body_py)
        decl = ", ".join(["int a", "int b"] + [f"{ty} {a}" for ty, a in zip(types, args)])
        cpp.append(G.comment("//", COST, doc_cpp) + f"    LEETCODE_NO_SANITIZE {ret} {full}({decl}) const {{\n"
                   + G.cpp_check(full, ("a", "b")) + "        Roots rs = roots(a, b);\n"
                   + ("        int size = countOf(rs);\n" if "size" in body_cpp else "") + body_cpp + "    }\n")
    return py, cpp, costs


def make(edge):
    w = R.Words(edge)
    t = w.t
    folder = f"path-rank-updates-{t}"
    val_word, x = ("weight", "w") if edge else ("val", "x")
    at = "a - b" if edge else "node"
    nodes = ("a", "b") if edge else ("node",)
    path_py, path_cpp, costs = path_methods(w)
    py_ops, cpp_ops = [], []

    def add_op(name, args, types, ret, cost, doc, py_body, cpp_body, hot=False):
        full = t + name
        costs[full] = cost
        py_ops.append(G.comment("#", cost, doc) + f"    def {full}(self, {', '.join(list(nodes) + args)}):\n" + py_body)
        decl = ", ".join([f"int {v}" for v in nodes] + [f"{ty} {a}" for ty, a in zip(types, args)])
        mark = "LEETCODE_NO_SANITIZE " if hot else ""  # (an update grows the pool: left to the sanitizers)
        cpp_ops.append(G.comment("//", cost, doc) + f"    {mark}{ret} {full}({decl}){' const' if hot else ''} {{\n" + cpp_body
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
    inside = "; the new value must lie in [valLo, valHi]"
    v = "v" if edge else "node"

    def here(name):
        if edge:
            return f'        v = self._edge("{t}{name}", a, b)\n', f'        int v = edgeAt("{t}{name}", a, b);\n'
        return G.py_check(t + name, nodes), G.cpp_check(t + name, nodes)

    p, c = here("Get")
    add_op("Get", [], [], "T", "1", f"{val_word}({at}){either}", p + f"        return self.val[{v}]\n",
           c + f"        return val[{v}];\n", hot=True)
    p, c = here("Assign")
    add_op("Assign", [x], ["T"], "void", COST, f"{val_word}({at}) = {x}{inside}{either}", p + f"        self._set({v}, {x})\n",
           c + f"        setValue({v}, {x});\n")
    p, c = here("Add")
    add_op("Add", [x], ["T"], "void", COST, f"{val_word}({at}) += {x}{inside}{either}",
           p + f"        self._set({v}, self.val[{v}] + {x})\n", c + f"        setValue({v}, val[{v}] + {x});\n")
    for name, sign in (("Chmax", ">"), ("Chmin", "<")):
        p, c = here(name)
        add_op(name, [x], ["T"], "void", COST, f"{val_word}({at}) = {name[2:].lower()}({val_word}, {x}){inside}{either}",
               p + f"        if {x} {sign} self.val[{v}]:\n            self._set({v}, {x})\n",
               c + f"        if ({x} {sign} val[{v}]) setValue({v}, {x});\n")

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
            "  build: N*log(U)",
            "@memory:",
            "  layout: none",
            "  node: lc[1*N*log(U)] rc[1*N*log(U)] cnt[1*N*log(U)] tot[1*N*log(U)]",
            "  tags: none",
            f"  other: top[1*N] ver[1*N] val[1*N] {G.LAYOUT_ARRAYS}",
            "  note: U = valHi - valLo + 1. On top of the sizes above, every update adds up to 4*log(N)*log(U) nodes to lc / rc "
            "/ cnt / tot, and none is ever freed. Measured in C++ at N = 2*10^5, U = 10^9: 124 MB to start, then about 500 "
            "nodes (10 KB) an update, so 10^4 updates add 100 MB",
        ]
        return "".join(f"{cm} {line}\n" for line in lines)

    held = "edges on its path from the root, each as its weight" if edge else "values on its path from the root"
    formula = "root..a + root..b - 2 * root..lca" if edge else "root..a + root..b - root..lca - root..parent(lca)"
    how = ("How it works: every node keeps a version of a persistent segment tree over the value range [valLo, valHi], holding "
           f"the starting {held}. A version copies its parent's and adds one value. Changes go into a Fenwick tree over the "
           "heavy-light positions, each of its nodes a tree over the value range too: changing the value at v from old to new "
           "counts old one time less and new one time more from pos[v] on, and the opposite from just past v's subtree on. So "
           "the path root..u is u's version plus the O(log n) Fenwick trees through pos[u], a path a..b is "
           f"{formula}, and all those trees walk down the value range together: O(log n * log U) a query, with U = valHi - "
           "valLo + 1.")
    memory = ("Memory is the price. The versions take about n * log U tree nodes, and every update adds up to 4 * log n * "
              "log U more, none of them ever freed. Measured in C++ with n = 2 * 10^5 and U = 10^9: 124 MB to start, then "
              "about 500 nodes (10 KB) an update, so 10^4 updates add 100 MB and 10^5 would add a gigabyte. A tighter [valLo, "
              "valHi] makes both smaller. With no updates at all, the path-rank templates (fixed values) are lighter and a log "
              "faster.")
    info = type("R", (), {"extra_names": ["valLo", "valHi"], "cls": ""})
    pool = ("lc, rc, cnt, tot: one pool of tree nodes over the value range (a value's place in it is value - valLo): a node's "
            "two children, how many values it holds and their sum; node 0 is the empty tree. ver[v] is the root of v's version: "
            f"its parent's, plus {'the weight of the edge above it' if edge else 'its own value'} (the versions share everything "
            "else).")
    if edge:
        doc_py = G.fill_doc(G.PY_DOC_EDGE, "#", info, "edges, root, valLo, valHi", ", valLo, valHi", "edge")
        doc_cpp = G.fill_doc(G.CPP_DOC_EDGE, "//", info, "edges, root, valLo, valHi", ", valLo, valHi", "edge")
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
        py_nodes, py_prev, first, cpp_prev = "bfs[1:]", "ver[par[v]]", "1", "ver[par[v]]"
        py_above = "        self._gather(c, minus)  # (twice: both root paths hold the edges above the lca)"
        cpp_above = "        gather(c, rs);  // (twice: both root paths hold the edges above the lca)"
        path_words = "the edges of the path a..b"
        val_note = "val[v]: the weight of the edge above v (the root has none)"
    else:
        doc_py = G.fill_doc(G.PY_DOC, "#", info, "edges, root, vals, valLo, valHi", ", valLo, valHi")
        doc_cpp = G.fill_doc(G.CPP_DOC, "//", info, "edges, root, vals, valLo, valHi", ", valLo, valHi")
        py_ctor, cpp_ctor = "edges, root, vals", "const vector<vector<E>>& edges, int root, const vector<T>& vals"
        py_values = G.PY_VALS + "        val = list(vals)\n"
        cpp_values = ("        if ((int)vals.size() != hi + 1)\n"
                      '            throw invalid_argument("Tree: vals[node] is node\'s value, so nodes " + nodes + " need vals.size() = " +\n'
                      "                                   to_string(hi + 1) + \", got \" + to_string(vals.size()));\n"
                      "        val.assign(vals.begin(), vals.end());\n")
        py_nodes, py_prev, first, cpp_prev = "bfs", "ver[par[v]] if v != root else 0", "0", "v == root ? 0 : ver[par[v]]"
        py_above = "        if c != self.root:\n            self._gather(self.par[c], minus)"
        cpp_above = "        if (c != root) gather(par[c], rs);"
        path_words = "the path a..b"
        val_note = "the node values"
    bad = "an edge has no weight" if edge else "vals has the wrong length"
    py_marks = {
        "@CTOR_NOTE@": note("#", "O(n log U) -- builds the layout and a version per node; raises ValueError when the edges are "
                            f"not one tree on nodes 0..n-1 or 1..n, {bad}, or a value is outside [valLo, valHi]", 4),
        "@POOL_NOTE@": note("#", pool, 8), "@CTOR@": py_ctor, "@LAYOUT@": shape.py_layout_body(), "@VALUES@": py_values,
        "@NODES@": py_nodes, "@PREV@": py_prev, "@ABOVE@": py_above,
        "@ROOTS_NOTE@": note("#", f"the trees whose counts add up to {path_words}: (the ones that count for it, the ones that "
                             "count against it)", 4),
    }
    sig = f"    template <typename E = int> Tree({cpp_ctor}, long long valLo, long long valHi)"
    if len(sig) > 118:
        sig = f"    template <typename E = int> Tree({cpp_ctor},\n" + " " * 36 + "long long valLo, long long valHi)"
    sig += "\n        : root(root), valLo(valLo), valHi(valHi), span(valHi - valLo + 1)"
    cpp_marks = {
        "@CTOR_NOTE@": note("//", "O(n log U) -- builds the layout and a version per node; throws invalid_argument when the "
                            f"edges are not one tree on nodes 0..n-1 or 1..n, {bad}, or a value is outside [valLo, valHi]", 4),
        "@POOL_NOTE@": note("//", pool, 4), "@CTOR@": sig, "@LAYOUT@": shape.cpp_layout_body(), "@VALUES@": cpp_values,
        "@FIRST@": first, "@PREV@": cpp_prev, "@ABOVE@": cpp_above, "@PATH@": path_words, "@VAL_NOTE@": val_note,
        "@MEMBERS@": shape.cpp_members().rstrip("\n"),
    }

    def doc_with(doc, cm):
        cut = doc.index(f"{cm} How it works")
        return doc[:cut] + G.wrap(cm, how) + f"{cm}\n" + G.wrap(cm, memory)

    def fill(text, marks):
        for k, val in marks.items():
            text = text.replace(k, val)
        return text

    py = (header("#", "py") + "\nfrom bisect import bisect_left\n\n\n" + doc_with(doc_py, "#") + fill(PY, py_marks)
          + "\n" + "\n".join(py_ops + path_py) + "\n" + shape.py_shape_methods())
    cpp = (header("//", "cpp") + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n" + shape.FAST_NOTE
           + shape.PRELUDE + doc_with(doc_cpp, "//") + fill(CPP, cpp_marks)
           + "\n" + "\n".join(cpp_ops + path_cpp) + "\n" + shape.cpp_shape_methods().rstrip("\n") + "\n};\n")
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
            print(f"FAIL  tree-queries/{rel}: differs from what gen_tree_rank_updates.py writes (rerun it)")
        print(f"{len(stale)} stale by-rank-with-updates files" if stale else "by-rank path templates with updates are fresh")
        sys.exit(1 if stale else 0)
    print(f"{len(sources())} by-rank-with-updates files, {len(stale)} written")


if __name__ == "__main__":
    main()
