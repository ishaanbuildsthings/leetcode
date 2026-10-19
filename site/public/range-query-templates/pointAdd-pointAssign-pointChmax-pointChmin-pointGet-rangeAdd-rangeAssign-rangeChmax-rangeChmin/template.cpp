// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   rangeAssign: log(N)
//   rangeChmax: log(N)
//   rangeChmin: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: none
//   tags: A[1*N] B[1*N] C[1*N]
//   other: val[1*N]
//   note: each internal node holds one pending clamp x -> min(A, max(B, x + C)); val holds the leaf values

// Range add / assign / chmax / chmin + point ops, no range aggregates. All indices 0-based, ranges inclusive.
// Every update is a clamp f(x) = min(A, max(B, x + C)) with B <= A:
//   add v -> (INF, -INF, v)    chmax v -> (INF, v, 0)    chmin v -> (v, -INF, 0)    assign v -> (v, v, 0)
// Clamps compose into a clamp, but not commutatively, so before tagging the covering nodes we push the tags on
// the paths to l and r (the standard 2N trick for non-commutative updates with point reads).
// T: int, long long, ...; values must stay strictly inside (min(T), max(T)), which are the sentinels.
template <typename T>
struct ClampTree {
    static constexpr T INF = numeric_limits<T>::max(), NINF = numeric_limits<T>::lowest();
    int n;
    vector<T> A, B, C;  // internal nodes 1 .. n-1: pending clamp x -> min(A, max(B, x + C))
    vector<T> val;      // leaf values

    // O(N)
    explicit ClampTree(const vector<T>& a) : n((int)a.size()), A(a.size(), INF), B(a.size(), NINF), C(a.size(), 0), val(a) {}

    // apply clamp (a, b, c) on top of whatever node x already holds
    void apply(int x, T a, T b, T c) {
        if (x >= n) {
            T v = val[x - n] + c;
            val[x - n] = min(a, max(b, v));
            return;
        }
        T p = A[x] == INF ? INF : A[x] + c;
        T q = B[x] == NINF ? NINF : B[x] + c;
        T na = min(a, max(b, p));
        A[x] = na;
        B[x] = min(max(b, q), na);
        C[x] += c;
    }

    // O(logN) -- push every pending tag on leaf p's root-to-leaf path down to its children
    void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            
            if (!(A[x] == INF && B[x] == NINF && C[x] == 0)) {
                apply(2 * x, A[x], B[x], C[x]);
                apply(2 * x + 1, A[x], B[x], C[x]);
                A[x] = INF, B[x] = NINF, C[x] = 0;
            }
        }
    }
    void update(int l, int r, T a, T b, T c) {
        l += n, r += n;
        push(l), push(r);
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) apply(l++, a, b, c);
            if (r & 1) apply(--r, a, b, c);
        }
    }

    // O(logN) -- a[i] += v for i in [l, r]
    void rangeAdd(int l, int r, T v) { update(l, r, INF, NINF, v); }

    // O(logN) -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) { update(l, r, v, v, 0); }

    // O(logN) -- a[i] = max(a[i], v) for i in [l, r]
    void rangeChmax(int l, int r, T v) { update(l, r, INF, v, 0); }

    // O(logN) -- a[i] = min(a[i], v) for i in [l, r]
    void rangeChmin(int l, int r, T v) { update(l, r, v, NINF, 0); }

    // O(logN) -- a[i]: start from the leaf and apply ancestors' clamps bottom-up (deeper tags are older)
    T pointGet(int i) const {
        T v = val[i];
        for (int p = (i + n) >> 1; p; p >>= 1) v = min(A[p], max(B[p], v + C[p]));
        return v;
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
