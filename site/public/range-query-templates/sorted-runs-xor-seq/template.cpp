// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sorted-runs-xor-seq/template.cpp
// @operations: append appendLeft cut getAll insertAt insertCopiesAt merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeReverse rangeRotateLeft rangeRotateRight rangeSortAsc rangeSortDesc rangeXorQuery split trisect
// @data-structure-type: sorted-runs
// @complexities:
//   append: log(N)+log(U) amortized
//   appendLeft: log(N)+log(U) amortized
//   cut: log(N)+log(U) amortized
//   getAll: N*log(U)
//   insertAt: log(N)+log(U) amortized
//   insertCopiesAt: log(N)+log(U) amortized
//   merge: log(N)+log(U) amortized
//   paste: log(N)+log(U) amortized
//   pointAdd: log(N)+log(U) amortized
//   pointAssign: log(N)+log(U) amortized
//   pointChmax: log(N)+log(U) amortized
//   pointChmin: log(N)+log(U) amortized
//   pointGet: log(N)+log(U) expected
//   rangeAssign: log(N)+log(U) amortized
//   rangeReverse: log(N)+log(U) amortized
//   rangeRotateLeft: log(N)+log(U) amortized
//   rangeRotateRight: log(N)+log(U) amortized
//   rangeSortAsc: log(N)+log(U) amortized
//   rangeSortDesc: log(N)+log(U) amortized
//   rangeXorQuery: log(N)+log(U) amortized
//   split: log(N)+log(U) amortized
//   trisect: log(N)+log(U) amortized
//   build: N*log(U)
// @memory:
//   layout: none
//   node: Lc[1*N*log(U)] Rc[1*N*log(U)] cnt[1*N*log(U)] xr[1*N*log(U)]
//   tags: none
//   other: TL[1*N] TR[1*N] TP[1*N] TV[1*N] TN[1*N] TD[1*N] TS[1*N] TF[1*N] Sxr[1*N]
//   note: value nodes: N log U to start, plus O(log U) per cut (merges free nodes, which are reused); the runs are the nodes of an implicit treap (expected depth log N); U = valHi - valLo + 1

// An array whose ranges you can sort in place (ascending or descending), amortized O(log N + log U) a sort, with point
// reads / writes, rangeAssign, range xors, insert / erase / reverse / rotate / move anywhere and the whole array. It
// is kept as a sequence of sorted runs: each run is a dynamic value seg tree over [valLo, valHi] (copies per node) and
// an up / down flag, and the runs, in order, are the nodes of an implicit treap (random priorities, expected depth log
// N), each also keeping its subtree's length and xor; a reverse flips the order of the runs and each run's up / down
// flag. Sorting [l, r] cuts the runs at l and r + 1 and merges every run inside into one; a[i] is the k-th value of
// the run holding it; a query cuts at l and r + 1 too, then reads whole runs. Merges cost about as many nodes as they
// free and every run is merged away at most once, hence the amortized bounds (the treap's are expected as well).
// Indices 0-based, ranges inclusive, every index is a position in the current array.
// T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct SortedRunsXorSeq {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    // one node pool shared by every SortedRunsXorSeq<T>: cut / paste move nodes between them, so a piece from one can
    // go into any other (node 0 = the empty tree). Nodes freed by merges are reused, and there is nothing to reset
    // between test cases
    struct VNode {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        long long cnt = 0;
        T xr = T(0);
        int Lc = 0;
        int Rc = 0;
    };
    static inline vector<VNode> vn{VNode{}};  // node 0 = the empty tree
    struct Run {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long TP = 0;
        T Sxr = T(0);
        int TL = 0;
        int TR = 0;
        int TV = 0;
        int TN = 0;
        int TS = 0;
        char TD = 0;
        char TF = 0;
    };
    static inline vector<Run> rn{Run{}};  // node 0 = the empty tree
    static inline vector<int> freeList;  // value nodes freed by merges, reused first
    // treap of runs (node 0 = empty): children TL / TR, priority TP, value tree TV, length TN, descending TD,
    // subtree length TS, pending reverse TF, subtree xor
    static inline vector<int> tfree;
    long long vlo, vhi;  // (each one's value range)
    int n = 0, rt = 0;

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(N log U) -- arr: the initial array; every value a[i] ever holds must lie in [valLo, valHi]
    // (U = valHi - valLo + 1)
    SortedRunsXorSeq(const vector<T>& arr, long long valLo, long long valHi) : vlo(valLo),
        vhi(valHi) { buildFrom(arr); }

    // (a new, empty one: same pool, same value range)
    SortedRunsXorSeq makeEmpty() const { return SortedRunsXorSeq({}, vlo, vhi); }

    void buildFrom(const vector<T>& arr) {
        n = (int)arr.size();
        vector<int> st;  // O(N) build: the treap's right spine
        for (const T& v : arr) {
            int x = run(leaf(v), 1, false), last = 0;
            while (!st.empty() && rn[st.back()].TP < rn[x].TP) last = st.back(), st.pop_back(), tpull(last);
            rn[x].TL = last;
            if (!st.empty()) rn[st.back()].TR = x;
            st.push_back(x);
        }
        for (int i = (int)st.size() - 1; i >= 0; i--) tpull(st[i]);
        rt = st.empty() ? 0 : st[0];
    }

    // O(1) -- the current length
    int size() const { return n; }

    // O(log N + log U) expected -- a[i]
    T pointGet(int i) {
        for (int x = rt;;) {
            push(x);
            int ls = rn[rn[x].TL].TS;
            if (i < ls) x = rn[x].TL;
            else if (i < ls + rn[x].TN) {
                int k = i - ls;
                return kth(rn[x].TV, rn[x].TD ? rn[x].TN - k : k + 1);
            } else i -= ls + rn[x].TN, x = rn[x].TR;
        }
    }

    // O(log N + log U) amortized -- a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // O(log N + log U) amortized -- a[i] += v
    void pointAdd(int i, T v) { pointAssign(i, pointGet(i) + v); }

    // O(log N + log U) amortized -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(log N + log U) amortized -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }

    // O(log N + log U) amortized -- sort a[l..r] ascending
    void rangeSortAsc(int l, int r) { sortRange(l, r, false); }

    // O(log N + log U) amortized -- sort a[l..r] descending
    void rangeSortDesc(int l, int r) { sortRange(l, r, true); }

    // O(log N + log U) amortized -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) {
        auto [A, B, C] = extract(l, r);
        drop(B);
        join(A, run(leaf(v, r - l + 1), r - l + 1, false), C);
    }

    // O(log N + log U) amortized -- reverse a[l..r]
    void rangeReverse(int l, int r) {
        auto [A, B, C] = extract(l, r);
        rev(B);
        join(A, B, C);
    }

    // O(log N + log U) amortized -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) { insertCopiesAt(i, v, 1); }

    // O(log N + log U) amortized -- insert k copies of v starting at index i (0 <= i <= size(); k <= 0 does nothing)
    void insertCopiesAt(int i, T v, long long k) {
        if (k <= 0) return;
        n += (int)k;
        auto [A, C] = tsplit(rt, i);
        rt = tmerge(tmerge(A, run(leaf(v, k), (int)k, false)), C);
    }

    // O(log N + log U) amortized -- append v
    void append(T v) { insertCopiesAt(n, v, 1); }

    // O(log N + log U) amortized -- insert v at the front (it becomes a[0])
    void appendLeft(T v) { insertCopiesAt(0, v, 1); }

    // O(log N + log U) amortized -- remove a[l..r] and return it as one of its own (indices from 0)
    SortedRunsXorSeq cut(int l, int r) {
        auto [A, B, C] = extract(l, r);
        rt = tmerge(A, C), n -= r - l + 1;
        SortedRunsXorSeq piece = makeEmpty();
        piece.rt = B, piece.n = r - l + 1;
        return piece;
    }

    // O(log N + log U) amortized -- insert all of other (one with the same valLo / valHi, e.g. a cut piece) so it
    // starts at a[i] (0 <= i <= size()); other is left empty
    void paste(int i, SortedRunsXorSeq& other) {
        n += other.n;
        auto [A, C] = tsplit(rt, i);
        rt = tmerge(tmerge(A, other.rt), C), other.rt = other.n = 0;
    }

    // O(log N + log U) amortized -- append all of other at the end, leaving it empty (it must share this one's nodes)
    void merge(SortedRunsXorSeq& other) { paste(n, other); }

    // O(log N + log U) amortized -- (a[0..k-1], a[k..]) as two of their own; this one is left empty
    pair<SortedRunsXorSeq, SortedRunsXorSeq> split(int k) {
        SortedRunsXorSeq left = makeEmpty(), right = makeEmpty();
        tie(left.rt, right.rt) = tsplit(rt, k);
        left.n = k, right.n = n - k, rt = n = 0;
        return {left, right};
    }

    // O(log N + log U) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three of their own; this one is left empty
    tuple<SortedRunsXorSeq, SortedRunsXorSeq, SortedRunsXorSeq> trisect(int l, int r) {
        SortedRunsXorSeq left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        tie(left.rt, mid.rt, right.rt) = extract(l, r);
        left.n = l, mid.n = r - l + 1, right.n = n - r - 1, rt = n = 0;
        return {left, mid, right};
    }

    // O(log N + log U) amortized -- rotate a[l..r] left by k (a[l + k] comes first); k can be huge or
    // negative: it is taken mod the length (negative = right)
    void rangeRotateLeft(int l, int r, long long k) {
        long long m = r - l + 1;
        k = ((k % m) + m) % m;
        if (!k) return;
        auto [A, B, C] = extract(l, r);
        auto [X, Y] = tsplit(B, (int)k);
        join(A, tmerge(Y, X), C);
    }

    // O(log N + log U) amortized -- rotate a[l..r] right by k; k can be huge or negative: it is taken mod
    // the length (negative = left)
    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(log N + log U) amortized -- a[l] ^ ... ^ a[r]
    T rangeXorQuery(int l, int r) {
        auto [A, B, C] = extract(l, r);
        T res = rn[B].Sxr;
        join(A, B, C);
        return res;
    }

    // O(N log U) -- the whole current array
    vector<T> getAll() {
        vector<T> out;
        out.reserve(n);
        vector<int> st;
        for (int x = rt; !st.empty() || x;) {
            for (; x; x = rn[x].TL) push(x), st.push_back(x);
            x = st.back();
            st.pop_back();
            values(rn[x].TV, rn[x].TD, out);
            x = rn[x].TR;
        }
        return out;
    }

    // ---- internals: the treap of runs ----

    // a new run node: value tree t, length ln, descending?
    int run(int t, int ln, bool d) {
        int x;
        if (!tfree.empty()) x = tfree.back(), tfree.pop_back(), rn[x].TL = rn[x].TR = 0, rn[x].TF = 0;
        else {
            x = (int)rn.size();
            Run n;
            n.TL = 0, n.TR = 0, n.TV = 0, n.TN = 0, n.TS = 0, n.TP = 0, n.TD = 0, n.TF = 0, n.Sxr = T(0);
            rn.push_back(n);
        }
        rn[x].TP = rnd(), rn[x].TV = t, rn[x].TN = ln, rn[x].TD = d;
        tpull(x);
        return x;
    }

    void tpull(int x) {
        int L = rn[x].TL, R = rn[x].TR, t = rn[x].TV;
        rn[x].TS = rn[L].TS + rn[x].TN + rn[R].TS;
        rn[x].Sxr = rn[L].Sxr ^ vn[t].xr ^ rn[R].Sxr;
    }

    void rev(int x) {  // reverse x's subtree: swap its children (and below, lazily), flip its run
        if (x) swap(rn[x].TL, rn[x].TR), rn[x].TD ^= 1, rn[x].TF ^= 1;
    }

    void push(int x) {
        if (rn[x].TF) rev(rn[x].TL), rev(rn[x].TR), rn[x].TF = 0;
    }

    // (the first k elements, the rest), cutting the run that straddles k
    pair<int, int> tsplit(int x, int k) {
        if (!x || k <= 0) return {0, x};
        if (k >= rn[x].TS) return {x, 0};
        push(x);
        int ls = rn[rn[x].TL].TS;
        if (k <= ls) {
            auto [a, b] = tsplit(rn[x].TL, k);
            rn[x].TL = b;
            tpull(x);
            return {a, x};
        }
        if (k >= ls + rn[x].TN) {
            auto [a, b] = tsplit(rn[x].TR, k - ls - rn[x].TN);
            rn[x].TR = a;
            tpull(x);
            return {x, b};
        }
        k -= ls;  // cut this run: x keeps its first k elements, a new node the rest
        int t = rn[x].TV, ln = rn[x].TN, a, b;
        if (rn[x].TD) split(t, ln - k, vlo, vhi, b, a);  // the first k are the k largest
        else split(t, k, vlo, vhi, a, b);
        rn[x].TV = a, rn[x].TN = k;
        int u = run(b, ln - k, rn[x].TD), R = rn[x].TR;
        rn[x].TR = 0;
        tpull(x);
        return {x, tmerge(u, R)};
    }

    int tmerge(int a, int b) {
        if (!a || !b) return a ? a : b;
        if (rn[a].TP > rn[b].TP) {
            push(a);
            int r = tmerge(rn[a].TR, b);
            rn[a].TR = r;
            tpull(a);
            return a;
        }
        push(b);
        int l = tmerge(a, rn[b].TL);
        rn[b].TL = l;
        tpull(b);
        return b;
    }

    // (before l, a[l..r], after r) as three treaps
    tuple<int, int, int> extract(int l, int r) {
        auto [A, B] = tsplit(rt, l);
        auto [B2, C] = tsplit(B, r - l + 1);
        return {A, B2, C};
    }

    void join(int A, int B, int C) { rt = tmerge(tmerge(A, B), C); }

    vector<int> nodes(int x) const {  // every run node of x's treap
        vector<int> out, st;
        if (x) st.push_back(x);
        while (!st.empty()) {
            int y = st.back();
            st.pop_back();
            out.push_back(y);
            if (rn[y].TL) st.push_back(rn[y].TL);
            if (rn[y].TR) st.push_back(rn[y].TR);
        }
        return out;
    }

    void drop(int x) {  // free every run of x (value trees and treap nodes)
        for (int y : nodes(x)) freeTree(rn[y].TV), tfree.push_back(y);
    }

    // a[l..r] becomes one sorted run: every run inside merges into one
    void sortRange(int l, int r, bool d) {
        auto [A, B, C] = extract(l, r);
        int t = 0;
        for (int y : nodes(B)) t = merge(t, rn[y].TV, vlo, vhi), tfree.push_back(y);
        join(A, run(t, r - l + 1, d), C);
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
        n.Lc = 0, n.Rc = 0, n.cnt = 0, n.xr = T(0);
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
        vn[x].xr = (c & 1) ? T(v) : T(0);
    }

    void pull(int x) {
        int l = vn[x].Lc, r = vn[x].Rc;
        vn[x].cnt = vn[l].cnt + vn[r].cnt;
        vn[x].xr = vn[l].xr ^ vn[r].xr;
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

// Example (pieces move between treaps; merge appends and leaves its argument empty):
//     SortedRunsXorSeq<int> t({1, 2, 3, 4, 5}, 1, 5);
//     auto [left, mid, right] = t.trisect(1, 3);  // left = [1], mid = [2, 3, 4], right = [5]; t is empty now
//     t.merge(right);                             // t = [5]
//     t.merge(mid);                               // t = [5, 2, 3, 4]
//     t.merge(left);                              // t = [5, 2, 3, 4, 1]
