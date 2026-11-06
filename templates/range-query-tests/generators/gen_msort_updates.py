"""Merge sort trees with point updates: count / sum / xor of the values below x in a[l..r], and the nearest values to x,
while point updates change the array. O(log^2 N) instead of the log(N) * log(U) of the trees of value trees.

    python3 gen_msort_updates.py      # then gen_fast.py, then npm run gen:range-queries in site/

A segment tree over positions (bottom-up: node p >= n is a[p - n], node p < n covers its two children), every inner
node keeping the values at its positions in a searchable structure. a[l..r] is O(log N) nodes; a point update changes
one value in each of the O(log N) nodes above its position. Leaves keep nothing: a leaf is answered from a[i] itself.

Inner structures (one template folder each, times the families of ops it can carry):
  sortedlist   online, no value range: sorted buckets of 256 to 512 values with a Fenwick tree over the bucket sizes
               (like SortedList). Counts and nearest values.
  treap        online, no value range: a treap per node, keyed by value with copies counted, keeping subtree sums
               and xors. Adds the sum / xor families (counts alone are cheaper with sortedlist).
  hashfenwick  online over a value range [valLo, valHi]: a Fenwick tree over the whole value range per node, stored
               sparsely in one hash table. log(N) * log(U), C++ only (in Python the dict lookups are far too slow).
  offline      every point assignment listed up front: each node keeps the sorted values its positions can ever hold
               and Fenwick trees over them, in flat arrays. The fastest, with worst-case bounds.
"""
import os

DIR = os.environ.get("RANGE_DIR") or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
URL = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries"
FAM_OPS = {
    "count": ["countGtX", "countGteX", "countInValRange", "countLtX", "countLteX"],
    "near": ["largestLtX", "largestLteX", "smallestGtX", "smallestGteX"],
    "sums": ["sumAbsDiffToX", "sumGtX", "sumGteX", "sumInValRange", "sumLtX", "sumLteX"],
    "xor": ["xorGtX", "xorGteX", "xorInValRange", "xorLtX", "xorLteX"],
}
ONLINE_POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
OFFLINE_POINT = ["pointAssign", "pointGet"]
INNERS = {"sortedlist": [()], "treap": [("sums",), ("xor",), ("sums", "xor")],
          "hashfenwick": [(), ("sums",), ("xor",), ("sums", "xor")], "offline": [(), ("sums",), ("xor",), ("sums", "xor")]}
RULE = "needs 0 <= l <= r < n"

# ------------------------------------------------------------------------------------------------ query ops (shared)

QUERY_DOC = {
    "countLtX": "# of i in [l, r] with a[i] < x", "countLteX": "# of i in [l, r] with a[i] <= x",
    "countGtX": "# of i in [l, r] with a[i] > x", "countGteX": "# of i in [l, r] with a[i] >= x",
    "countInValRange": "# of i in [l, r] with lowVal <= a[i] <= highVal (0 if lowVal > highVal)",
    "smallestGteX": "smallest a[i] >= x in [l, r]", "smallestGtX": "smallest a[i] > x in [l, r]",
    "largestLteX": "largest a[i] <= x in [l, r]", "largestLtX": "largest a[i] < x in [l, r]",
    "sumLtX": "sum of a[i] < x in [l, r]", "sumLteX": "sum of a[i] <= x in [l, r]",
    "sumGtX": "sum of a[i] > x in [l, r]", "sumGteX": "sum of a[i] >= x in [l, r]",
    "sumInValRange": "sum of a[i] with lowVal <= a[i] <= highVal in [l, r] (0 if lowVal > highVal)",
    "sumAbsDiffToX": "sum of |a[i] - x| over [l, r]",
    "xorLtX": "xor of a[i] < x in [l, r]", "xorLteX": "xor of a[i] <= x in [l, r]",
    "xorGtX": "xor of a[i] > x in [l, r]", "xorGteX": "xor of a[i] >= x in [l, r]",
    "xorInValRange": "xor of a[i] with lowVal <= a[i] <= highVal in [l, r] (0 if lowVal > highVal)",
}


def cpp_query_ops(fams, cost):
    s = ""

    def op(name, ret, params, body, note=""):
        nonlocal s
        args = ", ".join(f"T {p}" for p in params)
        s += f"    // O({cost}) -- {QUERY_DOC[name]}{note}; {RULE}, else throws out_of_range\n"
        s += f"    {ret} {name}(int l, int r, {args}) const {{\n"
        s += f'        if (l < 0 || l > r || r >= n) throw out_of_range("{name}: {RULE}");\n'
        s += "".join(f"        {line}\n" for line in body) + "    }\n\n"

    op("countLtX", "long long", ["x"], ["return countLess(l, r, x, true);"])
    op("countLteX", "long long", ["x"], ["return countLess(l, r, x, false);"])
    op("countGtX", "long long", ["x"], ["return (r - l + 1) - countLess(l, r, x, false);"])
    op("countGteX", "long long", ["x"], ["return (r - l + 1) - countLess(l, r, x, true);"])
    op("countInValRange", "long long", ["lowVal", "highVal"],
       ["if (lowVal > highVal) return 0;", "return countLess(l, r, highVal, false) - countLess(l, r, lowVal, true);"])
    none = "; nullopt if there is none"
    op("smallestGteX", "optional<T>", ["x"], ["return firstAtLeast(l, r, x, false);"], none)
    op("smallestGtX", "optional<T>", ["x"], ["return firstAtLeast(l, r, x, true);"], none)
    op("largestLteX", "optional<T>", ["x"], ["return lastBelow(l, r, x, false);"], none)
    op("largestLtX", "optional<T>", ["x"], ["return lastBelow(l, r, x, true);"], none)
    if "sums" in fams:
        op("sumLtX", "S", ["x"], ["return sumLess(l, r, x, true);"])
        op("sumLteX", "S", ["x"], ["return sumLess(l, r, x, false);"])
        op("sumGtX", "S", ["x"], ["return sumAll(l, r) - sumLess(l, r, x, false);"])
        op("sumGteX", "S", ["x"], ["return sumAll(l, r) - sumLess(l, r, x, true);"])
        op("sumInValRange", "S", ["lowVal", "highVal"],
           ["if (lowVal > highVal) return 0;", "return sumLess(l, r, highVal, false) - sumLess(l, r, lowVal, true);"])
        op("sumAbsDiffToX", "S", ["x"], [
            "long long below = countLess(l, r, x, true);",
            "S belowSum = sumLess(l, r, x, true), total = sumAll(l, r);",
            "return S(x) * below - belowSum + (total - belowSum) - S(x) * ((r - l + 1) - below);"])
    if "xor" in fams:
        op("xorLtX", "T", ["x"], ["return xorLess(l, r, x, true);"])
        op("xorLteX", "T", ["x"], ["return xorLess(l, r, x, false);"])
        op("xorGtX", "T", ["x"], ["return xorAll(l, r) ^ xorLess(l, r, x, false);"])
        op("xorGteX", "T", ["x"], ["return xorAll(l, r) ^ xorLess(l, r, x, true);"])
        op("xorInValRange", "T", ["lowVal", "highVal"],
           ["if (lowVal > highVal) return 0;", "return xorLess(l, r, highVal, false) ^ xorLess(l, r, lowVal, true);"])
    return s


def cpp_range_helpers(fams):
    s = """    template <class F>
    void forNodes(int l, int r, F f) const {  // the O(log n) nodes that cover a[l..r]
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) f(l++);
            if (r & 1) f(--r);
        }
    }

    long long countLess(int l, int r, T x, bool strict) const {  // # of values < x (strict) or <= x in a[l..r]
        long long res = 0;
        forNodes(l, r, [&](int p) {
            if (p >= n) res += strict ? A[p - n] < x : !(x < A[p - n]);
            else res += countBelow(p, x, strict);
        });
        return res;
    }

    optional<T> firstAtLeast(int l, int r, T x, bool strict) const {  // smallest value > x (strict) or >= x
        optional<T> best;
        forNodes(l, r, [&](int p) {
            optional<T> got;
            if (p >= n) {
                if (strict ? x < A[p - n] : !(A[p - n] < x)) got = A[p - n];
            } else {
                got = firstIn(p, x, strict);
            }
            if (got && (!best || *got < *best)) best = got;
        });
        return best;
    }

    optional<T> lastBelow(int l, int r, T x, bool strict) const {  // largest value < x (strict) or <= x
        optional<T> best;
        forNodes(l, r, [&](int p) {
            optional<T> got;
            if (p >= n) {
                if (strict ? A[p - n] < x : !(x < A[p - n])) got = A[p - n];
            } else {
                got = lastIn(p, x, strict);
            }
            if (got && (!best || *best < *got)) best = got;
        });
        return best;
    }

"""
    if "sums" in fams:
        s += """    S sumLess(int l, int r, T x, bool strict) const {
        S res = 0;
        forNodes(l, r, [&](int p) {
            if (p >= n) {
                if (strict ? A[p - n] < x : !(x < A[p - n])) res += A[p - n];
            } else {
                res += sumBelow(p, x, strict);
            }
        });
        return res;
    }

    S sumAll(int l, int r) const {
        S res = 0;
        forNodes(l, r, [&](int p) { res += p >= n ? S(A[p - n]) : total[p]; });
        return res;
    }

"""
    if "xor" in fams:
        s += """    T xorLess(int l, int r, T x, bool strict) const {
        T res = 0;
        forNodes(l, r, [&](int p) {
            if (p >= n) {
                if (strict ? A[p - n] < x : !(x < A[p - n])) res ^= A[p - n];
            } else {
                res ^= xorBelow(p, x, strict);
            }
        });
        return res;
    }

    T xorAll(int l, int r) const {
        T res = 0;
        forNodes(l, r, [&](int p) { res ^= p >= n ? A[p - n] : xorTotal[p]; });
        return res;
    }

"""
    return s


def py_query_ops(fams, cost):
    s = ""

    def op(name, params, body, note=""):
        nonlocal s
        args = "".join(f", {p}" for p in params)
        s += f"    # O({cost}) -- {QUERY_DOC[name]}{note}; {RULE}, else raises IndexError\n"
        s += f"    def {name}(self, l, r{args}):\n"
        s += f'        if l < 0 or l > r or r >= self.n:\n            raise IndexError(f"{name}: {RULE}, got l={{l}}, r={{r}}, n={{self.n}}")\n'
        s += "".join(f"        {line}\n" for line in body) + "\n"

    op("countLtX", ["x"], ["return self._countLess(l, r, x, True)"])
    op("countLteX", ["x"], ["return self._countLess(l, r, x, False)"])
    op("countGtX", ["x"], ["return (r - l + 1) - self._countLess(l, r, x, False)"])
    op("countGteX", ["x"], ["return (r - l + 1) - self._countLess(l, r, x, True)"])
    op("countInValRange", ["lowVal", "highVal"],
       ["if lowVal > highVal:", "    return 0", "return self._countLess(l, r, highVal, False) - self._countLess(l, r, lowVal, True)"])
    none = "; None if there is none"
    op("smallestGteX", ["x"], ["return self._firstAtLeast(l, r, x, False)"], none)
    op("smallestGtX", ["x"], ["return self._firstAtLeast(l, r, x, True)"], none)
    op("largestLteX", ["x"], ["return self._lastBelow(l, r, x, False)"], none)
    op("largestLtX", ["x"], ["return self._lastBelow(l, r, x, True)"], none)
    if "sums" in fams:
        op("sumLtX", ["x"], ["return self._sumLess(l, r, x, True)"])
        op("sumLteX", ["x"], ["return self._sumLess(l, r, x, False)"])
        op("sumGtX", ["x"], ["return self._sumAll(l, r) - self._sumLess(l, r, x, False)"])
        op("sumGteX", ["x"], ["return self._sumAll(l, r) - self._sumLess(l, r, x, True)"])
        op("sumInValRange", ["lowVal", "highVal"],
           ["if lowVal > highVal:", "    return 0", "return self._sumLess(l, r, highVal, False) - self._sumLess(l, r, lowVal, True)"])
        op("sumAbsDiffToX", ["x"], [
            "below = self._countLess(l, r, x, True)",
            "belowSum, total = self._sumLess(l, r, x, True), self._sumAll(l, r)",
            "return x * below - belowSum + (total - belowSum) - x * ((r - l + 1) - below)"])
    if "xor" in fams:
        op("xorLtX", ["x"], ["return self._xorLess(l, r, x, True)"])
        op("xorLteX", ["x"], ["return self._xorLess(l, r, x, False)"])
        op("xorGtX", ["x"], ["return self._xorAll(l, r) ^ self._xorLess(l, r, x, False)"])
        op("xorGteX", ["x"], ["return self._xorAll(l, r) ^ self._xorLess(l, r, x, True)"])
        op("xorInValRange", ["lowVal", "highVal"],
           ["if lowVal > highVal:", "    return 0", "return self._xorLess(l, r, highVal, False) ^ self._xorLess(l, r, lowVal, True)"])
    return s


def py_range_helpers(fams):
    s = """    def _nodes(self, l, r):  # the O(log n) nodes that cover a[l..r]
        n = self.n
        l += n
        r += n + 1
        out = []
        while l < r:
            if l & 1:
                out.append(l)
                l += 1
            if r & 1:
                r -= 1
                out.append(r)
            l >>= 1
            r >>= 1
        return out

    def _countLess(self, l, r, x, strict):  # number of values < x (strict) or <= x in a[l..r]
        n, A, res = self.n, self.A, 0
        for p in self._nodes(l, r):
            if p >= n:
                v = A[p - n]
                res += (v < x) if strict else (v <= x)
            else:
                res += self._countBelow(p, x, strict)
        return res

    def _firstAtLeast(self, l, r, x, strict):  # smallest value > x (strict) or >= x
        n, A, best = self.n, self.A, None
        for p in self._nodes(l, r):
            if p >= n:
                v = A[p - n]
                got = v if ((v > x) if strict else (v >= x)) else None
            else:
                got = self._firstIn(p, x, strict)
            if got is not None and (best is None or got < best):
                best = got
        return best

    def _lastBelow(self, l, r, x, strict):  # largest value < x (strict) or <= x
        n, A, best = self.n, self.A, None
        for p in self._nodes(l, r):
            if p >= n:
                v = A[p - n]
                got = v if ((v < x) if strict else (v <= x)) else None
            else:
                got = self._lastIn(p, x, strict)
            if got is not None and (best is None or got > best):
                best = got
        return best

"""
    if "sums" in fams:
        s += """    def _sumLess(self, l, r, x, strict):
        n, A, res = self.n, self.A, 0
        for p in self._nodes(l, r):
            if p >= n:
                v = A[p - n]
                if (v < x) if strict else (v <= x):
                    res += v
            else:
                res += self._sumBelow(p, x, strict)
        return res

    def _sumAll(self, l, r):
        n, A, total = self.n, self.A, self.total
        return sum(A[p - n] if p >= n else total[p] for p in self._nodes(l, r))

"""
    if "xor" in fams:
        s += """    def _xorLess(self, l, r, x, strict):
        n, A, res = self.n, self.A, 0
        for p in self._nodes(l, r):
            if p >= n:
                v = A[p - n]
                if (v < x) if strict else (v <= x):
                    res ^= v
            else:
                res ^= self._xorBelow(p, x, strict)
        return res

    def _xorAll(self, l, r):
        n, A, res, xorTotal = self.n, self.A, 0, self.xorTotal
        for p in self._nodes(l, r):
            res ^= A[p - n] if p >= n else xorTotal[p]
        return res

"""
    return s


# ------------------------------------------------------------------------------------------------ point updates

def cpp_online_points(cost, ranged):
    s = '    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range\n    T pointGet(int i) const {\n        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");\n        return A[i];\n    }\n\n'
    extra = " and the new value in [valLo, valHi]" if ranged else ""
    for op, doc, value in (("pointAssign", "a[i] = v (overwrite)", "v"), ("pointAdd", "a[i] += v", "T(A[i] + v)"),
                           ("pointChmax", "a[i] = max(a[i], v)", "max(A[i], v)"), ("pointChmin", "a[i] = min(a[i], v)", "min(A[i], v)")):
        s += f"    // O({cost}) -- {doc}; needs 0 <= i < n{extra}, else throws out_of_range\n    void {op}(int i, T v) {{\n"
        s += f'        if (i < 0 || i >= n) throw out_of_range("{op}: needs 0 <= i < n");\n        write(i, {value}, "{op}");\n    }}\n\n'
    return s


def cpp_write(fams, ranged):
    s = "    void write(int i, T v, [[maybe_unused]] const char* op) {\n        T old = A[i];\n        if (old == v) return;\n"
    if ranged:
        s += '        if ((long long)v < lo || (long long)v > hi) throw out_of_range(string(op) + ": the new value must be in [valLo, valHi]");\n'
    s += "        for (int p = (i + n) >> 1; p >= 1; p >>= 1) {\n            eraseValue(p, old);\n            insertValue(p, v);\n"
    if "sums" in fams:
        s += "            total[p] += S(v) - S(old);\n"
    if "xor" in fams:
        s += "            xorTotal[p] ^= old ^ v;\n"
    s += "        }\n        A[i] = v;\n    }\n\n"
    return s


def py_online_points(cost, ranged):
    s = '    # O(1) -- a[i]; needs 0 <= i < n, else raises IndexError\n    def pointGet(self, i):\n        if i < 0 or i >= self.n:\n            raise IndexError(f"pointGet: needs 0 <= i < n, got i={i}, n={self.n}")\n        return self.A[i]\n\n'
    for op, doc, value in (("pointAssign", "a[i] = v (overwrite)", "v"), ("pointAdd", "a[i] += v", "self.A[i] + v"),
                           ("pointChmax", "a[i] = max(a[i], v)", "max(self.A[i], v)"), ("pointChmin", "a[i] = min(a[i], v)", "min(self.A[i], v)")):
        s += f"    # O({cost}) -- {doc}; needs 0 <= i < n, else raises IndexError\n    def {op}(self, i, v):\n"
        s += f'        if i < 0 or i >= self.n:\n            raise IndexError(f"{op}: needs 0 <= i < n, got i={{i}}, n={{self.n}}")\n        self._write(i, {value})\n\n'
    return s


def py_write(fams):
    s = "    def _write(self, i, v):\n        old = self.A[i]\n        if old == v:\n            return\n        p = (i + self.n) >> 1\n        while p:\n"
    s += "            self._erase(p, old)\n            self._insert(p, v)\n"
    if "sums" in fams:
        s += "            self.total[p] += v - old\n"
    if "xor" in fams:
        s += "            self.xorTotal[p] ^= old ^ v\n"
    s += "            p >>= 1\n        self.A[i] = v\n\n"
    return s


CPP_TOTALS = """    void buildTotals() {  // the sum / xor of every node's values
FILL    }
"""


def cpp_totals(fams):
    body = ""
    if "sums" in fams:
        body += "        total.assign(2 * n, 0);\n        for (int i = 0; i < n; i++) total[n + i] = A[i];\n        for (int p = n - 1; p >= 1; p--) total[p] = total[2 * p] + total[2 * p + 1];\n"
    if "xor" in fams:
        body += "        xorTotal.assign(2 * n, 0);\n        for (int i = 0; i < n; i++) xorTotal[n + i] = A[i];\n        for (int p = n - 1; p >= 1; p--) xorTotal[p] = xorTotal[2 * p] ^ xorTotal[2 * p + 1];\n"
    return CPP_TOTALS.replace("FILL", body) + "\n" if body else ""


def py_totals(fams):
    s = ""
    if "sums" in fams:
        s += "        self.total = total = [0] * n + list(A)\n        for p in range(n - 1, 0, -1):\n            total[p] = total[2 * p] + total[2 * p + 1]\n"
    if "xor" in fams:
        s += "        self.xorTotal = xorTotal = [0] * n + list(A)\n        for p in range(n - 1, 0, -1):\n            xorTotal[p] = xorTotal[2 * p] ^ xorTotal[2 * p + 1]\n"
    return s


def cpp_total_fields(fams):
    return ("    vector<S> total;  // total[p]: sum of node p's values\n" if "sums" in fams else "") + \
           ("    vector<T> xorTotal;  // xorTotal[p]: xor of node p's values\n" if "xor" in fams else "")


CPP_SORTED_BUILD = """        vector<vector<T>> sortedVals(2 * n);  // node p's values, sorted (freed once its parent has them)
        for (int i = 0; i < n; i++) sortedVals[n + i] = {A[i]};
        for (int p = n - 1; p >= 1; p--) {
            vector<T>& left = sortedVals[2 * p];
            vector<T>& right = sortedVals[2 * p + 1];
            sortedVals[p].resize(left.size() + right.size());
            merge(left.begin(), left.end(), right.begin(), right.end(), sortedVals[p].begin());
            vector<T>().swap(left);
            vector<T>().swap(right);
            BUILD_NODE
        }
"""

PY_SORTED_BUILD = """        sortedVals = [None] * n + [[v] for v in A]  # node p's values, sorted (dropped once its parent has them)
        for p in range(n - 1, 0, -1):
            vals = sortedVals[2 * p] + sortedVals[2 * p + 1]
            vals.sort()  # (two sorted runs: timsort merges them in linear time)
            sortedVals[2 * p] = sortedVals[2 * p + 1] = None
            sortedVals[p] = vals
            BUILD_NODE
"""

# ------------------------------------------------------------------------------------------------ sortedlist inner

SL_CPP_FIELDS = """    static constexpr int LOAD = 256;  // buckets hold LOAD to 2 * LOAD values
    vector<vector<vector<T>>> buckets;  // buckets[p]: node p's values sorted, cut into buckets
    vector<vector<T>> maxes;  // maxes[p][b]: the last value of node p's bucket b
    vector<vector<int>> sizes;  // sizes[p]: Fenwick tree over node p's bucket sizes (1-indexed)
"""

SL_CPP_METHODS = """    void reindex(int p) {  // maxes and the size Fenwick tree of node p, from its buckets
        const auto& bs = buckets[p];
        int count = (int)bs.size();
        maxes[p].resize(count);
        sizes[p].assign(count + 1, 0);
        for (int j = 1; j <= count; j++) {
            maxes[p][j - 1] = bs[j - 1].back();
            sizes[p][j] += (int)bs[j - 1].size();
            int up = j + (j & -j);
            if (up <= count) sizes[p][up] += sizes[p][j];
        }
    }

    int before(int p, int b) const {  // # of node p's values in its buckets 0 .. b - 1
        int res = 0;
        for (int j = b; j > 0; j &= j - 1) res += sizes[p][j];
        return res;
    }

    void bump(int p, int b, int delta) {
        int count = (int)sizes[p].size() - 1;
        for (int j = b + 1; j <= count; j += j & -j) sizes[p][j] += delta;
    }

    long long countBelow(int p, T x, bool strict) const {
        const auto& m = maxes[p];
        int b = int((strict ? lower_bound(m.begin(), m.end(), x) : upper_bound(m.begin(), m.end(), x)) - m.begin());
        if (b == (int)m.size()) return before(p, b);
        const auto& bucket = buckets[p][b];
        auto it = strict ? lower_bound(bucket.begin(), bucket.end(), x) : upper_bound(bucket.begin(), bucket.end(), x);
        return before(p, b) + int(it - bucket.begin());
    }

    optional<T> firstIn(int p, T x, bool strict) const {  // smallest value > x (strict) or >= x in node p
        const auto& m = maxes[p];
        int b = int((strict ? upper_bound(m.begin(), m.end(), x) : lower_bound(m.begin(), m.end(), x)) - m.begin());
        if (b == (int)m.size()) return nullopt;
        const auto& bucket = buckets[p][b];
        return *(strict ? upper_bound(bucket.begin(), bucket.end(), x) : lower_bound(bucket.begin(), bucket.end(), x));
    }

    optional<T> lastIn(int p, T x, bool strict) const {  // largest value < x (strict) or <= x in node p
        const auto& m = maxes[p];
        int b = int((strict ? lower_bound(m.begin(), m.end(), x) : upper_bound(m.begin(), m.end(), x)) - m.begin());
        if (b < (int)m.size()) {
            const auto& bucket = buckets[p][b];
            auto it = strict ? lower_bound(bucket.begin(), bucket.end(), x) : upper_bound(bucket.begin(), bucket.end(), x);
            if (it != bucket.begin()) return *prev(it);
        }
        if (b == 0) return nullopt;
        return buckets[p][b - 1].back();
    }

    void insertValue(int p, T v) {
        auto& bs = buckets[p];
        const auto& m = maxes[p];
        int b = int(lower_bound(m.begin(), m.end(), v) - m.begin());
        if (b == (int)bs.size()) b--;
        vector<T>& bucket = bs[b];
        bucket.insert(upper_bound(bucket.begin(), bucket.end(), v), v);
        if ((int)bucket.size() > 2 * LOAD) {  // split it in two
            vector<T> upper(bucket.begin() + LOAD, bucket.end());
            bucket.resize(LOAD);
            bs.insert(bs.begin() + b + 1, std::move(upper));
            reindex(p);
        } else {
            maxes[p][b] = bucket.back();
            bump(p, b, 1);
        }
    }

    void eraseValue(int p, T v) {  // v is in node p
        auto& bs = buckets[p];
        const auto& m = maxes[p];
        int b = int(lower_bound(m.begin(), m.end(), v) - m.begin());
        vector<T>& bucket = bs[b];
        bucket.erase(lower_bound(bucket.begin(), bucket.end(), v));
        if (bucket.empty()) {
            bs.erase(bs.begin() + b);
            reindex(p);
        } else {
            maxes[p][b] = bucket.back();
            bump(p, b, -1);
        }
    }
"""

SL_CPP_NODE = """auto& bs = buckets[p];
            for (size_t k = 0; k < sortedVals[p].size(); k += LOAD)
                bs.emplace_back(sortedVals[p].begin() + k, sortedVals[p].begin() + min(sortedVals[p].size(), k + LOAD));
            reindex(p);"""

SL_PY_METHODS = """    def _reindex(self, p):  # maxes and the size Fenwick tree of node p, from its buckets
        bs = self.buckets[p]
        self.maxes[p] = [b[-1] for b in bs]
        count = len(bs)
        f = [0] * (count + 1)
        for j in range(1, count + 1):
            f[j] += len(bs[j - 1])
            up = j + (j & -j)
            if up <= count:
                f[up] += f[j]
        self.sizes[p] = f

    def _before(self, p, b):  # number of node p's values in its buckets 0 .. b - 1
        f, res = self.sizes[p], 0
        while b:
            res += f[b]
            b &= b - 1
        return res

    def _countBelow(self, p, x, strict):
        m = self.maxes[p]
        b = bisect_left(m, x) if strict else bisect_right(m, x)
        if b == len(m):
            return self.nodeSize[p]
        bucket = self.buckets[p][b]
        return self._before(p, b) + (bisect_left(bucket, x) if strict else bisect_right(bucket, x))

    def _firstIn(self, p, x, strict):  # smallest value > x (strict) or >= x in node p
        m = self.maxes[p]
        b = bisect_right(m, x) if strict else bisect_left(m, x)
        if b == len(m):
            return None
        bucket = self.buckets[p][b]
        return bucket[bisect_right(bucket, x) if strict else bisect_left(bucket, x)]

    def _lastIn(self, p, x, strict):  # largest value < x (strict) or <= x in node p
        m = self.maxes[p]
        b = bisect_left(m, x) if strict else bisect_right(m, x)
        if b < len(m):
            bucket = self.buckets[p][b]
            k = bisect_left(bucket, x) if strict else bisect_right(bucket, x)
            if k:
                return bucket[k - 1]
        return self.buckets[p][b - 1][-1] if b else None

    def _insert(self, p, v):
        bs, m = self.buckets[p], self.maxes[p]
        b = bisect_left(m, v)
        if b == len(bs):
            b -= 1
        bucket = bs[b]
        insort(bucket, v)
        if len(bucket) > 2 * self.LOAD:  # split it in two
            bs[b:b + 1] = [bucket[:self.LOAD], bucket[self.LOAD:]]
            self._reindex(p)
        else:
            m[b] = bucket[-1]
            f, j, count = self.sizes[p], b + 1, len(bs)
            while j <= count:
                f[j] += 1
                j += j & -j

    def _erase(self, p, v):  # v is in node p
        bs, m = self.buckets[p], self.maxes[p]
        b = bisect_left(m, v)
        bucket = bs[b]
        del bucket[bisect_left(bucket, v)]
        if not bucket:
            del bs[b]
            self._reindex(p)
        else:
            m[b] = bucket[-1]
            f, j, count = self.sizes[p], b + 1, len(bs)
            while j <= count:
                f[j] -= 1
                j += j & -j
"""

SL_PY_NODE = """self.buckets[p] = [vals[k:k + self.LOAD] for k in range(0, len(vals), self.LOAD)]
            self._reindex(p)"""

# ------------------------------------------------------------------------------------------------ treap inner

def treap_cpp(fams):
    sums, xors = "sums" in fams, "xor" in fams
    fields = """    vector<T> key;  // treap nodes, shared by every seg node (node 0 = the empty tree); a removed node isn't reused
    vector<int> copies, under, leftChild, rightChild;  // copies of the key, values in the subtree, children
    vector<unsigned> priority;
"""
    fields += ("    vector<S> subSum;  // sum of the subtree's values\n" if sums else "") + ("    vector<T> subXor;  // xor of the subtree's values\n" if xors else "")
    fields += "    vector<int> root;  // root[p]: node p's treap\n    unsigned long long rngState;\n"
    pull = "        under[t] = under[leftChild[t]] + under[rightChild[t]] + copies[t];\n"
    if sums:
        pull += "        subSum[t] = subSum[leftChild[t]] + subSum[rightChild[t]] + S(key[t]) * copies[t];\n"
    if xors:
        pull += "        subXor[t] = subXor[leftChild[t]] ^ subXor[rightChild[t]] ^ (copies[t] & 1 ? key[t] : T(0));\n"
    push_new = "        key.push_back(v);\n        copies.push_back(count);\n        under.push_back(0);\n        leftChild.push_back(0);\n        rightChild.push_back(0);\n        priority.push_back(nextRandom());\n"
    push_new += ("        subSum.push_back(0);\n" if sums else "") + ("        subXor.push_back(0);\n" if xors else "")
    init = "        key.assign(1, T(0));\n        copies.assign(1, 0);\n        under.assign(1, 0);\n        leftChild.assign(1, 0);\n        rightChild.assign(1, 0);\n        priority.assign(1, 0);\n"
    init += ("        subSum.assign(1, 0);\n" if sums else "") + ("        subXor.assign(1, 0);\n" if xors else "")
    init += "        root.assign(max(n, 1), 0);\n        rngState = chrono::steady_clock::now().time_since_epoch().count() | 1;\n"

    def walk(name, ret, field, op, leaf_value):
        return f"""    {ret} {name}(int p, T x, bool strict) const {{
        {ret} res = 0;
        for (int t = root[p]; t;) {{
            if (strict ? key[t] < x : !(x < key[t])) {{
                res {op}= {field}[leftChild[t]] {op} {leaf_value};
                t = rightChild[t];
            }} else {{
                t = leftChild[t];
            }}
        }}
        return res;
    }}

"""
    methods = f"""    unsigned nextRandom() {{
        rngState ^= rngState << 7;
        rngState ^= rngState >> 9;
        return unsigned(rngState);
    }}

    int newNode(T v, int count) {{
{push_new}        pull((int)key.size() - 1);
        return (int)key.size() - 1;
    }}

    void pull(int t) {{
{pull}    }}

    int buildTreap(const vector<T>& sortedVals) {{  // a treap of sortedVals (sorted) in O(len): a Cartesian tree by priority
        vector<int> stack;
        for (size_t k = 0; k < sortedVals.size();) {{
            size_t next = k;
            while (next < sortedVals.size() && !(sortedVals[k] < sortedVals[next])) next++;
            int t = newNode(sortedVals[k], int(next - k)), last = 0;
            k = next;
            while (!stack.empty() && priority[stack.back()] < priority[t]) {{
                last = stack.back();
                stack.pop_back();
            }}
            leftChild[t] = last;
            if (!stack.empty()) rightChild[stack.back()] = t;
            stack.push_back(t);
        }}
        if (stack.empty()) return 0;
        pullAll(stack[0]);
        return stack[0];
    }}

    void pullAll(int t) {{  // (recursion depth = the treap's height, O(log n) expected)
        if (!t) return;
        pullAll(leftChild[t]);
        pullAll(rightChild[t]);
        pull(t);
    }}

    pair<int, int> split(int t, T v, bool orEqual) {{  // (keys < v, or <= v if orEqual; the rest)
        if (!t) return {{0, 0}};
        if (orEqual ? !(v < key[t]) : key[t] < v) {{
            auto [low, high] = split(rightChild[t], v, orEqual);
            rightChild[t] = low;
            pull(t);
            return {{t, high}};
        }}
        auto [low, high] = split(leftChild[t], v, orEqual);
        leftChild[t] = high;
        pull(t);
        return {{low, t}};
    }}

    int join(int a, int b) {{  // every key of a is below every key of b
        if (!a || !b) return a | b;
        if (priority[a] > priority[b]) {{
            rightChild[a] = join(rightChild[a], b);
            pull(a);
            return a;
        }}
        leftChild[b] = join(a, leftChild[b]);
        pull(b);
        return b;
    }}

    void insertValue(int p, T v) {{
        auto [low, rest] = split(root[p], v, false);
        auto [same, high] = split(rest, v, true);
        if (same) {{
            copies[same]++;
            pull(same);
        }} else {{
            same = newNode(v, 1);
        }}
        root[p] = join(join(low, same), high);
    }}

    void eraseValue(int p, T v) {{  // v is in node p
        auto [low, rest] = split(root[p], v, false);
        auto [same, high] = split(rest, v, true);
        if (--copies[same] == 0) same = 0;
        else pull(same);
        root[p] = join(join(low, same), high);
    }}

{walk("countBelow", "long long", "under", "+", "copies[t]")}"""
    if sums:
        methods += walk("sumBelow", "S", "subSum", "+", "S(key[t]) * copies[t]")
    if xors:
        methods += walk("xorBelow", "T", "subXor", "^", "(copies[t] & 1 ? key[t] : T(0))")
    methods += """    optional<T> firstIn(int p, T x, bool strict) const {  // smallest value > x (strict) or >= x in node p
        optional<T> best;
        for (int t = root[p]; t;) {
            if (strict ? x < key[t] : !(key[t] < x)) {
                best = key[t];
                t = leftChild[t];
            } else {
                t = rightChild[t];
            }
        }
        return best;
    }

    optional<T> lastIn(int p, T x, bool strict) const {  // largest value < x (strict) or <= x in node p
        optional<T> best;
        for (int t = root[p]; t;) {
            if (strict ? key[t] < x : !(x < key[t])) {
                best = key[t];
                t = rightChild[t];
            } else {
                t = leftChild[t];
            }
        }
        return best;
    }
"""
    return fields, init, "root[p] = buildTreap(sortedVals[p]);", methods


def treap_py(fams):
    sums, xors = "sums" in fams, "xor" in fams
    init = "        self.key, self.copies, self.under, self.leftChild, self.rightChild, self.priority = [0], [0], [0], [0], [0], [0]\n"
    init += ("        self.subSum = [0]\n" if sums else "") + ("        self.subXor = [0]\n" if xors else "")
    init += "        self.root = [0] * max(n, 1)\n"
    pull = "        L, R = self.leftChild[t], self.rightChild[t]\n        self.under[t] = self.under[L] + self.under[R] + self.copies[t]\n"
    if sums:
        pull += "        self.subSum[t] = self.subSum[L] + self.subSum[R] + self.key[t] * self.copies[t]\n"
    if xors:
        pull += "        self.subXor[t] = self.subXor[L] ^ self.subXor[R] ^ (self.key[t] if self.copies[t] & 1 else 0)\n"
    new = "        self.key.append(v)\n        self.copies.append(count)\n        self.under.append(0)\n        self.leftChild.append(0)\n        self.rightChild.append(0)\n        self.priority.append(random())\n"
    new += ("        self.subSum.append(0)\n" if sums else "") + ("        self.subXor.append(0)\n" if xors else "")

    def walk(name, field, op, value):
        return f"""    def {name}(self, p, x, strict):
        key, leftChild, rightChild, {field}, copies = self.key, self.leftChild, self.rightChild, self.{field}, self.copies
        res, t = 0, self.root[p]
        while t:
            k = key[t]
            if (k < x) if strict else (k <= x):
                res {op}= {field}[leftChild[t]] {op} {value}
                t = rightChild[t]
            else:
                t = leftChild[t]
        return res

"""
    methods = f"""    def _newNode(self, v, count):
{new}        t = len(self.key) - 1
        self._pull(t)
        return t

    def _pull(self, t):
{pull}
    def _buildTreap(self, vals):  # a treap of vals (sorted) in O(len): a Cartesian tree by priority
        stack, k, size = [], 0, len(vals)
        leftChild, rightChild, priority = self.leftChild, self.rightChild, self.priority
        while k < size:
            nxt = k
            while nxt < size and vals[nxt] == vals[k]:
                nxt += 1
            t, last = self._newNode(vals[k], nxt - k), 0
            k = nxt
            while stack and priority[stack[-1]] < priority[t]:
                last = stack.pop()
            leftChild[t] = last
            if stack:
                rightChild[stack[-1]] = t
            stack.append(t)
        order, todo = [], [stack[0]] if stack else []
        while todo:  # (pull children before parents)
            t = todo.pop()
            order.append(t)
            for c in (leftChild[t], rightChild[t]):
                if c:
                    todo.append(c)
        for t in reversed(order):
            self._pull(t)
        return stack[0] if stack else 0

    def _split(self, t, v, orEqual):  # (keys < v, or <= v if orEqual; the rest)
        if not t:
            return 0, 0
        k = self.key[t]
        if (k <= v) if orEqual else (k < v):
            low, high = self._split(self.rightChild[t], v, orEqual)
            self.rightChild[t] = low
            self._pull(t)
            return t, high
        low, high = self._split(self.leftChild[t], v, orEqual)
        self.leftChild[t] = high
        self._pull(t)
        return low, t

    def _join(self, a, b):  # every key of a is below every key of b
        if not a or not b:
            return a or b
        if self.priority[a] > self.priority[b]:
            self.rightChild[a] = self._join(self.rightChild[a], b)
            self._pull(a)
            return a
        self.leftChild[b] = self._join(a, self.leftChild[b])
        self._pull(b)
        return b

    def _insert(self, p, v):
        low, rest = self._split(self.root[p], v, False)
        same, high = self._split(rest, v, True)
        if same:
            self.copies[same] += 1
            self._pull(same)
        else:
            same = self._newNode(v, 1)
        self.root[p] = self._join(self._join(low, same), high)

    def _erase(self, p, v):  # v is in node p
        low, rest = self._split(self.root[p], v, False)
        same, high = self._split(rest, v, True)
        self.copies[same] -= 1
        if self.copies[same]:
            self._pull(same)
        else:
            same = 0
        self.root[p] = self._join(self._join(low, same), high)

{walk("_countBelow", "under", "+", "copies[t]")}"""
    if sums:
        methods += walk("_sumBelow", "subSum", "+", "k * copies[t]")
    if xors:
        methods += walk("_xorBelow", "subXor", "^", "(k if copies[t] & 1 else 0)")
    methods += """    def _firstIn(self, p, x, strict):  # smallest value > x (strict) or >= x in node p
        key, leftChild, rightChild = self.key, self.leftChild, self.rightChild
        best, t = None, self.root[p]
        while t:
            k = key[t]
            if (k > x) if strict else (k >= x):
                best = k
                t = leftChild[t]
            else:
                t = rightChild[t]
        return best

    def _lastIn(self, p, x, strict):  # largest value < x (strict) or <= x in node p
        key, leftChild, rightChild = self.key, self.leftChild, self.rightChild
        best, t = None, self.root[p]
        while t:
            k = key[t]
            if (k < x) if strict else (k <= x):
                best = k
                t = rightChild[t]
            else:
                t = leftChild[t]
        return best
"""
    return init, "self.root[p] = self._buildTreap(vals)", methods


# ------------------------------------------------------------------------------------------------ hashed Fenwick inner (C++)

def hashfen_cpp(fams):
    sums, xors = "sums" in fams, "xor" in fams
    fields = """    long long lo, hi, span;  // values live in [lo, hi]; span = hi - lo + 1 Fenwick slots per node
    // one open-addressing hash table for every node's Fenwick tree: key (node << 32) | slot
    vector<unsigned long long> slotKey;
    vector<int> slotCount;
"""
    fields += ("    vector<S> slotSum;\n" if sums else "") + ("    vector<T> slotXor;\n" if xors else "")
    fields += "    size_t used = 0;\n    unsigned long long seed;\n    vector<int> nodeSize;  // nodeSize[p]: how many positions node p covers\n"
    grow_copy = "                slotCount[at] = oldCount[k];\n" + ("                slotSum[at] = oldSum[k];\n" if sums else "") + ("                slotXor[at] = oldXor[k];\n" if xors else "")
    grow_save = "        vector<int> oldCount = std::move(slotCount);\n" + ("        vector<S> oldSum = std::move(slotSum);\n" if sums else "") + ("        vector<T> oldXor = std::move(slotXor);\n" if xors else "")
    grow_alloc = "        slotCount.assign(capacity, 0);\n" + ("        slotSum.assign(capacity, 0);\n" if sums else "") + ("        slotXor.assign(capacity, 0);\n" if xors else "")
    add_body = "            slotCount[at] += delta;\n" + ("            slotSum[at] += S(v) * delta;\n" if sums else "") + ("            slotXor[at] ^= v;\n" if xors else "")

    def prefix(name, ret, table, op):
        return f"""    {ret} {name}(int p, T x, bool strict) const {{  // over node p's values < x (strict) or <= x
        long long k = (long long)x - lo + (strict ? 0 : 1);
        if (k <= 0) return 0;
        if (k > span) k = span;
        {ret} res = 0;
        unsigned long long base = (unsigned long long)p << 32;
        for (long long j = k; j > 0; j &= j - 1) {{
            long long at = find(base | (unsigned long long)j);
            if (at >= 0) res {op}= {table}[at];
        }}
        return res;
    }}

"""
    methods = f"""    static unsigned long long mix(unsigned long long z) {{  // splitmix64
        z += 0x9e3779b97f4a7c15ULL;
        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
        z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
        return z ^ (z >> 31);
    }}

    long long find(unsigned long long k) const {{  // the slot holding key k, or -1
        size_t mask = slotKey.size() - 1, at = mix(k ^ seed) & mask;
        while (slotKey[at] != EMPTY) {{
            if (slotKey[at] == k) return (long long)at;
            at = (at + 1) & mask;
        }}
        return -1;
    }}

    size_t findOrAdd(unsigned long long k) {{
        if (2 * (used + 1) > slotKey.size()) grow();
        size_t mask = slotKey.size() - 1, at = mix(k ^ seed) & mask;
        while (slotKey[at] != EMPTY && slotKey[at] != k) at = (at + 1) & mask;
        if (slotKey[at] == EMPTY) {{
            slotKey[at] = k;
            used++;
        }}
        return at;
    }}

    void grow() {{
        size_t capacity = max<size_t>(1024, 2 * slotKey.size());
        vector<unsigned long long> oldKey = std::move(slotKey);
{grow_save}        slotKey.assign(capacity, EMPTY);
{grow_alloc}        size_t mask = capacity - 1;
        for (size_t k = 0; k < oldKey.size(); k++) {{
            if (oldKey[k] != EMPTY) {{
                size_t at = mix(oldKey[k] ^ seed) & mask;
                while (slotKey[at] != EMPTY) at = (at + 1) & mask;
                slotKey[at] = oldKey[k];
{grow_copy}            }}
        }}
    }}

    void add(int p, T v, int delta) {{  // delta copies of v into node p's Fenwick tree
        unsigned long long base = (unsigned long long)p << 32;
        for (long long j = (long long)v - lo + 1; j <= span; j += j & -j) {{
            size_t at = findOrAdd(base | (unsigned long long)j);
{add_body}        }}
    }}

    void insertValue(int p, T v) {{ add(p, v, 1); }}

    void eraseValue(int p, T v) {{ add(p, v, -1); }}

{prefix("countBelow", "long long", "slotCount", "+")}"""
    if sums:
        methods += prefix("sumBelow", "S", "slotSum", "+")
    if xors:
        methods += prefix("xorBelow", "T", "slotXor", "^")
    methods += """    T kth(int p, long long k) const {  // node p's k-th smallest value (1-indexed; 1 <= k <= nodeSize[p])
        unsigned long long base = (unsigned long long)p << 32;
        long long pos = 0, step = 1;
        while (step * 2 <= span) step *= 2;
        for (; step; step >>= 1) {
            if (pos + step > span) continue;
            long long at = find(base | (unsigned long long)(pos + step));
            int here = at >= 0 ? slotCount[at] : 0;
            if (here < k) {
                pos += step;
                k -= here;
            }
        }
        return T(lo + pos);
    }

    optional<T> firstIn(int p, T x, bool strict) const {  // smallest value > x (strict) or >= x in node p
        long long below = countBelow(p, x, !strict);
        if (below >= nodeSize[p]) return nullopt;
        return kth(p, below + 1);
    }

    optional<T> lastIn(int p, T x, bool strict) const {  // largest value < x (strict) or <= x in node p
        long long below = countBelow(p, x, strict);
        if (below == 0) return nullopt;
        return kth(p, below);
    }
"""
    init = """        if (valLo > valHi || (long long)valHi - (long long)valLo >= (1LL << 32) - 1)
            throw out_of_range("MergeSortTreeUpdates: needs valLo <= valHi and valHi - valLo < 2^32 - 1");
        lo = valLo, hi = valHi, span = hi - lo + 1;
        for (int i = 0; i < n; i++)
            if ((long long)A[i] < lo || (long long)A[i] > hi) throw out_of_range("MergeSortTreeUpdates: every a[i] must be in [valLo, valHi]");
        seed = mix(chrono::steady_clock::now().time_since_epoch().count());
        nodeSize.assign(2 * n, 1);
        for (int p = n - 1; p >= 1; p--) nodeSize[p] = nodeSize[2 * p] + nodeSize[2 * p + 1];
        for (int i = 0; i < n; i++)
            for (int p = (i + n) >> 1; p >= 1; p >>= 1) add(p, A[i], 1);
"""
    return fields, init, methods


# ------------------------------------------------------------------------------------------------ offline inner

def offline_cpp(fams):
    sums, xors = "sums" in fams, "xor" in fams
    fields = """    vector<int> start;  // node p's possible values are vals[start[p] .. start[p + 1]); its Fenwick slots 1 .. size sit at
                        // fenStart(p) + 1 .. fenStart(p) + size
    vector<T> vals;
    vector<int> counts;  // Fenwick trees of copies, one per node
"""
    fields += ("    vector<S> sums;  // Fenwick trees of sums\n" if sums else "") + ("    vector<T> xors;  // Fenwick trees of xors\n" if xors else "")
    fields += "    vector<int> nodeSize;  // nodeSize[p]: how many positions node p covers\n"
    raw = "                counts[f + j + 1] = c;\n" + ("                sums[f + j + 1] = S(v) * c;\n" if sums else "") + ("                xors[f + j + 1] = c & 1 ? v : T(0);\n" if xors else "")
    fen_build = "                    counts[f + up] += counts[f + j];\n" + ("                    sums[f + up] += sums[f + j];\n" if sums else "") + ("                    xors[f + up] ^= xors[f + j];\n" if xors else "")
    alloc = "        counts.assign(slots, 0);\n" + ("        sums.assign(slots, 0);\n" if sums else "") + ("        xors.assign(slots, 0);\n" if xors else "")
    init = f"""        vector<vector<T>> possible(2 * n);  // node p's possible values, sorted, distinct
        vector<vector<int>> copiesNow(2 * n);  // and how many positions under p hold each right now
        for (int i = 0; i < n; i++) possible[n + i] = {{A[i]}};
        for (const auto& [i, v] : updates) {{
            if (i < 0 || i >= n) throw out_of_range("MergeSortTreeOffline: every listed update needs 0 <= i < n");
            possible[n + i].push_back(v);
        }}
        for (int i = 0; i < n; i++) {{
            vector<T>& here = possible[n + i];
            sort(here.begin(), here.end());
            here.erase(unique(here.begin(), here.end()), here.end());
            copiesNow[n + i].assign(here.size(), 0);
            copiesNow[n + i][lower_bound(here.begin(), here.end(), A[i]) - here.begin()] = 1;
        }}
        nodeSize.assign(2 * n, 1);
        for (int p = n - 1; p >= 1; p--) {{  // merge the children's lists, adding up the copies
            nodeSize[p] = nodeSize[2 * p] + nodeSize[2 * p + 1];
            const vector<T>& a = possible[2 * p];
            const vector<T>& b = possible[2 * p + 1];
            const vector<int>& ca = copiesNow[2 * p];
            const vector<int>& cb = copiesNow[2 * p + 1];
            size_t x = 0, y = 0;
            while (x < a.size() || y < b.size()) {{
                if (y == b.size() || (x < a.size() && a[x] < b[y])) {{
                    possible[p].push_back(a[x]), copiesNow[p].push_back(ca[x++]);
                }} else if (x == a.size() || b[y] < a[x]) {{
                    possible[p].push_back(b[y]), copiesNow[p].push_back(cb[y++]);
                }} else {{
                    possible[p].push_back(a[x]), copiesNow[p].push_back(ca[x++] + cb[y++]);
                }}
            }}
            if (2 * p >= n) vector<T>().swap(possible[2 * p]), vector<int>().swap(copiesNow[2 * p]);
            if (2 * p + 1 >= n) vector<T>().swap(possible[2 * p + 1]), vector<int>().swap(copiesNow[2 * p + 1]);
        }}
        start.assign(n + 1, 0);
        for (int p = 1; p < n; p++) start[p + 1] = start[p] + (int)possible[p].size();
        vals.resize(start[n]);
        size_t slots = (size_t)start[n] + n;
{alloc}        for (int p = 1; p < n; p++) {{
            int size = (int)possible[p].size(), f = fenStart(p);
            for (int j = 0; j < size; j++) {{
                T v = possible[p][j];
                int c = copiesNow[p][j];
                vals[start[p] + j] = v;
{raw}            }}
            for (int j = 1; j <= size; j++) {{  // (each slot into the Fenwick tree in O(1))
                int up = j + (j & -j);
                if (up <= size) {{
{fen_build}                }}
            }}
            vector<T>().swap(possible[p]);
            vector<int>().swap(copiesNow[p]);
        }}
"""

    def prefix(name, ret, table, op):
        return f"""    {ret} {name}(int p, T x, bool strict) const {{  // over node p's values < x (strict) or <= x
        {ret} res = 0;
        int f = fenStart(p);
        for (int j = slotOf(p, x, strict); j > 0; j &= j - 1) res {op}= {table}[f + j];
        return res;
    }}

"""
    move_body = "        counts[f + j] += delta;\n" + ("        sums[f + j] += S(v) * delta;\n" if sums else "") + ("        xors[f + j] ^= v;\n" if xors else "")
    methods = f"""    int fenStart(int p) const {{ return start[p] + p - 1; }}

    int slotOf(int p, T x, bool strict) const {{  // # of node p's possible values < x (strict) or <= x
        auto first = vals.begin() + start[p], last = vals.begin() + start[p + 1];
        return int((strict ? lower_bound(first, last, x) : upper_bound(first, last, x)) - first);
    }}

    bool listed(int p, T v) const {{
        auto first = vals.begin() + start[p], last = vals.begin() + start[p + 1];
        auto it = lower_bound(first, last, v);
        return it != last && !(v < *it);
    }}

    void add(int p, T v, int delta) {{
        int f = fenStart(p), size = start[p + 1] - start[p];
        for (int j = slotOf(p, v, true) + 1; j <= size; j += j & -j) addAt(f, j, v, delta);
    }}

    void addAt(int f, int j, [[maybe_unused]] T v, int delta) {{
{move_body}    }}

{prefix("countBelow", "long long", "counts", "+")}"""
    if sums:
        methods += prefix("sumBelow", "S", "sums", "+")
    if xors:
        methods += prefix("xorBelow", "T", "xors", "^")
    methods += """    T kth(int p, long long k) const {  // node p's k-th smallest value (1-indexed; 1 <= k <= nodeSize[p])
        int f = fenStart(p), size = start[p + 1] - start[p], pos = 0, step = 1;
        while (step * 2 <= size) step *= 2;
        for (; step; step >>= 1) {
            if (pos + step <= size && counts[f + pos + step] < k) {
                pos += step;
                k -= counts[f + pos];
            }
        }
        return vals[start[p] + pos];
    }

    optional<T> firstIn(int p, T x, bool strict) const {  // smallest value > x (strict) or >= x in node p
        long long below = countBelow(p, x, !strict);
        if (below >= nodeSize[p]) return nullopt;
        return kth(p, below + 1);
    }

    optional<T> lastIn(int p, T x, bool strict) const {  // largest value < x (strict) or <= x in node p
        long long below = countBelow(p, x, strict);
        if (below == 0) return nullopt;
        return kth(p, below);
    }
"""
    return fields, init, methods


def offline_py(fams):
    sums, xors = "sums" in fams, "xor" in fams
    init = """        possible = [None] * n + [[v] for v in A]  # node p's possible values, sorted, distinct
        for i, v in updates:
            if i < 0 or i >= n:
                raise IndexError(f"MergeSortTreeOffline: every listed update needs 0 <= i < n, got i={i}, n={n}")
            possible[n + i].append(v)
        copiesNow = [None] * (2 * n)  # and how many positions under p hold each right now
        for i in range(n):
            here = sorted(set(possible[n + i]))
            possible[n + i] = here
            row = [0] * len(here)
            row[bisect_left(here, A[i])] = 1
            copiesNow[n + i] = row
        self.nodeSize = nodeSize = [1] * (2 * n)
        self.vals, self.counts = [None] * n, [None] * n
"""
    init += ("        self.sums = [None] * n\n" if sums else "") + ("        self.xors = [None] * n\n" if xors else "")
    init += """        for p in range(n - 1, 0, -1):
            nodeSize[p] = nodeSize[2 * p] + nodeSize[2 * p + 1]
            merged = {}
            for side in (2 * p, 2 * p + 1):
                for v, c in zip(possible[side], copiesNow[side]):
                    merged[v] = merged.get(v, 0) + c
            vals = sorted(merged)
            row = [merged[v] for v in vals]
            possible[p], copiesNow[p] = vals, row
            if 2 * p >= n:
                possible[2 * p] = copiesNow[2 * p] = None
            if 2 * p + 1 >= n:
                possible[2 * p + 1] = copiesNow[2 * p + 1] = None
            size = len(vals)
            self.vals[p] = vals
            self.counts[p] = self._fenwick([0] + row, size, False)
"""
    if sums:
        init += "            self.sums[p] = self._fenwick([0] + [v * c for v, c in zip(vals, row)], size, False)\n"
    if xors:
        init += "            self.xors[p] = self._fenwick([0] + [v if c & 1 else 0 for v, c in zip(vals, row)], size, True)\n"
    init += "        for p in range(1, n):\n            if 2 * p < n:\n                possible[2 * p] = copiesNow[2 * p] = None\n"

    def prefix(name, table, op):
        return f"""    def {name}(self, p, x, strict):  # over node p's values < x (strict) or <= x
        f, res = self.{table}[p], 0
        j = bisect_left(self.vals[p], x) if strict else bisect_right(self.vals[p], x)
        while j:
            res {op}= f[j]
            j &= j - 1
        return res

"""
    add_parts = "        counts = self.counts[p]\n" + ("        sums = self.sums[p]\n" if sums else "") + ("        xors = self.xors[p]\n" if xors else "")
    add_loop = "            counts[j] += delta\n" + ("            sums[j] += v * delta\n" if sums else "") + ("            xors[j] ^= v\n" if xors else "")
    methods = f"""    @staticmethod
    def _fenwick(f, size, isXor):  # f[1..size] raw values -> a Fenwick tree in O(size)
        for j in range(1, size + 1):
            up = j + (j & -j)
            if up <= size:
                if isXor:
                    f[up] ^= f[j]
                else:
                    f[up] += f[j]
        return f

    def _listed(self, p, v):
        vals = self.vals[p]
        k = bisect_left(vals, v)
        return k < len(vals) and vals[k] == v

    def _add(self, p, v, delta):
{add_parts}        size = len(self.vals[p])
        j = bisect_left(self.vals[p], v) + 1
        while j <= size:
{add_loop}            j += j & -j

{prefix("_countBelow", "counts", "+")}"""
    if sums:
        methods += prefix("_sumBelow", "sums", "+")
    if xors:
        methods += prefix("_xorBelow", "xors", "^")
    methods += """    def _kth(self, p, k):  # node p's k-th smallest value (1-indexed; 1 <= k <= nodeSize[p])
        f, size, pos = self.counts[p], len(self.vals[p]), 0
        step = 1 << (size.bit_length() - 1) if size else 0
        while step:
            if pos + step <= size and f[pos + step] < k:
                pos += step
                k -= f[pos]
            step >>= 1
        return self.vals[p][pos]

    def _firstIn(self, p, x, strict):  # smallest value > x (strict) or >= x in node p
        below = self._countBelow(p, x, not strict)
        return None if below >= self.nodeSize[p] else self._kth(p, below + 1)

    def _lastIn(self, p, x, strict):  # largest value < x (strict) or <= x in node p
        below = self._countBelow(p, x, strict)
        return self._kth(p, below) if below else None
"""
    return init, methods


# ------------------------------------------------------------------------------------------------ assembling

def header(c, ops, costs, memory, note, offline):
    lines = [f"@operations: {' '.join(sorted(ops))}", "@data-structure-type: merge-sort-tree", "@fractional-cascading: no"]
    if offline:
        lines.append("@values: offline")
    lines += ["@complexities:"] + [f"  {op}: {costs[op]}" for op in sorted(ops)] + [f"  build: {costs['build']}", "@memory:", "  layout: none"]
    lines += [f"  {k}: {memory[k]}" for k in ("node", "tags", "other")] + [f"  note: {note}"]
    return "\n".join(f"{c} {x}" for x in lines) + "\n"


def write_folder(folder, py, cpp, ops, costs, memory, note, offline, about):
    path = os.path.join(DIR, folder)
    os.makedirs(path, exist_ok=True)
    for name, text, c in (("template.py", py, "#"), ("template.cpp", cpp, "//")):
        if text is None:
            continue
        top = f"{c} Template by https://github.com/ishaanbuildsthings\n{c} {URL}/{folder}/{name}\n"
        if c == "//":
            top += "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n"
        top += header(c, ops, costs, memory, note, offline) + "\n" + "".join(f"{c} {x}\n" for x in about)
        with open(os.path.join(path, name), "w") as f:
            f.write(top + "\n" + text if c == "#" else top + text)


ABOUT = ["Merge sort tree with point updates: a segment tree over positions (bottom-up: node p >= n is a[p - n]), each",
         "inner node keeping its positions' values in a searchable structure ({inner}). a[l..r] is O(log n) nodes, and a",
         "point update changes one value in each of the O(log n) nodes above it. All indices 0-based, ranges inclusive."]
INNER_TEXT = {"sortedlist": "sorted buckets of 256 to 512 values, with a Fenwick tree over the bucket sizes",
              "treap": "a treap keyed by value, copies counted, with subtree sizes / sums / xors",
              "hashfenwick": "a Fenwick tree over the whole value range [valLo, valHi], stored sparsely in one hash table",
              "offline": "the sorted values its positions can ever hold, with Fenwick trees over them"}


def build(inner, fams):
    all_fams = ("count", "near") + fams
    folder = "merge-sort-tree-updates-" + inner + "".join(f"-{f}" for f in fams)
    offline, ranged = inner == "offline", inner == "hashfenwick"
    points = OFFLINE_POINT if offline else ONLINE_POINT
    ops = points + ["getAll"] + [op for f in all_fams for op in FAM_OPS[f]]
    query = {"sortedlist": "log^2(N)", "treap": "log^2(N) expected", "hashfenwick": "log(N)*log(U)", "offline": "log^2(N)"}[inner]
    update = {"sortedlist": "log^2(N) amortized", "treap": "log^2(N) expected", "hashfenwick": "log(N)*log(U)", "offline": "log^2(N)"}[inner]
    costs = {op: query for f in all_fams for op in FAM_OPS[f]}
    costs.update({op: update for op in points if op != "pointGet"})
    costs.update({"pointGet": "1", "getAll": "N", "build": "N*log(N)*log(U)" if ranged else "N*log(N)"})
    if inner == "sortedlist":
        node = ["vals[1*N*log(N)]"]
    elif inner == "treap":
        node = [f"{a}[1*N*log(N)]" for a in ("key", "copies", "under", "leftChild", "rightChild", "priority")]
        node += ["subSum[1*N*log(N)]"] * ("sums" in fams) + ["subXor[1*N*log(N)]"] * ("xor" in fams)
    elif ranged:
        node = ["slotKey[2*N*log(N)*log(U)]", "slotCount[2*N*log(N)*log(U)]"]
        node += ["slotSum[2*N*log(N)*log(U)]"] * ("sums" in fams) + ["slotXor[2*N*log(N)*log(U)]"] * ("xor" in fams)
    else:
        node = ["vals[1*N*log(N)]", "counts[1*N*log(N)]"]
        node += ["sums[1*N*log(N)]"] * ("sums" in fams) + ["xors[1*N*log(N)]"] * ("xor" in fams)
    other = ["A[1*N]"] + (["total[2*N]"] if "sums" in fams else []) + (["xorTotal[2*N]"] if "xor" in fams else [])
    other += {"treap": ["root[1*N]"], "hashfenwick": ["nodeSize[2*N]"], "offline": ["start[1*N]", "nodeSize[2*N]"]}.get(inner, [])
    memory = {"node": " ".join(node), "tags": "none", "other": " ".join(other)}
    note = {"sortedlist": "no value range and nothing up front; buckets hold 256 to 512 values, so an update also moves up to 512 values in each of its log N nodes",
            "treap": "no value range and nothing up front; each update makes at most log N new treap nodes and none are reused, so N counts updates too",
            "hashfenwick": "every value must stay in [valLo, valHi] (U = its size); the hash table is kept at most half full, and N counts updates too (each adds up to log N log U keys)",
            "offline": "the constructor takes every (i, v) a pointAssign will ever use, so N is the array length plus that list's length; worst-case bounds and flat arrays, the fastest of these"}[inner]
    about = [x.replace("{inner}", INNER_TEXT[inner]) for x in ABOUT]
    if offline:
        about += ["Offline: the constructor takes every (i, v) that a pointAssign will ever use (read every query first). For adds",
                  "or chmax / chmin, work out the new value yourself and list that."]
    if ranged:
        about += ["Every value a[i] ever holds must be in [valLo, valHi]; query arguments can be anything."]
    if inner == "sortedlist":
        about += ["Counts and nearest values only: sums and xors need the treap or offline versions."]
    about.append("T: int, long long, ...; sums are kept in S (long long for small T).")
    cpp = cpp_file(inner, fams, query, update)
    py = None if ranged else py_file(inner, fams, query, update)
    write_folder(folder, py, cpp, ops, costs, memory, note, offline, about)
    return folder


def cpp_file(inner, fams, query, update):
    name = "MergeSortTreeOffline" if inner == "offline" else "MergeSortTreeUpdates"
    s = f"template <typename T>\nstruct {name} {{\n    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n"
    if inner == "hashfenwick":
        s += "    static constexpr unsigned long long EMPTY = ~0ULL;\n"
    s += "    int n;\n    vector<T> A;\n" + cpp_total_fields(fams)
    if inner == "sortedlist":
        fields, init, node, methods = SL_CPP_FIELDS, "        buckets.resize(max(n, 1));\n        maxes.resize(max(n, 1));\n        sizes.resize(max(n, 1));\n", SL_CPP_NODE, SL_CPP_METHODS
    elif inner == "treap":
        fields, init, node, methods = treap_cpp(fams)
    elif inner == "hashfenwick":
        fields, init, methods = hashfen_cpp(fams)
    else:
        fields, init, methods = offline_cpp(fams)
    s += fields + "\n"
    if inner == "offline":
        s += f"    // O(build) -- arr: the initial array. updates: every (i, v) that pointAssign will ever be called with (any order,\n"
        s += f"    // repeats fine); a pointAssign with a pair not listed throws invalid_argument\n"
        s += f"    {name}(const vector<T>& arr, const vector<pair<int, T>>& updates) {{\n        n = (int)arr.size();\n        A = arr;\n"
    elif inner == "hashfenwick":
        s += "    // O(build) -- arr: the initial array. Every value a[i] ever holds must be in [valLo, valHi]\n"
        s += f"    {name}(const vector<T>& arr, T valLo, T valHi) {{\n        n = (int)arr.size();\n        A = arr;\n"
    else:
        s += "    // O(build) -- arr: the initial array\n"
        s += f"    explicit {name}(const vector<T>& arr) {{\n        n = (int)arr.size();\n        A = arr;\n"
    s += init
    if inner in ("sortedlist", "treap"):
        s += CPP_SORTED_BUILD.replace("BUILD_NODE", node)
    if fams:
        s += "        buildTotals();\n"
    s += "    }\n\n"
    s += "    // O(n) -- the whole array\n    vector<T> getAll() const { return vector<T>(A.begin(), A.end()); }\n\n"
    if inner == "offline":
        s += '    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range\n    T pointGet(int i) const {\n        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");\n        return A[i];\n    }\n\n'
        s += f"    // O({update}) -- a[i] = v (overwrite); needs 0 <= i < n, else throws out_of_range, and (i, v) listed in the\n"
        s += "    // constructor's updates (or v == a[i]), else throws invalid_argument\n"
        s += """    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        T old = A[i];
        if (old == v) return;
        if (n > 1 && !listed((i + n) >> 1, v)) throw invalid_argument("pointAssign: (i, v) was not in the constructor's updates");
        for (int p = (i + n) >> 1; p >= 1; p >>= 1) {
            add(p, old, -1);
            add(p, v, 1);
"""
        s += ("            total[p] += S(v) - S(old);\n" if "sums" in fams else "") + ("            xorTotal[p] ^= old ^ v;\n" if "xor" in fams else "")
        s += "        }\n        A[i] = v;\n    }\n\n"
    else:
        s += cpp_online_points(update, inner == "hashfenwick")
    s += cpp_query_ops(("count", "near") + fams, query)
    s += "    // ---- internals ----\n\n" + cpp_totals(fams) + cpp_range_helpers(fams)
    if inner != "offline":
        s += cpp_write(fams, inner == "hashfenwick")
    s += methods + "};\n"
    if inner == "offline":
        s += """
// Example:
//     vector<long long> a = {5, 1, 4};
//     MergeSortTreeOffline<long long> t(a, {{1, 7}, {0, 2}});  // later: pointAssign(1, 7) and pointAssign(0, 2)
//     t.countLtX(0, 2, 5);  // 2 (1 and 4)
//     t.pointAssign(1, 7);
//     t.countLtX(0, 2, 5);  // 1 (4)
"""
    return s


def py_file(inner, fams, query, update):
    name = "MergeSortTreeOffline" if inner == "offline" else "MergeSortTreeUpdates"
    imports = "from bisect import bisect_left, bisect_right" + (", insort" if inner == "sortedlist" else "") + "\n"
    if inner == "treap":
        imports += "from random import random\n"
    s = imports + "\n\nclass " + name + ":\n"
    if inner == "sortedlist":
        s += "    LOAD = 256  # buckets hold LOAD to 2 * LOAD values\n\n"
    if inner == "offline":
        s += "    # O(build) -- arr: the initial array. updates: every (i, v) that pointAssign will ever be called with (any order,\n"
        s += "    # repeats fine); a pointAssign with a pair not listed raises ValueError\n"
        s += "    def __init__(self, arr, updates):\n"
    else:
        s += "    # O(build) -- arr: the initial array\n    def __init__(self, arr):\n"
    s += "        self.A = A = list(arr)\n        self.n = n = len(A)\n"
    if inner == "offline":
        init, methods = offline_py(fams)
        s += init
    else:
        s += "        self.nodeSize = nodeSize = [1] * (2 * n)\n        for p in range(n - 1, 0, -1):\n            nodeSize[p] = nodeSize[2 * p] + nodeSize[2 * p + 1]\n"
        if inner == "sortedlist":
            s += "        self.buckets, self.maxes, self.sizes = [None] * n, [None] * n, [None] * n\n"
            s += PY_SORTED_BUILD.replace("BUILD_NODE", SL_PY_NODE)
            methods = SL_PY_METHODS
        else:
            init, node, methods = treap_py(fams)
            s += init + PY_SORTED_BUILD.replace("BUILD_NODE", node)
    s += py_totals(fams) + "\n"
    s += "    # O(n) -- the whole array\n    def getAll(self):\n        return list(self.A)\n\n"
    if inner == "offline":
        s += '    # O(1) -- a[i]; needs 0 <= i < n, else raises IndexError\n    def pointGet(self, i):\n        if i < 0 or i >= self.n:\n            raise IndexError(f"pointGet: needs 0 <= i < n, got i={i}, n={self.n}")\n        return self.A[i]\n\n'
        s += f"    # O({update}) -- a[i] = v (overwrite); needs 0 <= i < n, else raises IndexError, and (i, v) listed in the\n"
        s += "    # constructor's updates (or v == a[i]), else raises ValueError\n"
        s += """    def pointAssign(self, i, v):
        n = self.n
        if i < 0 or i >= n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i={i}, n={n}")
        old = self.A[i]
        if old == v:
            return
        if n > 1 and not self._listed((i + n) >> 1, v):
            raise ValueError(f"pointAssign: ({i}, {v}) was not in the constructor's updates")
        p = (i + n) >> 1
        while p:
            self._add(p, old, -1)
            self._add(p, v, 1)
"""
        s += ("            self.total[p] += v - old\n" if "sums" in fams else "") + ("            self.xorTotal[p] ^= old ^ v\n" if "xor" in fams else "")
        s += "            p >>= 1\n        self.A[i] = v\n\n"
    else:
        s += py_online_points(update, False)
    s += py_query_ops(("count", "near") + fams, query)
    s += "    # ---- internals ----\n\n" + py_range_helpers(fams)
    if inner != "offline":
        s += py_write(fams)
    s += methods
    return s.rstrip() + "\n"


def main():
    folders = [build(inner, fams) for inner, variants in INNERS.items() for fams in variants]
    print(f"{len(folders)} merge sort trees with updates in {DIR}")


if __name__ == "__main__":
    main()
