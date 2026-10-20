// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/maxPrefixSum-maxSubarraySum-maxSuffixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeSum/template.cpp
// @operations: maxPrefixSum maxSubarraySum maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeSum
// @data-structure-type: lazy-seg-tree
// @complexities:
//   maxPrefixSum: log(N)
//   maxSubarraySum: log(N)
//   maxSuffixSum: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAssign: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: pow2-iterative
//   node: sm[4*N] pre[4*N] suf[4*N] best[4*N]
//   tags: asg[2*N] hasAsg[2*N]
//   other: none
//   note: node = (sum, best prefix, best suffix, best subarray); the one tag is a pending assign. Range add is not supported: it changes which subarray wins

// Max subarray / max prefix / max suffix sum of a range, plus range sum, with RANGE ASSIGN and point updates.
// All indices 0-based, ranges inclusive [l, r]. All three maxima are over NON-EMPTY pieces; when the empty piece is
// allowed (answer >= 0), take max(0, ...).
// A node assigned v over len slots is fully known: sum = v * len, and its best prefix / suffix / subarray are all
// v * len if v > 0, else just v (one element). So assign is an ordinary lazy tag. Range ADD is not: adding d moves
// every piece by d * (its length), which changes which piece wins, and a node can't recompute that from a tag.
// Iterative lazy tree over a power-of-two layout; queries fold a left and a right accumulator (not commutative).
// T: int, long long, ...; every sum is kept in S (long long for small T).
template <typename T>
struct MaxSubarrayAssignTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { S sm, pre, suf, best; };
    int n, size, H;
    vector<Node> t;
    vector<T> asg;        // tags, internal nodes only
    vector<char> hasAsg;

    static Node merge(const Node& a, const Node& b) {
        return {a.sm + b.sm, max(a.pre, a.sm + b.pre), max(b.suf, b.sm + a.suf), max({a.best, b.best, a.suf + b.pre})};
    }

    // O(N)
    explicit MaxSubarrayAssignTree(const vector<T>& a) : n((int)a.size()), size(1), H(0) {
        while (size < max(n, 1)) size <<= 1, H++;
        t.assign(2 * size, Node{0, 0, 0, 0}), asg.assign(size, 0), hasAsg.assign(size, 0);
        for (int i = 0; i < n; i++) t[size + i] = {S(a[i]), S(a[i]), S(a[i]), S(a[i])};
        for (int x = size - 1; x > 0; x--) t[x] = merge(t[2 * x], t[2 * x + 1]);
    }

    // node x (covering len slots) becomes len copies of v
    void setAll(int x, int len, T v) {
        S s = S(v) * len, b = v > 0 ? s : S(v);
        t[x] = {s, b, b, b};
        if (x < size) hasAsg[x] = 1, asg[x] = v;
    }

    void push(int x, int childLen) {
        if (!hasAsg[x]) return;
        setAll(2 * x, childLen, asg[x]), setAll(2 * x + 1, childLen, asg[x]);
        hasAsg[x] = 0;
    }

    void pushToRoot(int p) {
        for (int s = H; s > 0; s--) push(p >> s, 1 << (s - 1));
    }

    // a node assigned during this update keeps its own tag's value
    void recomputeToRoot(int p) {
        int len = 2;
        for (p >>= 1; p; p >>= 1, len <<= 1) {
            if (hasAsg[p]) setAll(p, len, asg[p]);
            else t[p] = merge(t[2 * p], t[2 * p + 1]);
        }
    }

    // O(logN) -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) {
        if (l > r) return;
        int l0 = l + size, r0 = r + size;
        pushToRoot(l0), pushToRoot(r0);
        for (int lo = l0, hi = r0 + 1, len = 1; lo < hi; lo >>= 1, hi >>= 1, len <<= 1) {
            if (lo & 1) setAll(lo++, len, v);
            if (hi & 1) setAll(--hi, len, v);
        }
        recomputeToRoot(l0), recomputeToRoot(r0);
    }

    // O(logN) -- (sum, best prefix, best suffix, best subarray) of a[l..r], l <= r
    Node query(int l, int r) {
        l += size, r += size;
        pushToRoot(l), pushToRoot(r);
        Node left{}, right{};
        bool lEmpty = true, rEmpty = true;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) left = lEmpty ? t[l] : merge(left, t[l]), lEmpty = false, l++;
            if (r & 1) --r, right = rEmpty ? t[r] : merge(t[r], right), rEmpty = false;
        }
        if (rEmpty) return left;
        if (lEmpty) return right;
        return merge(left, right);
    }

    // O(logN) -- max over l <= i <= j <= r of a[i] + ... + a[j]
    S maxSubarraySum(int l, int r) { return query(l, r).best; }

    // O(logN) -- max over l <= i <= r of a[l] + ... + a[i]
    S maxPrefixSum(int l, int r) { return query(l, r).pre; }

    // O(logN) -- max over l <= i <= r of a[i] + ... + a[r]
    S maxSuffixSum(int l, int r) { return query(l, r).suf; }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) { return l <= r ? query(l, r).sm : S(0); }

    // O(logN) -- a[i]
    T pointGet(int i) {
        pushToRoot(i + size);
        return T(t[i + size].sm);
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { rangeAssign(i, i, pointGet(i) + delta); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) rangeAssign(i, i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) rangeAssign(i, i, v); }
};
