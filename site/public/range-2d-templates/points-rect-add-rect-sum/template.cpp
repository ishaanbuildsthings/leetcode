// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-rect-add-rect-sum/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointAdd pointGet rectAdd rectSum sumAll sumGteGte sumGteLte sumLteGte sumLteLte
// @data-structure-type: BIT
// @input: points
// @model: area
// @complexities:
//   pointAdd: log^2(N)
//   pointGet: log^2(N)
//   rectAdd: log^2(N)
//   rectSum: log^2(N)
//   sumAll: 1
//   sumGteGte: log^2(N)
//   sumGteLte: log^2(N)
//   sumLteGte: log^2(N)
//   sumLteLte: log^2(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: s0[4*N*log(N)] sx[4*N*log(N)] sy[4*N*log(N)] sxy[4*N*log(N)]
//   tags: none
//   other: ys[4*N*log(N)] xs[4*N] off[4*N] cnt[4*N] rects[4*N]
//   note: N = how many rectangles; each makes four corner marks, and every mark's y is listed in each of the O(log N) Fenwick x-nodes covering it

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


// Rectangle add and rectangle sum where the update rectangles are listed up front, any integers (negative is fine):
// O(log^2 N) per operation with N log N memory, N = how many rectangles. A rect add is four point marks at its
// corners (+v, -v, -v, +v), and the sum of the cells with x <= X and y <= Y comes from four sums over the marks below
// and left of (X, Y): of d, d * x, d * y and d * x * y. Those are point updates at known places, so a Fenwick tree
// over the marks' x's whose every node is a Fenwick tree over just its own y's keeps them. The constructor takes
// every rectangle a rectAdd will use (a pointAdd is the rectangle (x, y, x, y)); queries take any integers, never
// listed. Every cell starts at 0, and sums are true area sums: a rect add of v on a 3 by 4 rectangle adds 12 * v.
// T is any integer type (int, long long, ...); the four sums are kept in __int128, so coordinates up to about 10^9 and
// values up to about 10^9 are fine, as long as every answer fits in T. Coordinates are long long.
template <typename T>
struct PointsRectAddRectSum2D {
    using ll = long long;
    using L = __int128;
    HotVector<array<ll, 4>> rects;  // the rectangles given, sorted, each once
    // the marks' distinct x's; per Fenwick x-node, the distinct y's it covers (off / cnt locate them)
    HotVector<ll> xs, ys;
    HotVector<int> off, cnt;
    HotVector<array<L, 4>> s;  // the sums of d, d * x, d * y, d * x * y, Fenwick-style per x-node
    ll maxX, maxY;  // (past the last mark, a prefix sum stops changing)
    L total = 0;

    // O(N log N) -- rects: every {x1, y1, x2, y2} a rectAdd will use, x1 <= x2 and y1 <= y2 (a pointAdd at (x, y) needs
    // {x, y, x, y}); repeats are fine; queries are never listed. Needs at least one, else throws invalid_argument
    explicit PointsRectAddRectSum2D(vector<array<ll, 4>> rs) : rects(std::move(rs)) {
        if (rects.empty()) throw invalid_argument("PointsRectAddRectSum2D: needs at least one rectangle");
        sort(rects.begin(), rects.end());
        rects.erase(unique(rects.begin(), rects.end()), rects.end());
        vector<pair<ll, ll>> marks;  // (y, x), to visit them by y
        for (auto& r : rects) {
            if (r[0] > r[2] || r[1] > r[3])
                throw invalid_argument("PointsRectAddRectSum2D: needs x1 <= x2 and y1 <= y2");
            marks.push_back({r[1], r[0]}), marks.push_back({r[1], r[2] + 1});
            marks.push_back({r[3] + 1, r[0]}), marks.push_back({r[3] + 1, r[2] + 1});
        }
        sort(marks.begin(), marks.end());
        marks.erase(unique(marks.begin(), marks.end()), marks.end());
        for (auto& m : marks) xs.push_back(m.second);
        sort(xs.begin(), xs.end());
        xs.erase(unique(xs.begin(), xs.end()), xs.end());
        maxX = xs.back(), maxY = marks.back().first;
        int n = (int)xs.size();
        vector<vector<ll>> lists(n + 1);
        for (auto& [y, x] : marks)
            for (int i = int(lower_bound(xs.begin(), xs.end(), x) - xs.begin()) + 1; i <= n; i += i & -i)
                if (lists[i].empty() || lists[i].back() != y) lists[i].push_back(y);
        off.assign(n + 1, 0), cnt.assign(n + 1, 0);
        for (int i = 1; i <= n; i++) {
            off[i] = (int)ys.size(), cnt[i] = (int)lists[i].size();
            ys.insert(ys.end(), lists[i].begin(), lists[i].end());
        }
        s.assign(ys.size(), array<L, 4>{0, 0, 0, 0});
    }

    LEETCODE_NO_SANITIZE void mark(ll x, ll y, L d) {
        L dx = d * x, dy = d * y, dxy = dx * y;
        int n = (int)xs.size();
        for (int i = int(lower_bound(xs.begin(), xs.end(), x) - xs.begin()) + 1; i <= n; i += i & -i) {
            const ll* base = ys.data() + off[i];
            int c = cnt[i];
            array<L, 4>* t = s.data() + off[i] - 1;
            for (int k = int(lower_bound(base, base + c, y) - base) + 1; k <= c; k += k & -k)
                t[k][0] += d, t[k][1] += dx, t[k][2] += dy, t[k][3] += dxy;
        }
    }

    // the sum of the cells with x <= X and y <= Y (any integers)
    LEETCODE_NO_SANITIZE L prefix(ll X, ll Y) const {
        if (X > maxX) X = maxX;
        if (Y > maxY) Y = maxY;
        L a = 0, b = 0, c = 0, e = 0;
        for (int i = int(upper_bound(xs.begin(), xs.end(), X) - xs.begin()); i > 0; i &= i - 1) {
            const ll* base = ys.data() + off[i];
            const array<L, 4>* t = s.data() + off[i] - 1;
            for (int k = int(upper_bound(base, base + cnt[i], Y) - base); k > 0; k &= k - 1)
                a += t[k][0], b += t[k][1], c += t[k][2], e += t[k][3];
        }
        return (L)(X + 1) * (Y + 1) * a - (L)(Y + 1) * b - (L)(X + 1) * c + e;
    }

    LEETCODE_NO_SANITIZE void add(ll x1, ll y1, ll x2, ll y2, T v, const char* name) {
        if (!binary_search(rects.begin(), rects.end(), array<ll, 4>{x1, y1, x2, y2}))
            throw out_of_range(string(name) + ": the rectangle is not one of the rectangles given to the constructor");
        total += (L)v * (x2 - x1 + 1) * (y2 - y1 + 1);
        mark(x1, y1, v), mark(x2 + 1, y1, -(L)v), mark(x1, y2 + 1, -(L)v), mark(x2 + 1, y2 + 1, v);
    }

    LEETCODE_NO_SANITIZE L sumOf(ll x1, ll y1, ll x2, ll y2) const {
        return prefix(x2, y2) - prefix(x1 - 1, y2) - prefix(x2, y1 - 1) + prefix(x1 - 1, y1 - 1);
    }

    // O(log^2 N) -- adds v to every cell with x1 <= x <= x2 and y1 <= y <= y2; needs {x1, y1, x2, y2} to be one of the
    // rectangles given, else throws out_of_range
    LEETCODE_NO_SANITIZE void rectAdd(ll x1, ll y1, ll x2, ll y2, T v) { add(x1, y1, x2, y2, v, "rectAdd"); }

    // O(log^2 N) -- adds v to the cell (x, y); needs {x, y, x, y} to be one of the rectangles given, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(ll x, ll y, T v) { add(x, y, x, y, v, "pointAdd"); }

    // O(log^2 N) -- the value at (x, y); any integers
    LEETCODE_NO_SANITIZE T pointGet(ll x, ll y) const { return (T)sumOf(x, y, x, y); }

    // O(log^2 N) -- sum of the cells with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1 <= y2,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE T rectSum(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectSum: needs x1 <= x2 and y1 <= y2");
        return (T)sumOf(x1, y1, x2, y2);
    }

    // O(1) -- sum of every cell
    LEETCODE_NO_SANITIZE T sumAll() const { return (T)total; }

    // O(log^2 N) -- sum of the cells with x <= the given x and y <= the given y; any integers
    LEETCODE_NO_SANITIZE T sumLteLte(ll x, ll y) const {
        return (T)(prefix(x, y));
    }

    // O(log^2 N) -- sum of the cells with x <= the given x and y >= the given y; any integers
    LEETCODE_NO_SANITIZE T sumLteGte(ll x, ll y) const {
        return (T)(prefix(x, maxY) - prefix(x, y - 1));
    }

    // O(log^2 N) -- sum of the cells with x >= the given x and y <= the given y; any integers
    LEETCODE_NO_SANITIZE T sumGteLte(ll x, ll y) const {
        return (T)(prefix(maxX, y) - prefix(x - 1, y));
    }

    // O(log^2 N) -- sum of the cells with x >= the given x and y >= the given y; any integers
    LEETCODE_NO_SANITIZE T sumGteGte(ll x, ll y) const {
        return (T)(total - prefix(x - 1, maxY) - prefix(maxX, y - 1) + prefix(x - 1, y - 1));
    }
};
