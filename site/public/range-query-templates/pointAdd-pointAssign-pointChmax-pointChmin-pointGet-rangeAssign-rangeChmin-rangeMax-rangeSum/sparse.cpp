// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeChmin-rangeMax-rangeSum/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmin rangeMax rangeSum
// @data-structure-type: beats
// @complexities:
//   pointAdd: log(U) amortized
//   pointAssign: log(U) amortized
//   pointChmax: log(U) amortized
//   pointChmin: log(U) amortized
//   pointGet: log(U)
//   rangeAssign: log(U) amortized
//   rangeChmin: log(U) amortized
//   rangeMax: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[4*log(U)] mx2[4*log(U)] cnt[4*log(U)] tot[4*log(U)]
//   tags: none
//   other: none
//   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. A node pool per tree

// Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root is one
// block of zeros; children are created on demand as blocks of zeros (every count = their length) right before anything
// descends past a node or pushes its tags. Nodes live in a pool the tree owns. Otherwise the beats logic below is the
// dense tree's, with children in Lc / Rc instead of at 2i / 2i + 1.

// Segment tree beats, one side, no add: range chmin / assign, range sum / max, point ops. 0-based, inclusive.
// Each node keeps its max (mx), strict second max (mx2), how many times the max appears, and the sum. A chmin
// with x strictly between mx2 and mx only moves the max copies, so it is O(1) at that node; otherwise it
// descends, and each descent glues two distinct values together, which pays for it: O(log U) amortized, with no
// add tags at all (that is the saving over the beats trees that support range add).
// No tag arrays either: a node's own mx is its pending chmin for the children, and a node holding a single distinct
// value (mx2 == SENT) is its own pending assign.
// T: int, long long, ...; sums accumulate in S (long long for small T).
template <typename T>
struct SparseChminSumBeats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T SENT = numeric_limits<T>::lowest();
    struct Node { T mx, mx2; long long cnt; S tot; };
    mutable vector<Node> t{Node{}};  // node 0 is a placeholder
    mutable vector<int> Lc{0}, Rc{0};  // children (0: none yet)
    mutable vector<long long> ln{0};   // how many positions each node covers
    long long lo, hi;
    int root;

    static bool better(T a, T b) { return a > b; }

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseChminSumBeats(long long lo, long long hi) : lo(lo), hi(hi) { root = node(hi - lo + 1); }


    // optional -- reserve room for this many nodes up front
    void reservePool(size_t nodes) { t.reserve(nodes); Lc.reserve(nodes); Rc.reserve(nodes); ln.reserve(nodes); }

    // a fresh node: a block of k zeros
    int node(long long k) const {  // const: it only grows the (mutable) pool
        t.push_back(Node{0, SENT, k, S(0)});
        Lc.push_back(0), Rc.push_back(0), ln.push_back(k);
        return (int)ln.size() - 1;
    }

    // create node i's children (blocks of zeros: the left one gets the extra position) if it has none yet
    void kids(int i) const {
        if (Lc[i] || ln[i] <= 1) return;
        int a = node((ln[i] + 1) / 2), b = node(ln[i] / 2);
        Lc[i] = a, Rc[i] = b;
    }

    void pull(int i) {
        const Node &a = t[Lc[i]], &b = t[Rc[i]];
        Node& x = t[i];
        x.tot = a.tot + b.tot;
        if (better(a.mx, b.mx)) x.mx = a.mx, x.cnt = a.cnt, x.mx2 = better(a.mx2, b.mx) ? a.mx2 : b.mx;
        else if (better(b.mx, a.mx)) x.mx = b.mx, x.cnt = b.cnt, x.mx2 = better(b.mx2, a.mx) ? b.mx2 : a.mx;
        else x.mx = a.mx, x.cnt = a.cnt + b.cnt, x.mx2 = better(a.mx2, b.mx2) ? a.mx2 : b.mx2;
    }

    // every max copy in node i becomes x (only valid while x is strictly between mx2 and mx)
    void moveExtreme(int i, T x) { t[i].tot += S(x - t[i].mx) * t[i].cnt, t[i].mx = x; }

    void setAll(int i, long long len, T v) { t[i] = Node{v, SENT, len, S(v) * len}; }

    void push(int i, long long tl, long long tr) {
        kids(i);
        if (tl == tr) return;
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        if (t[i].mx2 == SENT) {  // one distinct value: a pending assign
            setAll(Lc[i], tm - tl + 1, t[i].mx), setAll(Rc[i], tr - tm, t[i].mx);
            return;
        }
        for (int c : {Lc[i], Rc[i]})
            if (better(t[c].mx, t[i].mx)) moveExtreme(c, t[i].mx);  // the child still has values past the parent's cap
    }

    void ch(int i, long long tl, long long tr, long long l, long long r, T x) {
        if (r < tl || tr < l || !better(t[i].mx, x)) return;
        if (l <= tl && tr <= r && better(x, t[i].mx2)) { moveExtreme(i, x); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        ch(Lc[i], tl, tm, l, r, x), ch(Rc[i], tm + 1, tr, l, r, x);
        pull(i);
    }

    void assign(int i, long long tl, long long tr, long long l, long long r, T v) {
        if (r < tl || tr < l) return;
        if (l <= tl && tr <= r) { setAll(i, tr - tl + 1, v); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        assign(Lc[i], tl, tm, l, r, v), assign(Rc[i], tm + 1, tr, l, r, v);
        pull(i);
    }

    S qsum(int i, long long tl, long long tr, long long l, long long r) {
        if (r < tl || tr < l) return 0;
        if (l <= tl && tr <= r) return t[i].tot;
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return qsum(Lc[i], tl, tm, l, r) + qsum(Rc[i], tm + 1, tr, l, r);
    }

    T qext(int i, long long tl, long long tr, long long l, long long r) {
        if (r < tl || tr < l) return SENT;
        if (l <= tl && tr <= r) return t[i].mx;
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        T a = qext(Lc[i], tl, tm, l, r), b = qext(Rc[i], tm + 1, tr, l, r);
        return better(a, b) ? a : b;
    }

    // amortized O(logU) -- a[i] = min(a[i], x) for i in [l, r]
    void rangeChmin(long long l, long long r, T x) { if (l <= r) ch(root, lo, hi, l, r, x); }

    // amortized O(logU) -- a[i] = x for i in [l, r]
    void rangeAssign(long long l, long long r, T x) { if (l <= r) assign(root, lo, hi, l, r, x); }

    // O(logU) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) { return l <= r ? qsum(root, lo, hi, l, r) : S(0); }

    // O(logU) -- max of a[l..r]
    T rangeMax(long long l, long long r) { return qext(root, lo, hi, l, r); }

    // O(logU) -- a[i]
    T pointGet(long long i) { return qext(root, lo, hi, i, i); }

    // amortized O(logU) -- a[i] = v
    void pointAssign(long long i, T v) { rangeAssign(i, i, v); }

    // amortized O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { rangeChmin(i, i, v); }

    // amortized O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // amortized O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }
};
