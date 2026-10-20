// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeFloorDiv/template.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorDiv
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeFloorDiv: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[1*N]
//   tags: tree[1*N]
//   other: none
//   note: tree[n:] holds the values, tree[1:n] holds each node's pending divisor (product of divisions, capped); leaves count as node data, internal nodes as tags

// Range floor-divide + point ops. All indices 0-based, ranges inclusive [l, r]. T: int, long long, ...
// floor(floor(x / a) / b) == floor(x / (a * b)) for positive integers a, b and any integer x, so pending
// divisions are just a product. Products are capped at CAP = max(T): once a divisor exceeds every |value|,
// any larger divisor gives the same floor. Requires every divisor >= 1 and |a[i]| < CAP.
template <typename T>
struct RangeFloorDivTree {
    static constexpr T CAP = numeric_limits<T>::max();
    int n;
    vector<T> tree;  // tree[n + i] = a[i]; tree[1 .. n-1] = pending divisor product (1 = none)

    static T floorDiv(T x, T d) { T q = x / d; return (x % d != 0 && x < 0) ? q - 1 : q; }
    static T mulCap(T a, T b) { return a > CAP / b ? CAP : a * b; }

    // O(N)
    explicit RangeFloorDivTree(const vector<T>& a) : n((int)a.size()), tree(2 * a.size(), T(1)) {
        for (int i = 0; i < n; i++) tree[n + i] = a[i];
    }

    void apply(int x, T d) { tree[x] = x >= n ? floorDiv(tree[x], d) : mulCap(tree[x], d); }

    // O(logN) -- a[i] = floor(a[i] / d) for i in [l, r], d >= 1
    void rangeFloorDiv(int l, int r, T d) {
        if (d == 1) return;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) apply(l++, d);
            if (r & 1) apply(--r, d);
        }
    }

    // O(logN) -- apply the divisors on leaf p's path, so nothing above p is pending
    void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            if (tree[x] != 1) apply(2 * x, tree[x]), apply(2 * x + 1, tree[x]), tree[x] = 1;
        }
    }

    // O(logN) -- a[i]
    T pointGet(int i) const {
        int p = i + n;
        T d = 1;
        for (int x = p >> 1; x; x >>= 1) d = mulCap(d, tree[x]);
        return floorDiv(tree[p], d);
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { push(i + n); tree[i + n] = v; }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { push(i + n); tree[i + n] += delta; }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { push(i + n); if (v > tree[i + n]) tree[i + n] = v; }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { push(i + n); if (v < tree[i + n]) tree[i + n] = v; }
};
