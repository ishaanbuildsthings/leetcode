"""Writes the by-rank path templates: tree-queries/path-rank-node and path-rank-edge, each template.{py,cpp}.

What a range structure cannot give a path piece by piece: the kth smallest value on a path, the sum of its k smallest,
its values' distance to their median. Here every node keeps a version of a persistent segment tree over the values
(by rank), holding the values on its path from the root; a path a..b is then

    nodes:  ver[a] + ver[b] - ver[lca] - ver[parent(lca)]
    edges:  ver[a] + ver[b] - 2 * ver[lca]        (a node's version holds the edges above it)

and the versions walk down together, O(log n) per query. The values are fixed (no updates). Counts and sums by value
and nearest-to-x come out of the same walk in one log, where the wrapped templates (gen_tree.py) take log^2.

    python3 gen_tree_rank.py           # write
    python3 gen_tree_rank.py --check   # exit 1 if a file on disk differs from what this would write

The layout, the shape ops and the comment style are gen_tree_shape.py's and gen_tree.py's.
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
KIND = "persistent-paths"
VERSION_ARRAYS = "lc[1*N*log(N)] rc[1*N*log(N)] cnt[1*N*log(N)] tot[1*N*log(N)]"
OTHER_ARRAYS = f"ver[1*N] srt[1*N] val[1*N] {G.LAYOUT_ARRAYS}"


class Words:
    """What differs between the node template and the edge one."""

    def __init__(self, edge):
        self.edge = edge
        self.t = "edge" if edge else "node"
        self.vals = "edge weights" if edge else "node values"
        self.one = "edge" if edge else "node"
        self.val = "weight" if edge else "val"
        self.roots = "A, B, X" if edge else "A, B, X, Y"
        self.croots = "int A, int B, int X" if edge else "int A, int B, int X, int Y"

    def over(self, arr, child=""):
        """arr summed over the path's versions (at their `child` children when given): the path's own total."""
        at = (lambda v: f"{arr}[{child}[{v}]]") if child else (lambda v: f"{arr}[{v}]")
        if self.edge:
            return f"{at('A')} + {at('B')} - 2 * {at('X')}"
        return f"{at('A')} + {at('B')} - {at('X')} - {at('Y')}"

    def go(self, child, cpp):
        names = self.roots.split(", ")
        if cpp:
            return ", ".join(f"{v} = {child}[{v}]" for v in names) + ";"
        return f"{self.roots} = {', '.join(f'{child}[{v}]' for v in names)}"

    def fill(self, text, cpp):
        """Puts in the @...@ pieces: the versions of a path, their totals, a step down."""
        t = text.replace("@R@", self.roots).replace("@CR@", self.croots)
        for arr in ("cnt", "tot"):
            for child in ("lc", "rc", ""):
                t = t.replace(f"@{arr}({child})@", self.over(arr, child))
        for child in ("lc", "rc"):
            t = t.replace(f"@go({child})@", self.go(child, cpp))
        return (t.replace("@T@", self.t).replace("@VALS@", self.vals).replace("@ONE@", self.one)
                .replace("@VAL@", self.val))


# ------------------------------------------------------------------------------------------------ Python
PY_HELPERS_NODE = '''\
    # the versions whose counts add up to the path a..b: ver[a] + ver[b] - ver[lca] - ver[parent(lca)]
    def _roots(self, a, b):
        c = self._lca(a, b)
        ver = self.ver
        return ver[a], ver[b], ver[c], (0 if c == self.root else ver[self.par[c]])
'''
PY_HELPERS_EDGE = '''\
    # the versions whose counts add up to the edges of the path a..b: ver[a] + ver[b] - 2 * ver[lca]
    def _roots(self, a, b):
        ver = self.ver
        return ver[a], ver[b], ver[self._lca(a, b)]
'''
PY_HELPERS = '''\
    # the kth smallest value of a path (1 <= k <= its size): its versions walk down together
    def _kthValue(self, @R@, k):
        lc, rc, cnt = self.lc, self.rc, self.cnt
        lo, hi = 0, len(self.srt) - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            left = @cnt(lc)@
            if k <= left:
                @go(lc)@
                hi = mid
            else:
                k -= left
                @go(rc)@
                lo = mid + 1
        return self.srt[lo]

    # (how many, their sum) of a path's values that are among the r smallest distinct values of the tree
    def _valuesBelow(self, @R@, r):
        lc, rc, cnt, tot = self.lc, self.rc, self.cnt, self.tot
        lo, hi = 0, len(self.srt) - 1
        if r <= 0:
            return 0, 0
        if r > hi:
            return @cnt()@, @tot()@
        many = total = 0
        while lo < hi:
            mid = (lo + hi) >> 1
            if r > mid:  # the whole left half is wanted
                many += @cnt(lc)@
                total += @tot(lc)@
                @go(rc)@
                lo = mid + 1
            else:
                @go(lc)@
                hi = mid
        return many, total

    # the sum of a path's k smallest values (0 <= k <= its size)
    def _smallestSum(self, @R@, k):
        if k <= 0:
            return 0
        lc, rc, cnt, tot = self.lc, self.rc, self.cnt, self.tot
        total = 0
        lo, hi = 0, len(self.srt) - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            left = @cnt(lc)@
            if k <= left:
                @go(lc)@
                hi = mid
            else:
                k -= left
                total += @tot(lc)@
                @go(rc)@
                lo = mid + 1
        return total + k * self.srt[lo]
'''

# ------------------------------------------------------------------------------------------------ C++
CPP_HELPERS_NODE = '''\
    // the versions whose counts add up to the path a..b: ver[a] + ver[b] - ver[lca] - ver[parent(lca)]
    LEETCODE_NO_SANITIZE void roots(int a, int b, int& A, int& B, int& X, int& Y) const {
        int c = lcaOf(a, b);
        A = ver[a], B = ver[b], X = ver[c], Y = c == root ? 0 : ver[par[c]];
    }
'''
CPP_HELPERS_EDGE = '''\
    // the versions whose counts add up to the edges of the path a..b: ver[a] + ver[b] - 2 * ver[lca]
    LEETCODE_NO_SANITIZE void roots(int a, int b, int& A, int& B, int& X) const {
        A = ver[a], B = ver[b], X = ver[lcaOf(a, b)];
    }
'''
CPP_HELPERS = '''\
    // how many of the tree's distinct values are < x (after: <= x): the rank x would take
    LEETCODE_NO_SANITIZE int rankOf(T x, bool after) const {
        int lo = 0, hi = (int)srt.size();
        while (lo < hi) {
            int mid = (lo + hi) >> 1;
            if (srt[mid] < x || (after && !(x < srt[mid]))) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }

    // the kth smallest value of a path (1 <= k <= its size): its versions walk down together
    LEETCODE_NO_SANITIZE T kthValue(@CR@, int k) const {
        int lo = 0, hi = (int)srt.size() - 1;
        while (lo < hi) {
            int mid = (lo + hi) >> 1, left = @cnt(lc)@;
            if (k <= left) {
                @go(lc)@
                hi = mid;
            } else {
                k -= left;
                @go(rc)@
                lo = mid + 1;
            }
        }
        return srt[lo];
    }

    // how many of a path's values are among the r smallest distinct values of the tree; total: their sum
    LEETCODE_NO_SANITIZE int valuesBelow(@CR@, int r, S& total) const {
        int lo = 0, hi = (int)srt.size() - 1, many = 0;
        total = 0;
        if (r <= 0) return 0;
        if (r > hi) {
            total = @tot()@;
            return @cnt()@;
        }
        while (lo < hi) {
            int mid = (lo + hi) >> 1;
            if (r > mid) {  // the whole left half is wanted
                many += @cnt(lc)@;
                total += @tot(lc)@;
                @go(rc)@
                lo = mid + 1;
            } else {
                @go(lc)@
                hi = mid;
            }
        }
        return many;
    }

    // the sum of a path's k smallest values (0 <= k <= its size)
    LEETCODE_NO_SANITIZE S smallestSum(@CR@, int k) const {
        if (k <= 0) return 0;
        S total = 0;
        int lo = 0, hi = (int)srt.size() - 1;
        while (lo < hi) {
            int mid = (lo + hi) >> 1, left = @cnt(lc)@;
            if (k <= left) {
                @go(lc)@
                hi = mid;
            } else {
                k -= left;
                total += @tot(lc)@;
                @go(rc)@
                lo = mid + 1;
            }
        }
        return total + (S)k * srt[lo];
    }
'''


# ------------------------------------------------------------------------------------------------ the public ops
def ops(w):
    """[(name, args, C++ arg types, C++ return type, doc, Python body, C++ body)]: every path op, bodies indented by 8.
    Each body starts with the path's versions (@R@) and `size` (how many values the path has) already there."""
    e = w.edge
    size_words, size_now = "the path's size", "{size} (the path's size)"  # (a Python message says the size itself)
    none_py, none_cpp = ("; None", "; nullopt")
    empty = (lambda py, cpp: (f"; {py} when a == b (no edges)", f"; {cpp} when a == b (no edges)")) if e else (lambda py, cpp: ("", ""))
    needs_one = ("; needs at least one edge (a != b), else IndexError", "; needs at least one edge (a != b), else throws out_of_range") if e else ("", "")
    out = []

    def add(name, args, types, ret, doc, py, cpp, tail=("", "")):
        out.append((name, args, types, ret, (doc + tail[0], doc + tail[1]), py, cpp))

    def rank_check(name, cond_py, cond_cpp, rule):
        py = (f"        if not {cond_py}:\n"
              f"            raise IndexError(f\"{w.t}Path{name}: needs {rule.replace(size_words, size_now)}, \"\n"
              "                             f\"got {{ARGS}}\")\n")
        cpp = f"        if ({cond_cpp})\n            throw out_of_range(\"{w.t}Path{name}: needs {rule}\");\n"
        return py, cpp

    q = dict((s, d) for s, _, _, _, d in G.QUERIES)
    doc = lambda s: q[s].format(vals=w.vals, where="on the path a..b", one=w.one, value=w.val if e else "value",  # noqa: E731
                                val=w.val, none="{none}")

    # ---- by rank
    for name, k_expr in (("KthSmallest", "k"), ("KthLargest", "size + 1 - k")):
        cp, cc = rank_check(name, "1 <= k <= size", "k < 1 || k > size", "1 <= k <= the path's size")
        add(name, ["k"], ["int"], "T", doc(name) + "; needs 1 <= k <= the path's size, else {raises}",
            cp.replace("{{ARGS}}", "k = {k}") + f"        return self._kthValue(@R@, {k_expr})\n",
            cc + f"        return kthValue(@R@, {k_expr});\n")
    cp, cc = rank_check("SumSmallestK", "0 <= k <= size", "k < 0 || k > size", "0 <= k <= the path's size")
    add("SumSmallestK", ["k"], ["int"], "S", doc("SumSmallestK") + "; needs 0 <= k <= the path's size, else {raises}",
        cp.replace("{{ARGS}}", "k = {k}") + "        return self._smallestSum(@R@, k)\n", cc + "        return smallestSum(@R@, k);\n")
    cp, cc = rank_check("SumLargestK", "0 <= k <= size", "k < 0 || k > size", "0 <= k <= the path's size")
    add("SumLargestK", ["k"], ["int"], "S", doc("SumLargestK") + "; needs 0 <= k <= the path's size, else {raises}",
        cp.replace("{{ARGS}}", "k = {k}") + "        return @tot()@ - self._smallestSum(@R@, size - k)\n",
        cc + "        return @tot()@ - smallestSum(@R@, size - k);\n")
    for name, hi_k, lo_k in (("SumKthSmallestRange", "kTo", "kFrom - 1"), ("SumKthLargestRange", "size - kFrom + 1", "size - kTo")):
        cp, cc = rank_check(name, "1 <= kFrom <= kTo <= size", "kFrom < 1 || kFrom > kTo || kTo > size",
                            "1 <= kFrom <= kTo <= the path's size")
        add(name, ["kFrom", "kTo"], ["int", "int"], "S", doc(name) + "; needs 1 <= kFrom <= kTo <= the path's size, else {raises}",
            cp.replace("{{ARGS}}", "kFrom = {kFrom}, kTo = {kTo}")
            + f"        return self._smallestSum(@R@, {hi_k}) - self._smallestSum(@R@, {lo_k})\n",
            cc + f"        return smallestSum(@R@, {hi_k}) - smallestSum(@R@, {lo_k});\n")

    # ---- the whole path
    add("Sum", [], [], "S", doc("Sum"), "        return @tot()@\n", "        return @tot()@;\n", empty("0", "0"))
    for name, k_expr, py_none, cpp_none in (("Min", "1", 'float("inf")', "numeric_limits<T>::max()"),
                                            ("Max", "size", 'float("-inf")', "numeric_limits<T>::lowest()")):
        guard_py = f"        if size == 0:\n            return {py_none}\n" if e else ""
        guard_cpp = f"        if (size == 0) return {cpp_none};\n" if e else ""
        words = empty("inf" if name == "Min" else "-inf", "the largest value of its type" if name == "Min" else "the smallest value of its type")
        add(name, [], [], "T", doc(name), guard_py + f"        return self._kthValue(@R@, {k_expr})\n",
            guard_cpp + f"        return kthValue(@R@, {k_expr});\n", words)

    # ---- by value: how many / the sum of the values below a rank
    for cmp_, side, flip in (("Lt", "left", False), ("Lte", "right", False), ("Gt", "right", True), ("Gte", "left", True)):
        after = "true" if side == "right" else "false"
        for what, idx, ret, total in (("Count", 0, "int", "size"), ("Sum", 1, "S", "@tot()@")):
            name = f"{what}{cmp_}X"
            py = f"self._valuesBelow(@R@, bisect_{side}(self.srt, x))[{idx}]"
            if what == "Count":
                cpp = "        S unused;\n" + (f"        return size - valuesBelow(@R@, rankOf(x, {after}), unused);\n" if flip
                                               else f"        return valuesBelow(@R@, rankOf(x, {after}), unused);\n")
            else:
                cpp = (f"        S low;\n        valuesBelow(@R@, rankOf(x, {after}), low);\n"
                       + (f"        return {total} - low;\n" if flip else "        return low;\n"))
            add(name, ["x"], ["T"], ret, doc(name), f"        return {total + ' - ' if flip else ''}{py}\n", cpp, empty("0", "0"))
    add("CountInValRange", ["low", "high"], ["T", "T"], "int", doc("CountInValRange"),
        "        if low > high:\n            return 0\n"
        "        upTo = self._valuesBelow(@R@, bisect_right(self.srt, high))[0]\n"
        "        return upTo - self._valuesBelow(@R@, bisect_left(self.srt, low))[0]\n",
        "        if (high < low) return 0;\n        S unused;\n"
        "        int upTo = valuesBelow(@R@, rankOf(high, true), unused);\n"
        "        return upTo - valuesBelow(@R@, rankOf(low, false), unused);\n", empty("0", "0"))
    add("SumInValRange", ["low", "high"], ["T", "T"], "S", doc("SumInValRange"),
        "        if low > high:\n            return 0\n"
        "        upTo = self._valuesBelow(@R@, bisect_right(self.srt, high))[1]\n"
        "        return upTo - self._valuesBelow(@R@, bisect_left(self.srt, low))[1]\n",
        "        if (high < low) return 0;\n        S upTo, under;\n"
        "        valuesBelow(@R@, rankOf(high, true), upTo), valuesBelow(@R@, rankOf(low, false), under);\n"
        "        return upTo - under;\n", empty("0", "0"))
    add("CountOccurrences", ["x"], ["T"], "int", doc("CountOccurrences"),
        "        upTo = self._valuesBelow(@R@, bisect_right(self.srt, x))[0]\n"
        "        return upTo - self._valuesBelow(@R@, bisect_left(self.srt, x))[0]\n",
        "        S unused;\n        return valuesBelow(@R@, rankOf(x, true), unused) - valuesBelow(@R@, rankOf(x, false), unused);\n",
        empty("0", "0"))

    # ---- distance sums: the values below x pull up to it, the rest pull down
    dist_py = ("        many, low = self._valuesBelow(@R@, bisect_left(self.srt, x))\n"
               "        return x * many - low + (@tot()@ - low) - x * (size - many)\n")
    dist_cpp = ("        S low;\n        int many = valuesBelow(@R@, rankOf(x, false), low);\n"
                "        return (S)x * many - low + (@tot()@ - low) - (S)x * (size - many);\n")
    add("SumAbsDiffToX", ["x"], ["T"], "S", doc("SumAbsDiffToX"), dist_py, dist_cpp, empty("0", "0"))
    add("SumAbsDiffToMedian", [], [], "S", doc("SumAbsDiffToMedian") + " (the lower median)",
        (f"        if size == 0:\n            raise IndexError(\"{w.t}PathSumAbsDiffToMedian: needs at least one edge (a != b)\")\n" if e else "")
        + "        x = self._kthValue(@R@, (size + 1) // 2)\n" + dist_py,
        (f"        if (size == 0) throw out_of_range(\"{w.t}PathSumAbsDiffToMedian: needs at least one edge (a != b)\");\n" if e else "")
        + "        T x = kthValue(@R@, (size + 1) / 2);\n" + dist_cpp, needs_one)

    # ---- nearest to x
    for name, side, up in (("SmallestGteX", "left", True), ("SmallestGtX", "right", True),
                           ("LargestLteX", "right", False), ("LargestLtX", "left", False)):
        after = "true" if side == "right" else "false"
        if up:
            py = (f"        k = self._valuesBelow(@R@, bisect_{side}(self.srt, x))[0]\n"
                  "        return None if k == size else self._kthValue(@R@, k + 1)\n")
            cpp = (f"        S unused;\n        int k = valuesBelow(@R@, rankOf(x, {after}), unused);\n"
                   "        if (k == size) return nullopt;\n        return kthValue(@R@, k + 1);\n")
        else:
            py = (f"        k = self._valuesBelow(@R@, bisect_{side}(self.srt, x))[0]\n"
                  "        return None if k == 0 else self._kthValue(@R@, k)\n")
            cpp = (f"        S unused;\n        int k = valuesBelow(@R@, rankOf(x, {after}), unused);\n"
                   "        if (k == 0) return nullopt;\n        return kthValue(@R@, k);\n")
        add(name, ["x"], ["T"], "optional<T>", doc(name), py, cpp)
    return out


def methods(w):
    """(the Python methods, the C++ methods, {op: cost}) for one target."""
    py, cpp, costs = [], [], {}
    for name, args, types, ret, (doc_py, doc_cpp), body_py, body_cpp in ops(w):
        full = f"{w.t}Path{name}"
        costs[full] = "log(N)"
        params = ["a", "b"] + args
        doc_py = doc_py.format(none="None", raises="IndexError")
        doc_cpp = doc_cpp.format(none="nullopt", raises="throws out_of_range")
        py.append(G.comment("#", "log(N)", doc_py) + f"    def {full}(self, {', '.join(params)}):\n" + G.py_check(full, ("a", "b"))
                  + "        @R@ = self._roots(a, b)\n"
                  + ("        cnt, tot = self.cnt, self.tot\n" if "@tot" in body_py else "        cnt = self.cnt\n"
                     if "size" in body_py else "")
                  + ("        size = @cnt()@\n" if "size" in body_py else "") + body_py)
        decl = ", ".join(["int a", "int b"] + [f"{t} {a}" for t, a in zip(types, args)])
        cpp.append(G.comment("//", "log(N)", doc_cpp) + f"    LEETCODE_NO_SANITIZE {ret} {full}({decl}) const {{\n"
                   + G.cpp_check(full, ("a", "b")) + f"        int {w.roots};\n        roots(a, b, {w.roots});\n"
                   + ("        int size = @cnt()@;\n" if "size" in body_cpp else "") + body_cpp + "    }\n")
    return "\n".join(py), "\n".join(cpp), costs


# ------------------------------------------------------------------------------------------------ the two files
HOW = ("How it works: every node keeps a version of a persistent segment tree over the values (by rank), holding the "
       "{held}. A version copies its parent's and adds one value, so all of them take O(n log n) nodes. A path a..b is "
       "then {formula}, and the versions walk down together: O(log n) a query. The values are fixed: there are no "
       "updates.")


def header(cm, folder, costs, ext):
    costs = dict(costs)
    costs.update({op: shape.COSTS[op][0] for op in G.SHAPE_OPS})
    lines = [
        "Template by https://github.com/ishaanbuildsthings",
        f"{G.URL}/{folder}/template.{ext}",
        "@operations: " + " ".join(sorted(costs)),
        f"@data-structure-type: {KIND}",
        "@complexities:",
        *[f"  {op}: {costs[op]}" for op in sorted(costs)],
        "  build: N*log(N)",
        "@memory:",
        "  layout: none",
        f"  node: {VERSION_ARRAYS}",
        "  tags: none",
        f"  other: {OTHER_ARRAYS}",
        "  note: a version is a root in lc / rc / cnt / tot; each adds log(N) nodes to its parent's",
    ]
    return "".join(f"{cm} {line}\n" for line in lines)


PY_VERSIONS = '''\
        # one version per node: its parent's, plus {its_value} (the versions share everything else)
        srt = sorted({{{values}}})  # the distinct values: a version is a tree over their ranks
        rank = {{x: i for i, x in enumerate(srt)}}
        depth = max(1, (len(srt) - 1).bit_length())
        lc = [0] * (n * (depth + 1) + 1)  # node 0 is the empty version
        rc = lc[:]
        cnt = lc[:]
        tot = lc[:]
        ver = [0] * (hi + 1)
        used = 1
        for v in {nodes}:
            prev = {prev}
            x = val[v]
            i = rank[x]
            cur = ver[v] = used
            a, b = 0, len(srt) - 1
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
        self.srt, self.lc, self.rc, self.cnt, self.tot, self.ver, self.val = srt, lc, rc, cnt, tot, ver, val
'''
CPP_VERSIONS = '''\
        // one version per node: its parent's, plus {its_value} (the versions share everything else)
        vector<T> sorted;  // the distinct values: a version is a tree over their ranks
        for (int i = {first}; i < n; i++) sorted.push_back(val[bfs[i]]);
        sort(sorted.begin(), sorted.end());
        sorted.erase(unique(sorted.begin(), sorted.end()), sorted.end());
        srt.assign(sorted.begin(), sorted.end());
        int depth = 1;
        while ((1 << depth) < (int)srt.size()) depth++;
        size_t cap = (size_t)n * (depth + 1) + 1;  // node 0 is the empty version
        lc.assign(cap, 0), rc.assign(cap, 0), cnt.assign(cap, 0), tot.assign(cap, 0);
        ver.assign(hi + 1, 0);
        int used = 1;
        for (int k = {first}; k < n; k++) {{
            int v = bfs[k], prev = {prev};
            T x = val[v];
            int i = (int)(lower_bound(sorted.begin(), sorted.end(), x) - sorted.begin());
            int cur = ver[v] = used, a = 0, b = (int)srt.size() - 1;
            while (true) {{
                cnt[cur] = cnt[prev] + 1, tot[cur] = tot[prev] + x;
                used++;
                if (a == b) break;
                int mid = (a + b) >> 1;
                if (i <= mid) rc[cur] = rc[prev], lc[cur] = used, prev = lc[prev], b = mid;
                else lc[cur] = lc[prev], rc[cur] = used, prev = rc[prev], a = mid + 1;
                cur = used;
            }}
        }}
'''


def make(edge):
    w = Words(edge)
    folder = f"path-rank-{w.t}"
    py_methods, cpp_methods, costs = methods(w)
    get = f"{w.t}Get"
    costs[get] = "1"
    how = HOW.format(held="edges on its path from the root, each as its weight" if edge else "values on its path from the root",
                     formula="ver[a] + ver[b] - 2 * ver[lca]" if edge else "ver[a] + ver[b] - ver[lca] - ver[parent(lca)]")

    # ---- Python
    class_info = type("R", (), {"extra_names": [], "cls": ""})
    if edge:
        doc = G.fill_doc(G.PY_DOC_EDGE, "#", class_info, "edges, root", "", "edge")
        doc = doc[:doc.index("# How it works")] + G.wrap("#", how)
        ctor = (G.comment("#", "N*log(N)", "builds the layout and a version per node; raises ValueError when the edges are not "
                          "one tree on nodes 0..n-1 or 1..n, or an edge has no weight")
                + "    def __init__(self, edges, root):\n" + shape.py_layout_body()
                + "        for e in edges:\n"
                "            if len(e) != 3:\n"
                '                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")\n'
                "        val = [0] * (hi + 1)  # val[v]: the weight of the edge above v (the root has none)\n"
                "        for e in edges:\n"
                "            val[e[0] if par[e[0]] == e[1] else e[1]] = e[2]\n"
                + PY_VERSIONS.format(its_value="the weight of the edge above it", values="val[v] for v in bfs[1:]",
                                     nodes="bfs[1:]", prev="ver[par[v]]"))
        get_py = ("    # O(1) -- weight(a - b); a and b are the edge's two ends, in either order\n"
                  f"    def {get}(self, a, b):\n" + G.py_check(get, ("a", "b"))
                  + "        if self.par[a] == b:\n            return self.val[a]\n"
                  "        if self.par[b] == a:\n            return self.val[b]\n"
                  f'        raise IndexError(f"{get}: needs an edge between a and b, got {{a}} and {{b}}")\n')
        helpers = PY_HELPERS_EDGE
    else:
        doc = G.fill_doc(G.PY_DOC, "#", class_info, "edges, root, vals", "")
        doc = doc[:doc.index("# How it works")] + G.wrap("#", how)
        ctor = (G.comment("#", "N*log(N)", "builds the layout and a version per node; raises ValueError when the edges are not "
                          "one tree on nodes 0..n-1 or 1..n, or vals has the wrong length")
                + "    def __init__(self, edges, root, vals):\n" + shape.py_layout_body() + G.PY_VALS
                + "        val = list(vals)\n"
                + PY_VERSIONS.format(its_value="its own value", values="val[v] for v in bfs", nodes="bfs",
                                     prev="ver[par[v]] if v != root else 0"))
        get_py = (f"    # O(1) -- val(node)\n    def {get}(self, node):\n" + G.py_check(get, ("node",))
                  + "        return self.val[node]\n")
        helpers = PY_HELPERS_NODE
    py = (header("#", folder, costs, "py") + "\nfrom bisect import bisect_left, bisect_right\n\n\n" + doc + "class Tree:\n" + ctor
          + "\n" + get_py + "\n" + w.fill(helpers + "\n" + PY_HELPERS + "\n" + py_methods, False) + "\n" + shape.py_shape_methods())

    # ---- C++
    members = (shape.cpp_members().rstrip("\n") + "\n"
               "    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;  // what sums are kept in\n"
               "    HotVector<int> lc, rc, cnt;  // the versions' nodes: children and how many values (node 0 is the empty version)\n"
               "    HotVector<S> tot;  // ... and their sum\n"
               "    HotVector<int> ver;  // ver[v]: the root of v's version\n"
               "    HotVector<T> srt;  // the distinct values, sorted: a version is a tree over their ranks\n"
               f"    HotVector<T> val;  // {'val[v]: the weight of the edge above v (the root has none)' if edge else 'the node values'}\n")
    if edge:
        doc = G.fill_doc(G.CPP_DOC_EDGE, "//", class_info, "edges, root", "", "edge")
        doc = doc[:doc.index("// How it works")] + G.wrap("//", how)
        ctor = (G.comment("//", "N*log(N)", "builds the layout and a version per node; throws invalid_argument when the edges "
                          "are not one tree on nodes 0..n-1 or 1..n, or an edge has no weight")
                + "    template <typename E = int> Tree(const vector<vector<E>>& edges, int root) : root(root) {\n"
                + shape.cpp_layout_body() + "\n"
                "        for (const auto& e : edges)\n"
                '            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");\n'
                "        val.assign(hi + 1, T(0));\n"
                "        for (const auto& e : edges) {\n"
                "            int a = (int)e[0], b = (int)e[1];\n"
                "            val[par[a] == b ? a : b] = (T)e[2];\n"
                "        }\n"
                + CPP_VERSIONS.format(its_value="the weight of the edge above it", first="1", prev="ver[par[v]]") + "    }\n")
        get_cpp = ("    // O(1) -- weight(a - b); a and b are the edge's two ends, in either order\n"
                   f"    LEETCODE_NO_SANITIZE T {get}(int a, int b) const {{\n" + G.cpp_check(get, ("a", "b"))
                   + "        if (par[a] == b) return val[a];\n        if (par[b] == a) return val[b];\n"
                   f'        throw out_of_range("{get}: needs an edge between a and b");\n    }}\n')
        helpers = CPP_HELPERS_EDGE
    else:
        doc = G.fill_doc(G.CPP_DOC, "//", class_info, "edges, root, vals", "")
        doc = doc[:doc.index("// How it works")] + G.wrap("//", how)
        ctor = (G.comment("//", "N*log(N)", "builds the layout and a version per node; throws invalid_argument when the edges "
                          "are not one tree on nodes 0..n-1 or 1..n, or vals has the wrong size")
                + "    template <typename E = int> Tree(const vector<vector<E>>& edges, int root, const vector<T>& vals) : root(root) {\n"
                + shape.cpp_layout_body() + "\n"
                "        if ((int)vals.size() != hi + 1)\n"
                '            throw invalid_argument("Tree: vals[node] is node\'s value, so nodes " + nodes + " need vals.size() = " +\n'
                "                                   to_string(hi + 1) + \", got \" + to_string(vals.size()));\n"
                "        val.assign(vals.begin(), vals.end());\n"
                + CPP_VERSIONS.format(its_value="its own value", first="0", prev="v == root ? 0 : ver[par[v]]") + "    }\n")
        get_cpp = (f"    // O(1) -- val(node)\n    LEETCODE_NO_SANITIZE T {get}(int node) const {{\n" + G.cpp_check(get, ("node",))
                   + "        return val[node];\n    }\n")
        helpers = CPP_HELPERS_NODE
    cpp = (header("//", folder, costs, "cpp") + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n"
           + shape.FAST_NOTE + shape.PRELUDE + doc + "template <typename T>\nstruct Tree {\n" + members + "\n" + ctor + "\n" + get_cpp
           + "\n" + w.fill(helpers + "\n" + CPP_HELPERS + "\n" + cpp_methods, True) + "\n"
           + shape.cpp_shape_methods().rstrip("\n") + "\n};\n")
    return folder, py, cpp


def sources():
    out = {}
    for edge in (False, True):
        folder, py, cpp = make(edge)
        for name, text in (("template.py", py), ("template.cpp", cpp)):
            too_long = long_lines(text)
            assert not too_long, f"{folder}/{name}: a line past 120 columns: line {too_long[0]}"
            out[os.path.join(folder, name)] = check_finished(text, f"{folder}/{name}")
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
            print(f"FAIL  tree-queries/{rel}: differs from what gen_tree_rank.py writes (rerun it)")
        print(f"{len(stale)} stale by-rank path files" if stale else "by-rank path templates are fresh")
        sys.exit(1 if stale else 0)
    print(f"{len(sources())} by-rank path files, {len(stale)} written")


if __name__ == "__main__":
    main()
