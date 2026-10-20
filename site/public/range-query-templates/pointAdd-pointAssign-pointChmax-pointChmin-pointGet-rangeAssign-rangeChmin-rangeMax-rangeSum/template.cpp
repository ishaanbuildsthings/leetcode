// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeChmin-rangeMax-rangeSum/template.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmin rangeMax rangeSum
// @data-structure-type: beats
// @complexities:
//   pointAdd: log(N) amortized
//   pointAssign: log(N) amortized
//   pointChmax: log(N) amortized
//   pointChmin: log(N) amortized
//   pointGet: log(N)
//   rangeAssign: log(N) amortized
//   rangeChmin: log(N) amortized
//   rangeMax: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: mx[4*N] mx2[4*N] cnt[4*N] tot[4*N]
//   tags: none
//   other: none
//   note: no tag arrays: a node's mx is its pending chmin, and a node with one distinct value (mx2 = sentinel) is a pending assign

// Segment tree beats, one side, no add: range chmin / assign, range sum / max, point ops. 0-based, inclusive.
// Each node keeps its max (mx), strict second max (mx2), how many times the max appears, and the sum. A chmin
// with x strictly between mx2 and mx only moves the max copies, so it is O(1) at that node; otherwise it
// descends, and each descent glues two distinct values together, which pays for it: O(log N) amortized, with no
// add tags at all (that is the saving over the beats trees that support range add).
// No tag arrays either: a node's own mx is its pending chmin for the children, and a node holding a single distinct
// value (mx2 == SENT) is its own pending assign.
// T: int, long long, ...; sums accumulate in S (long long for small T).
template <typename T>
struct ChminSumBeats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T SENT = numeric_limits<T>::lowest();
    struct Node { T mx, mx2; int cnt; S tot; };
    int n;
    vector<Node> t;

    static bool better(T a, T b) { return a > b; }

    // O(N)
    explicit ChminSumBeats(const vector<T>& a) : n((int)a.size()), t(4 * max(1, n)) {
        if (n) build(1, 0, n - 1, a);
    }

    void build(int i, int tl, int tr, const vector<T>& a) {
        if (tl == tr) { t[i] = Node{a[tl], SENT, 1, S(a[tl])}; return; }
        int tm = (tl + tr) / 2;
        build(2 * i, tl, tm, a), build(2 * i + 1, tm + 1, tr, a);
        pull(i);
    }

    void pull(int i) {
        const Node &a = t[2 * i], &b = t[2 * i + 1];
        Node& x = t[i];
        x.tot = a.tot + b.tot;
        if (better(a.mx, b.mx)) x.mx = a.mx, x.cnt = a.cnt, x.mx2 = better(a.mx2, b.mx) ? a.mx2 : b.mx;
        else if (better(b.mx, a.mx)) x.mx = b.mx, x.cnt = b.cnt, x.mx2 = better(b.mx2, a.mx) ? b.mx2 : a.mx;
        else x.mx = a.mx, x.cnt = a.cnt + b.cnt, x.mx2 = better(a.mx2, b.mx2) ? a.mx2 : b.mx2;
    }

    // every max copy in node i becomes x (only valid while x is strictly between mx2 and mx)
    void moveExtreme(int i, T x) { t[i].tot += S(x - t[i].mx) * t[i].cnt, t[i].mx = x; }

    void setAll(int i, int len, T v) { t[i] = Node{v, SENT, len, S(v) * len}; }

    void push(int i, int tl, int tr) {
        if (tl == tr) return;
        int tm = (tl + tr) / 2;
        if (t[i].mx2 == SENT) {  // one distinct value: a pending assign
            setAll(2 * i, tm - tl + 1, t[i].mx), setAll(2 * i + 1, tr - tm, t[i].mx);
            return;
        }
        for (int c : {2 * i, 2 * i + 1})
            if (better(t[c].mx, t[i].mx)) moveExtreme(c, t[i].mx);  // the child still has values past the parent's cap
    }

    void ch(int i, int tl, int tr, int l, int r, T x) {
        if (r < tl || tr < l || !better(t[i].mx, x)) return;
        if (l <= tl && tr <= r && better(x, t[i].mx2)) { moveExtreme(i, x); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        ch(2 * i, tl, tm, l, r, x), ch(2 * i + 1, tm + 1, tr, l, r, x);
        pull(i);
    }

    void assign(int i, int tl, int tr, int l, int r, T v) {
        if (r < tl || tr < l) return;
        if (l <= tl && tr <= r) { setAll(i, tr - tl + 1, v); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        assign(2 * i, tl, tm, l, r, v), assign(2 * i + 1, tm + 1, tr, l, r, v);
        pull(i);
    }

    S qsum(int i, int tl, int tr, int l, int r) {
        if (r < tl || tr < l) return 0;
        if (l <= tl && tr <= r) return t[i].tot;
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return qsum(2 * i, tl, tm, l, r) + qsum(2 * i + 1, tm + 1, tr, l, r);
    }

    T qext(int i, int tl, int tr, int l, int r) {
        if (r < tl || tr < l) return SENT;
        if (l <= tl && tr <= r) return t[i].mx;
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        T a = qext(2 * i, tl, tm, l, r), b = qext(2 * i + 1, tm + 1, tr, l, r);
        return better(a, b) ? a : b;
    }

    // amortized O(logN) -- a[i] = min(a[i], x) for i in [l, r]
    void rangeChmin(int l, int r, T x) { if (l <= r && n) ch(1, 0, n - 1, l, r, x); }

    // amortized O(logN) -- a[i] = x for i in [l, r]
    void rangeAssign(int l, int r, T x) { if (l <= r && n) assign(1, 0, n - 1, l, r, x); }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) { return l <= r && n ? qsum(1, 0, n - 1, l, r) : S(0); }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) { return qext(1, 0, n - 1, l, r); }

    // O(logN) -- a[i]
    T pointGet(int i) { return qext(1, 0, n - 1, i, i); }

    // amortized O(logN) -- a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // amortized O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { rangeChmin(i, i, v); }

    // amortized O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // amortized O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }
};
