// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/maxAltSubseqSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/template.cpp
// @operations: maxAltSubseqSum pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: seg-tree
// @complexities:
//   maxAltSubseqSum: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: pp[2*N] pm[2*N] mp[2*N] mm[2*N]
//   tags: none
//   other: vals[1*N]
//   note: f[s][e] = best alternating sum inside the node that starts with sign s and ends with sign e; queries fold a left and a right accumulator

// Max alternating subsequence sum  +a[i1] - a[i2] + a[i3] - ...  (i1 < i2 < ..., non-empty, starts with +) inside
// a[l..r], with point updates. All indices 0-based, ranges inclusive.
// Each node keeps the best sum for each (first sign, last sign) pair. Joining A then B either takes one side alone
// or glues A's piece ending in sign x to B's piece starting with the opposite sign. Not commutative, so a query
// folds a left and a right accumulator. Only a single leaf has impossible pairs (+..- and -..+); they hold NEG,
// which is small enough to lose every max and big enough that NEG + NEG cannot overflow.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct AltSumTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;
    struct Node { S pp, pm, mp, mm; };  // starts + / -, ends + / -
    int n;
    vector<T> vals;
    vector<Node> t;

    static Node leaf(T v) { return {S(v), NEG, NEG, -S(v)}; }

    static Node merge(const Node& a, const Node& b) {
        return {max({a.pp, b.pp, a.pp + b.mp, a.pm + b.pp}), max({a.pm, b.pm, a.pp + b.mm, a.pm + b.pm}),
                max({a.mp, b.mp, a.mp + b.mp, a.mm + b.pp}), max({a.mm, b.mm, a.mp + b.mm, a.mm + b.pm})};
    }

    // O(N)
    explicit AltSumTree(const vector<T>& a) : n((int)a.size()), vals(a), t(2 * a.size()) {
        for (int i = 0; i < n; i++) t[n + i] = leaf(a[i]);
        for (int x = n - 1; x > 0; x--) t[x] = merge(t[2 * x], t[2 * x + 1]);
    }

    // O(logN) -- max over non-empty subsequences of a[l..r] of +first - second + third - ...
    S maxAltSubseqSum(int l, int r) const {
        Node left{}, right{};
        bool lEmpty = true, rEmpty = true;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) left = lEmpty ? t[l] : merge(left, t[l]), lEmpty = false, l++;
            if (r & 1) --r, right = rEmpty ? t[r] : merge(t[r], right), rEmpty = false;
        }
        Node res = rEmpty ? left : lEmpty ? right : merge(left, right);
        return max(res.pp, res.pm);
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {
        vals[i] = v;
        int p = i + n;
        t[p] = leaf(v);
        for (p >>= 1; p; p >>= 1) t[p] = merge(t[2 * p], t[2 * p + 1]);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return vals[i]; }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, vals[i] + delta); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > vals[i]) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < vals[i]) pointAssign(i, v); }
};
