// @operations: longestEqualRun pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: seg-tree
// @complexities:
//   longestEqualRun: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: ln[2*N] pre[2*N] suf[2*N] best[2*N] lv[2*N] rv[2*N]
//   tags: none
//   other: none
//   note: per node: length, equal-run at the left / right end, best run inside, and the end values; queries fold a left and a right accumulator
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/LongestContiguousBlockSeg.cpp

// Longest run of equal adjacent values inside a[l..r], with point updates. All indices 0-based, ranges inclusive.
// Iterative 2N tree. Merging A then B: the runs at the seam join when A's last value == B's first value. The merge
// is not commutative, so a query folds a left accumulator and a right accumulator, then joins them.
// T: any type with ==.
template <typename T>
struct EqualRunTree {
    struct Node { int ln, pre, suf, best; T lv, rv; };
    int n;
    vector<Node> t;

    static Node leaf(T v) { return {1, 1, 1, 1, v, v}; }

    static Node merge(const Node& a, const Node& b) {
        bool join = a.rv == b.lv;
        Node r{a.ln + b.ln, a.pre, b.suf, max(a.best, b.best), a.lv, b.rv};
        if (join && a.pre == a.ln) r.pre = a.ln + b.pre;
        if (join && b.suf == b.ln) r.suf = b.ln + a.suf;
        if (join) r.best = max(r.best, a.suf + b.pre);
        return r;
    }

    // O(N)
    explicit EqualRunTree(const vector<T>& a) : n((int)a.size()), t(2 * a.size()) {
        for (int i = 0; i < n; i++) t[n + i] = leaf(a[i]);
        for (int x = n - 1; x > 0; x--) t[x] = merge(t[2 * x], t[2 * x + 1]);
    }

    // O(logN) -- length of the longest block of equal adjacent values inside a[l..r]
    int longestEqualRun(int l, int r) const {
        Node left{}, right{};
        bool lEmpty = true, rEmpty = true;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) left = lEmpty ? t[l] : merge(left, t[l]), lEmpty = false, l++;
            if (r & 1) --r, right = rEmpty ? t[r] : merge(t[r], right), rEmpty = false;
        }
        if (rEmpty) return left.best;
        if (lEmpty) return right.best;
        return merge(left, right).best;
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {
        int p = i + n;
        t[p] = leaf(v);
        for (p >>= 1; p; p >>= 1) t[p] = merge(t[2 * p], t[2 * p + 1]);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return t[i + n].lv; }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
