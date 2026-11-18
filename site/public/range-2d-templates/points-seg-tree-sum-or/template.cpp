// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-seg-tree-sum-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: orAll pointAdd pointAssign pointChmax pointChmin pointGet rectOr rectSum sumAll sumGteGte sumGteLte sumLteGte sumLteLte
// @data-structure-type: seg-tree
// @input: points
// @complexities:
//   orAll: 1
//   pointAdd: log^2(N)
//   pointAssign: log^2(N)
//   pointChmax: log^2(N)
//   pointChmin: log^2(N)
//   pointGet: log(N)
//   rectOr: log^2(N)
//   rectSum: log^2(N)
//   sumAll: 1
//   sumGteGte: log^2(N)
//   sumGteLte: log^2(N)
//   sumLteGte: log^2(N)
//   sumLteLte: log^2(N)
//   build: N*log(N)
// @memory:
//   layout: 2n-iterative
//   node: sm[2*N*log(N)] orr[2*N*log(N)]
//   tags: none
//   other: ys[1*N*log(N)] pts[2*N] vals[1*N] xs[1*N] off[2*N] cnt[2*N]
//   note: every point's y is listed in each of the O(log N) x-nodes above it; an x-node's column tree is twice its list

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

// 2D segment tree over a fixed list of points (sum, OR): point updates and any-rectangle queries in O(log^2 N), with
// N log N memory whatever the coordinates are (any integers, negative is fine). The constructor takes every (x, y)
// your point operations will use; rectangles and corners take any integers, never listed. A bottom-up tree over the
// distinct x's; every node of it keeps the sorted y's of the points under it and a bottom-up tree over just those.
// Rectangles are inclusive, x1..x2 by y1..y2, and their corners can be any integers, given or not. Every point given
// starts at 0.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T). Coordinates are long
// long.
template <typename T>
struct PointsSegTree2D {
    using ll = long long;
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr ll LOW = numeric_limits<ll>::min(), HIGH = numeric_limits<ll>::max();  // no bound on a coordinate
    int n;
    HotVector<pair<ll, ll>> pts;
    HotVector<T> vals;
    HotVector<ll> xs, ys;
    HotVector<int> off, cnt;
    HotVector<S> sm;  // x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])
    HotVector<T> orr;  // x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])

    // O(N log N) -- points: every (x, y) a point operation (pointGet, pointAdd, ...) will use (negative is fine,
    // repeats are fine); not rectangle or corner coordinates, those can be anything. Needs at least one, else throws
    // invalid_argument
    explicit PointsSegTree2D(vector<pair<ll, ll>> points) : pts(std::move(points)) {
        if (pts.empty()) throw invalid_argument("PointsSegTree2D: needs at least one point");
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
        off.assign(2 * n + 1, 0);
        cnt.assign(2 * n, 0);
        fillLists(byY.data(), (int)byY.size(), true);  // how long each list is
        for (int p = 1; p < 2 * n; p++) off[p + 1] = off[p] + cnt[p];
        ys.assign(off[2 * n], 0);
        fill(cnt.begin(), cnt.end(), 0);
        fillLists(byY.data(), (int)byY.size(), false);  // the lists themselves
        sm.assign(2 * ys.size(), S(0));
        orr.assign(2 * ys.size(), T(0));
    }

    // every x-node's sorted distinct y's, back to back in ys (x-node p's start at off[p]); called twice: to count, then
    // to write
    LEETCODE_NO_SANITIZE void fillLists(const pair<ll, int>* byY, int m, bool countOnly) {
        HotVector<ll> last(2 * n, 0);  // the y most recently added to each x-node
        for (int i = 0; i < m; i++) {
            ll y = byY[i].first;
            for (int p = byY[i].second + n; p >= 1; p >>= 1) {
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

    // point (x, y) = v, then every node above it
    LEETCODE_NO_SANITIZE void setPoint(ll x, ll y, T v) {
        int p = hotLowerBound(&xs[0], n, x) + n;
        S vSum = v;  // this aggregate over the points with this y under x-node p
        T vOr = v;  // this aggregate over the points with this y under x-node p
        while (true) {
            const ll* first = &ys[off[p]];
            int base = 2 * off[p], k = hotLowerBound(first, cnt[p], y) + cnt[p];
            sm[base + k] = vSum;
            orr[base + k] = vOr;
            for (k >>= 1; k >= 1; k >>= 1) {
                sm[base + k] = sm[base + 2 * k] + sm[base + 2 * k + 1];
                orr[base + k] = orr[base + 2 * k] | orr[base + 2 * k + 1];
            }
            if (p == 1) break;
            int s = p ^ 1;  // the other half of the parent: does it have this y too?
            first = &ys[off[s]];
            int j = hotLowerBound(first, cnt[s], y);
            if (j < cnt[s] && first[j] == y) {
                j += 2 * off[s] + cnt[s];
                vSum += sm[j];
                vOr |= orr[j];
            }
            p >>= 1;
        }
    }

    // O(log N) -- the value at (x, y); needs (x, y) to be one of the points given, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(ll x, ll y) const {
        int i = indexOf(x, y, "pointGet");
        return vals[i];
    }

    // O(log^2 N) -- the point (x, y) becomes v (it may go down as well as up); needs (x, y) to be one of the points
    // given, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointAssign");
        vals[i] = v;
        setPoint(x, y, v);
    }

    // O(log^2 N) -- adds v to the point (x, y); needs (x, y) to be one of the points given, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointAdd");
        vals[i] = T(vals[i] + v);
        setPoint(x, y, vals[i]);
    }

    // O(log^2 N) -- the point (x, y) becomes max(itself, v); needs (x, y) to be one of the points given, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointChmax");
        if (!(v > vals[i])) return;
        vals[i] = v;
        setPoint(x, y, v);
    }

    // O(log^2 N) -- the point (x, y) becomes min(itself, v); needs (x, y) to be one of the points given, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointChmin");
        if (!(v < vals[i])) return;
        vals[i] = v;
        setPoint(x, y, v);
    }

    LEETCODE_NO_SANITIZE S sumOf(ll x1, ll y1, ll x2, ll y2) const {
        S res = S(0);
        int l = hotLowerBound(&xs[0], n, x1) + n, r = hotUpperBound(&xs[0], n, x2) + n;
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) {
                const ll* first = &ys[off[l]];
                int base = 2 * off[l], c = cnt[l];
                int lo = hotLowerBound(first, c, y1) + c, hi = hotUpperBound(first, c, y2) + c;
                for (; lo < hi; lo >>= 1, hi >>= 1) {
                    if (lo & 1) res += sm[base + lo++];
                    if (hi & 1) res += sm[base + --hi];
                }
                l++;
            }
            if (r & 1) {
                --r;
                const ll* first = &ys[off[r]];
                int base = 2 * off[r], c = cnt[r];
                int lo = hotLowerBound(first, c, y1) + c, hi = hotUpperBound(first, c, y2) + c;
                for (; lo < hi; lo >>= 1, hi >>= 1) {
                    if (lo & 1) res += sm[base + lo++];
                    if (hi & 1) res += sm[base + --hi];
                }
            }
        }
        return res;
    }

    // O(log^2 N) -- sum of the points with x1 <= x <= x2 and y1 <= y <= y2 (0 if no point is there); needs x1 <= x2 and
    // y1 <= y2, else throws out_of_range
    LEETCODE_NO_SANITIZE S rectSum(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectSum: needs x1 <= x2 and y1 <= y2");
        return sumOf(x1, y1, x2, y2);
    }

    // O(1) -- sum of every point
    LEETCODE_NO_SANITIZE S sumAll() const {
        return sm[2 * off[1] + 1];
    }

    // O(log^2 N) -- sum of the set points with x <= the given x and y <= the given y; any integers
    LEETCODE_NO_SANITIZE S sumLteLte(ll x, ll y) const {
        return sumOf(LOW, LOW, x, y);
    }

    // O(log^2 N) -- sum of the set points with x <= the given x and y >= the given y; any integers
    LEETCODE_NO_SANITIZE S sumLteGte(ll x, ll y) const {
        return sumOf(LOW, y, x, HIGH);
    }

    // O(log^2 N) -- sum of the set points with x >= the given x and y <= the given y; any integers
    LEETCODE_NO_SANITIZE S sumGteLte(ll x, ll y) const {
        return sumOf(x, LOW, HIGH, y);
    }

    // O(log^2 N) -- sum of the set points with x >= the given x and y >= the given y; any integers
    LEETCODE_NO_SANITIZE S sumGteGte(ll x, ll y) const {
        return sumOf(x, y, HIGH, HIGH);
    }

    LEETCODE_NO_SANITIZE T orOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = T(0);
        int l = hotLowerBound(&xs[0], n, x1) + n, r = hotUpperBound(&xs[0], n, x2) + n;
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) {
                const ll* first = &ys[off[l]];
                int base = 2 * off[l], c = cnt[l];
                int lo = hotLowerBound(first, c, y1) + c, hi = hotUpperBound(first, c, y2) + c;
                for (; lo < hi; lo >>= 1, hi >>= 1) {
                    if (lo & 1) res |= orr[base + lo++];
                    if (hi & 1) res |= orr[base + --hi];
                }
                l++;
            }
            if (r & 1) {
                --r;
                const ll* first = &ys[off[r]];
                int base = 2 * off[r], c = cnt[r];
                int lo = hotLowerBound(first, c, y1) + c, hi = hotUpperBound(first, c, y2) + c;
                for (; lo < hi; lo >>= 1, hi >>= 1) {
                    if (lo & 1) res |= orr[base + lo++];
                    if (hi & 1) res |= orr[base + --hi];
                }
            }
        }
        return res;
    }

    // O(log^2 N) -- OR of the points with x1 <= x <= x2 and y1 <= y <= y2 (0 if no point is there); needs x1 <= x2 and
    // y1 <= y2, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectOr(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectOr: needs x1 <= x2 and y1 <= y2");
        return orOf(x1, y1, x2, y2);
    }

    // O(1) -- OR of every point
    LEETCODE_NO_SANITIZE T orAll() const {
        return orr[2 * off[1] + 1];
    }
};
