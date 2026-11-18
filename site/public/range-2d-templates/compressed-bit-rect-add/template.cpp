// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/compressed-bit-rect-add/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rectAdd
// @data-structure-type: BIT
// @input: compressed
// @complexities:
//   pointAdd: log(X)*log(Y)
//   pointAssign: log(X)*log(Y)
//   pointChmax: log(X)*log(Y)
//   pointChmin: log(X)*log(Y)
//   pointGet: log(X)*log(Y)
//   rectAdd: log(X)*log(Y)
//   build: X*Y
// @memory:
//   layout: none
//   node: bit[1*X*Y]
//   tags: none
//   other: xs[1*X] ys[1*Y] xAt[1*X] yAt[1*Y]
//   note: X = how many distinct x's, Y = distinct y's; one Fenwick tree over the marks a rectangle add leaves at its four corners; each is (R + 1) by (C + 1), flat

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

// Rectangle add and point read on an R x C grid with one 2D Fenwick tree, O(log R * log C) each. An add of v on rows
// r1..r2, columns c1..c2 leaves four marks, +v at (r1, c1) and (r2 + 1, c2 + 1), -v at (r1, c2 + 1) and (r2 + 1, c1);
// a cell's value is the sum of the marks above-left of it, a prefix query. When every add comes before any read, the
// difference array does this in O(1) per add. Rows and columns are 0-based and rectangles are inclusive. The (R, C)
// constructor starts with every cell 0.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T).
template <typename T>
struct RectAddFenwick2D {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int R, C, W;
    HotVector<S> bit;

    // O(R*C) -- R rows by C columns, every cell 0; needs R >= 1 and C >= 1, else throws invalid_argument
    RectAddFenwick2D(int rows, int cols) : R(rows), C(cols), W(cols + 1) {
        if (R < 1 || C < 1) throw invalid_argument("RectAddFenwick2D: needs R >= 1 and C >= 1");
        bit.assign((size_t)(R + 1) * W, 0);
    }

    // O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit RectAddFenwick2D(const vector<vector<T>>& grid)
        : RectAddFenwick2D((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("RectAddFenwick2D: every row needs the same C values");
        for (int r = 0; r < R; r++) {
            for (int c = 0; c < C; c++) {
                // the mark that makes this cell's value come out right
                S left = c ? S(grid[r][c - 1]) : 0, up = r ? S(grid[r - 1][c]) : 0;
                S upLeft = r && c ? S(grid[r - 1][c - 1]) : 0;
                S d = S(grid[r][c]) - left - up + upLeft;
                size_t at = (size_t)(r + 1) * W + c + 1;
                bit[at] = d;
            }
        }
        for (auto* t : {&bit}) {
            for (int r = 1; r <= R; r++)
                for (int c = 1; c <= C; c++) {
                    int j = c + (c & -c);
                    if (j <= C) (*t)[r * W + j] += (*t)[r * W + c];
                }
            for (int r = 1; r <= R; r++) {
                int j = r + (r & -r);
                if (j > R) continue;
                for (int c = 1; c <= C; c++) (*t)[j * W + c] += (*t)[r * W + c];
            }
        }
    }

    // a mark d at (r, c): every cell at or below-right of it gains d
    LEETCODE_NO_SANITIZE void mark(int r, int c, S d) {
        for (int i = r + 1; i <= R; i += i & -i)
            for (int j = c + 1; j <= C; j += j & -j) bit[i * W + j] += d;
    }

    LEETCODE_NO_SANITIZE void addRect(int r1, int c1, int r2, int c2, S v) {
        mark(r1, c1, v);
        if (c2 + 1 < C) mark(r1, c2 + 1, -v);
        if (r2 + 1 < R) mark(r2 + 1, c1, -v);
        if (r2 + 1 < R && c2 + 1 < C) mark(r2 + 1, c2 + 1, v);
    }

    LEETCODE_NO_SANITIZE S get(int r, int c) const {
        S res = 0;
        for (int i = r + 1; i > 0; i &= i - 1)
            for (int j = c + 1; j > 0; j &= j - 1) res += bit[i * W + j];
        return res;
    }

    // O(log R * log C) -- adds v to every cell of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <=
    // c2 < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void rectAdd(int r1, int c1, int r2, int c2, T v) {
        if (r1 < 0 || r1 > r2 || r2 >= R || c1 < 0 || c1 > c2 || c2 >= C)
            throw out_of_range("rectAdd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C");
        addRect(r1, c1, r2, c2, v);
    }

    // O(log R * log C) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointGet: needs 0 <= r < R and 0 <= c < C");
        return T(get(r, c));
    }

    // O(log R * log C) -- the cell at (r, c) becomes v; needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAssign: needs 0 <= r < R and 0 <= c < C");
        addRect(r, c, r, c, S(v) - get(r, c));
    }

    // O(log R * log C) -- adds v to the cell at (r, c); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointAdd: needs 0 <= r < R and 0 <= c < C");
        addRect(r, c, r, c, v);
    }

    // O(log R * log C) -- the cell at (r, c) becomes max(itself, v); needs 0 <= r < R and 0 <= c < C, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmax: needs 0 <= r < R and 0 <= c < C");
        S cur = get(r, c);
        if (S(v) > cur) addRect(r, c, r, c, S(v) - cur);
    }

    // O(log R * log C) -- the cell at (r, c) becomes min(itself, v); needs 0 <= r < R and 0 <= c < C, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmin: needs 0 <= r < R and 0 <= c < C");
        S cur = get(r, c);
        if (S(v) < cur) addRect(r, c, r, c, S(v) - cur);
    }
};

// Coordinate compression in front of RectAddFenwick2D: coordinates can be any integers (huge, negative, ...). You
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
    RectAddFenwick2D<T> ds;

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

    LEETCODE_NO_SANITIZE static RectAddFenwick2D<T> make(const vector<ll>& xs, const vector<ll>& ys) {
        if (xs.empty() || ys.empty()) throw invalid_argument("Compressed2D: needs at least one x and one y");
        int X = (int)xs.size(), Y = (int)ys.size();
        return RectAddFenwick2D<T>(X, Y);
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

    // O(log X * log Y) -- adds v to the cell (x, y); x must be one of the xs and y one of the ys, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE auto pointAdd(ll x, ll y, T v) {
        return ds.pointAdd(xAt(x, "pointAdd"), yAt(y, "pointAdd"), v);
    }

    // O(log X * log Y) -- the cell (x, y) becomes v; x must be one of the xs and y one of the ys, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE auto pointAssign(ll x, ll y, T v) {
        return ds.pointAssign(xAt(x, "pointAssign"), yAt(y, "pointAssign"), v);
    }

    // O(log X * log Y) -- the cell (x, y) becomes max(itself, v); x must be one of the xs and y one of the ys, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE auto pointChmax(ll x, ll y, T v) {
        return ds.pointChmax(xAt(x, "pointChmax"), yAt(y, "pointChmax"), v);
    }

    // O(log X * log Y) -- the cell (x, y) becomes min(itself, v); x must be one of the xs and y one of the ys, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE auto pointChmin(ll x, ll y, T v) {
        return ds.pointChmin(xAt(x, "pointChmin"), yAt(y, "pointChmin"), v);
    }

    // O(log X * log Y) -- the value at (x, y); x must be one of the xs and y one of the ys, else throws out_of_range
    LEETCODE_NO_SANITIZE auto pointGet(ll x, ll y) {
        return ds.pointGet(xAt(x, "pointGet"), yAt(y, "pointGet"));
    }

    // O(log X * log Y) -- adds v to every cell with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and
    // y1 <= y2, else throws out_of_range; no cell inside: nothing happens
    LEETCODE_NO_SANITIZE void rectAdd(ll x1, ll y1, ll x2, ll y2, T v) {
        auto [r1, c1, r2, c2] = rect(x1, y1, x2, y2, "rectAdd");
        if (r1 >= 0) ds.rectAdd(r1, c1, r2, c2, v);
    }
};
