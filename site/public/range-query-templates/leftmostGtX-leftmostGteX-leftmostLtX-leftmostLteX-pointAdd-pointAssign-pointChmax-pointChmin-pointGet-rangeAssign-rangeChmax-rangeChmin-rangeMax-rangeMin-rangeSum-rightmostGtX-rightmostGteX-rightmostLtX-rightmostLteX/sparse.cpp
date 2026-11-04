// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostGtX-leftmostGteX-leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeChmax-rangeChmin-rangeMax-rangeMin-rangeSum-rightmostGtX-rightmostGteX-rightmostLtX-rightmostLteX/sparse.cpp
// @operations: leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmax rangeChmin rangeMax rangeMin rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX
// @data-structure-type: beats
// @complexities:
//   leftmostGtX: log(U)
//   leftmostGteX: log(U)
//   leftmostLtX: log(U)
//   leftmostLteX: log(U)
//   pointAdd: log(U) amortized
//   pointAssign: log(U) amortized
//   pointChmax: log(U) amortized
//   pointChmin: log(U) amortized
//   pointGet: log(U)
//   rangeAssign: log(U) amortized
//   rangeChmax: log(U) amortized
//   rangeChmin: log(U) amortized
//   rangeMax: log(U)
//   rangeMin: log(U)
//   rangeSum: log(U)
//   rightmostGtX: log(U)
//   rightmostGteX: log(U)
//   rightmostLtX: log(U)
//   rightmostLteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[4*log(U)] mx2[4*log(U)] cntMx[4*log(U)] mn[4*log(U)] mn2[4*log(U)] cntMn[4*log(U)] tot[4*log(U)]
//   tags: none
//   other: none
//   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. A node pool per tree

// Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root is one
// block of zeros; children are created on demand as blocks of zeros (every count = their length) right before anything
// descends past a node or pushes its tags. Nodes live in a pool the tree owns. Otherwise the beats logic below is the
// dense tree's, with children in Lc / Rc instead of at 2i / 2i + 1.

// Segment tree beats: range chmin (a[i] = min(a[i], x)) and chmax (a[i] = max(a[i], x)) and range assign, with range
// sums and the range max / min, plus point ops. All indices 0-based, ranges inclusive. How it works: a chmin only
// changes the max values of a node it covers, so a node keeps its max, its strict second max and how many copies of
// the max it has; a chmin x with mx2 < x < mx moves just those copies (the sum drops by (mx - x) * cntMx) and stops
// there, and only x <= mx2 has to go further down. a chmax is the same with the min: mn, mn2 and cntMn. A node's own
// mx / mn doubles as its pending clamp: push clamps each child to it, so there is no chmin / chmax tag. There is no
// assign tag either: when all of a node's values are equal (mn == mx), push hands that value to both children as an
// assign. Amortized O(log U) per update (beats: every extra descent removes a distinct value).
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseChminChmaxBeats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NEG_INF = numeric_limits<T>::lowest(), POS_INF = numeric_limits<T>::max();
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        S tot = S();
        long long cntMx = 0;
        long long cntMn = 0;
        long long ln = 0;
        T mx = T();
        T mx2 = T();
        T mn = T();
        T mn2 = T();
        int Lc = 0;
        int Rc = 0;
    };
    mutable vector<Node> nd{Node{}};  // node 0 = the empty tree
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseChminChmaxBeats(long long lo, long long hi) : lo(lo), hi(hi) { root = node(hi - lo + 1); }


    // optional -- reserve room for this many nodes up front
    void reservePool(size_t nodes) { nd.reserve(nodes); }

    // a fresh node: a block of k zeros
    int node(long long k) const {  // const: it only grows the (mutable) pool
        Node n;
        n.mx = 0, n.mx2 = NEG_INF, n.mn = 0, n.mn2 = POS_INF, n.cntMx = k, n.cntMn = k, n.tot = 0, n.Lc = 0, n.Rc = 0,
        n.ln = k;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    // create node i's children (blocks of zeros: the left one gets the extra position) if it has none yet
    void kids(int i) const {
        if (nd[i].Lc || nd[i].ln <= 1) return;
        int a = node((nd[i].ln + 1) / 2), b = node(nd[i].ln / 2);
        nd[i].Lc = a, nd[i].Rc = b;
    }

    void pull(int i) {
        int l = nd[i].Lc, r = nd[i].Rc;
        nd[i].tot = nd[l].tot + nd[r].tot;
        if (nd[l].mx > nd[r].mx) nd[i].mx = nd[l].mx, nd[i].cntMx = nd[l].cntMx, nd[i].mx2 = max(nd[l].mx2, nd[r].mx);
        else if (nd[l].mx < nd[r].mx) nd[i].mx = nd[r].mx, nd[i].cntMx = nd[r].cntMx,
            nd[i].mx2 = max(nd[r].mx2, nd[l].mx);
        else nd[i].mx = nd[l].mx, nd[i].cntMx = nd[l].cntMx + nd[r].cntMx, nd[i].mx2 = max(nd[l].mx2, nd[r].mx2);
        if (nd[l].mn < nd[r].mn) nd[i].mn = nd[l].mn, nd[i].cntMn = nd[l].cntMn, nd[i].mn2 = min(nd[l].mn2, nd[r].mn);
        else if (nd[l].mn > nd[r].mn) nd[i].mn = nd[r].mn, nd[i].cntMn = nd[r].cntMn,
            nd[i].mn2 = min(nd[r].mn2, nd[l].mn);
        else nd[i].mn = nd[l].mn, nd[i].cntMn = nd[l].cntMn + nd[r].cntMn, nd[i].mn2 = min(nd[l].mn2, nd[r].mn2);
    }

    // every value under node i (sz of them) becomes v
    void applyAssign(int i, long long sz, T v) {
        nd[i].mx = v, nd[i].mx2 = NEG_INF, nd[i].cntMx = sz, nd[i].mn = v, nd[i].mn2 = POS_INF, nd[i].cntMn = sz,
            nd[i].tot = S(v) * sz;
    }

    // chmin by v on node i, with mx2 < v: only the copies of the max move
    void applyChmin(int i, long long sz, T v) {
        if (nd[i].mn >= v) { applyAssign(i, sz, v); return; }
        if (nd[i].mx > v) {
            if (nd[i].mn2 == nd[i].mx) nd[i].mn2 = v;
            nd[i].tot -= S(nd[i].mx - v) * nd[i].cntMx;
            nd[i].mx = v;
        }
    }

    // chmax by v on node i, with v < mn2: only the copies of the min move
    void applyChmax(int i, long long sz, T v) {
        if (nd[i].mx <= v) { applyAssign(i, sz, v); return; }
        if (nd[i].mn < v) {
            if (nd[i].mx2 == nd[i].mn) nd[i].mx2 = v;
            nd[i].tot += S(v - nd[i].mn) * nd[i].cntMn;
            nd[i].mn = v;
        }
    }

    // hand node i's pending changes to its children: all one value (an assign), else the add, then its own clamp
    void push(int i, long long tl, long long tr) {
        kids(i);
        if (tl == tr) return;
        kids(i);
        long long tm = tl + (tr - tl) / 2, l = nd[i].Lc, r = nd[i].Rc;
        long long lsz = tm - tl + 1, rsz = tr - tm;
        if (nd[i].mn == nd[i].mx) { applyAssign(l, lsz, nd[i].mx), applyAssign(r, rsz, nd[i].mx); return; }
        applyChmin(l, lsz, nd[i].mx), applyChmin(r, rsz, nd[i].mx);
        applyChmax(l, lsz, nd[i].mn), applyChmax(r, rsz, nd[i].mn);
    }

    void chmin(int i, long long tl, long long tr, long long ql, long long qr, T x) {
        if (qr < tl || ql > tr || x >= nd[i].mx) return;
        if (ql <= tl && tr <= qr && x > nd[i].mx2) { applyChmin(i, tr - tl + 1, x); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        chmin(nd[i].Lc, tl, tm, ql, qr, x), chmin(nd[i].Rc, tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void chmax(int i, long long tl, long long tr, long long ql, long long qr, T x) {
        if (qr < tl || ql > tr || x <= nd[i].mn) return;
        if (ql <= tl && tr <= qr && x < nd[i].mn2) { applyChmax(i, tr - tl + 1, x); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        chmax(nd[i].Lc, tl, tm, ql, qr, x), chmax(nd[i].Rc, tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void assign(int i, long long tl, long long tr, long long ql, long long qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAssign(i, tr - tl + 1, v); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        assign(nd[i].Lc, tl, tm, ql, qr, v), assign(nd[i].Rc, tm + 1, tr, ql, qr, v);
        pull(i);
    }

    S qsum(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && tr <= qr) return nd[i].tot;
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return qsum(nd[i].Lc, tl, tm, ql, qr) + qsum(nd[i].Rc, tm + 1, tr, ql, qr);
    }

    T qmax(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return NEG_INF;
        if (ql <= tl && tr <= qr) return nd[i].mx;
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return max(qmax(nd[i].Lc, tl, tm, ql, qr), qmax(nd[i].Rc, tm + 1, tr, ql, qr));
    }

    T qmin(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return POS_INF;
        if (ql <= tl && tr <= qr) return nd[i].mn;
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return min(qmin(nd[i].Lc, tl, tm, ql, qr), qmin(nd[i].Rc, tm + 1, tr, ql, qr));
    }

    // amortized O(logU) -- a[i] = min(a[i], x) for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeChmin(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeChmin: needs lo <= l <= r <= hi");
        if (l <= r) chmin(root, lo, hi, l, r, x);
    }

    // amortized O(logU) -- a[i] = max(a[i], x) for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeChmax(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeChmax: needs lo <= l <= r <= hi");
        if (l <= r) chmax(root, lo, hi, l, r, x);
    }

    // amortized O(logU) -- a[i] = x for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeAssign(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAssign: needs lo <= l <= r <= hi");
        if (l <= r) assign(root, lo, hi, l, r, x);
    }

    // O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    S rangeSum(long long l, long long r) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        return l > r ? S(0) : qsum(root, lo, hi, l, r);
    }

    // O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeMax(long long l, long long r) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMax: needs lo <= l <= r <= hi");
        return l > r ? NEG_INF : qmax(root, lo, hi, l, r);
    }

    // O(logU) -- min of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeMin(long long l, long long r) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMin: needs lo <= l <= r <= hi");
        return l > r ? POS_INF : qmin(root, lo, hi, l, r);
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    T pointGet(long long i) {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return rangeMax(i, i);
    }

    // amortized O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        rangeAssign(i, i, v);
    }

    // amortized O(logU) -- a[i] += v; needs lo <= i <= hi, else throws out_of_range
    void pointAdd(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        rangeAssign(i, i, pointGet(i) + v);
    }

    // amortized O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmax(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmax: needs lo <= i <= hi");
        rangeChmax(i, i, v);
    }

    // amortized O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmin(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmin: needs lo <= i <= hi");
        rangeChmin(i, i, v);
    }

    // O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostGtX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostGtX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return nd[i].mx > x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the first i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostGteX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostGteX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return nd[i].mx >= x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the first i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostLtX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostLtX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return nd[i].mn < x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the first i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostLteX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostLteX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return nd[i].mn <= x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostGtX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostGtX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return nd[i].mx > x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostGteX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostGteX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return nd[i].mx >= x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostLtX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostLtX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return nd[i].mn < x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostLteX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostLteX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return nd[i].mn <= x; });
        return res == NONE ? lo - 1 : res;
    }

    static constexpr long long NONE = LLONG_MIN;  // ("no index": any long long can be an index here)

    // the first index in [l, r] under node i whose value passes ok(node), or NONE: O(logU), since only one
    // node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    template <class F>
    long long firstPass(int i, long long tl, long long tr, long long l, long long r, const F& ok) {
        if (r < tl || tr < l || !ok(i)) return NONE;
        if (tl == tr) return tl;
        push(i, tl, tr), kids(i);
        long long tm = tl + (tr - tl) / 2, res = firstPass(nd[i].Lc, tl, tm, l, r, ok);
        return res != NONE ? res : firstPass(nd[i].Rc, tm + 1, tr, l, r, ok);
    }

    // the last index in [l, r] under node i whose value passes ok(node), or NONE: O(logU), since only one
    // node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    template <class F>
    long long lastPass(int i, long long tl, long long tr, long long l, long long r, const F& ok) {
        if (r < tl || tr < l || !ok(i)) return NONE;
        if (tl == tr) return tl;
        push(i, tl, tr), kids(i);
        long long tm = tl + (tr - tl) / 2, res = lastPass(nd[i].Rc, tm + 1, tr, l, r, ok);
        return res != NONE ? res : lastPass(nd[i].Lc, tl, tm, l, r, ok);
    }
};