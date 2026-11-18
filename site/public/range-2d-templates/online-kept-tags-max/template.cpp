// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-kept-tags-max/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointChmax pointGet rectChmax
// @data-structure-type: seg-tree-kept-tags
// @input: online
// @empty-cells: yes
// @complexities:
//   pointChmax: log^2(U)
//   pointGet: log^2(U)
//   rectChmax: log^2(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: none
//   tags: tag[4*log^2(U)]
//   other: yLeft[4*log^2(U)] yRight[4*log^2(U)] xLeft[2*log(U)] xRight[2*log(U)] xTree[2*log(U)]
//   note: sizes are per update: a rectangle makes up to about 2 log U x-nodes and, in each of the O(log U) it tags, up to about 2 log U y-nodes

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


// Rectangle chmax with point reads over a huge coordinate range, nothing known up front: O(log^2 U) per rectChmax,
// O(log^2 U) per pointGet, and up to about 4 log^2 U new nodes per rectChmax. A dynamic tree over x whose every node
// owns a dynamic tree over y, nodes made only where an update goes. rectChmax(x1, y1, x2, y2, v) leaves v as a tag
// on the O(log U) x-nodes that make up x1..x2, and in each of them on the O(log U) y-nodes that make up y1..y2;
// pointGet(x, y) takes the max of the tags on the way down to (x, y). Tags are never pushed down, which works because
// chmax never has to be undone. A cell no update has reached reads NO_MAX.
// T is any integer type (int, long long, ...). Coordinates are long long.
template <typename T>
struct OnlineRectChmax2D {
    using ll = long long;
    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a cell no update has reached reads
    ll xLo, xHi, yLo, yHi;
    int xUsed = 2, yUsed = 1;  // how many x-nodes / y-nodes exist (the arrays are longer: they double when full)
    // x-node 0 = nothing there, 1 = the root; xTree = its own y-tree's root (0 = none)
    HotVector<int> xLeft, xRight, xTree;
    HotVector<int> yLeft, yRight;  // y-node 0 = nothing there
    HotVector<T> tag;

    // O(1) -- every cell of [xLo, xHi] by [yLo, yHi] unreached; needs xLo <= xHi and yLo <= yHi, else throws
    // invalid_argument
    OnlineRectChmax2D(ll xLo, ll xHi, ll yLo, ll yHi)
        : xLo(xLo), xHi(xHi), yLo(yLo), yHi(yHi), xLeft(64, 0), xRight(64, 0), xTree(64, 0) {
        if (xLo > xHi || yLo > yHi) throw invalid_argument("OnlineRectChmax2D: needs xLo <= xHi and yLo <= yHi");
        yLeft.assign(64, 0), yRight.assign(64, 0), tag.assign(64, NO_MAX);
    }

    // a new node is the next unused slot (already blank); a full array doubles
    LEETCODE_NO_SANITIZE int newX() {
        if (xUsed == (int)xLeft.size())
            xLeft.resize(2 * xUsed, 0), xRight.resize(2 * xUsed, 0), xTree.resize(2 * xUsed, 0);
        return xUsed++;
    }

    LEETCODE_NO_SANITIZE int newY() {
        if (yUsed == (int)yLeft.size())
            yLeft.resize(2 * (size_t)yUsed, 0), yRight.resize(2 * (size_t)yUsed, 0),
                tag.resize(2 * (size_t)yUsed, NO_MAX);
        return yUsed++;
    }

    // y-node q (covering lo..hi): y1..y2 become max(themselves, v)
    LEETCODE_NO_SANITIZE void cols(int q, ll lo, ll hi, ll y1, ll y2, T v) {
        if (y1 <= lo && hi <= y2) {
            if (v > tag[q]) tag[q] = v;
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

    // x-node p (covering lo..hi): the rectangle's part of it
    LEETCODE_NO_SANITIZE void update(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T v) {
        if (x1 <= lo && hi <= x2) {
            if (!xTree[p]) { int made = newY(); xTree[p] = made; }
            cols(xTree[p], yLo, yHi, y1, y2, v);
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

    // O(log^2 U) -- every cell with x1 <= x <= x2 and y1 <= y <= y2 becomes max(itself, v) (one never reached becomes
    // v); needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rectChmax(ll x1, ll y1, ll x2, ll y2, T v) {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectChmax: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        update(1, xLo, xHi, x1, y1, x2, y2, v);
    }

    // O(log^2 U) -- the cell (x, y) becomes max(itself, v) (one never reached becomes v); needs xLo <= x <= xHi and
    // yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointChmax: needs xLo <= x <= xHi and yLo <= y <= yHi");
        update(1, xLo, xHi, x, y, x, y, v);
    }

    // O(log^2 U) -- the value at (x, y), NO_MAX if no update has reached it; needs xLo <= x <= xHi and yLo <= y <= yHi,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T res = NO_MAX;
        int p = 1;
        for (ll lo = xLo, hi = xHi; p;) {
            int q = xTree[p];
            for (ll ylo = yLo, yhi = yHi; q;) {
                if (tag[q] > res) res = tag[q];
                if (ylo == yhi) break;
                ll mid = ylo + (yhi - ylo) / 2;
                if (y <= mid) q = yLeft[q], yhi = mid;
                else q = yRight[q], ylo = mid + 1;
            }
            if (lo == hi) break;
            ll mid = lo + (hi - lo) / 2;
            if (x <= mid) p = xLeft[p], hi = mid;
            else p = xRight[p], lo = mid + 1;
        }
        return res;
    }
};
