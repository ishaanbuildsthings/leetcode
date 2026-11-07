// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndQuery-rangeAssign-rangeSortAsc-rangeSortDesc-rangeSum-rangeXorQuery/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andAll getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeAssign rangeSortAsc rangeSortDesc rangeSum rangeXorQuery sumAll xorAll
// @data-structure-type: sorted-runs
// @complexities:
//   getAll: N*log(U)
//   pointAdd: log(N)+log(U) amortized
//   pointAssign: log(N)+log(U) amortized
//   pointChmax: log(N)+log(U) amortized
//   pointChmin: log(N)+log(U) amortized
//   pointGet: log(N)+log(U)
//   rangeAndQuery: log(N)+log(U) amortized
//   rangeAssign: log(N)+log(U) amortized
//   rangeSortAsc: log(N)+log(U) amortized
//   rangeSortDesc: log(N)+log(U) amortized
//   rangeSum: log(N)+log(U) amortized
//   rangeXorQuery: log(N)+log(U) amortized
//   sumAll: log(N)+log(U) amortized
//   xorAll: log(N)+log(U) amortized
//   andAll: log(N)+log(U) amortized
//   build: N*log(U)
// @memory:
//   layout: none
//   node: Lc[1*N*log(U)] Rc[1*N*log(U)] cnt[1*N*log(U)] sm[1*N*log(U)] xr[1*N*log(U)] av[1*N*log(U)]
//   tags: none
//   other: root[1*N] len[1*N] desc[1*N] bc[1*N] qs[4*N] qx[4*N] qa[4*N]
//   note: value nodes: N log U to start, plus O(log U) per cut (merges free nodes, which are reused); a seg tree over positions holds each run's sum / xor / and at its start; U = valHi - valLo + 1

// An array whose ranges you can sort in place (ascending or descending), amortized O(log N + log U) a sort, with point
// reads / writes, rangeAssign, range sums, range xors, range ands and the whole array. It is kept as a sequence of
// sorted runs: each run is a dynamic value seg tree over [valLo, valHi] (copies per node) and an up / down flag, and a
// Fenwick tree over positions marks where runs start, and a seg tree over positions holds each run's sum / xor / and
// at its start. Sorting [l, r] cuts the runs at l and r + 1 and merges every run inside into one; a[i] is the k-th
// value of the run holding it; a query cuts at l and r + 1 too, then reads whole runs. Merges cost about as many nodes
// as they free and every run is merged away at most once, hence the amortized bounds. Indices 0-based, ranges
// inclusive, every index is a position in the current array.
// T: int, long long, ...; sums in S (long long for small T).
// FAST MODE drawbacks compared with template.cpp:
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.
#ifdef __SSE2__
#include <immintrin.h>
#endif

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A vector whose [] and size() always inline, even with sanitizers skipped (libstdc++ only; elsewhere a plain vector)
template <typename U>
struct HotVector : vector<U> {
    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct SortedRunsSumXorAnd {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, top;
    long long vlo, vhi;
    struct VNode {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        S sm = S(0);
        long long cnt = 0;
        T xr = T(0);
        T av = T(~T(0));
        int Lc = 0;
        int Rc = 0;
    };
    HotVector<VNode> vn{VNode{}};  // value node 0 = the empty tree
    HotVector<int> freeList;  // value nodes freed by merges, reused first
    HotVector<int> root, len;  // per run start: its value tree, its length
    HotVector<char> desc;      // per run start: sorted descending?
    HotVector<int> bc;         // Fenwick: 1 at each run start
    int size;               // seg tree over positions: each run's aggregates at its start
    HotVector<S> qs;
    HotVector<T> qx;
    HotVector<T> qa;

    // O(N log U) -- arr: the initial array; every value a[i] ever holds must lie in [valLo, valHi] (U = valHi - valLo
    // + 1)
    SortedRunsSumXorAnd(const vector<T>& arr, long long valLo, long long valHi)
        : n((int)arr.size()), vlo(valLo), vhi(valHi), root(n), len(n, 1), desc(n, 0), bc(n + 1, 1) {
        for (int i = 0; i < n; i++) root[i] = leaf(arr[i]);
        top = n ? 1 << (31 - __builtin_clz(n)) : 0;
        bc[0] = 0;
        for (int i = 1; i <= n; i++) {  // O(N) Fenwick builds
            int j = i + (i & -i);
            if (j <= n) bc[j] += bc[i];
        }
        for (size = 1; size < n; size <<= 1) {}
        qs.assign(2 * size, S(0));
        qx.assign(2 * size, T(0));
        qa.assign(2 * size, T(~T(0)));
        for (int s = 0; s < n; s++) setPos(s + size, s);
        for (int p = size - 1; p > 0; p--) up(p);
    }

    // O(log N + log U) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int s = startOf(i), k = i - s;
        return kth(root[s], desc[s] ? len[s] - k : k + 1);
    }

    // O(log N + log U) amortized -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        cutAt(i), cutAt(i + 1);
        io(i, -1);
        freeTree(root[i]);
        int t = leaf(v);
        root[i] = t;
        io(i, 1);
    }

    // O(log N + log U) amortized -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + v);
    }

    // O(log N + log U) amortized -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(log N + log U) amortized -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) pointAssign(i, v);
    }

    // O(log N + log U) amortized -- sort a[l..r] ascending; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeSortAsc(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSortAsc: needs 0 <= l <= r < n");
        sortRange(l, r, false, false, T(0));
    }

    // O(log N + log U) amortized -- sort a[l..r] descending; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeSortDesc(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSortDesc: needs 0 <= l <= r < n");
        sortRange(l, r, true, false, T(0));
    }

    // O(log N + log U) amortized -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        sortRange(l, r, false, true, v);
    }

    // O(log N + log U) amortized -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        cutAt(l), cutAt(r + 1);
        return ask_qs(l, r);
    }

    // O(log N + log U) amortized -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeXorQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeXorQuery: needs 0 <= l <= r < n");
        cutAt(l), cutAt(r + 1);
        return ask_qx(l, r);
    }

    // O(log N + log U) amortized -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeAndQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndQuery: needs 0 <= l <= r < n");
        cutAt(l), cutAt(r + 1);
        return ask_qa(l, r);
    }

    // O(N log U) -- the whole current array
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out;
        out.reserve(n);
        for (int s = 0; s < n; s += len[s]) values(root[s], desc[s], out);
        return out;
    }

    // O(log(N)+log(U) amortized) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

    // O(log(N)+log(U) amortized) -- xor of the whole array a[0..n-1] (rangeXorQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto xorAll() {
        if (n < 1) throw out_of_range("xorAll: needs n >= 1");
        return rangeXorQuery(0, n - 1);
    }

    // O(log(N)+log(U) amortized) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto andAll() {
        if (n < 1) throw out_of_range("andAll: needs n >= 1");
        return rangeAndQuery(0, n - 1);
    }

    // ---- internals: runs ----

    // cut at l and r + 1, then turn a[l..r] into one run: every run inside merged (assign false) or thrown away for a
    // run of r - l + 1 copies of v
    LEETCODE_NO_SANITIZE void sortRange(int l, int r, bool d, bool assign, T v) {
        cutAt(l), cutAt(r + 1);
        io(l, -1);
        int t = root[l];
        if (assign) freeTree(t);
        for (int s = l + len[l]; s <= r;) {  // every run inside goes
            int b = root[s], nxt = s + len[s];
            io(s, -1);
            fen(bc, s, -1);
            if (assign) freeTree(b);
            else t = merge(t, b, vlo, vhi);
            s = nxt;
        }
        if (assign) t = leaf(v, r - l + 1);
        root[l] = t, len[l] = r - l + 1, desc[l] = d;
        io(l, 1);
    }

    // make a run start at p (0 < p < n): split the run holding it by count
    LEETCODE_NO_SANITIZE void cutAt(int p) {
        if (p <= 0 || p >= n) return;
        int s = startOf(p);
        if (s == p) return;
        io(s, -1);
        int t = root[s], k = p - s, ln = len[s], a, b;
        if (desc[s]) split(t, ln - k, vlo, vhi, b, a);  // the first k are the k largest
        else split(t, k, vlo, vhi, a, b);
        root[s] = a, len[s] = k;
        root[p] = b, len[p] = ln - k, desc[p] = desc[s];
        fen(bc, p, 1);
        io(s, 1);
        io(p, 1);
    }

    // the start of the run holding i: the (# of starts <= i)-th start, by binary lifting
    LEETCODE_NO_SANITIZE int startOf(int i) const {
        int k = pre(bc, i + 1), pos = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= n && bc[pos + step] < k) pos += step, k -= bc[pos];
        return pos;
    }

    template <class V>
    LEETCODE_NO_SANITIZE void fen(vector<V>& f, int i, V v) {
        for (i++; i <= n; i += i & -i) f[i] += v;
    }

    template <class V>
    LEETCODE_NO_SANITIZE static V pre(const vector<V>& f, int i) {  // f's total over positions 0..i-1
        V s = 0;
        for (; i > 0; i &= i - 1) s += f[i];
        return s;
    }

    // leaf p of the position tree <- the aggregates of the run starting at s
    LEETCODE_NO_SANITIZE void setPos(int p, int s) {
        int t = root[s];
        qs[p] = vn[t].sm;
        qx[p] = vn[t].xr;
        qa[p] = vn[t].av;
    }

    LEETCODE_NO_SANITIZE void up(int p) {
        qs[p] = qs[2 * p] + qs[2 * p + 1];
        qx[p] = qx[2 * p] ^ qx[2 * p + 1];
        qa[p] = qa[2 * p] & qa[2 * p + 1];
    }

    // add (sgn = 1) or take out (sgn = -1) the run starting at s from the position tree
    LEETCODE_NO_SANITIZE void io(int s, int sgn) {
        int p = s + size;
        if (sgn > 0) setPos(p, s);
        else qs[p] = S(0), qx[p] = T(0), qa[p] = T(~T(0));
        for (p >>= 1; p; p >>= 1) up(p);
    }

    LEETCODE_NO_SANITIZE S ask_qs(int l, int r) const {  // the sum over positions l..r
        S res = S(0);
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res += qs[l++];
            if (r & 1) res += qs[--r];
        }
        return res;
    }

    LEETCODE_NO_SANITIZE T ask_qx(int l, int r) const {  // the xor over positions l..r
        T res = T(0);
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res ^= qx[l++];
            if (r & 1) res ^= qx[--r];
        }
        return res;
    }

    LEETCODE_NO_SANITIZE T ask_qa(int l, int r) const {  // the and over positions l..r
        T res = T(~T(0));
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res &= qa[l++];
            if (r & 1) res &= qa[--r];
        }
        return res;
    }

    // ---- internals: value trees (node 0 = the empty tree) ----

    LEETCODE_NO_SANITIZE int node() {
        if (!freeList.empty()) {
            int t = freeList.back();
            freeList.pop_back();
            vn[t].Lc = vn[t].Rc = 0, vn[t].cnt = 0;
            return t;
        }
        VNode n;
        n.Lc = 0, n.Rc = 0, n.cnt = 0, n.sm = S(0), n.xr = T(0), n.av = T(~T(0));
        vn.push_back(n);
        return (int)vn.size() - 1;
    }

    LEETCODE_NO_SANITIZE void freeTree(int t) {  // hand every node of t back
        vector<int> st;
        if (t) st.push_back(t);
        while (!st.empty()) {
            int u = st.back();
            st.pop_back();
            freeList.push_back(u);
            if (vn[u].Lc) st.push_back(vn[u].Lc);
            if (vn[u].Rc) st.push_back(vn[u].Rc);
        }
    }

    // node x holds c copies of v (a leaf, or a node with one value under it)
    LEETCODE_NO_SANITIZE void setLeaf(int x, long long v, long long c) {
        vn[x].cnt = c;
        vn[x].sm = S(c) * S(v);
        vn[x].xr = (c & 1) ? T(v) : T(0);
        vn[x].av = T(v);
    }

    LEETCODE_NO_SANITIZE void pull(int x) {
        int l = vn[x].Lc, r = vn[x].Rc;
        vn[x].cnt = vn[l].cnt + vn[r].cnt;
        vn[x].sm = vn[l].sm + vn[r].sm;
        vn[x].xr = vn[l].xr ^ vn[r].xr;
        vn[x].av = vn[l].av & vn[r].av;
    }

    // a tree holding c copies of v: one node per level
    LEETCODE_NO_SANITIZE int leaf(T v, long long c = 1) {
        int top_ = node(), t = top_;
        long long nl = vlo, nh = vhi;
        while (true) {
            setLeaf(t, (long long)v, c);
            if (nl == nh) return top_;
            long long mid = nl + (nh - nl) / 2;
            int u = node();
            if ((long long)v <= mid) vn[t].Lc = u, nh = mid;
            else vn[t].Rc = u, nl = mid + 1;
            t = u;
        }
    }

    // a = the k smallest of t, b = the rest (0 <= k <= cnt[t]); t keeps the first part, new nodes (one path) the second
    LEETCODE_NO_SANITIZE void split(int t, long long k, long long nl, long long nh, int& a, int& b) {
        if (k <= 0) { a = 0, b = t; return; }
        if (k >= vn[t].cnt) { a = t, b = 0; return; }
        int nb = node();
        if (nl == nh) {  // one value: split its copies
            setLeaf(nb, nl, vn[t].cnt - k), setLeaf(t, nl, k);
            a = t, b = nb;
            return;
        }
        long long mid = nl + (nh - nl) / 2, cl = vn[vn[t].Lc].cnt;
        int x, y;
        if (k <= cl) {
            split(vn[t].Lc, k, nl, mid, x, y);
            vn[t].Lc = x, vn[nb].Lc = y, vn[nb].Rc = vn[t].Rc, vn[t].Rc = 0;
        } else {
            split(vn[t].Rc, k - cl, mid + 1, nh, x, y);
            vn[t].Rc = x, vn[nb].Rc = y;
        }
        pull(t), pull(nb);
        a = t, b = nb;
    }

    // the union of a and b, overlaid node by node (b's nodes where both have one are freed)
    LEETCODE_NO_SANITIZE int merge(int a, int b, long long nl, long long nh) {
        if (!a || !b) return a ? a : b;
        if (nl == nh) {
            setLeaf(a, nl, vn[a].cnt + vn[b].cnt);
        } else {
            long long mid = nl + (nh - nl) / 2;
            int x = merge(vn[a].Lc, vn[b].Lc, nl, mid);
            vn[a].Lc = x;
            int y = merge(vn[a].Rc, vn[b].Rc, mid + 1, nh);
            vn[a].Rc = y;
            pull(a);
        }
        freeList.push_back(b);
        return a;
    }

    // the k-th smallest value of t, 1 <= k <= cnt[t]
    LEETCODE_NO_SANITIZE T kth(int t, long long k) const {
        long long nl = vlo, nh = vhi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, cl = vn[vn[t].Lc].cnt;
            if (k <= cl) t = vn[t].Lc, nh = mid;
            else k -= cl, t = vn[t].Rc, nl = mid + 1;
        }
        return T(nl);
    }

    // append t's values, ascending (or descending), to out
    LEETCODE_NO_SANITIZE void values(int t, bool d, vector<T>& out) const {
        size_t from = out.size();
        vector<tuple<int, long long, long long>> st{{t, vlo, vhi}};
        while (!st.empty()) {  // in-order, pushed right first
            auto [u, nl, nh] = st.back();
            st.pop_back();
            if (!vn[u].cnt) continue;
            if (nl == nh) {
                out.insert(out.end(), vn[u].cnt, T(nl));
                continue;
            }
            long long mid = nl + (nh - nl) / 2;
            st.push_back({vn[u].Rc, mid + 1, nh}), st.push_back({vn[u].Lc, nl, mid});
        }
        if (d) reverse(out.begin() + from, out.end());
    }
};
