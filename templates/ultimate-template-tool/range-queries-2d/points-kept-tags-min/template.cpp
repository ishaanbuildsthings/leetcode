// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-kept-tags-min/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointChmin pointGet rectChmin
// @data-structure-type: seg-tree-kept-tags
// @input: points
// @empty-cells: yes
// @complexities:
//   pointChmin: log(N)
//   pointGet: log^2(N)
//   rectChmin: log^2(N)
//   build: N*log(N)
// @memory:
//   layout: 2n-iterative
//   node: none
//   tags: tag[2*N*log(N)]
//   other: ys[1*N*log(N)] xs[1*N] off[2*N] cnt[2*N] given[2*N]
//   note: every point's y is listed in each of the O(log N) x-nodes above it; an x-node's y-tree is twice its list

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


// Rectangle chmin with point reads over points known up front (any integers, negative is fine): O(log^2 N) per
// rectChmax, O(log^2 N) per pointGet, N log N memory. A tree over the distinct x's, where every x-node keeps a tree
// over the y's of its own points. rectChmin(x1, y1, x2, y2, v) leaves v as a tag on the O(log N) x-nodes that make up
// x1..x2, and in each of them on the O(log N) y-nodes that make up y1..y2; pointGet(x, y) takes the min of the tags on
// the way from (x, y) up. Tags are never pushed down, which works because chmin never has to be undone. The points
// given are the ones you will read or chmin one at a time; a rectangle's corners can be anything. A point no update has
// reached reads NO_MIN.
// T is any integer type (int, long long, ...). Coordinates are long long.
template <typename T>
struct PointsRectChmin2D {
    using ll = long long;
    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a point no update has reached reads
    int X;
    HotVector<pair<ll, ll>> given;  // sorted, each once
    HotVector<ll> xs, ys;  // ys: every x-node's y's, one x-node after another
    HotVector<int> off, cnt;  // x-node i's y's are ys[off[i] .. off[i] + cnt[i] - 1]
    HotVector<T> tag;  // x-node i's y-tree: tag[2 * off[i] + k], its leaves at k = cnt[i] + (the y's place in its list)

    // O(N log N) -- points: every (x, y) you will call pointGet or pointChmin on (negative is fine, repeats are
    // fine); needs at least one, else throws invalid_argument
    explicit PointsRectChmin2D(vector<pair<ll, ll>> points) : given(std::move(points)) {
        if (given.empty()) throw invalid_argument("PointsRectChmin2D: needs at least one point");
        sort(given.begin(), given.end());
        given.erase(unique(given.begin(), given.end()), given.end());
        for (auto& p : given)
            if (xs.empty() || xs.back() != p.first) xs.push_back(p.first);
        X = (int)xs.size();
        vector<vector<ll>> lists(2 * X);
        // (given is sorted by x, then y: each leaf's list comes sorted)
        for (size_t i = 0, j = 0; i < given.size(); i++) {
            while (xs[j] != given[i].first) j++;
            lists[X + j].push_back(given[i].second);
        }
        for (int i = X - 1; i >= 1; i--) {  // an x-node's y's: its two halves' y's, merged, each y once
            auto& out = lists[i];
            auto &a = lists[2 * i], &b = lists[2 * i + 1];
            merge(a.begin(), a.end(), b.begin(), b.end(), back_inserter(out));
            out.erase(unique(out.begin(), out.end()), out.end());
        }
        off.assign(2 * X, 0), cnt.assign(2 * X, 0);
        for (int i = 1; i < 2 * X; i++) {
            off[i] = (int)ys.size(), cnt[i] = (int)lists[i].size();
            ys.insert(ys.end(), lists[i].begin(), lists[i].end());
        }
        tag.assign(2 * ys.size(), NO_MIN);
    }

    // where (x, y) is among the given points (its x's place in xs), or -1
    LEETCODE_NO_SANITIZE int find(ll x, ll y) const {
        auto it = lower_bound(given.begin(), given.end(), make_pair(x, y));
        if (it == given.end() || *it != make_pair(x, y)) return -1;
        return hotLowerBound(&xs[0], X, x);
    }

    // x-node i: the y's in y1..y2 become min(themselves, v)
    LEETCODE_NO_SANITIZE void cols(int i, ll y1, ll y2, T v) {
        const ll* first = &ys[off[i]];
        int m = cnt[i], base = 2 * off[i];
        int a = hotLowerBound(first, m, y1) + m, b = hotUpperBound(first, m, y2) + m;
        T* t = &tag[base];
        for (; a < b; a >>= 1, b >>= 1) {
            if (a & 1) {
                if (v < t[a]) t[a] = v;
                a++;
            }
            if (b & 1) {
                b--;
                if (v < t[b]) t[b] = v;
            }
        }
    }

    // O(log^2 N) -- every given point with x1 <= x <= x2 and y1 <= y <= y2 becomes min(itself, v) (one never
    // reached becomes v); any integers; needs x1 <= x2 and y1 <= y2, else throws out_of_range
    LEETCODE_NO_SANITIZE void rectChmin(ll x1, ll y1, ll x2, ll y2, T v) {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectChmin: needs x1 <= x2 and y1 <= y2");
        int l = hotLowerBound(&xs[0], X, x1) + X, r = hotUpperBound(&xs[0], X, x2) + X;
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) cols(l++, y1, y2, v);
            if (r & 1) cols(--r, y1, y2, v);
        }
    }

    // O(log N) -- the point (x, y) becomes min(itself, v) (one never reached becomes v); needs (x, y) to be one of
    // the points given, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(ll x, ll y, T v) {
        int j = find(x, y);
        if (j < 0) throw out_of_range("pointChmin: (x, y) is not one of the points given to the constructor");
        int i = j + X, m = cnt[i];
        T& t = tag[2 * off[i] + hotLowerBound(&ys[off[i]], m, y) + m];
        if (v < t) t = v;
    }

    // O(log^2 N) -- the value at (x, y), NO_MIN if no update has reached it; needs (x, y) to be one of the points
    // given, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(ll x, ll y) {
        int j = find(x, y);
        if (j < 0) throw out_of_range("pointGet: (x, y) is not one of the points given to the constructor");
        T res = NO_MIN;
        for (int i = j + X; i; i >>= 1) {
            int m = cnt[i];
            const T* t = &tag[2 * off[i]];
            for (int k = hotLowerBound(&ys[off[i]], m, y) + m; k; k >>= 1)
                if (t[k] < res) res = t[k];
        }
        return res;
    }
};
