"""Order statistics over a[l..r] WITH point updates: a Fenwick tree (BIT) over positions whose every node is a dynamic
value seg tree over [valLo, valHi]. a[l..r]'s multiset is (BIT prefix r+1) minus (BIT prefix l), so a query walks
down all ~2 log N of those value trees at once: O(log N log U) for queries and point updates alike (U = valHi - valLo + 1).

    python3 gen_dynamic_order.py

Two templates (counts only, and counts + sums), each with a sparse version: any index range [lo, hi], every position
starting at 0 (only nonzero values are stored; the zeros of [l, r] are added in closed form, between the negatives and
the positives). The query methods are gen_wavelet.py's, with value thresholds in place of compressed ranks.
"""
import os
import re

from gen_wavelet import BASE, CPP_OPS, ORDER, PY_OPS, SUMS
from note_lang import write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
POINT_UPD = ["pointAdd", "pointAssign", "pointChmax", "pointChmin"]
DTYPE = "bit-of-trees"


def header(cm, ops, sums, sparse):
    q = "log(U)*log(U)" if sparse else "log(N)*log(U)"
    lines = [f"@operations: {' '.join(ops)}", f"@data-structure-type: {DTYPE}", "@complexities:"]
    lines += [f"  {op}: {'1' if op == 'pointGet' else q}" for op in ops] + [f"  build: {'1' if sparse else 'N*log(N)*log(U)'}"]
    per = "1*log(U)*log(U)" if sparse else "1*N*log(N)*log(U)"
    node = " ".join(f"{a}[{per}]" for a in ["L", "R", "C"] + (["S"] if sums else []))
    other = "root[1*log(U)] vals[1]" if sparse else "root[1*N] arr[1*N]"
    if sparse:
        note = ("any index range [lo, hi], every position starting at 0; only nonzero values are stored, and the zeros of "
                "[l, r] are counted in closed form; U = the larger of the index range and the value range [valLo, valHi]; "
                "sizes are per point update")
    else:
        note = ("BIT over positions, each BIT node a dynamic value seg tree over [valLo, valHi] (U = its size); nodes are "
                "never freed, so each point update adds up to 2 log N log U of them")
    lines += ["@memory:", f"  layout: {'sparse' if sparse else 'none'}", f"  node: {node}", "  tags: none", f"  other: {other}",
              f"  note: {note}"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


# ------------------------------------------------------------------------------------------------ Python

def py_query_ops(ops):
    out = []
    for op in ORDER:
        if op in ops and op != "pointGet" and op != "rangeMex":
            t = PY_OPS[op]
            t = re.sub(r"bisect_left\(self\.srt, (\w+)\)", r"\1", t)
            t = re.sub(r"bisect_right\(self\.srt, (\w+)\)", r"\1 + 1", t)  # integer values: <= x is < x + 1
            out.append(t)
    return "\n".join(out)


PY_DOC = '''# a[l..r] as a sorted multiset, with point updates. A Fenwick tree (BIT) over positions: BIT node j is a dynamic value
# seg tree over [valLo, valHi] holding the values of a[j - lowbit(j) .. j - 1]. The multiset of a[l..r] is the BIT
# prefix of r + 1 minus the prefix of l, so a query walks down those ~2 log N value trees together (pos adds, neg
# subtracts). Values are integers; query arguments (x, lowVal, ...) can be anything.
'''

PY_CORE = '''
    # ---- internals: walks over the value trees in pos (added) and neg (subtracted) ----

    def _newNode(self):
        self.L.append(0), self.R.append(0), self.C.append(0){snew}
        return len(self.C) - 1

    # tree t (0: a new one) with d more copies of v
    def _ins(self, t, v, d):
        L, R, C{scomma} = self.L, self.R, self.C{sself}
        if not t:
            t = self._newNode()
        top, nl, nh = t, self.vlo, self.vhi
        while True:
            C[t] += d
{sins}            if nl == nh:
                return top
            mid = (nl + nh) >> 1
            if v <= mid:
                if not L[t]:
                    L[t] = self._newNode()
                t, nh = L[t], mid
            else:
                if not R[t]:
                    R[t] = self._newNode()
                t, nl = R[t], mid + 1

    def _total(self, pos, neg, A):
        return sum(A[t] for t in pos) - sum(A[t] for t in neg)

    # the k-th smallest value, 1 <= k <= the trees' count
    def _kthIn(self, pos, neg, k):
        L, R, C = self.L, self.R, self.C
        nl, nh = self.vlo, self.vhi
        while nl != nh:
            mid = (nl + nh) >> 1
            c = sum(C[L[t]] for t in pos) - sum(C[L[t]] for t in neg)
            if k <= c:
                pos, neg, nh = [L[t] for t in pos if L[t]], [L[t] for t in neg if L[t]], mid
            else:
                k -= c
                pos, neg, nl = [R[t] for t in pos if R[t]], [R[t] for t in neg if R[t]], mid + 1
        return nl

    # (# of values < x, their sum), valLo < x <= valHi
    def _belowIn(self, pos, neg, x):
        L, R, C{scomma} = self.L, self.R, self.C{sself}
        nl, nh, cnt, sm = self.vlo, self.vhi, 0, 0
        while nl != nh:
            mid = (nl + nh) >> 1
            if x <= mid:
                pos, neg, nh = [L[t] for t in pos if L[t]], [L[t] for t in neg if L[t]], mid
            else:  # the whole left half is below x
                cnt += sum(C[L[t]] for t in pos) - sum(C[L[t]] for t in neg)
{sbelow}                pos, neg, nl = [R[t] for t in pos if R[t]], [R[t] for t in neg if R[t]], mid + 1
        return cnt, sm
'''
PY_SUM_CORE = '''
    # sum of the k smallest values, 0 <= k <= the trees' count
    def _sumFirstIn(self, pos, neg, k):
        if k <= 0:
            return 0
        L, R, C, S = self.L, self.R, self.C, self.S
        nl, nh, res = self.vlo, self.vhi, 0
        while nl != nh:
            mid = (nl + nh) >> 1
            c = sum(C[L[t]] for t in pos) - sum(C[L[t]] for t in neg)
            if k <= c:
                pos, neg, nh = [L[t] for t in pos if L[t]], [L[t] for t in neg if L[t]], mid
            else:  # the whole left half is among the k smallest
                k -= c
                res += sum(S[L[t]] for t in pos) - sum(S[L[t]] for t in neg)
                pos, neg, nl = [R[t] for t in pos if R[t]], [R[t] for t in neg if R[t]], mid + 1
        return res + k * nl
'''


def py_core(sums):
    return PY_CORE.format(
        snew=", self.S.append(0)" if sums else "", scomma=", S" if sums else "", sself=", self.S" if sums else "",
        sins="            S[t] += d * v\n" if sums else "",
        sbelow="                sm += sum(S[L[t]] for t in pos) - sum(S[L[t]] for t in neg)\n" if sums else "") + (PY_SUM_CORE if sums else "")


PY_POINT = '''    # O(1) -- a[i]
    def pointGet(self, i):
        return {get}

    # O(logN logU) -- a[i] = v
    def pointAssign(self, i, v):
        old = {get}
        if v != old:
            {assign}

    # O(logN logU) -- a[i] += v
    def pointAdd(self, i, v):
        self.pointAssign(i, self.pointGet(i) + v)

    # O(logN logU) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        self.pointAssign(i, max(self.pointGet(i), v))

    # O(logN logU) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        self.pointAssign(i, min(self.pointGet(i), v))
'''


def py_dense(ops, sums):
    slots = ["arr", "n", "vlo", "vhi", "root", "L", "R", "C"] + (["S"] if sums else [])
    return (PY_DOC + "\n\nclass DynamicOrderStats:\n" + f"    __slots__ = ({', '.join(repr(s) for s in slots)})\n\n" + '''    # O(N log N log U) -- arr: the initial array (a list), 0-indexed; every value a[i] ever holds must lie in
    # [valLo, valHi] (any integers, negative is fine; U = valHi - valLo + 1)
    def __init__(self, arr, valLo, valHi):
        self.arr = list(arr)
        self.n = len(arr)
        self.vlo, self.vhi = valLo, valHi
        self.root = [0] * (self.n + 1)  # BIT node j's value tree (0: empty)
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree
''' + ("        self.S = [0]\n" if sums else "") + '''        for i, v in enumerate(arr):
            self._add(i, v, 1)

''' + PY_POINT.format(get="self.arr[i]", assign="self._add(i, old, -1)\n            self._add(i, v, 1)\n            self.arr[i] = v") + "\n" +
            py_query_ops(ops) + '''
    # ---- internals ----

    # a[i] = v gains d copies in every BIT node covering i
    def _add(self, i, v, d):
        j = i + 1
        while j <= self.n:
            self.root[j] = self._ins(self.root[j], v, d)
            j += j & -j

    # (trees to add, trees to subtract) for a[l..r]
    def _sides(self, l, r):
        root, pos, neg = self.root, [], []
        j = r + 1
        while j:
            pos.append(root[j])
            j &= j - 1
        j = l
        while j:
            neg.append(root[j])
            j &= j - 1
        return pos, neg

    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    def _kth(self, l, r, k):
        return self._kthIn(*self._sides(l, r), k)

    # # of values < x in a[l..r]
    def _countBelow(self, l, r, x):
        if x <= self.vlo:
            return 0
        if x > self.vhi:
            return r - l + 1
        return self._belowIn(*self._sides(l, r), x)[0]
''' + ('''
    # sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    def _sumFirst(self, l, r, k):
        return self._sumFirstIn(*self._sides(l, r), k)

    # sum of the values < x in a[l..r]
    def _sumBelow(self, l, r, x):
        if x <= self.vlo:
            return 0
        pos, neg = self._sides(l, r)
        return self._total(pos, neg, self.S) if x > self.vhi else self._belowIn(pos, neg, x)[1]
''' if sums else "") + py_core(sums))


def py_sparse(ops, sums):
    slots = ["lo", "hi", "vals", "vlo", "vhi", "root", "L", "R", "C"] + (["S"] if sums else [])
    return (PY_DOC.replace("over positions:", "over the index range [lo, hi]:") + '''# Sparse: every position of [lo, hi] starts at 0 and only nonzero values are stored; the zeros of [l, r] (its length
# minus the stored values in it) sit between the stored negatives and positives.


class SparseDynamicOrderStats:
''' + f"    __slots__ = ({', '.join(repr(s) for s in slots)})\n\n" + '''    # O(1) -- indices: any integers in [lo, hi], every position starting at 0; every value a[i] ever holds must lie in
    # [valLo, valHi] (U = the larger of the two ranges' sizes)
    def __init__(self, lo, hi, valLo, valHi):
        self.lo, self.hi = lo, hi
        self.vlo, self.vhi = valLo, valHi
        self.vals = {}  # nonzero values only
        self.root = {}  # BIT node -> its value tree (missing: empty)
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree
''' + ("        self.S = [0]\n" if sums else "") + "\n" +
            PY_POINT.format(get="self.vals.get(i, 0)", assign='''if old:
                self._add(i, old, -1)
            if v:
                self._add(i, v, 1)
                self.vals[i] = v
            else:
                self.vals.pop(i, None)''') + "\n" + py_query_ops(ops) + '''
    # ---- internals ----

    # a[i] = v gains d copies in every BIT node covering i
    def _add(self, i, v, d):
        j, m = i - self.lo + 1, self.hi - self.lo + 1
        while j <= m:
            self.root[j] = self._ins(self.root.get(j, 0), v, d)
            j += j & -j

    # (trees to add, trees to subtract, zeros in a[l..r])
    def _sides(self, l, r):
        root, pos, neg = self.root, [], []
        j = r - self.lo + 1
        while j:
            pos.append(root.get(j, 0))
            j &= j - 1
        j = l - self.lo
        while j:
            neg.append(root.get(j, 0))
            j &= j - 1
        return pos, neg, (r - l + 1) - self._total(pos, neg, self.C)

    # # of stored (nonzero) values < x
    def _storedBelow(self, pos, neg, x):
        if x <= self.vlo:
            return 0
        if x > self.vhi:
            return self._total(pos, neg, self.C)
        return self._belowIn(pos, neg, x)[0]

    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    def _kth(self, l, r, k):
        pos, neg, zeros = self._sides(l, r)
        negs = self._storedBelow(pos, neg, 0)
        if k <= negs:
            return self._kthIn(pos, neg, k)
        if k <= negs + zeros:
            return 0
        return self._kthIn(pos, neg, k - zeros)

    # # of values < x in a[l..r]
    def _countBelow(self, l, r, x):
        pos, neg, zeros = self._sides(l, r)
        return self._storedBelow(pos, neg, x) + (zeros if 0 < x else 0)
''' + ('''
    # sum of the k smallest of a[l..r], 0 <= k <= r - l + 1 (zeros add nothing)
    def _sumFirst(self, l, r, k):
        pos, neg, zeros = self._sides(l, r)
        negs = self._storedBelow(pos, neg, 0)
        return self._sumFirstIn(pos, neg, k if k <= negs else max(negs, k - zeros))

    # sum of the values < x in a[l..r] (zeros add nothing)
    def _sumBelow(self, l, r, x):
        if x <= self.vlo:
            return 0
        pos, neg, _ = self._sides(l, r)
        return self._total(pos, neg, self.S) if x > self.vhi else self._belowIn(pos, neg, x)[1]
''' if sums else "") + py_core(sums))


# ------------------------------------------------------------------------------------------------ C++

def cpp_query_ops(ops):
    out = []
    for op in ORDER:
        if op in ops and op != "pointGet" and op != "rangeMex":
            t = CPP_OPS[op]
            for a, b in (("(int l, int r", "(long long l, long long r"), (", int k)", ", long long k)"),
                         (", int kFrom, int kTo)", ", long long kFrom, long long kTo)"), ("    int count", "    long long count"),
                         ("int n = r - l + 1", "long long n = r - l + 1"), ("int c = countBelow", "long long c = countBelow"),
                         ("int rk = lb(x), c = countBelow(l, r, rk);", "long long rk = lb(x), c = countBelow(l, r, rk);")):
                t = t.replace(a, b)
            out.append(t)
    return "\n".join(out)


CPP_DOC = '''// a[l..r] as a sorted multiset, with point updates. A Fenwick tree (BIT) over positions: BIT node j is a dynamic
// value seg tree over [valLo, valHi] holding the values of a[j - lowbit(j) .. j - 1]. The multiset of a[l..r] is the BIT
// prefix of r + 1 minus the prefix of l, so a query walks down those ~2 log N value trees together (pos adds, neg
// subtracts). Values are integers; query arguments (x, lowVal, ...) can be anything.
'''

CPP_CORE = '''
    // ---- internals: walks over the value trees in pos (added) and neg (subtracted) ----

    // a value threshold as "values < this": lb(x) = x, ub(x) = x + 1 (integers)
    static long long lb(T x) { return (long long)x; }
    static long long ub(T x) { return (long long)x + 1; }

    int newNode() {
        L.push_back(0), R.push_back(0), C.push_back(0){snew};
        return (int)C.size() - 1;
    }

    // tree t (0: a new one) with d more copies of v
    int ins(int t, T v, int d) {
        if (!t) t = newNode();
        int top = t;
        long long nl = vlo, nh = vhi;
        while (true) {
            C[t] += d;
{sins}            if (nl == nh) return top;
            long long mid = nl + (nh - nl) / 2;
            if (v <= mid) {
                if (!L[t]) { int x = newNode(); L[t] = x; }
                t = L[t], nh = mid;
            } else {
                if (!R[t]) { int x = newNode(); R[t] = x; }
                t = R[t], nl = mid + 1;
            }
        }
    }

    template <class A> auto total(const vector<int>& pos, const vector<int>& neg, const vector<A>& a) const {
        A s = 0;
        for (int t : pos) s += a[t];
        for (int t : neg) s -= a[t];
        return s;
    }
    void goLeft(vector<int>& v) const { for (int& t : v) t = L[t]; }
    void goRight(vector<int>& v) const { for (int& t : v) t = R[t]; }
    long long leftCount(const vector<int>& pos, const vector<int>& neg) const {
        long long c = 0;
        for (int t : pos) c += C[L[t]];
        for (int t : neg) c -= C[L[t]];
        return c;
    }

    // the k-th smallest value, 1 <= k <= the trees' count
    T kthIn(vector<int> pos, vector<int> neg, long long k) const {
        long long nl = vlo, nh = vhi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = leftCount(pos, neg);
            if (k <= c) goLeft(pos), goLeft(neg), nh = mid;
            else k -= c, goRight(pos), goRight(neg), nl = mid + 1;
        }
        return T(nl);
    }

    // # of values < x, valLo < x <= valHi{sbelowdoc}
    {btype} belowIn(vector<int> pos, vector<int> neg, long long x) const {
        long long nl = vlo, nh = vhi, cnt = 0;
{sbelowinit}        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (x <= mid) goLeft(pos), goLeft(neg), nh = mid;
            else {  // the whole left half is below x
                cnt += leftCount(pos, neg);
{sbelow}                goRight(pos), goRight(neg), nl = mid + 1;
            }
        }
        return {bret};
    }
'''
CPP_SUM_CORE = '''
    // sum of the k smallest values, 0 <= k <= the trees' count
    S sumFirstIn(vector<int> pos, vector<int> neg, long long k) const {
        if (k <= 0) return 0;
        long long nl = vlo, nh = vhi;
        S res = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = leftCount(pos, neg);
            if (k <= c) goLeft(pos), goLeft(neg), nh = mid;
            else {  // the whole left half is among the k smallest
                k -= c;
                for (int t : pos) res += Sm[L[t]];
                for (int t : neg) res -= Sm[L[t]];
                goRight(pos), goRight(neg), nl = mid + 1;
            }
        }
        return res + S(k) * S(nl);
    }
'''


def cpp_core(sums):
    return _fill(CPP_CORE, **dict(
        snew=", Sm.push_back(S(0))" if sums else "", sins="            Sm[t] += S(v) * d;\n" if sums else "",
        sbelowdoc=", and their sum" if sums else "", btype="pair<long long, S>" if sums else "long long",
        sbelowinit="        S sm = 0;\n" if sums else "",
        sbelow="                for (int t : pos) sm += Sm[L[t]];\n                for (int t : neg) sm -= Sm[L[t]];\n" if sums else "",
        bret="{cnt, sm}" if sums else "cnt")) + (CPP_SUM_CORE if sums else "")


def _fill(text, **kw):  # str.format without touching C++ braces
    for k, v in kw.items():
        text = text.replace("{" + k + "}", v)
    return text


CPP_POINT = '''    // O(1) -- a[i]
    T pointGet(long long i) const {{ return {get}; }}

    // O(logN logU) -- a[i] = v
    void pointAssign(long long i, T v) {{
        T old = pointGet(i);
        if (v == old) return;
{assign}    }}

    // O(logN logU) -- a[i] += v
    void pointAdd(long long i, T v) {{ pointAssign(i, pointGet(i) + v); }}

    // O(logN logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) {{ pointAssign(i, max(pointGet(i), v)); }}

    // O(logN logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) {{ pointAssign(i, min(pointGet(i), v)); }}
'''

USING = "    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n"


def cpp_dense(ops, sums):
    below = "belowIn(pos, neg, x).first" if sums else "belowIn(pos, neg, x)"
    return (CPP_DOC + "// T: int, long long, ..." + ("; sums are kept in S (long long for small T)" if sums else "") +
            ".\ntemplate <typename T>\nstruct DynamicOrderStats {\n" + (USING if sums else "") + '''    int n;
    long long vlo, vhi;
    vector<T> arr;
    vector<int> root, L, R, C;  // root[j]: BIT node j's value tree; node 0 = the empty tree
''' + ("    vector<S> Sm;\n" if sums else "") + '''
    // O(N log N log U) -- arr: the initial array, 0-indexed; every value a[i] ever holds must lie in [valLo, valHi]
    // (any integers, negative is fine; U = valHi - valLo + 1)
    DynamicOrderStats(const vector<T>& a, long long valLo, long long valHi)
        : n((int)a.size()), vlo(valLo), vhi(valHi), arr(a), root(n + 1, 0), L(1, 0), R(1, 0), C(1, 0)''' +
            (", Sm(1, S(0))" if sums else "") + ''' {
        for (int i = 0; i < n; i++) add(i, a[i], 1);
    }

''' + CPP_POINT.format(get="arr[i]", assign="        add(i, old, -1), add(i, v, 1), arr[i] = v;\n") + "\n" + cpp_query_ops(ops) + f'''
    // ---- internals ----

    // a[i] = v gains d copies in every BIT node covering i
    void add(long long i, T v, int d) {{
        for (long long j = i + 1; j <= n; j += j & -j) root[j] = ins(root[j], v, d);
    }}

    // trees to add / subtract for a[l..r]
    void sides(long long l, long long r, vector<int>& pos, vector<int>& neg) const {{
        for (long long j = r + 1; j; j &= j - 1) pos.push_back(root[j]);
        for (long long j = l; j; j &= j - 1) neg.push_back(root[j]);
    }}

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    T kth(long long l, long long r, long long k) const {{
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return kthIn(pos, neg, k);
    }}

    // # of values < x in a[l..r]
    long long countBelow(long long l, long long r, long long x) const {{
        if (x <= vlo) return 0;
        if (x > vhi) return r - l + 1;
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return {below};
    }}
''' + ('''
    // sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    S sumFirst(long long l, long long r, long long k) const {
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return sumFirstIn(pos, neg, k);
    }

    // sum of the values < x in a[l..r]
    S sumBelow(long long l, long long r, long long x) const {
        if (x <= vlo) return 0;
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return x > vhi ? total(pos, neg, Sm) : belowIn(pos, neg, x).second;
    }
''' if sums else "") + cpp_core(sums) + "};\n")


SAFE_HASH = '''    struct SafeHash {
        size_t operator()(long long x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
'''


def cpp_sparse(ops, sums):
    below = "belowIn(pos, neg, x).first" if sums else "belowIn(pos, neg, x)"
    return (CPP_DOC.replace("over positions:", "over the index range [lo, hi]:") + '''// Sparse: every position of [lo, hi] starts at 0 and only nonzero values are stored; the zeros of [l, r] (its length
// minus the stored values in it) sit between the stored negatives and positives.
// T: int, long long, ...''' + ("; sums are kept in S (long long for small T)" if sums else "") +
            ".\ntemplate <typename T>\nstruct SparseDynamicOrderStats {\n" + (USING if sums else "") + SAFE_HASH + '''    long long lo, hi, vlo, vhi;
    unordered_map<long long, T, SafeHash> vals;     // nonzero values only
    unordered_map<long long, int, SafeHash> root;   // BIT node -> its value tree (missing: empty)
    vector<int> L, R, C;                            // node 0 = the empty tree
''' + ("    vector<S> Sm;\n" if sums else "") + '''
    // O(1) -- indices: any integers in [lo, hi], every position starting at 0; every value a[i] ever holds must lie in
    // [valLo, valHi] (U = the larger of the two ranges' sizes)
    SparseDynamicOrderStats(long long lo, long long hi, long long valLo, long long valHi)
        : lo(lo), hi(hi), vlo(valLo), vhi(valHi), L(1, 0), R(1, 0), C(1, 0)''' + (", Sm(1, S(0))" if sums else "") + ''' {}

''' + CPP_POINT.format(get="vals.count(i) ? vals.at(i) : T(0)", assign='''        if (old != T(0)) add(i, old, -1);
        if (v != T(0)) add(i, v, 1), vals[i] = v;
        else vals.erase(i);
''') + "\n" + cpp_query_ops(ops) + f'''
    // ---- internals ----

    // a[i] = v gains d copies in every BIT node covering i
    void add(long long i, T v, int d) {{
        for (long long j = i - lo + 1, m = hi - lo + 1; j <= m; j += j & -j) {{
            auto it = root.find(j);
            int t = ins(it == root.end() ? 0 : it->second, v, d);
            root[j] = t;
        }}
    }}

    // trees to add / subtract for a[l..r]; returns the zeros in a[l..r]
    long long sides(long long l, long long r, vector<int>& pos, vector<int>& neg) const {{
        for (long long j = r - lo + 1; j; j &= j - 1) if (auto it = root.find(j); it != root.end()) pos.push_back(it->second);
        for (long long j = l - lo; j; j &= j - 1) if (auto it = root.find(j); it != root.end()) neg.push_back(it->second);
        return (r - l + 1) - total(pos, neg, C);
    }}

    // # of stored (nonzero) values < x
    long long storedBelow(const vector<int>& pos, const vector<int>& neg, long long x) const {{
        if (x <= vlo) return 0;
        if (x > vhi) return total(pos, neg, C);
        return {below};
    }}

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    T kth(long long l, long long r, long long k) const {{
        vector<int> pos, neg;
        long long zeros = sides(l, r, pos, neg), negs = storedBelow(pos, neg, 0);
        if (k <= negs) return kthIn(pos, neg, k);
        if (k <= negs + zeros) return T(0);
        return kthIn(pos, neg, k - zeros);
    }}

    // # of values < x in a[l..r]
    long long countBelow(long long l, long long r, long long x) const {{
        vector<int> pos, neg;
        long long zeros = sides(l, r, pos, neg);
        return storedBelow(pos, neg, x) + (0 < x ? zeros : 0);
    }}
''' + ('''
    // sum of the k smallest of a[l..r], 0 <= k <= r - l + 1 (zeros add nothing)
    S sumFirst(long long l, long long r, long long k) const {
        vector<int> pos, neg;
        long long zeros = sides(l, r, pos, neg), negs = storedBelow(pos, neg, 0);
        return sumFirstIn(pos, neg, k <= negs ? k : max(negs, k - zeros));
    }

    // sum of the values < x in a[l..r] (zeros add nothing)
    S sumBelow(long long l, long long r, long long x) const {
        if (x <= vlo) return 0;
        vector<int> pos, neg;
        sides(l, r, pos, neg);
        return x > vhi ? total(pos, neg, Sm) : belowIn(pos, neg, x).second;
    }
''' if sums else "") + cpp_core(sums) + "};\n")


def main():
    for sums in (False, True):
        ops = sorted(POINT_UPD + BASE + (SUMS if sums else []))
        folder = f"{DTYPE}-order-stats" + ("-sums" if sums else "")
        path = os.path.join(DIR, folder)
        os.makedirs(path, exist_ok=True)
        write_template(os.path.join(path, "template.py"), header("#", ops, sums, False) + "\n" + py_dense(ops, sums))
        write_template(os.path.join(path, "template.cpp"), header("//", ops, sums, False) + "\n" + cpp_dense(ops, sums))
        write_template(os.path.join(path, "sparse.py"), header("#", ops, sums, True) + "\n" + py_sparse(ops, sums))
        write_template(os.path.join(path, "sparse.cpp"), header("//", ops, sums, True) + "\n" + cpp_sparse(ops, sums))
        print("wrote", folder)


if __name__ == "__main__":
    main()
