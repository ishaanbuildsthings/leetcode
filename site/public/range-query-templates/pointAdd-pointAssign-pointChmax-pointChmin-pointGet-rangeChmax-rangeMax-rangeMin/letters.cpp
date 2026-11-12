// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeChmax-rangeMax-rangeMin/letters.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll maxAll minAll pointAssign pointChmax pointChmin pointGet rangeChmax rangeMax rangeMin
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeChmax: log(N)
//   rangeMax: log(N)
//   rangeMin: log(N)
//   minAll: log(N)
//   maxAll: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: mn[2*N] mx[2*N]
//   tags: lo[1*N]
//   other: none
//   note: tags live on the N internal nodes only; each holds one clamp tag x -> max(lo, x)

// Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
// operations that make sense on characters are listed.
// Range chmax with range min / max queries, plus point ops. All indices 0-based, ranges inclusive [l, r].
// Iterative 2N lazy tree: values on the leaves, a tag on each internal node meaning "applied here, not yet pushed to my
// children". The tag is the map x -> max(lo, x); these maps compose into the same form, and each is monotone, so it
// sends a node's min / max straight to the new min / max.
// An update pushes the tags on its two boundary paths, tags the covering nodes, then rebuilds the two paths.
// T: int, long long, ...; the INF / NEG sentinels in the tags are never shifted.
template <typename T>
struct ChmaxMinMaxTree {
    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();
    int n, h;
    vector<T> mn, mx;  // 2N: leaves are tree[n..2n)
    vector<T> lo;  // N: tags on internal nodes

    // O(N)
    explicit ChmaxMinMaxTree(const vector<T>& a) : n((int)a.size()),
        h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())) {
        mn.assign(2 * n, INF);
        mx.assign(2 * n, NEG);
        for (int i = 0; i < n; i++) mn[n + i] = mx[n + i] = a[i];
        for (int x = n - 1; x > 0; x--) mn[x] = std::min(mn[2 * x], mn[2 * x + 1]),
            mx[x] = std::max(mx[2 * x], mx[2 * x + 1]);
        lo.assign(n, NEG);
    }

    static T clampValue(T v, T l) { v = max(v, l); return v; }

    // apply the map to node x: to its values now, and (if internal) on top of its pending tag
    void apply(int x, T loArg) {
        mn[x] = clampValue(mn[x], loArg);
        mx[x] = clampValue(mx[x], loArg);
        if (x < n) {
            T nlo = lo[x];
            nlo = std::max(nlo, loArg);
            lo[x] = nlo;
        }
    }

    // push every tag on the root-to-leaf path of leaf p down one level
    void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s;
            if (lo[x] != NEG) {
                apply(2 * x, lo[x]), apply(2 * x + 1, lo[x]);
                lo[x] = NEG;
            }
        }
    }

    // recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    void rebuild(int p) {
        while (p > 1) {
            p >>= 1;
            mn[p] = clampValue(std::min(mn[2 * p], mn[2 * p + 1]), lo[p]);
            mx[p] = clampValue(std::max(mx[2 * p], mx[2 * p + 1]), lo[p]);
        }
    }

    void update(int l, int r, T lo) {
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1; i < j; i >>= 1, j >>= 1) {
            if (i & 1) apply(i++, lo);
            if (j & 1) apply(--j, lo);
        }
        rebuild(l0), rebuild(r0);
    }

    // O(logN) -- a[i] = max(a[i], v) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeChmax(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeChmax: needs 0 <= l <= r < n");
        update(l, r, v);
    }

    // O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeMin(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMin: needs 0 <= l <= r < n");
        l += n, r += n;
        push(l), push(r);
        T res = INF;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = std::min(res, mn[l++]);
            if (r & 1) res = std::min(res, mn[--r]);
        }
        return res;
    }

    // O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeMax(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        l += n, r += n;
        push(l), push(r);
        T res = NEG;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = std::max(res, mx[l++]);
            if (r & 1) res = std::max(res, mx[--r]);
        }
        return res;
    }

    // O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    // each node's tag is complete when it is pushed), then read the leaves
    vector<T> getAll() {
        for (int x = 1; x < n; x++)
            if (lo[x] != NEG) {
                apply(2 * x, lo[x]), apply(2 * x + 1, lo[x]);
                lo[x] = NEG;
            }
        return vector<T>(mn.begin() + n, mn.end());
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        push(i + n);
        return mn[i + n];
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        push(p);
        mn[p] = mx[p] = v;
        rebuild(p);
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) pointAssign(i, v);
    }

    // O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else throws out_of_range
    auto minAll() {
        if (n < 1) throw out_of_range("minAll: needs n >= 1");
        return rangeMin(0, n - 1);
    }

    // O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws out_of_range
    auto maxAll() {
        if (n < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, n - 1);
    }

};
