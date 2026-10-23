"""Sparse versions of the static (no update) templates: sparse.py + sparse.cpp per folder.

    python3 sparse_static.py

A static template can't start all zeros (nothing would ever change), so its sparse version is built from a list of
given values (index, value pairs, distinct indices) over any index range [lo, hi]; every other index is 0. N is the number of
given values. Each file embeds the dense class unchanged and wraps it:
  - max / min / and / or / gcd / LIS: the dense class runs on a compressed array where every maximal gap of zeros
    is one 0 (a run of zeros adds nothing more to any of these);
  - counts, sums, k-th, mode, distinct: the dense class runs on the given values alone, and the zeros of [l, r] (its
    length minus the given values inside) are added in closed form;
  - the costMono family is written fresh: it needs every piece's length, not just its value.
"""
import os

from note_lang import strip_attribution, write_template
import re

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
HEADER_LINE = re.compile(r"^(#|//) (@|  )")


def header(cm, ops, dtype, comp, mem, note):
    lines = [f"{cm} @operations: {' '.join(ops)}", f"{cm} @data-structure-type: {dtype}"]
    if dtype == "merge-sort-tree":
        lines.append(f"{cm} @fractional-cascading: yes")  # every merge sort tree here walks prefix counts down from one root search
    lines.append(f"{cm} @complexities:")
    lines += [f"{cm}   {o}: {comp[o]}" for o in ops] + [f"{cm}   build: {comp['build']}"]
    node, tags, other = mem
    lines += [f"{cm} @memory:", f"{cm}   layout: sparse", f"{cm}   node: {node}", f"{cm}   tags: {tags}",
              f"{cm}   other: {other}",
              f"{cm}   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; {note}"]
    return "\n".join(lines) + "\n"


def dense_body(folder, ext):
    """The dense template file without its @ header."""
    lines = strip_attribution(open(os.path.join(DIR, folder, f"template.{ext}")).read()).split("\n")
    k = 0
    while k < len(lines) and HEADER_LINE.match(lines[k]):
        k += 1
    return "\n".join(lines[k:]).strip("\n") + "\n"


def write(folder, dtype, comp, mem, note, py, cpp):
    ops = folder.split("-")
    path = os.path.join(DIR, folder)
    assert os.path.isdir(path), folder
    write_template(os.path.join(path, "sparse.py"), header("#", ops, dtype, comp, mem, note) + py)
    write_template(os.path.join(path, "sparse.cpp"), header("//", ops, dtype, comp, mem, note) + cpp)
    print("wrote", folder)


SPARSE_NOTE_PY = '''
# ======================================================================================== sparse wrapper

from bisect import bisect_left, bisect_right

'''
SPARSE_NOTE_CPP = '''
// ======================================================================================== sparse wrapper
'''

PY_POINT_GET = '''
    # O(logN) -- a[i]
    def pointGet(self, i):
        k = bisect_left(self.idx, i)
        return self.vals[k] if k < len(self.idx) and self.idx[k] == i else 0
'''
CPP_POINT_GET = '''
    // O(logN) -- a[i]
    T pointGet(long long i) const {
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }
'''

# ------------------------------------------------------------------------------------------------ compressed-array wrappers


def compressed(folder, inner, name, op, what, comp, mem, note, rtype="T"):
    py = dense_body(folder, "py") + SPARSE_NOTE_PY + f'''
# {what} over any index range [lo, hi], built from given values (index, value pairs); every other index is 0. A maximal gap
# of zeros adds nothing more than a single 0, so {inner} runs on the compressed array of given values with one 0 per gap,
# and a query maps l and r to the compressed elements containing them.


class {name}:
    __slots__ = ("lo", "hi", "idx", "vals", "starts", "inner")

    # O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    def __init__(self, lo, hi, values):
        self.lo, self.hi = lo, hi
        pts = sorted(values)
        self.idx = [i for i, _ in pts]
        self.vals = [v for _, v in pts]
        starts, arr = [], []  # starts[k] = first index of compressed element k
        prev = lo - 1
        for i, v in pts:
            if i > prev + 1:
                starts.append(prev + 1)
                arr.append(0)
            starts.append(i)
            arr.append(v)
            prev = i
        if prev < hi:
            starts.append(prev + 1)
            arr.append(0)
        self.starts = starts
        self.inner = {inner}(arr)

    # O(logN) -- {what.split(" (")[0].lower()} of a[l..r]
    def {op}(self, l, r):
        return self.inner.{op}(bisect_right(self.starts, l) - 1, bisect_right(self.starts, r) - 1)
''' + PY_POINT_GET
    cpp = dense_body(folder, "cpp") + SPARSE_NOTE_CPP + f'''
// {what} over any index range [lo, hi], built from given values (index, value pairs); every other index is 0. A maximal gap
// of zeros adds nothing more than a single 0, so {inner} runs on the compressed array of given values with one 0 per gap,
// and a query maps l and r to the compressed elements containing them.
template <typename T>
struct {name} {{
    long long lo, hi;
    vector<long long> idx, starts;  // given value indices; starts[k] = first index of compressed element k
    vector<T> vals;
    {inner}<T> inner;

    // O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    {name}(long long lo, long long hi, vector<pair<long long, T>> values) : lo(lo), hi(hi), inner(compress(values)) {{}}

    vector<T> compress(vector<pair<long long, T>>& pts) {{
        sort(pts.begin(), pts.end());
        vector<T> arr;
        long long prev = lo - 1;
        for (auto& [i, v] : pts) {{
            if (i > prev + 1) starts.push_back(prev + 1), arr.push_back(T(0));
            starts.push_back(i), arr.push_back(v);
            idx.push_back(i), vals.push_back(v);
            prev = i;
        }}
        if (prev < hi) starts.push_back(prev + 1), arr.push_back(T(0));
        return arr;
    }}

    int element(long long i) const {{ return int(upper_bound(starts.begin(), starts.end(), i) - starts.begin()) - 1; }}

    // O(logN) -- {what.split(" (")[0].lower()} of a[l..r]
    {rtype} {op}(long long l, long long r) const {{ return inner.{op}(element(l), element(r)); }}
''' + CPP_POINT_GET + "};\n"
    write(folder, "sparse-table" if inner.startswith("Sparse") else "merge-sort-tree", comp, mem, note, py, cpp)


TABLE_MEM = ("sparse[2*N*log(N)]", "none", "idx[1*N] vals[1*N] starts[2*N]")
TABLE_NOTE = "the sparse table runs on the given values plus one 0 per gap (at most 2N + 1 elements)"
for op, inner, name, what in [("rangeMax", "SparseMax", "SparseStaticMax", "Range max"),
                              ("rangeMin", "SparseMin", "SparseStaticMin", "Range min"),
                              ("rangeAndQuery", "SparseAnd", "SparseStaticAnd", "Range and"),
                              ("rangeOrQuery", "SparseOr", "SparseStaticOr", "Range or")]:
    compressed(f"pointGet-{op}", inner, name, op, what, {op: "log(N)", "pointGet": "log(N)", "build": "N*log(N)"},
               TABLE_MEM, TABLE_NOTE)
compressed("pointGet-rangeGcd", "SparseGcd", "SparseStaticGcd", "rangeGcd", "Range gcd",
           {"rangeGcd": "log(N)+log(U) ?", "pointGet": "log(N)", "build": "N*log(N)*log(U) ?"}, TABLE_MEM, TABLE_NOTE)
compressed("pointGet-rangeLIS", "RangeLIS", "SparseStaticLIS", "rangeLIS",
           "Range LIS (longest strictly increasing subsequence; a run of zeros adds at most one element)",
           {"rangeLIS": "log(N)", "pointGet": "log(N)", "build": "N*log^2(N)"},
           ("cnt[2*N*log(N)]", "none", "idx[1*N] vals[1*N] starts[2*N] E[2*N] sortedVals[2*N]"),
           "the seaweed LIS structure runs on the given values plus one 0 per gap (at most 2N + 1 elements)", rtype="int")

# ------------------------------------------------------------------------------------------------ given values-only wrappers

PY_POINTS_INIT = '''
    # O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    def __init__(self, lo, hi, values{extra_args}):
        self.lo, self.hi = lo, hi
        pts = sorted(values)
        self.idx = [i for i, _ in pts]
        self.vals = [v for _, v in pts]
        vals = self.vals or [0]  # (a dummy element when there are no given values; it is never queried)
{inits}
    # (i0, i1, zeros): the given values inside [l, r] are i0..i1, and the rest of [l, r] is that many zeros
    def _span(self, l, r):
        i0, i1 = bisect_left(self.idx, l), bisect_right(self.idx, r) - 1
        return i0, i1, (r - l + 1) - (i1 - i0 + 1)
'''

CPP_POINTS_INIT = '''
    // O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    {name}(long long lo, long long hi, vector<pair<long long, T>> values) : lo(lo), hi(hi){inits} {{}}

    vector<T> split(vector<pair<long long, T>>& pts) {{
        sort(pts.begin(), pts.end());
        for (auto& [i, v] : pts) idx.push_back(i), vals.push_back(v);
        return vals.empty() ? vector<T>{{T(0)}} : vals;  // (a dummy element when there are no given values; never queried)
    }}

    // the given values inside [l, r] are i0..i1, and the rest of [l, r] is zeros = (r - l + 1) - (i1 - i0 + 1) zeros
    void span(long long l, long long r, int& i0, int& i1, long long& zeros) const {{
        i0 = int(lower_bound(idx.begin(), idx.end(), l) - idx.begin());
        i1 = int(upper_bound(idx.begin(), idx.end(), r) - idx.begin()) - 1;
        zeros = (r - l + 1) - (i1 - i0 + 1);
    }}
'''

# k-th: if 0 fails the test, it is the dense k-th among the given values; if 0 passes, every zero counts too, so binary
# search the given value t before which the k-th qualifying index falls, then step into the gap before it.
PY_KTH = '''
    # the k-th i in [l, r] whose value passes (test); qual(t) = qualifying given values among i0..t-1; zeroOk: 0 passes
    def _kth(self, l, r, k, zeroOk, qual, denseKth):
        i0, i1, _ = self._span(l, r)
        if k <= 0:
            return self.lo - 1
        if not zeroOk:
            if k > i1 - i0 + 1:
                return self.lo - 1
            j = denseKth(i0, i1, k)
            return self.idx[j] if j != -1 else self.lo - 1
        idx = self.idx

        def g(t):  # qualifying indices in [l, (given value t) - 1]; given value i1 + 1 stands for r + 1
            return ((idx[t] if t <= i1 else r + 1) - l) - (t - i0) + qual(t)

        if g(i1 + 1) < k:
            return self.lo - 1
        a, b = i0, i1 + 1  # smallest t with g(t) >= k
        while a < b:
            m = (a + b) // 2
            if g(m) >= k:
                b = m
            else:
                a = m + 1
        t = a
        if t == i0:
            return l - 1 + k
        c = g(t - 1) + qual(t) - qual(t - 1)  # qualifying indices in [l, given value t - 1]
        return idx[t - 1] if c >= k else idx[t - 1] + (k - c)
'''
CPP_KTH = '''
    // the k-th i in [l, r] whose value passes the test; qual(t) = qualifying given values among i0..t-1; zeroOk: 0 passes;
    // denseKth(i0, i1, k) = the dense k-th among the given values (-1 if none)
    template <class Q, class K>
    long long kthWithZeros(long long l, long long r, long long k, bool zeroOk, Q qual, K denseKth) const {
        int i0, i1;
        long long zeros;
        span(l, r, i0, i1, zeros);
        if (k <= 0) return lo - 1;
        if (!zeroOk) {
            if (k > i1 - i0 + 1) return lo - 1;
            int j = denseKth(i0, i1, int(k));
            return j != -1 ? idx[j] : lo - 1;
        }
        auto g = [&](int t) {  // qualifying indices in [l, (given value t) - 1]; given value i1 + 1 stands for r + 1
            return ((t <= i1 ? idx[t] : r + 1) - l) - (t - i0) + qual(i0, t);
        };
        if (g(i1 + 1) < k) return lo - 1;
        int a = i0, b = i1 + 1;  // smallest t with g(t) >= k
        while (a < b) {
            int m = a + (b - a) / 2;
            if (g(m) >= k) b = m;
            else a = m + 1;
        }
        int t = a;
        if (t == i0) return l - 1 + k;
        long long c = g(t - 1) + qual(i0, t) - qual(i0, t - 1);  // qualifying indices in [l, given value t - 1]
        return c >= k ? idx[t - 1] : idx[t - 1] + (k - c);
    }
'''

KTH_SPECS = [  # op, does 0 pass (python / c++), qualifying given values among i0..t-1 (python / c++), dense k-th
    ("kthGteX", "0 >= x", "T(0) >= x", "self.inner.countGteX(i0, t - 1, x)", "inner.countGteX(i0, t - 1, x)", "a[i] >= x"),
    ("kthGtX", "0 > x", "T(0) > x", "self.inner.countGteX(i0, t - 1, x + 1)", "inner.countGteX(i0, t - 1, x + 1)", "a[i] > x"),
    ("kthLteX", "0 <= x", "T(0) <= x", "self.inner.countLteX(i0, t - 1, x)", "inner.countLteX(i0, t - 1, x)", "a[i] <= x"),
    ("kthLtX", "0 < x", "T(0) < x", "self.inner.countLteX(i0, t - 1, x - 1)", "inner.countLteX(i0, t - 1, x - 1)", "a[i] < x"),
]


def kth_methods(mst="self.inner"):
    py, cpp = PY_KTH, CPP_KTH
    for op, z_py, z_cpp, q_py, q_cpp, desc in KTH_SPECS:
        py += f'''
    # O(log^2 N) -- index of the k-th (1-indexed) i in [l, r] with {desc}, or lo - 1
    def {op}(self, l, r, k, x):
        i0 = bisect_left(self.idx, l)
        return self._kth(l, r, k, {z_py}, lambda t: {q_py} if t > i0 else 0,
                         lambda a, b, kk: {mst}.{op}(a, b, kk, x))
'''
        cpp += f'''
    // O(log^2 N) -- index of the k-th (1-indexed) i in [l, r] with {desc}, or lo - 1
    long long {op}(long long l, long long r, long long k, T x) const {{
        return kthWithZeros(l, r, k, {z_cpp}, [&](int i0, int t) -> long long {{ return t > i0 ? {q_cpp} : 0; }},
                            [&](int a, int b, int kk) {{ return inner.{op}(a, b, kk, x); }});
    }}
'''
    return py, cpp


COUNT_PY = '''
    # O(logN) -- # of i in [l, r] with valLow <= a[i] <= valHigh
    def countInValRange(self, l, r, valLow, valHigh):
        i0, i1, zeros = self._span(l, r)
        inside = self.inner.countInValRange(i0, i1, valLow, valHigh) if i0 <= i1 else 0
        return inside + (zeros if valLow <= 0 <= valHigh else 0)
'''
COUNT_CPP = '''
    // O(logN) -- # of i in [l, r] with valLow <= a[i] <= valHigh
    long long countInValRange(long long l, long long r, T valLow, T valHigh) const {
        int i0, i1;
        long long zeros;
        span(l, r, i0, i1, zeros);
        long long inside = i0 <= i1 ? inner.countInValRange(i0, i1, valLow, valHigh) : 0;
        return inside + (valLow <= T(0) && T(0) <= valHigh ? zeros : 0);
    }
'''

# k-th smallest / largest value: the sorted values of [l, r] are the given negatives, then every 0 (the zeros of [l, r]
# and the given 0s), then the given positives, so a k past the negatives and the zeros is the given (k - zeros)-th.
KTH_VAL_PY = '''
    # O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else IndexError
    def kthSmallestInRange(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallestInRange: k = {k} is outside [1, {r - l + 1}]")
        i0, i1, zeros = self._span(l, r)
        neg = self.inner.countInValRange(i0, i1, float("-inf"), -1) if i0 <= i1 else 0
        if k <= neg:
            return self.inner.kthSmallestInRange(i0, i1, k)
        if k <= neg + zeros:
            return 0
        return self.inner.kthSmallestInRange(i0, i1, k - zeros)

    # O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else IndexError
    def kthLargestInRange(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthLargestInRange: k = {k} is outside [1, {r - l + 1}]")
        return self.kthSmallestInRange(l, r, r - l + 2 - k)
'''
KTH_VAL_CPP = '''
    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthSmallestInRange(long long l, long long r, long long k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallestInRange: k outside [1, r - l + 1]");
        int i0, i1;
        long long zeros;
        span(l, r, i0, i1, zeros);
        long long neg = i0 <= i1 ? inner.countInValRange(i0, i1, numeric_limits<T>::lowest(), T(-1)) : 0;
        if (k <= neg) return inner.kthSmallestInRange(i0, i1, int(k));
        if (k <= neg + zeros) return T(0);
        return inner.kthSmallestInRange(i0, i1, int(k - zeros));
    }

    // O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthLargestInRange(long long l, long long r, long long k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthLargestInRange: k outside [1, r - l + 1]");
        return kthSmallestInRange(l, r, r - l + 2 - k);
    }
'''

# merge sort tree: count / k-th
kpy, kcpp = kth_methods()
folder = "countInValRange-kthGtX-kthGteX-kthLtX-kthLteX-pointGet"
WHAT = ("Count values in a value range / k-th index whose value passes a test, over any index range [lo, hi], built\n"
        "{c} from given values (index, value pairs); every other index is 0. The merge sort tree runs on the given values alone; the zeros\n"
        "{c} of [l, r] are its length minus the given values inside, and they count wherever 0 passes the test.")
write(folder, "merge-sort-tree",
      {"countInValRange": "log(N)", "kthGtX": "log^2(N)", "kthGteX": "log^2(N)", "kthLtX": "log^2(N)", "kthLteX": "log^2(N)",
       "pointGet": "log(N)", "build": "N*log(N)"},
      ("cnt[1*N*log(N)]", "none", "idx[1*N] vals[1*N] sortedVals[1*N]"),
      "the merge sort tree is over the given values only; a k-th whose test 0 passes binary-searches the gap it falls in",
      dense_body(folder, "py") + SPARSE_NOTE_PY + f'''
# {WHAT.format(c="#")}


class SparseStaticMergeSortTree:
    __slots__ = ("lo", "hi", "idx", "vals", "inner")
''' + PY_POINTS_INIT.format(extra_args="", inits="        self.inner = MergeSortTree(vals)\n") + COUNT_PY + kpy + PY_POINT_GET,
      dense_body(folder, "cpp") + SPARSE_NOTE_CPP + f'''
// {WHAT.format(c="//")}
template <typename T>
struct SparseStaticMergeSortTree {{
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    MergeSortTree<T> inner;
''' + CPP_POINTS_INIT.format(name="SparseStaticMergeSortTree", inits=", inner(split(values))") + COUNT_CPP + kcpp + CPP_POINT_GET + "};\n")

# merge sort tree + count distinct
folder = "countDistinct-countInValRange-kthGtX-kthGteX-kthLtX-kthLteX-pointGet"
write(folder, "merge-sort-tree",
      {"countDistinct": "log(N)", "countInValRange": "log(N)", "kthGtX": "log^2(N)", "kthGteX": "log^2(N)",
       "kthLtX": "log^2(N)", "kthLteX": "log^2(N)", "pointGet": "log(N)", "build": "N*log(N)"},
      ("cnt[2*N*log(N)]", "none", "idx[1*N] vals[1*N] sortedVals[2*N] nxt[1*N] zc[1*N]"),
      "both merge sort trees are over the given values only; zeros add one distinct value when [l, r] has a zero and no "
      "given value holding 0 (zc counts those given values)",
      dense_body(folder, "py") + SPARSE_NOTE_PY + f'''
# {WHAT.format(c="#")}
# Distinct values: the given values' distinct values, plus 0 if [l, r] has a zero index and no given value holding 0.


class SparseStaticMergeSortTree:
    __slots__ = ("lo", "hi", "idx", "vals", "inner", "distinct", "zc")
''' + PY_POINTS_INIT.format(extra_args="", inits="""        self.inner = MergeSortTree(vals)
        self.distinct = StaticDistinct(vals)
        self.zc = [0]  # zc[k] = # of the first k given values holding 0
        for v in self.vals:
            self.zc.append(self.zc[-1] + (v == 0))
""") + COUNT_PY + '''
    # O(logN) -- # of distinct values in a[l..r]
    def countDistinct(self, l, r):
        i0, i1, zeros = self._span(l, r)
        if i0 > i1:
            return 1
        return self.distinct.countDistinct(i0, i1) + (zeros > 0 and self.zc[i1 + 1] == self.zc[i0])
''' + kpy + PY_POINT_GET,
      dense_body(folder, "cpp") + SPARSE_NOTE_CPP + f'''
// {WHAT.format(c="//")}
// Distinct values: the given values' distinct values, plus 0 if [l, r] has a zero index and no given value holding 0.
template <typename T>
struct SparseStaticMergeSortTree {{
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    MergeSortTree<T> inner;
    StaticDistinct<T> distinct;
    vector<int> zc;  // zc[k] = # of the first k given values holding 0
''' + CPP_POINTS_INIT.format(name="SparseStaticMergeSortTree", inits=", inner(split(values)), distinct(vals.empty() ? vector<T>{T(0)} : vals), zc(1)").replace(
          "{}\n\n    vector<T> split", "{\n        for (T v : vals) zc.push_back(zc.back() + (v == T(0)));\n    }\n\n    vector<T> split") + COUNT_CPP + '''
    // O(logN) -- # of distinct values in a[l..r]
    long long countDistinct(long long l, long long r) const {
        int i0, i1;
        long long zeros;
        span(l, r, i0, i1, zeros);
        if (i0 > i1) return 1;
        return distinct.countDistinct(i0, i1) + (zeros > 0 && zc[i1 + 1] == zc[i0]);
    }
''' + kcpp + CPP_POINT_GET + "};\n")

# persistent: count / sum in a value range
folder = "countInValRange-kthLargestInRange-kthSmallestInRange-pointGet-sumInValRange"
write(folder, "persistent",
      {"countInValRange": "log(N)", "kthLargestInRange": "log(N)", "kthSmallestInRange": "log(N)", "pointGet": "log(N)",
       "sumInValRange": "log(N)", "build": "N*log(N)"},
      ("L[1*N*log(N)] R[1*N*log(N)] S[1*N*log(N)] C[1*N*log(N)]", "none", "idx[1*N] vals[1*N] root[1*N] srt[1*N]"),
      "the persistent tree is over the given values only; zeros add to counts (never to sums) and sit between the negatives and the positives for a k-th",
      dense_body(folder, "py") + SPARSE_NOTE_PY + '''
# Count / sum of the values in a value range and k-th smallest / largest, over any index range [lo, hi], built from given
# values (index, value pairs); every other index is 0. The persistent tree runs on the given values alone; the zeros of
# [l, r] (its length minus the given values inside) add to a count when 0 is in the value range, never to a sum, and
# sit between the given negatives and positives for a k-th.


class SparseStaticValueRangeSum:
    __slots__ = ("lo", "hi", "idx", "vals", "inner")
''' + PY_POINTS_INIT.format(extra_args="", inits="        self.inner = StaticValueRangeSum(vals)\n") + COUNT_PY + KTH_VAL_PY + '''
    # O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal
    def sumInValRange(self, l, r, lowVal, highVal):
        i0, i1, _ = self._span(l, r)
        return self.inner.sumInValRange(i0, i1, lowVal, highVal) if i0 <= i1 else 0
''' + PY_POINT_GET,
      dense_body(folder, "cpp") + SPARSE_NOTE_CPP + '''
// Count / sum of the values in a value range and k-th smallest / largest, over any index range [lo, hi], built from given
// values (index, value pairs); every other index is 0. The persistent tree runs on the given values alone; the zeros of
// [l, r] (its length minus the given values inside) add to a count when 0 is in the value range, never to a sum, and
// sit between the given negatives and positives for a k-th.
template <typename T>
struct SparseStaticValueRangeSum {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    StaticValueRangeSum<T> inner;
''' + CPP_POINTS_INIT.format(name="SparseStaticValueRangeSum", inits=", inner(split(values))") + COUNT_CPP.replace(
          "inner.countInValRange(i0, i1, valLow, valHigh)", "inner.countInValRange(i0, i1, valLow, valHigh)") + KTH_VAL_CPP + '''
    // O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal
    S sumInValRange(long long l, long long r, T lowVal, T highVal) const {
        int i0, i1;
        long long zeros;
        span(l, r, i0, i1, zeros);
        return i0 <= i1 ? S(inner.sumInValRange(i0, i1, lowVal, highVal)) : S(0);
    }
''' + CPP_POINT_GET + "};\n")

# wavelet matrix: count in a value range / k-th smallest / largest
folder = "countInValRange-kthLargestInRange-kthSmallestInRange-pointGet"
WHAT = ("Count of values in a value range and k-th smallest / largest, over any index range [lo, hi], built from given values\n"
        "{c} (index, value pairs); every other index is 0. The wavelet matrix runs on the given values alone; the zeros of [l, r]\n"
        "{c} (its length minus the given values inside) add to a count when 0 is in the value range, and sit between the given\n"
        "{c} negatives and positives for a k-th.")
write(folder, "wavelet",
      {"countInValRange": "log(N)", "kthLargestInRange": "log(N)", "kthSmallestInRange": "log(N)", "pointGet": "log(N)",
       "build": "N*log(N)"},
      ("zeros[1*N*log(N)]", "none", "idx[1*N] vals[1*N] arr[1*N] srt[1*N]"),
      "the wavelet matrix is over the given values only; zeros add to counts and sit between the negatives and the positives for a k-th",
      dense_body(folder, "py") + SPARSE_NOTE_PY + f'''
# {WHAT.format(c="#")}


class SparseWaveletMatrix:
    __slots__ = ("lo", "hi", "idx", "vals", "inner")
''' + PY_POINTS_INIT.format(extra_args="", inits="        self.inner = WaveletMatrix(vals)\n") + COUNT_PY + KTH_VAL_PY + PY_POINT_GET,
      dense_body(folder, "cpp") + SPARSE_NOTE_CPP + f'''
// {WHAT.format(c="//")}
template <typename T>
struct SparseWaveletMatrix {{
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    WaveletMatrix<T> inner;
''' + CPP_POINTS_INIT.format(name="SparseWaveletMatrix", inits=", inner(split(values))") + COUNT_CPP + KTH_VAL_CPP + CPP_POINT_GET + "};\n")

# range mode
folder = "pointGet-rangeMode"
write(folder, "sqrt", {"pointGet": "log(N)", "rangeMode": "sqrt(N)", "build": "N*sqrt(N)"},
      ("blockMode[1*N] blockCnt[1*N]", "none", "idx[1*N] vals[1*N] zc[1*N] comp[1*N] positions[1*N] posIdx[1*N]"),
      "the sqrt mode structure is over the given values only; 0's frequency is the zeros of [l, r] plus the given values holding 0 "
      "(zc), and it wins whenever it is at least the given values' mode frequency",
      dense_body(folder, "py") + SPARSE_NOTE_PY + '''
# Range mode over any index range [lo, hi], built from given values (index, value pairs); every other index is 0. The sqrt mode
# structure runs on the given values alone; 0 appears (zeros of [l, r]) + (given values holding 0) times, and is the answer
# whenever that is at least the given values' own mode frequency.


class SparseStaticRangeMode:
    __slots__ = ("lo", "hi", "idx", "vals", "inner", "zc")
''' + PY_POINTS_INIT.format(extra_args="", inits="""        self.inner = RangeMode(vals)
        self.zc = [0]  # zc[k] = # of the first k given values holding 0
        for v in self.vals:
            self.zc.append(self.zc[-1] + (v == 0))
""") + '''
    # O(sqrtN) -- (mode, frequency) of a[l..r]; ties: any one of the tied values
    def rangeMode(self, l, r):
        i0, i1, zeros = self._span(l, r)
        if i0 > i1:
            return 0, zeros
        v, f = self.inner.rangeMode(i0, i1)
        f0 = zeros + self.zc[i1 + 1] - self.zc[i0]
        return (0, f0) if f0 >= f else (v, f)
''' + PY_POINT_GET,
      dense_body(folder, "cpp") + SPARSE_NOTE_CPP + '''
// Range mode over any index range [lo, hi], built from given values (index, value pairs); every other index is 0. The sqrt mode
// structure runs on the given values alone; 0 appears (zeros of [l, r]) + (given values holding 0) times, and is the answer
// whenever that is at least the given values' own mode frequency.
template <typename T>
struct SparseStaticRangeMode {
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    RangeMode<T> inner;
    vector<int> zc;  // zc[k] = # of the first k given values holding 0
''' + CPP_POINTS_INIT.format(name="SparseStaticRangeMode", inits=", inner(split(values)), zc(1)").replace(
          "{}\n\n    vector<T> split", "{\n        for (T v : vals) zc.push_back(zc.back() + (v == T(0)));\n    }\n\n    vector<T> split") + '''
    // O(sqrtN) -- (mode, frequency) of a[l..r]; ties: any one of the tied values
    pair<T, long long> rangeMode(long long l, long long r) const {
        int i0, i1;
        long long zeros;
        span(l, r, i0, i1, zeros);
        if (i0 > i1) return {T(0), zeros};
        auto [v, f] = inner.rangeMode(i0, i1);
        long long f0 = zeros + zc[i1 + 1] - zc[i0];
        return f0 >= f ? pair<T, long long>{T(0), f0} : pair<T, long long>{v, f};
    }
''' + CPP_POINT_GET + "};\n")

# count occurrences (no inner structure needed: positions are kept as absolute indices)
write("countOccurrences-pointGet", "positions", {"countOccurrences": "log(N)", "pointGet": "log(N)", "build": "N*log(N)"},
      ("pos[1*N]", "none", "idx[1*N] vals[1*N]"),
      "pos maps each value to its sorted indices; 0 also counts the zeros of [l, r] (its length minus the given values inside)",
      '''from bisect import bisect_left, bisect_right

# "How many times does x appear in a[l..r]?" over any index range [lo, hi], built from given values (index, value pairs); every
# other index is 0. Each value keeps its sorted indices; x == 0 also counts the zeros of [l, r] (its length minus the
# given values inside).


class SparseStaticOccurrences:
    __slots__ = ("lo", "hi", "idx", "vals", "pos")

    # O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    def __init__(self, lo, hi, values):
        self.lo, self.hi = lo, hi
        pts = sorted(values)
        self.idx = [i for i, _ in pts]
        self.vals = [v for _, v in pts]
        pos = self.pos = {}
        for i, v in pts:
            if v in pos:
                pos[v].append(i)
            else:
                pos[v] = [i]

    # O(logN) -- # of i in [l, r] with a[i] == x
    def countOccurrences(self, l, r, x):
        if l > r:
            return 0
        p = self.pos.get(x)
        res = bisect_right(p, r) - bisect_left(p, l) if p else 0
        if x == 0:
            res += (r - l + 1) - (bisect_right(self.idx, r) - bisect_left(self.idx, l))
        return res
''' + PY_POINT_GET, '''
// "How many times does x appear in a[l..r]?" over any index range [lo, hi], built from given values (index, value pairs); every
// other index is 0. Each value keeps its sorted indices; x == 0 also counts the zeros of [l, r] (its length minus the
// given values inside). T: any type usable as a std::map key.
template <typename T>
struct SparseStaticOccurrences {
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    map<T, vector<long long>> pos;

    // O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    SparseStaticOccurrences(long long lo, long long hi, vector<pair<long long, T>> values) : lo(lo), hi(hi) {
        sort(values.begin(), values.end());
        for (auto& [i, v] : values) idx.push_back(i), vals.push_back(v), pos[v].push_back(i);
    }

    static long long countIn(const vector<long long>& p, long long l, long long r) {
        return (long long)(upper_bound(p.begin(), p.end(), r) - lower_bound(p.begin(), p.end(), l));
    }

    // O(logN) -- # of i in [l, r] with a[i] == x
    long long countOccurrences(long long l, long long r, const T& x) const {
        if (l > r) return 0;
        auto it = pos.find(x);
        long long res = it == pos.end() ? 0 : countIn(it->second, l, r);
        if (x == T(0)) res += (r - l + 1) - countIn(idx, l, r);
        return res;
    }
''' + CPP_POINT_GET + "};\n")

# ------------------------------------------------------------------------------------------------ costMono family

PY_PIECE = '''from bisect import bisect_left, bisect_right


class _PieceCost:
    """costMonoIncreasing (min +1 increments to make a[l..r] non-decreasing) over an array given as pieces: piece k
    starts at index starts[k], spans w[k] indices, and holds v[k] + slope[k] * t at its t-th index (slope 0 or -1,
    so a piece's own max is its first value). cost = sum of prefix maxes - sum of values. The prefix max is flat
    inside a piece, so sum over pieces of w * max(carry, max of v so far): a sparse table of argmax finds the first
    piece above the carry and the max, and suff[k] = sum over j >= k of w_j * max(v[k..j]) (by next-greater) does the
    rest."""
    __slots__ = ("starts", "v", "w", "slope", "W", "B", "sp", "suff")

    # O(N log N)
    def __init__(self, starts, v, w, slope):
        n = len(v)
        self.starts, self.v, self.w, self.slope = starts, v, w, slope
        W, B = [0] * (n + 1), [0] * (n + 1)  # prefix weights, prefix value sums
        for k in range(n):
            W[k + 1] = W[k] + w[k]
            B[k + 1] = B[k] + w[k] * v[k] + slope[k] * w[k] * (w[k] - 1) // 2
        self.W, self.B = W, B
        sp = [list(range(n))]  # sp[j][k] = index of the (leftmost) max of v[k .. k + 2^j - 1]
        j = 1
        while (1 << j) <= n:
            prev, h = sp[-1], 1 << (j - 1)
            sp.append([prev[k] if v[prev[k]] >= v[prev[k + h]] else prev[k + h] for k in range(n - (1 << j) + 1)])
            j += 1
        self.sp = sp
        suff, stack = [0] * (n + 1), []
        for k in range(n - 1, -1, -1):
            while stack and v[stack[-1]] <= v[k]:
                stack.pop()
            ng = stack[-1] if stack else n
            suff[k] = v[k] * (W[ng] - W[k]) + suff[ng]
            stack.append(k)
        self.suff = suff

    def _argmax(self, a, b):
        j = (b - a + 1).bit_length() - 1
        x, y = self.sp[j][a], self.sp[j][b - (1 << j) + 1]
        return x if self.v[x] >= self.v[y] else y

    def _carry(self, a, b, M):  # sum over pieces k in [a, b] of w_k * max(M, max(v[a..k]))
        v, W, sp = self.v, self.W, self.sp
        q = a  # first piece in [a, b] above M: skip blocks whose max is <= M
        for j in range(len(sp) - 1, -1, -1):
            if q + (1 << j) - 1 <= b and v[sp[j][q]] <= M:
                q += 1 << j
        if q > b:
            return M * (W[b + 1] - W[a])
        p = self._argmax(q, b)
        return M * (W[q] - W[a]) + self.suff[q] - self.suff[p] + v[p] * (W[b + 1] - W[p])

    def _part(self, k, x, y):  # sum of piece k's values at indices x..y
        n = y - x + 1
        return n * (self.v[k] + self.slope[k] * (x - self.starts[k])) + self.slope[k] * n * (n - 1) // 2

    # O(logN) -- a[l] + ... + a[r]
    def sum(self, l, r):
        starts, w = self.starts, self.w
        k0, k1 = bisect_right(starts, l) - 1, bisect_right(starts, r) - 1
        if k0 == k1:
            return self._part(k0, l, r)
        return self._part(k0, l, starts[k0] + w[k0] - 1) + self.B[k1] - self.B[k0 + 1] + self._part(k1, starts[k1], r)

    # O(logN) -- min +1 increments to make a[l..r] non-decreasing
    def cost(self, l, r):
        starts, v, w = self.starts, self.v, self.w
        k0, k1 = bisect_right(starts, l) - 1, bisect_right(starts, r) - 1
        m0 = v[k0] + self.slope[k0] * (l - starts[k0])  # the value at l: the prefix max all through l's piece
        if k0 == k1:
            return (r - l + 1) * m0 - self.sum(l, r)
        pref = m0 * (starts[k0] + w[k0] - l) + self._carry(k0 + 1, k1, m0)
        final = max(m0, v[self._argmax(k0 + 1, k1)])  # the prefix max all through r's piece
        pref -= (starts[k1] + w[k1] - 1 - r) * final  # r's piece only counts up to r
        return pref - self.sum(l, r)


def _pieces(lo, hi, pts, c):
    """The pieces of b[i] = a[i] + c * (i - lo) (c = 0, or -1 for the strict costs) for given values pts over [lo, hi]."""
    starts, v, w, slope = [], [], [], []
    prev = lo - 1
    for i, x in pts:
        if i > prev + 1:
            starts.append(prev + 1), v.append(c * (prev + 1 - lo)), w.append(i - prev - 1), slope.append(c)
        starts.append(i), v.append(x + c * (i - lo)), w.append(1), slope.append(0)
        prev = i
    if prev < hi:
        starts.append(prev + 1), v.append(c * (prev + 1 - lo)), w.append(hi - prev), slope.append(c)
    return starts, v, w, slope
'''

CPP_PIECE = '''
// costMonoIncreasing (min +1 increments to make a[l..r] non-decreasing) over an array given as pieces: piece k
// starts at index starts[k], spans w[k] indices, and holds v[k] + slope[k] * t at its t-th index (slope 0 or -1, so
// a piece's own max is its first value). cost = sum of prefix maxes - sum of values. The prefix max is flat inside a
// piece, so sum over pieces of w * max(carry, max of v so far): a sparse table of argmax finds the first piece above
// the carry and the max, and suff[k] = sum over j >= k of w_j * max(v[k..j]) (by next-greater) does the rest.
// Sums are unsigned 64-bit and wrap, so results are exact whenever they fit in long long.
struct PieceCost {
    using W = unsigned long long;
    int n;
    vector<long long> starts, v, w;
    vector<int> slope;
    vector<W> Wp, Bp, suff;  // prefix weights, prefix value sums
    vector<vector<int>> sp;  // sp[j][k] = index of the (leftmost) max of v[k .. k + 2^j - 1]

    static W tri(long long m) {  // m(m-1)/2 mod 2^64, exact
        W a = W(m), b = W(m - 1);
        return a % 2 == 0 ? (a / 2) * b : a * (b / 2);
    }

    // O(N log N)
    PieceCost(vector<long long> starts_, vector<long long> v_, vector<long long> w_, vector<int> slope_)
        : n((int)v_.size()), starts(move(starts_)), v(move(v_)), w(move(w_)), slope(move(slope_)), Wp(n + 1), Bp(n + 1), suff(n + 1) {
        for (int k = 0; k < n; k++) {
            Wp[k + 1] = Wp[k] + W(w[k]);
            Bp[k + 1] = Bp[k] + W(w[k]) * W(v[k]) - (slope[k] ? tri(w[k]) : W(0));
        }
        sp.push_back(vector<int>(n));
        iota(sp[0].begin(), sp[0].end(), 0);
        for (int j = 1; (1 << j) <= n; j++) {
            const vector<int>& prev = sp[j - 1];
            int h = 1 << (j - 1);
            vector<int> cur(n - (1 << j) + 1);
            for (int k = 0; k + (1 << j) <= n; k++) cur[k] = v[prev[k]] >= v[prev[k + h]] ? prev[k] : prev[k + h];
            sp.push_back(move(cur));
        }
        vector<int> stack;
        for (int k = n - 1; k >= 0; k--) {
            while (!stack.empty() && v[stack.back()] <= v[k]) stack.pop_back();
            int ng = stack.empty() ? n : stack.back();
            suff[k] = W(v[k]) * (Wp[ng] - Wp[k]) + suff[ng];
            stack.push_back(k);
        }
    }

    int argmax(int a, int b) const {
        int j = 31 - __builtin_clz(b - a + 1);
        int x = sp[j][a], y = sp[j][b - (1 << j) + 1];
        return v[x] >= v[y] ? x : y;
    }

    // sum over pieces k in [a, b] of w_k * max(M, max(v[a..k]))
    W carry(int a, int b, long long M) const {
        int q = a;  // first piece in [a, b] above M: skip blocks whose max is <= M
        for (int j = (int)sp.size() - 1; j >= 0; j--)
            if (q + (1 << j) - 1 <= b && v[sp[j][q]] <= M) q += 1 << j;
        if (q > b) return W(M) * (Wp[b + 1] - Wp[a]);
        int p = argmax(q, b);
        return W(M) * (Wp[q] - Wp[a]) + suff[q] - suff[p] + W(v[p]) * (Wp[b + 1] - Wp[p]);
    }

    W part(int k, long long x, long long y) const {  // sum of piece k's values at indices x..y
        long long m = y - x + 1;
        return W(m) * W(v[k] + slope[k] * (x - starts[k])) - (slope[k] ? tri(m) : W(0));
    }

    int piece(long long i) const { return int(upper_bound(starts.begin(), starts.end(), i) - starts.begin()) - 1; }

    // O(logN) -- a[l] + ... + a[r] (mod 2^64)
    W sum(long long l, long long r) const {
        int k0 = piece(l), k1 = piece(r);
        if (k0 == k1) return part(k0, l, r);
        return part(k0, l, starts[k0] + w[k0] - 1) + Bp[k1] - Bp[k0 + 1] + part(k1, starts[k1], r);
    }

    // O(logN) -- min +1 increments to make a[l..r] non-decreasing
    long long cost(long long l, long long r) const {
        int k0 = piece(l), k1 = piece(r);
        long long m0 = v[k0] + slope[k0] * (l - starts[k0]);  // the value at l: the prefix max all through l's piece
        if (k0 == k1) return (long long)(W(r - l + 1) * W(m0) - sum(l, r));
        W pref = W(m0) * W(starts[k0] + w[k0] - l) + carry(k0 + 1, k1, m0);
        long long fin = max(m0, v[argmax(k0 + 1, k1)]);  // the prefix max all through r's piece
        pref -= W(starts[k1] + w[k1] - 1 - r) * W(fin);  // r's piece only counts up to r
        return (long long)(pref - sum(l, r));
    }

    // the pieces of b[i] = a[i] + c * (i - lo) (c = 0, or -1 for the strict costs) for sorted given values over [lo, hi]
    template <typename T>
    static PieceCost of(long long lo, long long hi, const vector<pair<long long, T>>& pts, int c) {
        vector<long long> st, v, w;
        vector<int> sl;
        long long prev = lo - 1;
        auto gap = [&](long long s, long long e) { st.push_back(s), v.push_back(c * (s - lo)), w.push_back(e - s + 1), sl.push_back(c); };
        for (auto& [i, x] : pts) {
            if (i > prev + 1) gap(prev + 1, i - 1);
            st.push_back(i), v.push_back((long long)x + c * (i - lo)), w.push_back(1), sl.push_back(0);
            prev = i;
        }
        if (prev < hi) gap(prev + 1, hi);
        return PieceCost(st, v, w, sl);
    }
};
'''

COST_NOTE = ("a view is the array cut into pieces (each given value, each gap of zeros), with a sparse table of argmax and "
             "next-greater sums over the pieces; ")
write("costMonoDecreasing-costMonoIncreasing-costStrictDecreasing-costStrictIncreasing-pointGet-rangeSum", "sparse-table",
      {"costMonoDecreasing": "log(N)", "costMonoIncreasing": "log(N)", "costStrictDecreasing": "log(N)",
       "costStrictIncreasing": "log(N)", "pointGet": "log(N)", "rangeSum": "log(N)", "build": "N*log(N)"},
      ("sp[2*N*log(N)]", "none", "idx[1*N] vals[1*N] pf[1*N] starts[2*N] v[2*N] w[2*N] W[2*N] B[2*N] suff[2*N]"),
      "per cost kind you call (shown for one): each kind builds its own view on its first query, so kinds you never "
      "call cost nothing; " + COST_NOTE + "the four views: a, a mirrored, a[i] - i, and a mirrored minus its index "
      "(decreasing costs are increasing costs on the mirror, strict costs subtract the index); rangeSum / pointGet "
      "need no view; C++: sums wrap mod 2^64 (exact whenever the answer fits in long long)",
      PY_PIECE + '''

# Min +1 increments to make a[l..r] non-decreasing / non-increasing / strictly increasing / strictly decreasing,
# and range sum, over any index range [lo, hi], built from given values (index, value pairs); every other index is 0.
# Decreasing costs are increasing costs on the mirror image (index i -> lo + hi - i); strict costs are the
# non-strict ones on a[i] - i (shifting by a constant changes nothing). Each view is built on its first query.


class SparseMonoCosts:
    __slots__ = ("lo", "hi", "idx", "vals", "pf", "pts", "views")

    # O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    def __init__(self, lo, hi, values):
        self.lo, self.hi = lo, hi
        self.pts = sorted(values)
        self.idx = [i for i, _ in self.pts]
        self.vals = [v for _, v in self.pts]
        self.pf = [0]  # prefix sums of the given values
        for v in self.vals:
            self.pf.append(self.pf[-1] + v)
        self.views = {}

    def _view(self, mirrored, c):
        key = (mirrored, c)
        if key not in self.views:
            lo, hi = self.lo, self.hi
            pts = sorted((lo + hi - i, x) for i, x in self.pts) if mirrored else self.pts
            self.views[key] = _PieceCost(*_pieces(lo, hi, pts, c))
        return self.views[key]

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self.pf[bisect_right(self.idx, r)] - self.pf[bisect_left(self.idx, l)] if l <= r else 0

    # O(logN) -- min +1 increments to make a[l..r] non-decreasing
    def costMonoIncreasing(self, l, r):
        return self._view(False, 0).cost(l, r)

    # O(logN) -- min +1 increments to make a[l..r] non-increasing
    def costMonoDecreasing(self, l, r):
        return self._view(True, 0).cost(self.lo + self.hi - r, self.lo + self.hi - l)

    # O(logN) -- min +1 increments to make a[l..r] strictly increasing
    def costStrictIncreasing(self, l, r):
        return self._view(False, -1).cost(l, r)

    # O(logN) -- min +1 increments to make a[l..r] strictly decreasing
    def costStrictDecreasing(self, l, r):
        return self._view(True, -1).cost(self.lo + self.hi - r, self.lo + self.hi - l)
''' + PY_POINT_GET, CPP_PIECE + '''
// Min +1 increments to make a[l..r] non-decreasing / non-increasing / strictly increasing / strictly decreasing,
// and range sum, over any index range [lo, hi], built from given values (index, value pairs); every other index is 0.
// Decreasing costs are increasing costs on the mirror image (index i -> lo + hi - i); strict costs are the
// non-strict ones on a[i] - i (shifting by a constant changes nothing). Each view is built on its first query, so you
// only pay for the cost kinds you call. T: int, long long, ...
template <typename T>
struct SparseMonoCosts {
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    vector<unsigned long long> pf{0};  // prefix sums of the given values (mod 2^64)
    vector<pair<long long, T>> pts, mirrored;
    mutable optional<PieceCost> views[2][2];  // [mirrored][strict]

    // O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    SparseMonoCosts(long long lo, long long hi, vector<pair<long long, T>> values) : lo(lo), hi(hi), pts(move(values)) {
        sort(pts.begin(), pts.end());
        for (auto& [i, v] : pts) idx.push_back(i), vals.push_back(v), mirrored.push_back({lo + hi - i, v}), pf.push_back(pf.back() + (unsigned long long)(long long)v);
        reverse(mirrored.begin(), mirrored.end());
    }

    const PieceCost& view(bool mir, bool strict) const {
        auto& v = views[mir][strict];
        if (!v) v.emplace(PieceCost::of(lo, hi, mir ? mirrored : pts, strict ? -1 : 0));
        return *v;
    }

    // O(logN) -- a[l] + ... + a[r]
    long long rangeSum(long long l, long long r) const {
        if (l > r) return 0;
        size_t a = lower_bound(idx.begin(), idx.end(), l) - idx.begin(), b = upper_bound(idx.begin(), idx.end(), r) - idx.begin();
        return (long long)(pf[b] - pf[a]);
    }

    // O(logN) -- min +1 increments to make a[l..r] non-decreasing
    long long costMonoIncreasing(long long l, long long r) const { return view(false, false).cost(l, r); }

    // O(logN) -- min +1 increments to make a[l..r] non-increasing
    long long costMonoDecreasing(long long l, long long r) const { return view(true, false).cost(lo + hi - r, lo + hi - l); }

    // O(logN) -- min +1 increments to make a[l..r] strictly increasing
    long long costStrictIncreasing(long long l, long long r) const { return view(false, true).cost(l, r); }

    // O(logN) -- min +1 increments to make a[l..r] strictly decreasing
    long long costStrictDecreasing(long long l, long long r) const { return view(true, true).cost(lo + hi - r, lo + hi - l); }
''' + CPP_POINT_GET + "};\n")
