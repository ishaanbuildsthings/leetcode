// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmax rangeMin rangeSum
// @data-structure-type: beats
// @complexities:
//   pointAdd: log(U) amortized
//   pointAssign: log(U) amortized
//   pointChmax: log(U) amortized
//   pointChmin: log(U) amortized
//   pointGet: log(U)
//   rangeAssign: log(U) amortized
//   rangeChmax: log(U) amortized
//   rangeMin: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mn[4*log(U)] mn2[4*log(U)] cnt[4*log(U)] tot[4*log(U)]
//   tags: none
//   other: none
//   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. C++: one shared node pool, call resetPool() between test cases; Python: per-node lists that grow

// Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root
// is one block of zeros; children are created on demand as blocks of zeros (every count = their length)
// right before anything descends past a node or pushes its tags. Nodes live in one pool shared by every
// SparseChmaxSumBeats<T> (resetPool() between test cases). Otherwise the beats logic below is the dense tree's, with
// children in Lc / Rc instead of at 2i / 2i + 1.

// Segment tree beats, one side, no add: range chmax / assign, range sum / min, point ops. 0-based, inclusive.
// Each node keeps its min (mn), strict second min (mn2), how many times the min appears, and the sum. A chmax
// with x strictly between mn2 and mn only moves the min copies, so it is O(1) at that node; otherwise it
// descends, and each descent glues two distinct values together, which pays for it: O(log N) amortized, with no
// add tags at all (that is the saving over the beats trees that support range add).
// No tag arrays either: a node's own mn is its pending chmax for the children, and a node holding a single distinct
// value (mn2 == SENT) is its own pending assign.
// T: int, long long, ...; sums accumulate in S (long long for small T).
template <typename T>
struct SparseChmaxSumBeats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T SENT = numeric_limits<T>::max();
    struct Node { T mn, mn2; long long cnt; S tot; };
    static inline vector<Node> t{Node{}};  // node 0 is a placeholder
    static inline vector<int> Lc{0}, Rc{0};  // children (0: none yet)
    static inline vector<long long> ln{0};   // how many positions each node covers
    long long lo, hi;
    int root;

    static bool better(T a, T b) { return a < b; }

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseChmaxSumBeats(long long lo, long long hi) : lo(lo), hi(hi) { root = node(hi - lo + 1); }

    // O(1) -- forget every node of every SparseChmaxSumBeats<T>; call between test cases, then build new trees
    static void resetPool() { t.resize(1); Lc.resize(1); Rc.resize(1); ln.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { t.reserve(nodes); Lc.reserve(nodes); Rc.reserve(nodes); ln.reserve(nodes); }

    // a fresh node: a block of k zeros
    int node(long long k) const {  // const: it only touches the shared pool
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
        if (better(a.mn, b.mn)) x.mn = a.mn, x.cnt = a.cnt, x.mn2 = better(a.mn2, b.mn) ? a.mn2 : b.mn;
        else if (better(b.mn, a.mn)) x.mn = b.mn, x.cnt = b.cnt, x.mn2 = better(b.mn2, a.mn) ? b.mn2 : a.mn;
        else x.mn = a.mn, x.cnt = a.cnt + b.cnt, x.mn2 = better(a.mn2, b.mn2) ? a.mn2 : b.mn2;
    }

    // every min copy in node i becomes x (only valid while x is strictly between mn2 and mn)
    void moveExtreme(int i, T x) { t[i].tot += S(x - t[i].mn) * t[i].cnt, t[i].mn = x; }

    void setAll(int i, long long len, T v) { t[i] = Node{v, SENT, len, S(v) * len}; }

    void push(int i, long long tl, long long tr) {
        kids(i);
        if (tl == tr) return;
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        if (t[i].mn2 == SENT) {  // one distinct value: a pending assign
            setAll(Lc[i], tm - tl + 1, t[i].mn), setAll(Rc[i], tr - tm, t[i].mn);
            return;
        }
        for (int c : {Lc[i], Rc[i]})
            if (better(t[c].mn, t[i].mn)) moveExtreme(c, t[i].mn);  // the child still has values past the parent's cap
    }

    void ch(int i, long long tl, long long tr, long long l, long long r, T x) {
        if (r < tl || tr < l || !better(t[i].mn, x)) return;
        if (l <= tl && tr <= r && better(x, t[i].mn2)) { moveExtreme(i, x); return; }
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
        if (l <= tl && tr <= r) return t[i].mn;
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        T a = qext(Lc[i], tl, tm, l, r), b = qext(Rc[i], tm + 1, tr, l, r);
        return better(a, b) ? a : b;
    }

    // amortized O(logN) -- a[i] = max(a[i], x) for i in [l, r]
    void rangeChmax(long long l, long long r, T x) { if (l <= r) ch(root, lo, hi, l, r, x); }

    // amortized O(logN) -- a[i] = x for i in [l, r]
    void rangeAssign(long long l, long long r, T x) { if (l <= r) assign(root, lo, hi, l, r, x); }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) { return l <= r ? qsum(root, lo, hi, l, r) : S(0); }

    // O(logN) -- min of a[l..r]
    T rangeMin(long long l, long long r) { return qext(root, lo, hi, l, r); }

    // O(logN) -- a[i]
    T pointGet(long long i) { return qext(root, lo, hi, i, i); }

    // amortized O(logN) -- a[i] = v
    void pointAssign(long long i, T v) { rangeAssign(i, i, v); }

    // amortized O(logN) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { rangeChmax(i, i, v); }

    // amortized O(logN) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }

    // amortized O(logN) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }
};
