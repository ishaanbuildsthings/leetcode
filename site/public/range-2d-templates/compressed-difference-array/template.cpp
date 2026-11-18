// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/compressed-difference-array/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: getAll rectAdd
// @data-structure-type: difference-array
// @input: compressed
// @complexities:
//   getAll: X*Y
//   rectAdd: 1
//   build: X*Y
// @memory:
//   layout: none
//   node: diff[1*X*Y]
//   tags: none
//   other: base[1*X*Y] xs[1*X] ys[1*Y] xAt[1*X] yAt[1*Y]
//   note: X = how many distinct x's, Y = distinct y's; diff is (R + 1) by (C + 1), flat: each rectAdd writes its four corners

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

// 2D difference array: rectangle adds in O(1) each, then one O(R * C) pass (getAll) that turns them into the final
// grid. For when every update comes before any read: there are no queries in between (a Fenwick tree does rectAdd
// with pointGet in between at O(log R * log C) each). An add of v on rows r1..r2, columns c1..c2 marks +v at (r1, c1)
// and (r2 + 1, c2 + 1), and -v at (r1, c2 + 1) and (r2 + 1, c1); the 2D prefix sum of the marks is what every cell
// gained. Rows and columns are 0-based and rectangles are inclusive.
// T is any number type (int, long long, ...).
template <typename T>
struct DifferenceArray2D {
    int R, C, W;
    HotVector<vector<T>> base;
    HotVector<T> diff;

    // O(R*C) -- grid: R rows of C numbers each (the starting values); needs R >= 1 and C >= 1, else throws
    // invalid_argument
    explicit DifferenceArray2D(const vector<vector<T>>& grid)
        : R((int)grid.size()), C(grid.empty() ? 0 : (int)grid[0].size()), W(C + 1), base(grid) {
        if (R < 1 || C < 1) throw invalid_argument("DifferenceArray2D: needs R >= 1 and C >= 1");
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("DifferenceArray2D: every row needs the same C values");
        diff.assign((size_t)(R + 1) * W, 0);
    }

    // O(1) -- adds v to every cell of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE void rectAdd(int r1, int c1, int r2, int c2, T v) {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectAdd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        diff[r1 * W + c1] += v;
        diff[r1 * W + c2 + 1] -= v;
        diff[(r2 + 1) * W + c1] -= v;
        diff[(r2 + 1) * W + c2 + 1] += v;
    }

    // O(R*C) -- the whole grid as it stands (R rows of C values); more rectAdd calls can follow
    vector<vector<T>> getAll() const {
        vector<vector<T>> out(R, vector<T>(C));
        vector<T> above(C, 0);
        for (int r = 0; r < R; r++) {
            T run = 0;
            for (int c = 0; c < C; c++) {
                run += diff[r * W + c];
                above[c] += run;
                out[r][c] = above[c] + base[r][c];
            }
        }
        return out;
    }
};

// Coordinate compression in front of DifferenceArray2D: coordinates can be any integers (huge, negative, ...). You
// list every x and every y a point operation (pointGet, pointAdd, ...) will use; rectangles and corners can be any
// integers. Each listed x becomes a row and each listed y a column of a small grid, and the template above does the
// work on it. X = how many distinct x's, Y = distinct y's: memory and costs are the template's for an X by Y grid. A
// cell is a listed x with a listed y, and it is one point, not a block: a rectangle covers just the cells inside it
// (the gaps between listed coordinates don't exist), so a sum adds those cells' values, it is not an area. Cells you
// never set count as 0, a listed x with a listed y you never use together included.
template <typename T>
struct Compressed2D {
    using ll = long long;
    HotVector<ll> xs, ys;  // the listed coordinates, sorted, each once
    DifferenceArray2D<T> ds;

    // n coordinates 0..n-1: pass upTo(n) for an axis you don't want compressed
    LEETCODE_NO_SANITIZE static vector<ll> upTo(ll n) {
        vector<ll> v(n);
        iota(v.begin(), v.end(), 0LL);
        return v;
    }

    // O(X log X + Y log Y + the template's build) -- xs: every x a point operation will use (any order, repeats are
    // fine), or upTo(n) to leave x as 0..n-1; ys: the same for y. Every cell starts at 0. Needs at least one x and one
    // y, else throws invalid_argument
    Compressed2D(vector<ll> xs_, vector<ll> ys_)
        : xs(sorted(std::move(xs_))), ys(sorted(std::move(ys_))), ds(make(xs, ys)) {}

    LEETCODE_NO_SANITIZE static vector<ll> sorted(vector<ll> v) {
        sort(v.begin(), v.end());
        v.erase(unique(v.begin(), v.end()), v.end());
        return v;
    }

    LEETCODE_NO_SANITIZE static DifferenceArray2D<T> make(const vector<ll>& xs, const vector<ll>& ys) {
        if (xs.empty() || ys.empty()) throw invalid_argument("Compressed2D: needs at least one x and one y");
        int X = (int)xs.size(), Y = (int)ys.size();
        return DifferenceArray2D<T>(vector<vector<T>>(X, vector<T>(Y, T(0))));
    }

    // the row / column of a listed x
    LEETCODE_NO_SANITIZE int xAt(ll x, const char* name) const {
        int lo = 0, hi = (int)xs.size();
        while (lo < hi) {
            int mid = (lo + hi) >> 1;
            if (xs[mid] < x) lo = mid + 1;
            else hi = mid;
        }
        if (lo == (int)xs.size() || xs[lo] != x)
            throw out_of_range(string(name) + ": x is not one of the xs given to the constructor");
        return lo;
    }

    // the row / column of a listed y
    LEETCODE_NO_SANITIZE int yAt(ll y, const char* name) const {
        int lo = 0, hi = (int)ys.size();
        while (lo < hi) {
            int mid = (lo + hi) >> 1;
            if (ys[mid] < y) lo = mid + 1;
            else hi = mid;
        }
        if (lo == (int)ys.size() || ys[lo] != y)
            throw out_of_range(string(name) + ": y is not one of the ys given to the constructor");
        return lo;
    }

    // the rows and columns a rectangle covers, {r1, c1, r2, c2}; r1 = -1 when no listed x or no listed y is inside
    LEETCODE_NO_SANITIZE array<int, 4> rect(ll x1, ll y1, ll x2, ll y2, const char* name) const {
        if (x1 > x2 || y1 > y2) throw out_of_range(string(name) + ": needs x1 <= x2 and y1 <= y2");
        int r1 = int(lower_bound(xs.begin(), xs.end(), x1) - xs.begin());
        int r2 = int(upper_bound(xs.begin(), xs.end(), x2) - xs.begin()) - 1;
        int c1 = int(lower_bound(ys.begin(), ys.end(), y1) - ys.begin());
        int c2 = int(upper_bound(ys.begin(), ys.end(), y2) - ys.begin()) - 1;
        if (r1 > r2 || c1 > c2) return {-1, -1, -1, -1};
        return {r1, c1, r2, c2};
    }

    // O(X * Y) -- the whole grid, X rows of Y values: row i is the i-th smallest x, column j the j-th smallest y
    auto getAll() {
        return ds.getAll();
    }

    // O(1) -- adds v to every cell with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1 <= y2,
    // else throws out_of_range; no cell inside: nothing happens
    LEETCODE_NO_SANITIZE void rectAdd(ll x1, ll y1, ll x2, ll y2, T v) {
        auto [r1, c1, r2, c2] = rect(x1, y1, x2, y2, "rectAdd");
        if (r1 >= 0) ds.rectAdd(r1, c1, r2, c2, v);
    }
};
