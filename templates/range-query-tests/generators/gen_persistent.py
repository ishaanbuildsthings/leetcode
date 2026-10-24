"""Persistent seg trees for order statistics over a[l..r]: version p is the multiset of a[0..p-1], and a[l..r] is
version r + 1 minus version l.

    python3 gen_persistent.py

  persistent-order-stats[-sums]          static array, values compressed to ranks: O(log N). Dominated by the wavelet
                                          matrix (same costs, less memory) but kept on purpose (check_catalog KEPT).
  persistent-online-order-stats[-sums][-mex]
                                          the array grows with pushBack(v) and is queried in between; nothing is known
                                          up front, so the tree is over the value range [valLo, valHi]: O(log U). The
                                          mex versions add a persistent tree of each value's last index.
The query methods are gen_wavelet.py's (static: thresholds are compressed ranks) or gen_dynamic_order.py's (online:
thresholds are values).
"""
import os

import gen_wavelet as W
from gen_dynamic_order import cpp_query_ops, py_query_ops
from note_lang import write_template

DIR = W.DIR
LOGN, LOGU = "1*N*log(N)", "1*N*log(U)"


def header(cm, ops, online, sums, mex, node, other, note, offline=False):
    q = "log(U)" if online else "log(N)"
    lines = [f"@operations: {' '.join(ops)}", "@data-structure-type: persistent"] + (["@values: offline"] if offline else []) + ["@complexities:"]
    lines += [f"  {op}: {'1' if op == 'pointGet' else q}" for op in ops] + [f"  build: N*{q}"]
    lines += ["@memory:", "  layout: none", f"  node: {node}", "  tags: none", f"  other: {other}", f"  note: {note}"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


# ------------------------------------------------------------------------------------------------ Python

PY_PRIM = '''
    # ---- internals ----

    # copy of version node with one more {what} (key = its {key})
    def _ins(self, node, key, v):
        L, R, C{scomma} = self.L, self.R, self.C{sself}
        path = []
        nl, nh = self.klo, self.khi
        while nl != nh:
            mid = (nl + nh) >> 1
            if key <= mid:
                path.append((node, True))
                node, nh = L[node], mid
            else:
                path.append((node, False))
                node, nl = R[node], mid + 1
        cur = len(C)
        L.append(0), R.append(0), C.append(C[node] + 1){sleaf}
        for old, left in reversed(path):
            lc, rc = (cur, R[old]) if left else (L[old], cur)
            cur = len(C)
            L.append(lc), R.append(rc), C.append(C[lc] + C[rc]){spull}
        return cur

    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1: walk version r + 1 minus version l
    def _kth(self, l, r, k):
        L, R, C = self.L, self.R, self.C
        a, b, nl, nh = self.root[r + 1], self.root[l], self.klo, self.khi
        while nl != nh:
            mid = (nl + nh) >> 1
            c = C[L[a]] - C[L[b]]
            if k <= c:
                a, b, nh = L[a], L[b], mid
            else:
                k -= c
                a, b, nl = R[a], R[b], mid + 1
        return {leaf}

    # # of i in [l, r] whose {key} is < x
    def _countBelow(self, l, r, x):
        if x <= self.klo:
            return 0
        if x > self.khi:
            return r - l + 1
        L, R, C = self.L, self.R, self.C
        a, b, nl, nh, res = self.root[r + 1], self.root[l], self.klo, self.khi, 0
        while nl != nh:
            mid = (nl + nh) >> 1
            if x <= mid:
                a, b, nh = L[a], L[b], mid
            else:  # the whole left half is below x
                res += C[L[a]] - C[L[b]]
                a, b, nl = R[a], R[b], mid + 1
        return res
'''
PY_SUM_PRIM = '''
    # sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    def _sumFirst(self, l, r, k):
        if k <= 0:
            return 0
        L, R, C, S = self.L, self.R, self.C, self.S
        a, b, nl, nh, res = self.root[r + 1], self.root[l], self.klo, self.khi, 0
        while nl != nh:
            mid = (nl + nh) >> 1
            c = C[L[a]] - C[L[b]]
            if k <= c:
                a, b, nh = L[a], L[b], mid
            else:  # the whole left half is among the k smallest
                k -= c
                res += S[L[a]] - S[L[b]]
                a, b, nl = R[a], R[b], mid + 1
        return res + k * {leaf}

    # sum of the a[i], i in [l, r], whose {key} is < x
    def _sumBelow(self, l, r, x):
        if x <= self.klo:
            return 0
        L, R, S = self.L, self.R, self.S
        a, b = self.root[r + 1], self.root[l]
        if x > self.khi:
            return S[a] - S[b]
        nl, nh, res = self.klo, self.khi, 0
        while nl != nh:
            mid = (nl + nh) >> 1
            if x <= mid:
                a, b, nh = L[a], L[b], mid
            else:
                res += S[L[a]] - S[L[b]]
                a, b, nl = R[a], R[b], mid + 1
        return res
'''


def _fill(text, **kw):  # str.format that leaves every other brace alone
    for k, v in kw.items():
        text = text.replace("{" + k + "}", v)
    return text


def py_prims(online, sums):
    kw = dict(what="value", key="value" if online else "compressed rank", leaf="nl" if online else "self.srt[nl]",
              scomma=", S" if sums else "", sself=", self.S" if sums else "",
              sleaf=", S.append(S[node] + v)" if sums else "", spull=", S.append(S[lc] + S[rc])" if sums else "")
    return _fill(PY_PRIM, **kw) + (_fill(PY_SUM_PRIM, **kw) if sums else "")


# the persistent mex tree (gen_wavelet's), built one version per append over the values 0..mexHi
PY_MEX = W.PY_MEX_CORE[W.PY_MEX_CORE.index("    # O(logN) -- copy of node"):].format(R="mexRoot", n="(self.mexHi - 1)")


def py_static(ops, sums):
    slots = ["arr", "n", "srt", "m", "klo", "khi", "root", "L", "R", "C"] + (["S"] if sums else [])
    return ('''# Static array. Persistent seg tree over the values' compressed ranks: version p holds a[0..p-1], so a[l..r] is
# version r + 1 minus version l, and every query walks down those two versions together. Costs are log of the number
# of distinct values, never of the value range; query arguments (x, lowVal, ...) can be anything. 0-indexed, inclusive.
from bisect import bisect_left, bisect_right


class PersistentOrderStats:
''' + f"    __slots__ = ({', '.join(repr(s) for s in slots)})\n\n" + '''    # O(N log N) -- arr: the initial array (a list), 0-indexed
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)
        self.srt = srt = sorted(set(arr))
        self.m = len(srt)
        self.klo, self.khi = 0, max(self.m - 1, 0)  # the tree is over ranks 0..m-1
        where = {v: k for k, v in enumerate(srt)}
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree
''' + ("        self.S = [0]\n" if sums else "") + '''        self.root = [0]
        for v in arr:
            self.root.append(self._ins(self.root[-1], where[v], v))

''' + "\n".join(W.PY_OPS[op] for op in W.ORDER if op in ops) + py_prims(False, sums))


def py_online(ops, sums, mex):
    slots = ["arr", "n", "klo", "khi", "root", "L", "R", "C"] + (["S"] if sums else []) + (["mexHi", "mexRoot", "ML", "MR", "MN"] if mex else [])
    return ('''# An array that grows: pushBack(v) appends, and queries on any a[l..r] can come in between. Nothing is known up
# front, so the persistent seg tree is over the value range [valLo, valHi]: version p holds a[0..p-1], a[l..r] is
# version r + 1 minus version l, and each append adds one version. Values are integers; query arguments (x, lowVal,
# ...) can be anything. 0-indexed, inclusive.
''' + ('''# rangeMex: a second persistent tree, over the values 0..min(valHi, 2^30) + 1, holding each value's last index.
''' if mex else "") + '''

class PersistentOnlineOrderStats:
''' + f"    __slots__ = ({', '.join(repr(s) for s in slots)})\n\n" + '''    # O(N log U) -- arr: the initial array (a list, may be empty), 0-indexed; every value ever added must lie in
    # [valLo, valHi] (any integers, negative is fine; U = valHi - valLo + 1)
    def __init__(self, arr, valLo, valHi):
        self.arr, self.n = [], 0
        self.klo, self.khi = valLo, valHi
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree
''' + ("        self.S = [0]\n" if sums else "") + '''        self.root = [0]
''' + ('''        self.mexHi = min(max(valHi, 0), 1 << 30) + 1  # mex <= this: no value here is ever added
        self.ML, self.MR, self.MN = [0], [0], [-1]  # node 0 = the empty tree (every last index -1)
        self.mexRoot = [0]
''' if mex else "") + '''        for v in arr:
            self.pushBack(v)

    # O(logU) -- append v (valLo <= v <= valHi): it becomes a[n], and n grows by 1
    def pushBack(self, v):
        self.root.append(self._ins(self.root[-1], v, v))
''' + ('''        prev = self.mexRoot[-1]
        self.mexRoot.append(self._mexSet(prev, v, self.n) if 0 <= v <= self.mexHi else prev)
''' if mex else "") + '''        self.arr.append(v)
        self.n += 1

''' + W.PY_OPS["pointGet"] + "\n" + py_query_ops(ops) + ("\n" + W.PY_OPS["rangeMex"] if mex else "") +
            py_prims(True, sums) + ("\n" + PY_MEX if mex else ""))


# ------------------------------------------------------------------------------------------------ C++

CPP_PRIM = '''
    // ---- internals ----

    // copy of version node with one more value (key = its {key})
    int ins(int node, long long key, T v) {
        vector<pair<int, bool>> path;
        long long nl = klo, nh = khi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (key <= mid) path.push_back({node, true}), node = L[node], nh = mid;
            else path.push_back({node, false}), node = R[node], nl = mid + 1;
        }
        L.push_back(0), R.push_back(0), C.push_back(C[node] + 1){sleaf};
        int cur = (int)C.size() - 1;
        for (int k = (int)path.size() - 1; k >= 0; k--) {
            auto [old, left] = path[k];
            int lc = left ? cur : L[old], rc = left ? R[old] : cur;
            L.push_back(lc), R.push_back(rc), C.push_back(C[lc] + C[rc]){spull};
            cur = (int)C.size() - 1;
        }
        return cur;
    }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1: walk version r + 1 minus version l
    T kth(long long l, long long r, long long k) const {
        int a = root[r + 1], b = root[l];
        long long nl = klo, nh = khi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = C[L[a]] - C[L[b]];
            if (k <= c) a = L[a], b = L[b], nh = mid;
            else k -= c, a = R[a], b = R[b], nl = mid + 1;
        }
        return {leaf};
    }

    // # of i in [l, r] whose {key} is < x
    long long countBelow(long long l, long long r, long long x) const {
        if (x <= klo) return 0;
        if (x > khi) return r - l + 1;
        int a = root[r + 1], b = root[l];
        long long nl = klo, nh = khi, res = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (x <= mid) a = L[a], b = L[b], nh = mid;
            else res += C[L[a]] - C[L[b]], a = R[a], b = R[b], nl = mid + 1;  // the whole left half is below x
        }
        return res;
    }
'''
CPP_SUM_PRIM = '''
    // sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    S sumFirst(long long l, long long r, long long k) const {
        if (k <= 0) return 0;
        int a = root[r + 1], b = root[l];
        long long nl = klo, nh = khi;
        S res = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = C[L[a]] - C[L[b]];
            if (k <= c) a = L[a], b = L[b], nh = mid;
            else k -= c, res += Sm[L[a]] - Sm[L[b]], a = R[a], b = R[b], nl = mid + 1;  // the left half is among them
        }
        return res + S(k) * S({leaf});
    }

    // sum of the a[i], i in [l, r], whose {key} is < x
    S sumBelow(long long l, long long r, long long x) const {
        if (x <= klo) return 0;
        int a = root[r + 1], b = root[l];
        if (x > khi) return Sm[a] - Sm[b];
        long long nl = klo, nh = khi;
        S res = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (x <= mid) a = L[a], b = L[b], nh = mid;
            else res += Sm[L[a]] - Sm[L[b]], a = R[a], b = R[b], nl = mid + 1;
        }
        return res;
    }
'''


def cpp_prims(online, sums):
    kw = dict(key="value" if online else "compressed rank", leaf="T(nl)" if online else "srt[nl]",
              sleaf=", Sm.push_back(Sm[node] + S(v))" if sums else "", spull=", Sm.push_back(Sm[lc] + Sm[rc])" if sums else "")
    return _fill(CPP_PRIM, **kw) + (_fill(CPP_SUM_PRIM, **kw) if sums else "")


_m = W.CPP_MEX_CORE
CPP_MEX = _m[_m.index("    // copy of node with value v's last index set to i"):].replace("{R}", "mexRoot").replace("0, n + 1);", "0, mexHi);")
USING = "    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n"


def cpp_static(ops, sums):
    return ('''// Static array. Persistent seg tree over the values' compressed ranks: version p holds a[0..p-1], so a[l..r] is
// version r + 1 minus version l, and every query walks down those two versions together. Costs are log of the number
// of distinct values, never of the value range; query arguments (x, lowVal, ...) can be anything. 0-indexed, inclusive.
// T: int, long long, ...''' + ("; sums are kept in S (long long for small T)" if sums else "") + '''.
template <typename T>
struct PersistentOrderStats {
''' + (USING if sums else "") + '''    int n, m;
    long long klo, khi;            // the tree is over ranks 0..m-1
    vector<T> arr, srt;            // srt: sorted distinct values
    vector<int> root, L, R, C;     // node 0 = the empty tree
''' + ("    vector<S> Sm;\n" if sums else "") + '''
    // O(N log N) -- arr: the initial array, 0-indexed
    explicit PersistentOrderStats(const vector<T>& a) : n((int)a.size()), arr(a), srt(a), root(1, 0), L(1, 0), R(1, 0), C(1, 0)''' +
            (", Sm(1, S(0))" if sums else "") + ''' {
        sort(srt.begin(), srt.end());
        srt.erase(unique(srt.begin(), srt.end()), srt.end());
        m = (int)srt.size();
        klo = 0, khi = max(m - 1, 0);
        for (const T& v : a) root.push_back(ins(root.back(), lb(v), v));
    }

''' + "\n".join(W.CPP_OPS[op] for op in W.ORDER if op in ops) + '''
    int lb(const T& v) const { return int(lower_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    int ub(const T& v) const { return int(upper_bound(srt.begin(), srt.end(), v) - srt.begin()); }
''' + cpp_prims(False, sums) + "};\n")


def cpp_online(ops, sums, mex):
    return ('''// An array that grows: pushBack(v) appends, and queries on any a[l..r] can come in between. Nothing is known up
// front, so the persistent seg tree is over the value range [valLo, valHi]: version p holds a[0..p-1], a[l..r] is
// version r + 1 minus version l, and each append adds one version. Values are integers; query arguments (x, lowVal,
// ...) can be anything. 0-indexed, inclusive.
''' + ('''// rangeMex: a second persistent tree, over the values 0..min(valHi, 2^30) + 1, holding each value's last index.
''' if mex else "") + "// T: int, long long, ..." + ("; sums are kept in S (long long for small T)" if sums else "") + '''.
template <typename T>
struct PersistentOnlineOrderStats {
''' + (USING if sums else "") + '''    int n = 0;
    long long klo, khi;            // the tree is over the values valLo..valHi
    vector<T> arr;
    vector<int> root, L, R, C;     // node 0 = the empty tree
''' + ("    vector<S> Sm;\n" if sums else "") + ('''    int mexHi;                     // mex <= this: no value here is ever added
    vector<int> mexRoot, ML, MR, MN;
''' if mex else "") + '''
    // O(N log U) -- arr: the initial array (may be empty), 0-indexed; every value ever added must lie in [valLo, valHi]
    // (any integers, negative is fine; U = valHi - valLo + 1)
    PersistentOnlineOrderStats(const vector<T>& a, long long valLo, long long valHi)
        : klo(valLo), khi(valHi), root(1, 0), L(1, 0), R(1, 0), C(1, 0)''' + (", Sm(1, S(0))" if sums else "") +
            (", mexHi(int(min(max(valHi, 0LL), 1LL << 30) + 1)), mexRoot(1, 0), ML(1, 0), MR(1, 0), MN(1, -1)" if mex else "") + ''' {
        for (const T& v : a) pushBack(v);
    }

    // O(logU) -- append v (valLo <= v <= valHi): it becomes a[n], and n grows by 1
    void pushBack(T v) {
        root.push_back(ins(root.back(), (long long)v, v));
''' + ('''        int prev = mexRoot.back();
        mexRoot.push_back(T(0) <= v && (long long)v <= mexHi ? mexSet(prev, 0, mexHi, int(v), n) : prev);
''' if mex else "") + '''        arr.push_back(v), n++;
    }

''' + W.CPP_OPS["pointGet"] + "\n" + cpp_query_ops(ops) + ("\n" + W.CPP_OPS["rangeMex"] if mex else "") + '''
    static long long lb(T x) { return (long long)x; }       // "values < this" for < x
    static long long ub(T x) { return (long long)x + 1; }   // "values < this" for <= x (integers)
''' + cpp_prims(True, sums) + ("\n" + CPP_MEX if mex else "") + "};\n")


# ------------------------------------------------------------------------------------------------ appends, offline

OFFLINE_ARG = "allValuesThatWillEverBeInsertedForOfflineCompression"
OFFLINE_DOC = '''{c} An array that grows: pushBack(v) appends, and queries on any a[l..r] can come in between. Every value that will
{c} ever be added is given up front (only to compress them: nothing is added until you push it), so the persistent seg
{c} tree is over compressed ranks and costs are log N, never log U: version p holds a[0..p-1], a[l..r] is version r + 1
{c} minus version l, and each append adds one version. Query arguments (x, lowVal, ...) can be anything. 0-indexed.
'''


def py_offline(ops, sums, mex):
    slots = ["arr", "n", "srt", "m", "where", "klo", "khi", "root", "L", "R", "C"] + (["S"] if sums else []) + \
        (["mexHi", "mexRoot", "ML", "MR", "MN"] if mex else [])
    return (OFFLINE_DOC.format(c="#") + ('''# rangeMex: a second persistent tree, over the values 0..(# of distinct values) + 1, holding each value's last index.
''' if mex else "") + '''from bisect import bisect_left, bisect_right


class PersistentOfflineOrderStats:
''' + f"    __slots__ = ({', '.join(repr(s) for s in slots)})\n\n" + f'''    # O(N log N) -- arr: the initial array (a list, may be empty), 0-indexed; {OFFLINE_ARG}: every value
    # pushBack will ever get (any order, duplicates fine; arr's own values are included for you). N = # of distinct values
    def __init__(self, arr, {OFFLINE_ARG}):
        self.srt = srt = sorted(set({OFFLINE_ARG}) | set(arr))
''' + '''        self.m = len(srt)
        self.where = {v: k for k, v in enumerate(srt)}
        self.klo, self.khi = 0, max(self.m - 1, 0)  # the tree is over ranks 0..m-1
        self.arr, self.n = [], 0
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree
''' + ("        self.S = [0]\n" if sums else "") + '''        self.root = [0]
''' + ('''        self.mexHi = min(self.m, 1 << 30) + 1  # mex <= (# of distinct values) < this
        self.ML, self.MR, self.MN = [0], [0], [-1]  # node 0 = the empty tree (every last index -1)
        self.mexRoot = [0]
''' if mex else "") + '''        for v in arr:
            self.pushBack(v)

    # O(logN) -- append v (one of the values given to the constructor, else ValueError): it becomes a[n], n grows by 1
    def pushBack(self, v):
        k = self.where.get(v)
        if k is None:
            raise ValueError(f"pushBack: {v} was not in the values given to the constructor")
        self.root.append(self._ins(self.root[-1], k, v))
''' + ('''        prev = self.mexRoot[-1]
        self.mexRoot.append(self._mexSet(prev, v, self.n) if 0 <= v <= self.mexHi else prev)
''' if mex else "") + '''        self.arr.append(v)
        self.n += 1

''' + "\n".join(W.PY_OPS[op] for op in W.ORDER if op in ops) + py_prims(False, sums) + ("\n" + PY_MEX if mex else ""))


def cpp_offline(ops, sums, mex):
    return (OFFLINE_DOC.format(c="//") + ('''// rangeMex: a second persistent tree, over the values 0..(# of distinct values) + 1, holding each value's last index.
''' if mex else "") + "// T: int, long long, ..." + ("; sums are kept in S (long long for small T)" if sums else "") + '''.
template <typename T>
struct PersistentOfflineOrderStats {
''' + (USING if sums else "") + '''    int n = 0, m;
    long long klo, khi;            // the tree is over ranks 0..m-1
    vector<T> arr, srt;            // srt: sorted distinct values
    vector<int> root, L, R, C;     // node 0 = the empty tree
''' + ("    vector<S> Sm;\n" if sums else "") + ('''    int mexHi;                     // mex <= (# of distinct values) < this
    vector<int> mexRoot, ML, MR, MN;
''' if mex else "") + f'''
    // O(N log N) -- arr: the initial array (may be empty), 0-indexed; {OFFLINE_ARG}: every value pushBack will
    // ever get (any order, duplicates fine; arr's own values are included for you). N = # of distinct values
    PersistentOfflineOrderStats(const vector<T>& a, vector<T> {OFFLINE_ARG})
        : srt(move({OFFLINE_ARG})), root(1, 0), L(1, 0), R(1, 0), C(1, 0)''' + (", Sm(1, S(0))" if sums else "") + ''' {
        srt.insert(srt.end(), a.begin(), a.end());
        sort(srt.begin(), srt.end());
        srt.erase(unique(srt.begin(), srt.end()), srt.end());
        m = (int)srt.size();
        klo = 0, khi = max(m - 1, 0);
''' + ('''        mexHi = min(m, 1 << 30) + 1;
        mexRoot.assign(1, 0), ML.assign(1, 0), MR.assign(1, 0), MN.assign(1, -1);
''' if mex else "") + '''        for (const T& v : a) pushBack(v);
    }

    // O(logN) -- append v (one of the values given to the constructor, else throws invalid_argument): it becomes a[n],
    // and n grows by 1
    void pushBack(T v) {
        int k = lb(v);
        if (k == m || srt[k] != v) throw invalid_argument("pushBack: v was not in the values given to the constructor");
        root.push_back(ins(root.back(), k, v));
''' + ('''        int prev = mexRoot.back();
        mexRoot.push_back(T(0) <= v && (long long)v <= mexHi ? mexSet(prev, 0, mexHi, int(v), n) : prev);
''' if mex else "") + '''        arr.push_back(v), n++;
    }

''' + "\n".join(W.CPP_OPS[op] for op in W.ORDER if op in ops) + '''
    int lb(const T& v) const { return int(lower_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    int ub(const T& v) const { return int(upper_bound(srt.begin(), srt.end(), v) - srt.begin()); }
''' + cpp_prims(False, sums) + ("\n" + CPP_MEX if mex else "") + "};\n")


# ------------------------------------------------------------------------------------------------ write

def main():
    for sums in (False, True):
        ops = sorted(W.BASE + (W.SUMS if sums else []))
        folder = "persistent-order-stats" + ("-sums" if sums else "")
        path = os.path.join(DIR, folder)
        os.makedirs(path, exist_ok=True)
        node = " ".join(f"{a}[{LOGN}]" for a in ["L", "R", "C"] + (["S"] if sums else []))
        note = "persistent seg tree over the compressed values: about N log N nodes; L/R are child pointers, C counts" + (", S sums" if sums else "")
        for sparse in (False, True):
            other = ("idx[1*N] vals[1*N] " if sparse else "") + "root[1*N] arr[1*N] srt[1*N]"
            nt = note + ("; the tree is over the given values only, and the zeros of [l, r] are added in closed form (they "
                         "sit between the negatives and the positives)" if sparse else "")
            py, cpp = py_static(ops, sums), cpp_static(ops, sums)
            if sparse:
                names = ("SparsePersistentOrderStats", "PersistentOrderStats")
                py += W.py_sparse(ops, sums, False, names)
                cpp += W.cpp_sparse(ops, sums, False, names)
            stem = "sparse" if sparse else "template"
            write_template(os.path.join(path, f"{stem}.py"), W.header("#", ops, "persistent", sparse, node, other, nt) + "\n" + py)
            write_template(os.path.join(path, f"{stem}.cpp"), W.header("//", ops, "persistent", sparse, node, other, nt) + "\n" + cpp)
        print("wrote", folder)
    for sums in (False, True):
        for mex in (False, True):
            ops = sorted(["pushBack"] + W.BASE + (W.SUMS if sums else []) + (W.MEX if mex else []))
            folder = "persistent-online-order-stats" + ("-sums" if sums else "") + ("-mex" if mex else "")
            path = os.path.join(DIR, folder)
            os.makedirs(path, exist_ok=True)
            node = " ".join(f"{a}[{LOGU}]" for a in ["L", "R", "C"] + (["S"] if sums else []))
            other = "root[1*N] arr[1*N]" + (f" mexRoot[1*N] ML[{LOGU}] MR[{LOGU}] MN[{LOGU}]" if mex else "")
            note = ("N = every value ever added (initial array plus each pushBack); each adds one root-to-leaf path of log U "
                    "nodes over the value range [valLo, valHi]" + (" (and one in the mex tree)" if mex else ""))
            for ext, cm, code in (("py", "#", py_online(ops, sums, mex)), ("cpp", "//", cpp_online(ops, sums, mex))):
                write_template(os.path.join(path, f"template.{ext}"), header(cm, ops, True, sums, mex, node, other, note) + "\n" + code)
            print("wrote", folder)
    for sums in (False, True):
        for mex in (False, True):
            ops = sorted(["pushBack"] + W.BASE + (W.SUMS if sums else []) + (W.MEX if mex else []))
            folder = "persistent-offline-order-stats" + ("-sums" if sums else "") + ("-mex" if mex else "")
            path = os.path.join(DIR, folder)
            os.makedirs(path, exist_ok=True)
            node = " ".join(f"{a}[{LOGN}]" for a in ["L", "R", "C"] + (["S"] if sums else []))
            other = "root[1*N] arr[1*N] srt[1*N]" + (f" mexRoot[1*N] ML[{LOGN}] MR[{LOGN}] MN[{LOGN}]" if mex else "")
            note = ("N = every value ever added (initial array plus each pushBack); each adds one root-to-leaf path of log N "
                    "nodes over the compressed values" + (" (and one in the mex tree)" if mex else ""))
            for ext, cm, code in (("py", "#", py_offline(ops, sums, mex)), ("cpp", "//", cpp_offline(ops, sums, mex))):
                write_template(os.path.join(path, f"template.{ext}"),
                               header(cm, ops, False, sums, mex, node, other, note, offline=True) + "\n" + code)
            print("wrote", folder)


if __name__ == "__main__":
    main()
