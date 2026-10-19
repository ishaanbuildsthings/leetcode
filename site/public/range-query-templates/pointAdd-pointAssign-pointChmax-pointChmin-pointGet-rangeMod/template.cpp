// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeMod
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   rangeMod: log(N)*log(U) amortized
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: mx[2*N]
//   tags: none
//   other: none
//   note: mx[n:] holds the values, mx[1:n] the max of each node's subtree; there are no tags at all

// Range mod + point ops. All indices 0-based, ranges inclusive [l, r]. Requires a[i] >= 0, mod >= 1.
// Mods don't compose into a single tag, so rangeMod walks down into every covering node whose max is still
// >= mod. Each value that actually changes at least halves, so the work is amortized O((N + Q) logN logU).
// T: int, long long, ...
template <typename T>
struct RangeModTree {
    int n;
    vector<T> mx;  // mx[n + i] = a[i]; mx[1 .. n-1] = max of the subtree
    vector<int> stack, inner;

    // O(N)
    explicit RangeModTree(const vector<T>& a) : n((int)a.size()), mx(2 * a.size()) {
        for (int i = 0; i < n; i++) mx[n + i] = a[i];
        for (int i = n - 1; i > 0; i--) mx[i] = max(mx[2 * i], mx[2 * i + 1]);
    }

    // O(logN) -- recompute the maxes on leaf p's path to the root
    void pull(int p) {
        for (p >>= 1; p; p >>= 1) mx[p] = max(mx[2 * p], mx[2 * p + 1]);
    }

    void descend(int top, T mod) {
        stack.assign(1, top);
        inner.clear();
        while (!stack.empty()) {
            int y = stack.back();
            stack.pop_back();
            if (mx[y] < mod) continue;
            if (y >= n) mx[y] %= mod;
            else inner.push_back(y), stack.push_back(2 * y), stack.push_back(2 * y + 1);
        }
        // pre-order reversed puts every child before its parent
        for (int k = (int)inner.size() - 1; k >= 0; k--) {
            int y = inner[k];
            mx[y] = max(mx[2 * y], mx[2 * y + 1]);
        }
    }

    // amortized O(logN logU) -- a[i] %= mod for i in [l, r]
    void rangeMod(int l, int r, T mod) {
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) descend(lo++, mod);
            if (hi & 1) descend(--hi, mod);
        }
        pull(l + n), pull(r + n);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return mx[i + n]; }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { mx[i + n] = v; pull(i + n); }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { mx[i + n] += delta; pull(i + n); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > mx[i + n]) mx[i + n] = v, pull(i + n); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < mx[i + n]) mx[i + n] = v, pull(i + n); }
};
