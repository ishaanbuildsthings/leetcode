// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-bit-corner-min-ltegte-gtelte/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: minAll minGteLte minLteGte pointChmin
// @data-structure-type: BIT
// @input: points
// @empty-cells: yes
// @complexities:
//   minAll: 1
//   minGteLte: log^2(N)
//   minLteGte: log^2(N)
//   pointChmin: log^2(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: tree[2*N*log(N)]
//   tags: none
//   other: ys[2*N*log(N)] xs[2*N] off[2*N] cnt[2*N] pts[2*N]
//   note: one Fenwick-of-Fenwicks per corner direction asked for (a >= direction is the same structure on negated coordinates)

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

// min / max that still inline with sanitizers skipped (std::min and std::max do not)
template <typename A>
LEETCODE_NO_SANITIZE_INLINE A hotMin(A a, A b) { return b < a ? b : a; }
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

// Corner min over points known up front, with Fenwick trees: pointChmin at a point and the min over a corner of the
// plane (every point with x <= or >= a given x, and y <= or >= a given y) in O(log^2 N), with N log N memory per
// direction whatever the coordinates are (any integers, negative is fine). The constructor takes every (x, y) that
// will ever be updated. This works because values only move one way: a point can only go down, so a tree entry never
// has to forget a value; for a point that can move both ways, or for rectangles that aren't corners, use the segment
// tree version. Every point starts empty and queries only see points that have been set. A min over no set point is
// NO_MIN.
// T is any integer type (int, long long, ...). Coordinates are long long.
template <typename T>
struct PointsCornerMinFenwick2D {
    using ll = long long;
    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set point gives

    // min over the points with x <= a given x and y <= a given y, values only going down
    struct Prefix {
        int n = 0;
        HotVector<ll> xs, ys;
        HotVector<int> off, cnt;
        HotVector<T> tree;

        void build(vector<pair<ll, ll>> pts) {
            sort(pts.begin(), pts.end());
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
            tree.assign(ys.size(), NO_MIN);
        }

        // every x-node's sorted distinct y's, back to back in ys (x-node p's start at off[p]); called twice: to
        // count, then to write
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

        LEETCODE_NO_SANITIZE void improve(ll x, ll y, T v) {
            for (int k = hotLowerBound(&xs[0], n, x) + 1; k <= n; k += k & -k) {
                T* t = &tree[off[k]];  // (entry j of this node's tree is t[j - 1])
                for (int j = hotLowerBound(&ys[off[k]], cnt[k], y) + 1; j <= cnt[k]; j += j & -j)
                    t[j - 1] = hotMin(t[j - 1], v);
            }
        }

        LEETCODE_NO_SANITIZE T best(ll x, ll y) const {
            T res = NO_MIN;
            for (int k = hotUpperBound(&xs[0], n, x); k > 0; k &= k - 1) {
                const T* t = &tree[off[k]];  // (entry j of this node's tree is t[j - 1])
                for (int j = hotUpperBound(&ys[off[k]], cnt[k], y); j > 0; j &= j - 1) res = hotMin(res, t[j - 1]);
            }
            return res;
        }
    };

    HotVector<pair<ll, ll>> pts;
    T top = NO_MIN;
    Prefix tLteGte, tGteLte;

    // O(N log N) -- points: every (x, y) that will ever be updated (negative is fine, repeats are fine); needs at least
    // one, else throws invalid_argument
    explicit PointsCornerMinFenwick2D(vector<pair<ll, ll>> points) : pts(std::move(points)) {
        if (pts.empty()) throw invalid_argument("PointsCornerMinFenwick2D: needs at least one point");
        sort(pts.begin(), pts.end());
        pts.erase(unique(pts.begin(), pts.end()), pts.end());
        {
            auto flipped = pts;
            for (auto& p : flipped) p = {p.first, -p.second};
            tLteGte.build(std::move(flipped));
        }
        {
            auto flipped = pts;
            for (auto& p : flipped) p = {-p.first, p.second};
            tGteLte.build(std::move(flipped));
        }
    }

    // O(log^2 N) -- the point (x, y) becomes min(itself, v); an empty point becomes v; needs (x, y) to be one of the
    // points given, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(ll x, ll y, T v) {
        if (!binary_search(pts.begin(), pts.end(), make_pair(x, y)))
            throw out_of_range("pointChmin: (x, y) is not one of the points given to the constructor");
        top = hotMin(top, v);
        tLteGte.improve(x, -y, v);
        tGteLte.improve(-x, y, v);
    }

    // O(log^2 N) -- min of the set points with x <= the given x and y >= the given y (NO_MIN if there are none); any
    // integers
    LEETCODE_NO_SANITIZE T minLteGte(ll x, ll y) const {
        return tLteGte.best(x, -y);
    }

    // O(log^2 N) -- min of the set points with x >= the given x and y <= the given y (NO_MIN if there are none); any
    // integers
    LEETCODE_NO_SANITIZE T minGteLte(ll x, ll y) const {
        return tGteLte.best(-x, y);
    }

    // O(1) -- min of every set point (NO_MIN if there are none)
    LEETCODE_NO_SANITIZE T minAll() const {
        return top;
    }
};
