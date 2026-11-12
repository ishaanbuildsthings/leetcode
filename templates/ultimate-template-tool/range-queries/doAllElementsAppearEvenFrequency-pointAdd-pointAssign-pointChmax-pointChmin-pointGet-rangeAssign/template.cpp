// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/doAllElementsAppearEvenFrequency-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: doAllElementsAppearEvenFrequency getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
// @data-structure-type: lazy-seg-tree
// @letters: same
// @complexities:
//   doAllElementsAppearEvenFrequency: log(N)
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAssign: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: xr[2*N]
//   tags: asg[1*N] hasAsg[1*N]
//   other: vals[1*N]
//   note: xr holds the xor of value tags; a value's tag is splitmix64(value ^ seed), a keyed hash with a random per-run seed, so there is no value -> tag table; vals holds each leaf's value

// Range "does every value appear an even number of times?" via xor hashing, with range assign. All indices 0-based,
// ranges inclusive [l, r].
// Each distinct value gets a 64-bit tag, splitmix64(value ^ seed): a bijection on 64-bit ints keyed by a random per-run
// seed, so equal values share a tag and distinct integers never collide. Xor over a range cancels tags in pairs, so an
// all-even range hashes to 0; false positives (unequal tags whose xor cancels) have probability ~q / 2^64.
// Lazy segment tree (2N iterative) over the tags: a node assigned value v holds tag(v) if it covers an odd number of
// leaves, else 0. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s = its
// level), and every internal node holds its pending assign: an update pushes the tags on its two boundary leaf paths,
// tags the covering nodes, then rebuilds both paths.
// T: an integer type (or anything std::hash takes).
template <typename T>
struct XorEvenAssign {
    int n, h;
    unsigned long long seed;
    vector<unsigned long long> xr;  // xor of the tags under each node; leaves are xr[n + i]
    vector<T> vals;                 // vals[i] = the value at leaf i (once the assigns above it are pushed)
    vector<T> asg;                  // pending assign of each internal node
    vector<char> hasAsg;

    // O(N). Seeded from the clock: a fixed seed is hackable, since tags could be precomputed to collide.
    explicit XorEvenAssign(const vector<T>& arr)
        : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0),
          seed(mt19937_64(chrono::steady_clock::now().time_since_epoch().count())()), xr(2 * arr.size()), vals(arr),
          asg(arr.size()), hasAsg(arr.size(), 0) {
        for (int i = 0; i < n; i++) xr[n + i] = tagOf(arr[i]);
        for (int x = n - 1; x > 0; x--) xr[x] = xr[2 * x] ^ xr[2 * x + 1];
    }

    // O(1) -- the value's tag: splitmix64(v ^ seed)
    unsigned long long tagOf(const T& v) const {
        unsigned long long z;
        if constexpr (is_integral_v<T>) z = (unsigned long long)v;
        else z = hash<T>{}(v);
        z ^= seed;
        z += 0x9e3779b97f4a7c15ULL;
        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
        z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
        return z ^ (z >> 31);
    }

    // O(logN) -- true iff every value in a[l..r] appears an even number of times; needs 0 <= l <= r < n, else throws
    // out_of_range
    bool doAllElementsAppearEvenFrequency(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("doAllElementsAppearEvenFrequency: needs 0 <= l <= r < n");
        pushPath(l + n), pushPath(r + n);
        unsigned long long res = 0;
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res ^= xr[lo++];
            if (hi & 1) res ^= xr[--hi];
        }
        return res == 0;
    }

    // O(logN) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAssign(int l, int r, const T& v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        unsigned long long t = tagOf(v);
        pushPath(l + n), pushPath(r + n);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) apply(lo++, v, t);
            if (hi & 1) apply(--hi, v, t);
        }
        rebuild(l + n), rebuild(r + n);
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        pushPath(p);
        vals[i] = v, xr[p] = tagOf(v);
        rebuild(p);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        pushPath(i + n);
        return vals[i];
    }

    // O(N) -- the whole array, every pending assign pushed down on the way
    vector<T> getAll() {
        for (int x = 1; x < n; x++) push(x);  // (parents before children)
        return vals;
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, const T& delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, T(pointGet(i) + delta));
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) pointAssign(i, v);
    }

    // ---- internals ----

    void apply(int x, const T& v, unsigned long long t) {  // every value under node x becomes v, whose tag is t
        if (x >= n) {
            vals[x - n] = v, xr[x] = t;
        } else {
            xr[x] = 0;  // (an assigned internal node is a perfect subtree of 2^s >= 2 leaves: an even count)
            asg[x] = v, hasAsg[x] = 1;
        }
    }

    void push(int x) {  // hand node x's pending assign to its children
        if (!hasAsg[x]) return;
        unsigned long long t = tagOf(asg[x]);
        apply(2 * x, asg[x], t), apply(2 * x + 1, asg[x], t);
        hasAsg[x] = 0;
    }

    void pushPath(int p) {  // hand down every pending assign on the path from the root to leaf p
        for (int s = h; s > 0; s--) push(p >> s);
    }

    void rebuild(int p) {  // recompute every ancestor of leaf p (an assigned node keeps its own value)
        for (p >>= 1; p; p >>= 1)
            if (!hasAsg[p]) xr[p] = xr[2 * p] ^ xr[2 * p + 1];
    }
};
