// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndQuery-rangeAssign-rangeMax-rangeSortAsc-rangeSortDesc-rangeSum/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andAll getAll maxAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeAssign rangeMax rangeSortAsc rangeSortDesc rangeSum sumAll
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
//   rangeMax: log(N)+log(U) amortized
//   rangeSortAsc: log(N)+log(U) amortized
//   rangeSortDesc: log(N)+log(U) amortized
//   rangeSum: log(N)+log(U) amortized
//   sumAll: log(N)+log(U) amortized
//   maxAll: log(N)+log(U) amortized
//   andAll: log(N)+log(U) amortized
//   build: N*log(U)
// @memory:
//   layout: none
//   node: Lc[1*N*log(U)] Rc[1*N*log(U)] cnt[1*N*log(U)] sm[1*N*log(U)] av[1*N*log(U)]
//   tags: none
//   other: root[1*N] len[1*N] desc[1*N] bc[1*N] qs[4*N] qm[4*N] qa[4*N]
//   note: value nodes: N log U to start, plus O(log U) per cut (merges free nodes, which are reused); a seg tree over positions holds each run's sum / max / and at its start; U = valHi - valLo + 1

// An array whose ranges you can sort in place (ascending or descending), amortized O(log N + log U) a sort, with point
// reads / writes, rangeAssign, range sums, range maxes, range ands and the whole array. It is kept as a sequence of
// sorted runs: each run is a dynamic value seg tree over [valLo, valHi] (copies per node) and an up / down flag, and a
// Fenwick tree over positions marks where runs start, and a seg tree over positions holds each run's sum / max / and
// at its start. Sorting [l, r] cuts the runs at l and r + 1 and merges every run inside into one; a[i] is the k-th
// value of the run holding it; a query cuts at l and r + 1 too, then reads whole runs. Merges cost about as many nodes
// as they free and every run is merged away at most once, hence the amortized bounds. Indices 0-based, ranges
// inclusive, every index is a position in the current array.
// T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct SortedRunsSumMaxAnd {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, top;
    long long vlo, vhi;
    struct VNode {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        S sm = S(0);
        long long cnt = 0;
        T av = T(~T(0));
        int Lc = 0;
        int Rc = 0;
    };
    vector<VNode> vn{VNode{}};  // value node 0 = the empty tree
    vector<int> freeList;  // value nodes freed by merges, reused first
    vector<int> root, len;  // per run start: its value tree, its length
    vector<char> desc;      // per run start: sorted descending?
    vector<int> bc;         // Fenwick: 1 at each run start
    int size;               // seg tree over positions: each run's aggregates at its start
    vector<S> qs;
    vector<T> qm;
    vector<T> qa;

    // O(N log U) -- arr: the initial array; every value a[i] ever holds must lie in [valLo, valHi] (U = valHi - valLo
    // + 1)
    SortedRunsSumMaxAnd(const vector<T>& arr, long long valLo, long long valHi)
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
        qm.assign(2 * size, numeric_limits<T>::lowest());
        qa.assign(2 * size, T(~T(0)));
        for (int s = 0; s < n; s++) setPos(s + size, s);
        for (int p = size - 1; p > 0; p--) up(p);
    }

    // O(log N + log U) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int s = startOf(i), k = i - s;
        return kth(root[s], desc[s] ? len[s] - k : k + 1);
    }

    // O(log N + log U) amortized -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        cutAt(i), cutAt(i + 1);
        io(i, -1);
        freeTree(root[i]);
        int t = leaf(v);
        root[i] = t;
        io(i, 1);
    }

    // O(log N + log U) amortized -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + v);
    }

    // O(log N + log U) amortized -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(log N + log U) amortized -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) pointAssign(i, v);
    }

    // O(log N + log U) amortized -- sort a[l..r] ascending; needs 0 <= l <= r < n, else throws out_of_range
    void rangeSortAsc(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSortAsc: needs 0 <= l <= r < n");
        sortRange(l, r, false, false, T(0));
    }

    // O(log N + log U) amortized -- sort a[l..r] descending; needs 0 <= l <= r < n, else throws out_of_range
    void rangeSortDesc(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSortDesc: needs 0 <= l <= r < n");
        sortRange(l, r, true, false, T(0));
    }

    // O(log N + log U) amortized -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAssign(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        sortRange(l, r, false, true, v);
    }

    // O(log N + log U) amortized -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        cutAt(l), cutAt(r + 1);
        return ask_qs(l, r);
    }

    // O(log N + log U) amortized -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeMax(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        cutAt(l), cutAt(r + 1);
        return ask_qm(l, r);
    }

    // O(log N + log U) amortized -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeAndQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndQuery: needs 0 <= l <= r < n");
        cutAt(l), cutAt(r + 1);
        return ask_qa(l, r);
    }

    // O(N log U) -- the whole current array
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(n);
        for (int s = 0; s < n; s += len[s]) values(root[s], desc[s], out);
        return out;
    }

    // O(log(N)+log(U) amortized) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws
    // out_of_range
    auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

    // O(log(N)+log(U) amortized) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws
    // out_of_range
    auto maxAll() {
        if (n < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, n - 1);
    }

    // O(log(N)+log(U) amortized) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else
    // throws out_of_range
    auto andAll() {
        if (n < 1) throw out_of_range("andAll: needs n >= 1");
        return rangeAndQuery(0, n - 1);
    }

    // ---- internals: runs ----

    // cut at l and r + 1, then turn a[l..r] into one run: every run inside merged (assign false) or thrown away for a
    // run of r - l + 1 copies of v
    void sortRange(int l, int r, bool d, bool assign, T v) {
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
    void cutAt(int p) {
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
    int startOf(int i) const {
        int k = pre(bc, i + 1), pos = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= n && bc[pos + step] < k) pos += step, k -= bc[pos];
        return pos;
    }

    template <class V>
    void fen(vector<V>& f, int i, V v) {
        for (i++; i <= n; i += i & -i) f[i] += v;
    }

    template <class V>
    static V pre(const vector<V>& f, int i) {  // f's total over positions 0..i-1
        V s = 0;
        for (; i > 0; i &= i - 1) s += f[i];
        return s;
    }

    // leaf p of the position tree <- the aggregates of the run starting at s
    void setPos(int p, int s) {
        int t = root[s];
        qs[p] = vn[t].sm;
        qm[p] = kth(t, vn[t].cnt);
        qa[p] = vn[t].av;
    }

    void up(int p) {
        qs[p] = qs[2 * p] + qs[2 * p + 1];
        qm[p] = max(qm[2 * p], qm[2 * p + 1]);
        qa[p] = qa[2 * p] & qa[2 * p + 1];
    }

    // add (sgn = 1) or take out (sgn = -1) the run starting at s from the position tree
    void io(int s, int sgn) {
        int p = s + size;
        if (sgn > 0) setPos(p, s);
        else qs[p] = S(0), qm[p] = numeric_limits<T>::lowest(), qa[p] = T(~T(0));
        for (p >>= 1; p; p >>= 1) up(p);
    }

    S ask_qs(int l, int r) const {  // the sum over positions l..r
        S res = S(0);
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res += qs[l++];
            if (r & 1) res += qs[--r];
        }
        return res;
    }

    T ask_qm(int l, int r) const {  // the max over positions l..r
        T res = numeric_limits<T>::lowest();
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = max(res, qm[l++]);
            if (r & 1) res = max(res, qm[--r]);
        }
        return res;
    }

    T ask_qa(int l, int r) const {  // the and over positions l..r
        T res = T(~T(0));
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res &= qa[l++];
            if (r & 1) res &= qa[--r];
        }
        return res;
    }

    // ---- internals: value trees (node 0 = the empty tree) ----

    int node() {
        if (!freeList.empty()) {
            int t = freeList.back();
            freeList.pop_back();
            vn[t].Lc = vn[t].Rc = 0, vn[t].cnt = 0;
            return t;
        }
        VNode n;
        n.Lc = 0, n.Rc = 0, n.cnt = 0, n.sm = S(0), n.av = T(~T(0));
        vn.push_back(n);
        return (int)vn.size() - 1;
    }

    void freeTree(int t) {  // hand every node of t back
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
    void setLeaf(int x, long long v, long long c) {
        vn[x].cnt = c;
        vn[x].sm = S(c) * S(v);
        vn[x].av = T(v);
    }

    void pull(int x) {
        int l = vn[x].Lc, r = vn[x].Rc;
        vn[x].cnt = vn[l].cnt + vn[r].cnt;
        vn[x].sm = vn[l].sm + vn[r].sm;
        vn[x].av = vn[l].av & vn[r].av;
    }

    // a tree holding c copies of v: one node per level
    int leaf(T v, long long c = 1) {
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
    void split(int t, long long k, long long nl, long long nh, int& a, int& b) {
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
    int merge(int a, int b, long long nl, long long nh) {
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
    T kth(int t, long long k) const {
        long long nl = vlo, nh = vhi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, cl = vn[vn[t].Lc].cnt;
            if (k <= cl) t = vn[t].Lc, nh = mid;
            else k -= cl, t = vn[t].Rc, nl = mid + 1;
        }
        return T(nl);
    }

    // append t's values, ascending (or descending), to out
    void values(int t, bool d, vector<T>& out) const {
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
