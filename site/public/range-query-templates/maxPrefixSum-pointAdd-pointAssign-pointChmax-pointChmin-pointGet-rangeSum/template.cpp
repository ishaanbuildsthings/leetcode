// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/maxPrefixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum/template.cpp
// @operations: maxPrefixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeSum
// @data-structure-type: seg-tree
// @complexities:
//   maxPrefixSum: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: sm[2*N] pre[2*N]
//   tags: none
//   other: none
//   note: each node is (sum, best prefix); the merge is not commutative, so a query folds a left and a right accumulator

// Max prefix sum of a range, plus range sum, with point updates. All indices 0-based, ranges
// inclusive [l, r]. Maxima are over NON-EMPTY pieces; when the empty piece is allowed (answer >= 0), take max(0, ...).
// Iterative 2N tree. The merge is not commutative, so a query folds nodes into a left accumulator (left to right)
// and a right accumulator (right to left), then joins the two. Leaner than the max subarray tree: only
// (sm, pre) per node. T: int, long long, ...; every sum is kept in S (long long for small T).
template <typename T>
struct MaxPrefixSumTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { S sm, pre; };
    int n;
    vector<Node> t;

    static Node leaf(T v) { return {S(v), S(v)}; }

    static Node merge(const Node& a, const Node& b) { return {a.sm + b.sm, max(a.pre, a.sm + b.pre)}; }

    // O(N)
    explicit MaxPrefixSumTree(const vector<T>& a) : n((int)a.size()), t(2 * a.size()) {
        for (int i = 0; i < n; i++) t[n + i] = leaf(a[i]);
        for (int x = n - 1; x > 0; x--) t[x] = merge(t[2 * x], t[2 * x + 1]);
    }

    // O(logN) -- (sm, pre) of a[l..r], l <= r
    Node query(int l, int r) const {
        Node left{}, right{};
        bool lEmpty = true, rEmpty = true;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) left = lEmpty ? t[l] : merge(left, t[l]), lEmpty = false, l++;
            if (r & 1) --r, right = rEmpty ? t[r] : merge(t[r], right), rEmpty = false;
        }
        if (rEmpty) return left;
        if (lEmpty) return right;
        return merge(left, right);
    }

    // O(logN) -- max over l <= i <= r of a[l] + ... + a[i]
    S maxPrefixSum(int l, int r) const { return query(l, r).pre; }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) const { return l <= r ? query(l, r).sm : S(0); }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {
        int p = i + n;
        t[p] = leaf(v);
        for (p >>= 1; p; p >>= 1) t[p] = merge(t[2 * p], t[2 * p + 1]);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return T(t[i + n].sm); }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
