// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin rangeMax rangeMin
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
//   rangeMax: log(N)
//   rangeMin: log(N)
//   build: N
// @memory:
//   layout: pow2-iterative
//   node: mn[4*N] mx[4*N]
//   tags: A[2*N] B[2*N] C[2*N]
//   other: none
//   note: one clamp tag per node: x -> min(A, max(B, x + C))
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/rangeChmin-Chmax-Add-Assign-Min-Max-PointSet-NO-BEATS.cpp

// Lazy segment tree with one clamp tag per node: x -> min(A, max(B, x + C)). All indices 0-based, inclusive.
// add v = (INF, NINF, v), chmax v = (INF, v, 0), chmin v = (v, NINF, 0), assign v = (v, v, 0). Clamps compose into
// clamps, and a clamp is monotone, so it maps a node's min to the new min and its max to the new max: no beats
// needed, every op is a plain O(log N). (Range SUM would need beats, since a clamp does not move all values alike.)
// Composing new (a, b, c) after old (A, B, C): A' = min(a, max(b, A + c)), B' = min(max(b, B + c), A'), C' = C + c.
// Iterative over a power-of-two layout: push the two boundary paths, tag the covering nodes, recompute the paths.
// T: int, long long, ...; the INF / NINF sentinels are kept saturated, never shifted.
template <typename T>
struct LazyClamp {
    static constexpr T INF = numeric_limits<T>::max(), NINF = numeric_limits<T>::lowest();
    int n, size, H;
    vector<T> mn, mx;  // 2 * size slots; padding leaves are INF / NINF so they never win
    vector<T> A, B, C; // clamp tags on internal nodes only

    // O(N)
    explicit LazyClamp(const vector<T>& a) : n((int)a.size()), size(1), H(0) {
        while (size < max(n, 1)) size <<= 1, H++;
        mn.assign(2 * size, INF), mx.assign(2 * size, NINF);
        A.assign(size, INF), B.assign(size, NINF), C.assign(size, 0);
        for (int i = 0; i < n; i++) mn[size + i] = mx[size + i] = a[i];
        for (int x = size - 1; x > 0; x--) mn[x] = min(mn[2 * x], mn[2 * x + 1]), mx[x] = max(mx[2 * x], mx[2 * x + 1]);
    }

    bool identity(int i) const { return A[i] == INF && B[i] == NINF && C[i] == 0; }

    // only ever called on a real value (a node holding padding never carries a tag), so v + c cannot overflow
    static T eval(T v, T a, T b, T c) { return min(a, max(b, v + c)); }

    // a clamp is monotone, so it maps the node's min to the new min and its max to the new max
    void apply(int i, T a, T b, T c) {
        mn[i] = eval(mn[i], a, b, c), mx[i] = eval(mx[i], a, b, c);
        if (i < size) {
            T sA = A[i] == INF ? INF : A[i] + c, sB = B[i] == NINF ? NINF : B[i] + c;
            A[i] = min(a, max(b, sA));
            B[i] = min(max(b, sB), A[i]);
            C[i] += c;
        }
    }

    void push(int i) {
        if (identity(i)) return;
        apply(2 * i, A[i], B[i], C[i]), apply(2 * i + 1, A[i], B[i], C[i]);
        A[i] = INF, B[i] = NINF, C[i] = 0;
    }

    void pushToRoot(int p) {
        for (int s = H; s > 0; s--) push(p >> s);
    }

    // a node tagged during this update keeps its own clamp on top of its children
    void recomputeToRoot(int p) {
        for (p >>= 1; p; p >>= 1) {
            T lo = min(mn[2 * p], mn[2 * p + 1]), hi = max(mx[2 * p], mx[2 * p + 1]);
            if (identity(p)) mn[p] = lo, mx[p] = hi;
            else mn[p] = eval(lo, A[p], B[p], C[p]), mx[p] = eval(hi, A[p], B[p], C[p]);
        }
    }

    void upd(int l, int r, T a, T b, T c) {
        if (l > r) return;
        int l0 = l + size, r0 = r + size;
        pushToRoot(l0), pushToRoot(r0);
        for (int lo = l0, hi = r0 + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) apply(lo++, a, b, c);
            if (hi & 1) apply(--hi, a, b, c);
        }
        recomputeToRoot(l0), recomputeToRoot(r0);
    }

    // O(logN) -- a[i] = min(a[i], x) for i in [l, r]
    void rangeChmin(int l, int r, T x) { upd(l, r, x, NINF, 0); }

    // O(logN) -- a[i] = max(a[i], x) for i in [l, r]
    void rangeChmax(int l, int r, T x) { upd(l, r, INF, x, 0); }

    // O(logN) -- a[i] += x for i in [l, r]
    void rangeAdd(int l, int r, T x) { upd(l, r, INF, NINF, x); }

    // O(logN) -- a[i] = x for i in [l, r]
    void rangeAssign(int l, int r, T x) { upd(l, r, x, x, 0); }

    // O(logN) -- min of a[l..r]
    T rangeMin(int l, int r) {
        if (l > r) return INF;
        l += size, r += size;
        pushToRoot(l), pushToRoot(r);
        T res = INF;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = min(res, mn[l++]);
            if (r & 1) res = min(res, mn[--r]);
        }
        return res;
    }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) {
        if (l > r) return NINF;
        l += size, r += size;
        pushToRoot(l), pushToRoot(r);
        T res = NINF;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = max(res, mx[l++]);
            if (r & 1) res = max(res, mx[--r]);
        }
        return res;
    }

    // O(logN) -- a[i]
    T pointGet(int i) {
        pushToRoot(i + size);
        return mn[i + size];
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { rangeChmax(i, i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { rangeChmin(i, i, v); }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { rangeAdd(i, i, delta); }
};
