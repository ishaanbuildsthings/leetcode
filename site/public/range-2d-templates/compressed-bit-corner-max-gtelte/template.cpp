// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/compressed-bit-corner-max-gtelte/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: maxAll maxGteLte pointChmax
// @data-structure-type: BIT
// @input: compressed
// @empty-cells: yes
// @complexities:
//   maxAll: 1
//   maxGteLte: log(X)*log(Y)
//   pointChmax: log(X)*log(Y)
//   build: X*Y
// @memory:
//   layout: none
//   node: tGteLte[1*X*Y]
//   tags: none
//   other: xs[1*X] ys[1*Y] xAt[1*X] yAt[1*Y]
//   note: X = how many distinct x's, Y = distinct y's; one Fenwick tree per corner direction, each (R + 1) by (C + 1), flat; a >= direction is the same tree with that axis mirrored

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
LEETCODE_NO_SANITIZE_INLINE A hotMax(A a, A b) { return a < b ? b : a; }

// Corner max with a 2D Fenwick tree: pointChmax at a cell and the max over a corner of the grid (every cell with row
// <= r or >= r, and column <= c or >= c), O(log R * log C) each, with a quarter of a 2D segment tree's memory per
// direction and a much smaller constant. This works because values only move one way: a cell can only go up
// (pointChmax), so a tree entry never has to forget a value. For a cell that can move both ways, or for rectangles
// that aren't corners, use the 2D segment tree. A cell can be empty and queries only see set cells. Rows and columns
// are 0-based. The (R, C) constructor starts with every cell empty, and a max over no set cell is NO_MAX.
// T is any integer type (int, long long, ...).
template <typename T>
struct CornerMaxFenwick2D {
    static constexpr T NO_MAX = numeric_limits<T>::lowest();  // the smallest value T can hold: a max over no set cell
    int R, C, W;
    T best = NO_MAX;
    HotVector<T> tGteLte;

    // O(R*C) -- R rows by C columns, every cell empty; needs R >= 1 and C >= 1, else throws invalid_argument
    CornerMaxFenwick2D(int rows, int cols) : R(rows), C(cols), W(cols + 1) {
        if (R < 1 || C < 1) throw invalid_argument("CornerMaxFenwick2D: needs R >= 1 and C >= 1");
        tGteLte.assign((size_t)(R + 1) * W, NO_MAX);
    }

    // O(R*C) -- grid: R rows of C values each, every cell set; needs R >= 1 and C >= 1, else throws invalid_argument
    explicit CornerMaxFenwick2D(const vector<vector<T>>& grid)
        : CornerMaxFenwick2D((int)grid.size(), grid.empty() ? 0 : (int)grid[0].size()) {
        for (auto& row : grid)
            if ((int)row.size() != C) throw invalid_argument("CornerMaxFenwick2D: every row needs the same C values");
        for (auto& row : grid)
            for (T v : row) best = hotMax(best, v);
        for (int r = 0; r < R; r++)
            for (int c = 0; c < C; c++) tGteLte[(R - r) * W + c + 1] = grid[r][c];
        for (auto* t : {&tGteLte}) {
            for (int i = 1; i <= R; i++)
                for (int j = 1; j <= C; j++) {
                    int p = j + (j & -j);  // each entry is folded into the next one that covers it
                    if (p <= C) (*t)[i * W + p] = hotMax((*t)[i * W + p], (*t)[i * W + j]);
                }
            for (int i = 1; i <= R; i++) {
                int p = i + (i & -i);
                if (p > R) continue;
                for (int j = 1; j <= C; j++) (*t)[p * W + j] = hotMax((*t)[p * W + j], (*t)[i * W + j]);
            }
        }
    }

    // O(log R * log C) -- the cell at (r, c) becomes max(itself, v); an empty cell becomes v; needs 0 <= r < R and 0
    // <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int r, int c, T v) {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("pointChmax: needs 0 <= r < R and 0 <= c < C");
        best = hotMax(best, v);
        for (int i = R - r; i <= R; i += i & -i)
            for (int j = c + 1; j <= C; j += j & -j) tGteLte[i * W + j] = hotMax(tGteLte[i * W + j], v);
    }

    // O(log R * log C) -- max of the set cells with row >= r and column <= c (NO_MAX, automatically the smallest
    // value of your type T, if there are none); needs 0 <= r < R and 0 <= c < C, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxGteLte(int r, int c) const {
        if (r < 0 || r >= R || c < 0 || c >= C) throw out_of_range("maxGteLte: needs 0 <= r < R and 0 <= c < C");
        T res = NO_MAX;
        for (int i = R - r; i > 0; i &= i - 1)
            for (int j = c + 1; j > 0; j &= j - 1) res = hotMax(res, tGteLte[i * W + j]);
        return res;
    }

    // O(1) -- max of every set cell (NO_MAX, automatically the smallest value of your type T, if there are none)
    LEETCODE_NO_SANITIZE T maxAll() const {
        return best;
    }
};

// Coordinate compression in front of CornerMaxFenwick2D: coordinates can be any integers (huge, negative, ...). You
// list every x and every y a point operation (pointGet, pointAdd, ...) will use; rectangles and corners can be any
// integers. Each listed x becomes a row and each listed y a column of a small grid, and the template above does the
// work on it. X = how many distinct x's, Y = distinct y's: memory and costs are the template's for an X by Y grid. A
// cell is a listed x with a listed y, and it is one point, not a block: a rectangle covers just the cells inside it
// (the gaps between listed coordinates don't exist), so a sum adds those cells' values, it is not an area. Cells you
// never set count as empty, a listed x with a listed y you never use together included.
template <typename T>
struct Compressed2D {
    using ll = long long;
    static constexpr T NO_MAX = CornerMaxFenwick2D<T>::NO_MAX;
    HotVector<ll> xs, ys;  // the listed coordinates, sorted, each once
    CornerMaxFenwick2D<T> ds;

    // n coordinates 0..n-1: pass upTo(n) for an axis you don't want compressed
    LEETCODE_NO_SANITIZE static vector<ll> upTo(ll n) {
        vector<ll> v(n);
        iota(v.begin(), v.end(), 0LL);
        return v;
    }

    // O(X log X + Y log Y + the template's build) -- xs: every x a point operation will use (any order, repeats are
    // fine), or upTo(n) to leave x as 0..n-1; ys: the same for y. Every cell starts empty. Needs at least one x and one
    // y, else throws invalid_argument
    Compressed2D(vector<ll> xs_, vector<ll> ys_)
        : xs(sorted(std::move(xs_))), ys(sorted(std::move(ys_))), ds(make(xs, ys)) {}

    LEETCODE_NO_SANITIZE static vector<ll> sorted(vector<ll> v) {
        sort(v.begin(), v.end());
        v.erase(unique(v.begin(), v.end()), v.end());
        return v;
    }

    LEETCODE_NO_SANITIZE static CornerMaxFenwick2D<T> make(const vector<ll>& xs, const vector<ll>& ys) {
        if (xs.empty() || ys.empty()) throw invalid_argument("Compressed2D: needs at least one x and one y");
        int X = (int)xs.size(), Y = (int)ys.size();
        return CornerMaxFenwick2D<T>(X, Y);
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

    // the cell a corner query starts from: the last listed x <= x (xLte) or the first listed x >= x, the same for y;
    // {-1, -1} when there is none
    LEETCODE_NO_SANITIZE array<int, 2> corner(ll x, ll y, bool xLte, bool yLte) const {
        int r = xLte ? int(upper_bound(xs.begin(), xs.end(), x) - xs.begin()) - 1
                     : int(lower_bound(xs.begin(), xs.end(), x) - xs.begin());
        int c = yLte ? int(upper_bound(ys.begin(), ys.end(), y) - ys.begin()) - 1
                     : int(lower_bound(ys.begin(), ys.end(), y) - ys.begin());
        if (r < 0 || r >= (int)xs.size() || c < 0 || c >= (int)ys.size()) return {-1, -1};
        return {r, c};
    }

    // O(1) -- max of every set cell (NO_MAX, automatically the smallest value of your type T, if there are none)
    LEETCODE_NO_SANITIZE auto maxAll() {
        return ds.maxAll();
    }

    // O(log X * log Y) -- max of the cells with x >= the given x and y <= the given y (NO_MAX, automatically the
    // smallest value of your type T, if there are none); any integers; NO_MAX, automatically the smallest value of your
    // type T, if no cell is there
    LEETCODE_NO_SANITIZE auto maxGteLte(ll x, ll y) {
        auto [r1, c1] = corner(x, y, false, true);
        if (r1 < 0) return NO_MAX;
        return ds.maxGteLte(r1, c1);
    }

    // O(log X * log Y) -- the cell (x, y) becomes max(itself, v); an empty cell becomes v; x must be one of the xs
    // and y one of the ys, else throws out_of_range
    LEETCODE_NO_SANITIZE auto pointChmax(ll x, ll y, T v) {
        return ds.pointChmax(xAt(x, "pointChmax"), yAt(y, "pointChmax"), v);
    }
};
