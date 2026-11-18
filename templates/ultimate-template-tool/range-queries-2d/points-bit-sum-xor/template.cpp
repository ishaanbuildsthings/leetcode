// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-bit-sum-xor/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rectSum rectXor sumAll sumGteGte sumGteLte sumLteGte sumLteLte xorAll
// @data-structure-type: BIT
// @input: points
// @complexities:
//   pointAdd: log^2(N)
//   pointAssign: log^2(N)
//   pointChmax: log^2(N)
//   pointChmin: log^2(N)
//   pointGet: log(N)
//   rectSum: log^2(N)
//   rectXor: log^2(N)
//   sumAll: 1
//   sumGteGte: log^2(N)
//   sumGteLte: log^2(N)
//   sumLteGte: log^2(N)
//   sumLteLte: log^2(N)
//   xorAll: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: sm[1*N*log(N)] xr[1*N*log(N)]
//   tags: none
//   other: ys[1*N*log(N)] pts[2*N] vals[1*N] xs[1*N] off[1*N] cnt[1*N]
//   note: every point's y is listed in each of the O(log N) Fenwick x-nodes covering it; an x-node's own Fenwick tree is as long as its list

// Sanitizers are skipped inside this template (its methods start with LEETCODE_NO_SANITIZE): where they run, like on
// LeetCode, that is most of its speed. The drawback: a bad memory access inside the template goes unreported. Arguments
// are still checked and still throw. Constructors are left alone. It needs GCC or Clang and C++17.

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
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

// how many of the n sorted values at `first` are < x (std::lower_bound as a count, inlined with sanitizers skipped)
template <typename A>
LEETCODE_NO_SANITIZE_INLINE int hotLowerBound(const A* first, int n, A x) {
    int lo = 0;
    while (n > 0) {
        int half = n >> 1;
        if (first[lo + half] < x) lo += half + 1, n -= half + 1;
        else n = half;
    }
    return lo;
}
// how many of the n sorted values at `first` are <= x (std::upper_bound as a count)
template <typename A>
LEETCODE_NO_SANITIZE_INLINE int hotUpperBound(const A* first, int n, A x) {
    int lo = 0;
    while (n > 0) {
        int half = n >> 1;
        if (!(x < first[lo + half])) lo += half + 1, n -= half + 1;
        else n = half;
    }
    return lo;
}

// 2D Fenwick tree over points known up front (sum and xor): point updates and any-rectangle sum and xor in O(log^2
// N), with N log N memory whatever the coordinates are (any integers, negative is fine). The constructor takes every
// (x, y) that will ever be updated; every point starts at 0. A Fenwick tree over the distinct x's; every node of it
// keeps the sorted y's of the points it covers and a Fenwick tree over just those. Half the memory of the segment
// tree version and a smaller constant, for sum and xor only. Rectangles are inclusive, x1..x2 by y1..y2, and their
// corners can be any integers, given or not.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T). Coordinates are long
// long.
template <typename T>
struct PointsFenwick2D {
    using ll = long long;
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    HotVector<pair<ll, ll>> pts;
    HotVector<T> vals;
    HotVector<ll> xs, ys;
    HotVector<int> off, cnt;
    HotVector<S> sm;  // x-node i's own Fenwick tree is [off[i], off[i] + cnt[i]), 1-based inside
    S totalSum = 0;
    HotVector<T> xr;  // x-node i's own Fenwick tree is [off[i], off[i] + cnt[i]), 1-based inside
    T totalXor = 0;

    // O(N log N) -- points: every (x, y) that will ever be updated (negative is fine, repeats are fine); needs at least
    // one, else throws invalid_argument
    explicit PointsFenwick2D(vector<pair<ll, ll>> points) : pts(std::move(points)) {
        if (pts.empty()) throw invalid_argument("PointsFenwick2D: needs at least one point");
        sort(pts.begin(), pts.end());
        pts.erase(unique(pts.begin(), pts.end()), pts.end());
        vals.assign(pts.size(), T(0));
        for (auto& p : pts)
            if (xs.empty() || xs.back() != p.first) xs.push_back(p.first);
        n = (int)xs.size();
        vector<pair<ll, int>> byY(pts.size());  // (y, which x): the points in y order
        for (int i = 0, xi = -1; i < (int)pts.size(); i++) {
            if (i == 0 || pts[i].first != pts[i - 1].first) xi++;
            byY[i] = {pts[i].second, xi};
        }
        sort(byY.begin(), byY.end());
        off.assign((n + 1) + 1, 0);
        cnt.assign((n + 1), 0);
        fillLists(byY.data(), (int)byY.size(), true);  // how long each list is
        for (int p = 1; p < (n + 1); p++) off[p + 1] = off[p] + cnt[p];
        ys.assign(off[(n + 1)], 0);
        fill(cnt.begin(), cnt.end(), 0);
        fillLists(byY.data(), (int)byY.size(), false);  // the lists themselves
        sm.assign(ys.size(), 0);
        xr.assign(ys.size(), 0);
    }

    // every x-node's sorted distinct y's, back to back in ys (x-node p's start at off[p]); called twice: to count,
    // then to write
    LEETCODE_NO_SANITIZE void fillLists(const pair<ll, int>* byY, int m, bool countOnly) {
        HotVector<ll> last((n + 1), 0);  // the y most recently added to each x-node
        for (int i = 0; i < m; i++) {
            ll y = byY[i].first;
            for (int p = byY[i].second + 1; p <= n; p += p & -p) {
                if (cnt[p] && last[p] == y) continue;
                if (!countOnly) ys[off[p] + cnt[p]] = y;
                cnt[p]++, last[p] = y;
            }
        }
    }

    // where (x, y) is in the sorted points
    LEETCODE_NO_SANITIZE int indexOf(long long x, long long y, const char* name) const {
        auto it = lower_bound(pts.begin(), pts.end(), make_pair(x, y));
        if (it == pts.end() || *it != make_pair(x, y))
            throw out_of_range(string(name) + ": (x, y) is not one of the points given to the constructor");
        return (int)(it - pts.begin());
    }

    // point number i, at (x, y), becomes v
    LEETCODE_NO_SANITIZE void setPoint(int i, ll x, ll y, T v) {
        T old = vals[i];
        vals[i] = v;
        int xi = hotLowerBound(&xs[0], n, x) + 1;
        S dSum = S(v) - old;
        totalSum += dSum;
        for (int k = xi; k <= n; k += k & -k) {
            S* t = &sm[off[k]];  // (entry j of this node's tree is t[j - 1])
            for (int j = hotLowerBound(&ys[off[k]], cnt[k], y) + 1; j <= cnt[k]; j += j & -j) t[j - 1] += dSum;
        }
        T dXor = v ^ old;
        totalXor ^= dXor;
        for (int k = xi; k <= n; k += k & -k) {
            T* t = &xr[off[k]];  // (entry j of this node's tree is t[j - 1])
            for (int j = hotLowerBound(&ys[off[k]], cnt[k], y) + 1; j <= cnt[k]; j += j & -j) t[j - 1] ^= dXor;
        }
    }

    // sum of the points with x <= the given x and y <= the given y
    LEETCODE_NO_SANITIZE S prefixSum(ll x, ll y) const {
        S res = 0;
        for (int k = hotUpperBound(&xs[0], n, x); k > 0; k &= k - 1) {
            const S* t = &sm[off[k]];  // (entry j of this node's tree is t[j - 1])
            for (int j = hotUpperBound(&ys[off[k]], cnt[k], y); j > 0; j &= j - 1) res += t[j - 1];
        }
        return res;
    }

    // xor of the points with x <= the given x and y <= the given y
    LEETCODE_NO_SANITIZE T prefixXor(ll x, ll y) const {
        T res = 0;
        for (int k = hotUpperBound(&xs[0], n, x); k > 0; k &= k - 1) {
            const T* t = &xr[off[k]];  // (entry j of this node's tree is t[j - 1])
            for (int j = hotUpperBound(&ys[off[k]], cnt[k], y); j > 0; j &= j - 1) res ^= t[j - 1];
        }
        return res;
    }

    // O(log N) -- the value at (x, y); needs (x, y) to be one of the points given, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(ll x, ll y) const {
        return vals[indexOf(x, y, "pointGet")];
    }

    // O(log^2 N) -- the point (x, y) becomes v; needs (x, y) to be one of the points given, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointAssign");
        setPoint(i, x, y, v);
    }

    // O(log^2 N) -- adds v to the point (x, y); needs (x, y) to be one of the points given, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointAdd");
        setPoint(i, x, y, T(vals[i] + v));
    }

    // O(log^2 N) -- the point (x, y) becomes max(itself, v); needs (x, y) to be one of the points given, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointChmax");
        if (v > vals[i]) setPoint(i, x, y, v);
    }

    // O(log^2 N) -- the point (x, y) becomes min(itself, v); needs (x, y) to be one of the points given, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointChmin");
        if (v < vals[i]) setPoint(i, x, y, v);
    }

    // O(log^2 N) -- sum of the points with x1 <= x <= x2 and y1 <= y <= y2 (0 if no point is there); needs x1 <= x2 and
    // y1 <= y2, else throws out_of_range
    LEETCODE_NO_SANITIZE S rectSum(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectSum: needs x1 <= x2 and y1 <= y2");
        return prefixSum(x2, y2) - prefixSum(x1 - 1, y2) - prefixSum(x2, y1 - 1) + prefixSum(x1 - 1, y1 - 1);
    }

    // O(1) -- sum of every point
    LEETCODE_NO_SANITIZE S sumAll() const {
        return totalSum;
    }

    // O(log^2 N) -- xor of the points with x1 <= x <= x2 and y1 <= y <= y2 (0 if no point is there); needs x1 <= x2 and
    // y1 <= y2, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectXor(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectXor: needs x1 <= x2 and y1 <= y2");
        return prefixXor(x2, y2) ^ prefixXor(x1 - 1, y2) ^ prefixXor(x2, y1 - 1) ^ prefixXor(x1 - 1, y1 - 1);
    }

    // O(1) -- xor of every point
    LEETCODE_NO_SANITIZE T xorAll() const {
        return totalXor;
    }

    // O(log^2 N) -- sum of the points with x <= the given x and y <= the given y (0 if there are none); any integers
    LEETCODE_NO_SANITIZE S sumLteLte(ll x, ll y) const {
        return prefixSum(x, y);
    }

    // O(log^2 N) -- sum of the points with x <= the given x and y >= the given y (0 if there are none); any integers
    LEETCODE_NO_SANITIZE S sumLteGte(ll x, ll y) const {
        const ll HIGH = numeric_limits<ll>::max();
        return prefixSum(x, HIGH) - prefixSum(x, y - 1);
    }

    // O(log^2 N) -- sum of the points with x >= the given x and y <= the given y (0 if there are none); any integers
    LEETCODE_NO_SANITIZE S sumGteLte(ll x, ll y) const {
        const ll HIGH = numeric_limits<ll>::max();
        return prefixSum(HIGH, y) - prefixSum(x - 1, y);
    }

    // O(log^2 N) -- sum of the points with x >= the given x and y >= the given y (0 if there are none); any integers
    LEETCODE_NO_SANITIZE S sumGteGte(ll x, ll y) const {
        const ll HIGH = numeric_limits<ll>::max();
        return totalSum - prefixSum(x - 1, HIGH) - prefixSum(HIGH, y - 1) + prefixSum(x - 1, y - 1);
    }
};
