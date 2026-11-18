// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-kept-tags-rect-min/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: minAll minGteGte minGteLte minLteGte minLteLte pointChmin pointGet rectChmin rectMin
// @data-structure-type: seg-tree-kept-tags
// @input: online
// @empty-cells: yes
// @complexities:
//   minAll: 1
//   minGteGte: log^2(U)
//   minGteLte: log^2(U)
//   minLteGte: log^2(U)
//   minLteLte: log^2(U)
//   pointChmin: log^2(U)
//   pointGet: log^2(U)
//   rectChmin: log^2(U)
//   rectMin: log^2(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: none
//   tags: yCover[8*log^2(U)] yTouch[8*log^2(U)]
//   other: yLeft[8*log^2(U)] yRight[8*log^2(U)] xLeft[2*log(U)] xRight[2*log(U)] xCover[2*log(U)] xTouch[2*log(U)]
//   note: sizes are per update: a rectangle makes up to about 2 log U x-nodes and, in the two y-trees of each x-node it meets, up to about 2 log U y-nodes

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


// Rectangle chmin and rectangle min over a huge coordinate range, nothing known up front: O(log^2 U) per operation,
// and up to about 8 log^2 U new nodes per update. A dynamic tree over x whose every node owns two dynamic trees over
// y: one for the updates that cover all of its x's, one for the updates that touch any of them. Every y-node keeps
// the same two values for its y's. An update goes into the touch side of every node it meets and the cover side of
// the nodes that make up its rectangle; a query reads the touch side of the nodes that make up its rectangle and the
// cover side of the nodes above them (an update covering a whole node above covers the query's part of it too). Tags
// are never pushed down, which works because chmin never has to be undone and seeing one update twice doesn't change
// a min. A cell no update has reached is empty and queries only see set cells.
// T is any integer type (int, long long, ...). Coordinates are long long.
template <typename T>
struct OnlineRectChminRectMin2D {
    using ll = long long;
    static constexpr T NO_MIN = numeric_limits<T>::max();  // the largest value T can hold: an empty cell
    ll xLo, xHi, yLo, yHi;
    int xUsed = 2, yUsed = 1;  // how many x-nodes / y-nodes exist (the arrays are longer: they double when full)
    // x-node 0 = nothing there, 1 = the root; xCover / xTouch = its y-trees (roots, 0 = none) for the updates that
    // cover all of its x's / touch any of them
    HotVector<int> xLeft, xRight, xCover, xTouch;
    HotVector<int> yLeft, yRight;  // y-node 0 = nothing there
    HotVector<T> yCover, yTouch;  // the best update covering all of a y-node's y's / touching any of them
    T best = NO_MIN;

    // O(1) -- every cell of [xLo, xHi] by [yLo, yHi] empty; needs xLo <= xHi and yLo <= yHi, else throws
    // invalid_argument
    OnlineRectChminRectMin2D(ll xLo, ll xHi, ll yLo, ll yHi)
        : xLo(xLo), xHi(xHi), yLo(yLo), yHi(yHi), xLeft(64, 0), xRight(64, 0), xCover(64, 0), xTouch(64, 0) {
        if (xLo > xHi || yLo > yHi) throw invalid_argument("OnlineRectChminRectMin2D: needs xLo <= xHi and yLo <= yHi");
        yLeft.assign(64, 0), yRight.assign(64, 0), yCover.assign(64, NO_MIN), yTouch.assign(64, NO_MIN);
    }

    // a new node is the next unused slot (already blank); a full array doubles
    LEETCODE_NO_SANITIZE int newX() {
        if (xUsed == (int)xLeft.size()) {
            size_t n = 2 * (size_t)xUsed;
            xLeft.resize(n, 0), xRight.resize(n, 0), xCover.resize(n, 0), xTouch.resize(n, 0);
        }
        return xUsed++;
    }

    LEETCODE_NO_SANITIZE int newY() {
        if (yUsed == (int)yLeft.size()) {
            size_t n = 2 * (size_t)yUsed;
            yLeft.resize(n, 0), yRight.resize(n, 0), yCover.resize(n, NO_MIN), yTouch.resize(n, NO_MIN);
        }
        return yUsed++;
    }

    LEETCODE_NO_SANITIZE static bool better(T a, T b) { return a < b; }

    // y-node q (covering lo..hi): y1..y2 become min(themselves, v)
    LEETCODE_NO_SANITIZE void cols(int q, ll lo, ll hi, ll y1, ll y2, T v) {
        if (better(v, yTouch[q])) yTouch[q] = v;
        if (y1 <= lo && hi <= y2) {
            if (better(v, yCover[q])) yCover[q] = v;
            return;
        }
        ll mid = lo + (hi - lo) / 2;
        if (y1 <= mid) {
            if (!yLeft[q]) { int made = newY(); yLeft[q] = made; }
            cols(yLeft[q], lo, mid, y1, y2, v);
        }
        if (y2 > mid) {
            if (!yRight[q]) { int made = newY(); yRight[q] = made; }
            cols(yRight[q], mid + 1, hi, y1, y2, v);
        }
    }

    // the min y-node q (covering lo..hi, 0 = none) holds for y1..y2
    LEETCODE_NO_SANITIZE T colsBest(int q, ll lo, ll hi, ll y1, ll y2) const {
        if (!q) return NO_MIN;
        if (y1 <= lo && hi <= y2) return yTouch[q];
        T res = yCover[q];
        ll mid = lo + (hi - lo) / 2;
        if (y1 <= mid) {
            T got = colsBest(yLeft[q], lo, mid, y1, y2);
            if (better(got, res)) res = got;
        }
        if (y2 > mid) {
            T got = colsBest(yRight[q], mid + 1, hi, y1, y2);
            if (better(got, res)) res = got;
        }
        return res;
    }

    // x-node p (covering lo..hi): the update's part of it
    LEETCODE_NO_SANITIZE void update(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T v) {
        if (!xTouch[p]) { int made = newY(); xTouch[p] = made; }
        cols(xTouch[p], yLo, yHi, y1, y2, v);
        if (x1 <= lo && hi <= x2) {
            if (!xCover[p]) { int made = newY(); xCover[p] = made; }
            cols(xCover[p], yLo, yHi, y1, y2, v);
            return;
        }
        ll mid = lo + (hi - lo) / 2;
        if (x1 <= mid) {
            if (!xLeft[p]) { int made = newX(); xLeft[p] = made; }
            update(xLeft[p], lo, mid, x1, y1, x2, y2, v);
        }
        if (x2 > mid) {
            if (!xRight[p]) { int made = newX(); xRight[p] = made; }
            update(xRight[p], mid + 1, hi, x1, y1, x2, y2, v);
        }
    }

    // the min x-node p (covering lo..hi, 0 = none) holds for the rectangle
    LEETCODE_NO_SANITIZE T query(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2) const {
        if (!p) return NO_MIN;
        if (x1 <= lo && hi <= x2) return colsBest(xTouch[p], yLo, yHi, y1, y2);
        T res = colsBest(xCover[p], yLo, yHi, y1, y2);
        ll mid = lo + (hi - lo) / 2;
        if (x1 <= mid) {
            T got = query(xLeft[p], lo, mid, x1, y1, x2, y2);
            if (better(got, res)) res = got;
        }
        if (x2 > mid) {
            T got = query(xRight[p], mid + 1, hi, x1, y1, x2, y2);
            if (better(got, res)) res = got;
        }
        return res;
    }

    // O(log^2 U) -- every cell with x1 <= x <= x2 and y1 <= y <= y2 becomes min(itself, v) (an empty one becomes v);
    // needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rectChmin(ll x1, ll y1, ll x2, ll y2, T v) {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectChmin: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        if (better(v, best)) best = v;
        update(1, xLo, xHi, x1, y1, x2, y2, v);
    }

    // O(log^2 U) -- the cell (x, y) becomes min(itself, v) (an empty one becomes v); needs xLo <= x <= xHi and yLo <= y
    // <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointChmin: needs xLo <= x <= xHi and yLo <= y <= yHi");
        if (better(v, best)) best = v;
        update(1, xLo, xHi, x, y, x, y, v);
    }

    // O(log^2 U) -- the value at (x, y), NO_MIN, automatically the largest value of your type T, if the cell is empty;
    // needs xLo <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return query(1, xLo, xHi, x, y, x, y);
    }

    // O(log^2 U) -- min of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (NO_MIN, automatically the largest value
    // of your type T, if there are none); needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T rectMin(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectMin: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return query(1, xLo, xHi, x1, y1, x2, y2);
    }

    // O(1) -- min of every set cell (NO_MIN, automatically the largest value of your type T, if there are none)
    LEETCODE_NO_SANITIZE T minAll() const { return best; }

    // O(log^2 U) -- min of the set cells with x <= the given x and y <= the given y (NO_MIN, automatically the largest
    // value of your type T, if there are none); needs xLo <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T minLteLte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("minLteLte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return query(1, xLo, xHi, xLo, yLo, x, y);
    }

    // O(log^2 U) -- min of the set cells with x <= the given x and y >= the given y (NO_MIN, automatically the largest
    // value of your type T, if there are none); needs xLo <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T minLteGte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("minLteGte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return query(1, xLo, xHi, xLo, y, x, yHi);
    }

    // O(log^2 U) -- min of the set cells with x >= the given x and y <= the given y (NO_MIN, automatically the largest
    // value of your type T, if there are none); needs xLo <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T minGteLte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("minGteLte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return query(1, xLo, xHi, x, yLo, xHi, y);
    }

    // O(log^2 U) -- min of the set cells with x >= the given x and y >= the given y (NO_MIN, automatically the largest
    // value of your type T, if there are none); needs xLo <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T minGteGte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("minGteGte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return query(1, xLo, xHi, x, y, xHi, yHi);
    }
};
