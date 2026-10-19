// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd rangeLcm
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: ?
//   pointAssign: ?
//   pointChmax: ?
//   pointChmin: ?
//   pointGet: 1
//   rangeGcd: log(N)*log(U)
//   rangeLcm: ?
//   build: ?
// @memory:
//   layout: 2n-iterative
//   node: g[2*N] lcm[2*N]
//   tags: none
//   other: vals[1*N]
//   note: lcm values grow without bound (Python big ints; in C++ they overflow past 2^63), so lcm costs are unknown

// Range gcd + range lcm with point updates. All indices 0-based, ranges inclusive [l, r]. T: int, long long, ...
// Values may be negative or 0: gcd and lcm use absolute values, gcd(0, a) = a, lcm(0, a) = 0.
// Warning: lcm of a range overflows T quickly (lcm(1..43) > 2^63); only use it when lcms are known to stay small.
template <typename T>
struct GcdLcmTree {
    int n;
    vector<T> vals, g, lc;  // g / lc: 2N iterative trees of gcd / lcm of absolute values

    static T lcm(T a, T b) { return a == 0 || b == 0 ? T(0) : a / std::gcd(a, b) * b; }

    explicit GcdLcmTree(const vector<T>& a) : n((int)a.size()), vals(a), g(2 * a.size()), lc(2 * a.size()) {
        for (int i = 0; i < n; i++) g[n + i] = lc[n + i] = a[i] < 0 ? -a[i] : a[i];
        for (int x = n - 1; x > 0; x--) g[x] = std::gcd(g[2 * x], g[2 * x + 1]), lc[x] = lcm(lc[2 * x], lc[2 * x + 1]);
    }

    // O(logN logU) -- gcd of a[l..r]
    T rangeGcd(int l, int r) const {
        T res = 0;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = std::gcd(res, g[l++]);
            if (r & 1) res = std::gcd(res, g[--r]);
        }
        return res;
    }

    // lcm of a[l..r]
    T rangeLcm(int l, int r) const {
        T res = 1;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = lcm(res, lc[l++]);
            if (r & 1) res = lcm(res, lc[--r]);
        }
        return res;
    }

    // a[i] = v
    void pointAssign(int i, T v) {
        vals[i] = v;
        int p = i + n;
        g[p] = lc[p] = v < 0 ? -v : v;
        for (p >>= 1; p; p >>= 1) g[p] = std::gcd(g[2 * p], g[2 * p + 1]), lc[p] = lcm(lc[2 * p], lc[2 * p + 1]);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return vals[i]; }

    // a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > vals[i]) pointAssign(i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < vals[i]) pointAssign(i, v); }

    // a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, vals[i] + delta); }
};
