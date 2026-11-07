// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostGtX-leftmostGteX-leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeMax-rangeMin-rightmostGtX-rightmostGteX-rightmostLtX-rightmostLteX/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rightmostGtX rightmostGteX rightmostLtX rightmostLteX
// @data-structure-type: seg-tree
// @complexities:
//   leftmostGtX: log(U)
//   leftmostGteX: log(U)
//   leftmostLtX: log(U)
//   leftmostLteX: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeMax: log(U)
//   rangeMin: log(U)
//   rightmostGtX: log(U)
//   rightmostGteX: log(U)
//   rightmostLtX: log(U)
//   rightmostLteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[1*log(U)] mn[1*log(U)]
//   tags: none
//   other: children[2*log(U)]
//   note: per update, one node per level of the touched path;  a node pool per tree (node 0 = all zeros)

// Range max / min and leftmost / rightmost index with a[i] >= / > / <= / < x, with point updates, over any index range
// [lo, hi] (huge or negative is fine); every position starts at 0. Searches return lo - 1 when nothing qualifies (-1
// when lo = 0). Sparse: only the nodes on updated paths exist, in a pool the tree owns; node 0 is the all-zeros block.
// A search prunes any node whose max / min can't pass, so it visits O(log U) nodes. T: int, long long, ...
// FAST MODE drawbacks compared with sparse.cpp:
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.
#ifdef __SSE2__
#include <immintrin.h>
#endif

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A vector whose [] and size() always inline, even with sanitizers skipped (libstdc++ only; elsewhere a plain vector)
template <typename U>
struct HotVector : vector<U> {
    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct SparseMaxMinSearchTree {
    struct Agg { T mx; T mn; };
    struct Node { Agg v; int l, r; };
    HotVector<Node> pool{Node{Agg{}, 0, 0}};  // node 0: the all-zeros block
    long long lo, hi;
    int root = 0;

    // O(1) -- an all-zero array over [lo, hi]; any long long range works
    SparseMaxMinSearchTree(long long lo, long long hi) : lo(lo), hi(hi) {}


    // optional: reserve room for this many nodes up front (about log U per update)
    LEETCODE_NO_SANITIZE void reservePool(size_t nodes) { pool.reserve(nodes); }

    LEETCODE_NO_SANITIZE int make() {
        pool.push_back(Node{Agg{}, 0, 0});
        return (int)pool.size() - 1;
    }

    // walk from the root to leaf i, creating missing nodes; fills path[] with the nodes above the leaf and
    // returns the leaf. len[] / starts[] (when given) receive each path node's range.
    LEETCODE_NO_SANITIZE int descend(long long i, int* path, int& depth, long long* starts = nullptr, long long* ends = nullptr) {
        if (!root) root = make();
        int x = root;
        long long a = lo, b = hi;
        depth = 0;
        while (a < b) {
            if (starts) starts[depth] = a, ends[depth] = b;
            path[depth++] = x;
            long long m = a + (b - a) / 2;
            if (i <= m) {
                if (!pool[x].l) { int y = make(); pool[x].l = y; }
                x = pool[x].l, b = m;
            } else {
                if (!pool[x].r) { int y = make(); pool[x].r = y; }
                x = pool[x].r, a = m + 1;
            }
        }
        return x;
    }

    // O(logU) -- the leaf for i, or 0 if no update has touched it
    LEETCODE_NO_SANITIZE int find(long long i) const {
        int x = root;
        long long a = lo, b = hi;
        while (x && a < b) {
            long long m = a + (b - a) / 2;
            if (i <= m) x = pool[x].l, b = m;
            else x = pool[x].r, a = m + 1;
        }
        return x;
    }

    LEETCODE_NO_SANITIZE static Agg merge(const Agg& a, const Agg& b) { return Agg{max(a.mx, b.mx), min(a.mn, b.mn)}; }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        int path[130], depth;
        int x = descend(i, path, depth);
        pool[x].v = Agg{v, v};
        while (depth) {
            int y = path[--depth];
            pool[y].v = merge(pool[pool[y].l].v, pool[pool[y].r].v);
        }
    }

    LEETCODE_NO_SANITIZE T foldmx(int x, long long a, long long b, long long l, long long r) const {
        if (r < a || b < l) return numeric_limits<T>::lowest();
        if (!x || (l <= a && b <= r)) return pool[x].v.mx;  // node 0 holds 0, the value of a block of zeros
        long long m = a + (b - a) / 2;
        return max(foldmx(pool[x].l, a, m, l, r), foldmx(pool[x].r, m + 1, b, l, r));
    }

    // O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMax: needs lo <= l <= r <= hi");
        return foldmx(root, lo, hi, l, r);
    }

    LEETCODE_NO_SANITIZE T foldmn(int x, long long a, long long b, long long l, long long r) const {
        if (r < a || b < l) return numeric_limits<T>::max();
        if (!x || (l <= a && b <= r)) return pool[x].v.mn;  // node 0 holds 0, the value of a block of zeros
        long long m = a + (b - a) / 2;
        return min(foldmn(pool[x].l, a, m, l, r), foldmn(pool[x].r, m + 1, b, l, r));
    }

    // O(logU) -- min of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMin: needs lo <= l <= r <= hi");
        return foldmn(root, lo, hi, l, r);
    }

    LEETCODE_NO_SANITIZE long long leftGte(int x, long long a, long long b, long long l, long long r, T v) const {
        if (r < a || b < l || !(pool[x].v.mx >= v)) return lo - 1;
        if (!x) return max(a, l);  // a block of zeros, and 0 passes
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = leftGte(pool[x].l, a, m, l, r, v);
        return res != lo - 1 ? res : leftGte(pool[x].r, m + 1, b, l, r, v);
    }

    LEETCODE_NO_SANITIZE long long rightGte(int x, long long a, long long b, long long l, long long r, T v) const {
        if (r < a || b < l || !(pool[x].v.mx >= v)) return lo - 1;
        if (!x) return min(b, r);
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = rightGte(pool[x].r, m + 1, b, l, r, v);
        return res != lo - 1 ? res : rightGte(pool[x].l, a, m, l, r, v);
    }

    // O(logU) -- first i in [l, r] with a[i] >= x, or lo - 1; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostGteX: needs lo <= l <= r <= hi");
        return leftGte(root, lo, hi, l, r, x);
    }

    // O(logU) -- last i in [l, r] with a[i] >= x, or lo - 1; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostGteX: needs lo <= l <= r <= hi");
        return rightGte(root, lo, hi, l, r, x);
    }

    LEETCODE_NO_SANITIZE long long leftGt(int x, long long a, long long b, long long l, long long r, T v) const {
        if (r < a || b < l || !(pool[x].v.mx > v)) return lo - 1;
        if (!x) return max(a, l);  // a block of zeros, and 0 passes
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = leftGt(pool[x].l, a, m, l, r, v);
        return res != lo - 1 ? res : leftGt(pool[x].r, m + 1, b, l, r, v);
    }

    LEETCODE_NO_SANITIZE long long rightGt(int x, long long a, long long b, long long l, long long r, T v) const {
        if (r < a || b < l || !(pool[x].v.mx > v)) return lo - 1;
        if (!x) return min(b, r);
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = rightGt(pool[x].r, m + 1, b, l, r, v);
        return res != lo - 1 ? res : rightGt(pool[x].l, a, m, l, r, v);
    }

    // O(logU) -- first i in [l, r] with a[i] > x, or lo - 1; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostGtX: needs lo <= l <= r <= hi");
        return leftGt(root, lo, hi, l, r, x);
    }

    // O(logU) -- last i in [l, r] with a[i] > x, or lo - 1; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostGtX: needs lo <= l <= r <= hi");
        return rightGt(root, lo, hi, l, r, x);
    }

    LEETCODE_NO_SANITIZE long long leftLte(int x, long long a, long long b, long long l, long long r, T v) const {
        if (r < a || b < l || !(pool[x].v.mn <= v)) return lo - 1;
        if (!x) return max(a, l);  // a block of zeros, and 0 passes
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = leftLte(pool[x].l, a, m, l, r, v);
        return res != lo - 1 ? res : leftLte(pool[x].r, m + 1, b, l, r, v);
    }

    LEETCODE_NO_SANITIZE long long rightLte(int x, long long a, long long b, long long l, long long r, T v) const {
        if (r < a || b < l || !(pool[x].v.mn <= v)) return lo - 1;
        if (!x) return min(b, r);
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = rightLte(pool[x].r, m + 1, b, l, r, v);
        return res != lo - 1 ? res : rightLte(pool[x].l, a, m, l, r, v);
    }

    // O(logU) -- first i in [l, r] with a[i] <= x, or lo - 1; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostLteX: needs lo <= l <= r <= hi");
        return leftLte(root, lo, hi, l, r, x);
    }

    // O(logU) -- last i in [l, r] with a[i] <= x, or lo - 1; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostLteX: needs lo <= l <= r <= hi");
        return rightLte(root, lo, hi, l, r, x);
    }

    LEETCODE_NO_SANITIZE long long leftLt(int x, long long a, long long b, long long l, long long r, T v) const {
        if (r < a || b < l || !(pool[x].v.mn < v)) return lo - 1;
        if (!x) return max(a, l);  // a block of zeros, and 0 passes
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = leftLt(pool[x].l, a, m, l, r, v);
        return res != lo - 1 ? res : leftLt(pool[x].r, m + 1, b, l, r, v);
    }

    LEETCODE_NO_SANITIZE long long rightLt(int x, long long a, long long b, long long l, long long r, T v) const {
        if (r < a || b < l || !(pool[x].v.mn < v)) return lo - 1;
        if (!x) return min(b, r);
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = rightLt(pool[x].r, m + 1, b, l, r, v);
        return res != lo - 1 ? res : rightLt(pool[x].l, a, m, l, r, v);
    }

    // O(logU) -- first i in [l, r] with a[i] < x, or lo - 1; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostLtX: needs lo <= l <= r <= hi");
        return leftLt(root, lo, hi, l, r, x);
    }

    // O(logU) -- last i in [l, r] with a[i] < x, or lo - 1; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostLtX: needs lo <= l <= r <= hi");
        return rightLt(root, lo, hi, l, r, x);
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return pool[find(i)].v.mx;
    }

    // O(logU) -- a[i] += delta; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(long long i, T delta) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmax: needs lo <= i <= hi");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmin: needs lo <= i <= hi");
        if (v < pointGet(i)) pointAssign(i, v);
    }
};
