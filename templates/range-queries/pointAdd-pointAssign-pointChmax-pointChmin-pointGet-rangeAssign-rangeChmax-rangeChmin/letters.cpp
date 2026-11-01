// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeChmax-rangeChmin/letters.cpp
// @operations: getAll pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmax rangeChmin
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAssign: log(N)
//   rangeChmax: log(N)
//   rangeChmin: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: val[1*N]
//   tags: A[1*N] B[1*N]
//   other: none
//   note: each internal node holds one pending clamp x -> min(A, max(B, x)); val holds the leaf values

// Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
// operations that make sense on characters are listed.
// Range assign / chmax / chmin + point ops, no range aggregates. All indices 0-based, ranges inclusive.
// Every update is a clamp x -> min(A, max(B, x)); clamps compose into a clamp, but not commutatively, so before tagging
// the covering nodes we push the tags on the paths to l and r (the standard 2N trick for point reads).
// T: int, long long, ...; values must stay strictly inside (min(T), max(T)), which are the sentinels.
template <typename T>
struct ChminChmaxTree {
    static constexpr T INF = numeric_limits<T>::max(), NINF = numeric_limits<T>::lowest();
    int n;
    vector<T> A, B;  // internal nodes 1 .. n-1: pending clamp x -> min(A, max(B, x))
    vector<T> val;  // leaf values

    // O(N)
    explicit ChminChmaxTree(const vector<T>& a) : n((int)a.size()), A(a.size(), INF), B(a.size(), NINF), val(a) {}

    // apply clamp (a, b) on top of whatever node x already holds
    void apply(int x, T a, T b) {
        if (x >= n) { val[x - n] = min(a, max(b, val[x - n])); return; }
        T na = min(a, max(b, A[x]));
        B[x] = min(max(b, B[x]), na);
        A[x] = na;
    }

    // O(logN) -- push every pending tag on leaf p's root-to-leaf path down to its children
    void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            if (A[x] != INF || B[x] != NINF) apply(2 * x, A[x], B[x]), apply(2 * x + 1, A[x], B[x]), A[x] = INF, B[x] = NINF;
        }
    }

    void update(int l, int r, T a, T b) {
        l += n, r += n;
        push(l), push(r);
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) apply(l++, a, b);
            if (r & 1) apply(--r, a, b);
        }
    }

    // O(logN) -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) { update(l, r, v, v); }

    // O(logN) -- a[i] = max(a[i], v) for i in [l, r]
    void rangeChmax(int l, int r, T v) { update(l, r, INF, v); }

    // O(logN) -- a[i] = min(a[i], v) for i in [l, r]
    void rangeChmin(int l, int r, T v) { update(l, r, v, NINF); }

    // O(logN) -- a[i]: start from the leaf and apply ancestors' clamps bottom-up (deeper tags are older)
    T pointGet(int i) const {
        T v = val[i];
        for (int p = (i + n) >> 1; p; p >>= 1) v = min(A[p], max(B[p], v));
        return v;
    }

    // O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    // each node's tag is complete when it is pushed), then read the leaves
    vector<T> getAll() {
        for (int x = 1; x < n; x++)
            if (A[x] != INF || B[x] != NINF) apply(2 * x, A[x], B[x]), apply(2 * x + 1, A[x], B[x]), A[x] = INF, B[x] = NINF;
        return val;
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { push(i + n); val[i] = v; }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { push(i + n); val[i] = val[i] + delta; }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { push(i + n); if (v > val[i]) val[i] = v; }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { push(i + n); if (v < val[i]) val[i] = v; }
};
