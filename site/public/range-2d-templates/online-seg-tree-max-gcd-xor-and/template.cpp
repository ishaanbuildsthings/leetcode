// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-seg-tree-max-gcd-xor-and/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: andAll gcdAll maxAll maxGteGte maxGteLte maxLteGte maxLteLte pointAdd pointAssign pointChmax pointChmin pointGet rectAnd rectGcd rectMax rectXor xorAll
// @data-structure-type: seg-tree
// @input: online
// @empty-cells: yes
// @complexities:
//   andAll: 1
//   gcdAll: 1
//   maxAll: 1
//   maxGteGte: log^2(U)
//   maxGteLte: log^2(U)
//   maxLteGte: log^2(U)
//   maxLteLte: log^2(U)
//   pointAdd: log^2(U)*log(U) ?
//   pointAssign: log^2(U)*log(U) ?
//   pointChmax: log^2(U)*log(U) ?
//   pointChmin: log^2(U)*log(U) ?
//   pointGet: log(U)
//   rectAnd: log^2(U)
//   rectGcd: log^2(U)+log(U) ?
//   rectMax: log^2(U)
//   rectXor: log^2(U)
//   xorAll: 1
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[1*log^2(U)] gc[1*log^2(U)] xr[1*log^2(U)] an[1*log^2(U)]
//   tags: none
//   other: yLeft[1*log^2(U)] yRight[1*log^2(U)] xLeft[1*log(U)] xRight[1*log(U)] xTree[1*log(U)]
//   note: sizes are per update: it makes up to log U x-nodes, and a y-path of up to log U nodes in each x-node above the point

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

// Dynamic 2D segment tree (max, gcd, xor, AND): point updates and any-rectangle queries over any coordinate range
// [xLo, xHi] by [yLo, yHi] (as big as +-10^18, negative is fine), with nothing known up front. O(log^2 U) per op, U =
// the size of a coordinate range, and up to log^2 U new nodes per update: the heaviest option. When every point that
// will be updated can be listed before the first call, the points-known templates are much lighter. A segment tree
// over x whose nodes are made only where touched, each owning a segment tree over y made the same way. Rectangles are
// inclusive: x1..x2 by y1..y2. Every cell starts empty and queries only see cells that have been set: a min / max
// over no set cell is NO_MAX; a gcd / xor over none is 0; an AND over none is -1 (every bit set).
// T is any integer type (int, long long, ...). Coordinates are long long, with xHi - xLo and yHi - yLo below 2^63.
template <typename T>
struct DynamicSegTree2D {
    using ll = long long;
    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no set cell gives
    ll xLo, xHi, yLo, yHi;
    int xUsed = 2, yUsed = 1;  // how many x-nodes / y-nodes exist (the arrays are longer: they double when full)
    // x-node 0 = nothing there, 1 = the root; xTree = an x-node's own y-tree (its root)
    HotVector<int> xLeft, xRight, xTree;
    HotVector<int> yLeft, yRight;  // y-node 0 = nothing there: its aggregates are what an untouched range gives
    HotVector<T> mx;
    HotVector<T> gc;
    HotVector<T> xr;
    HotVector<T> an;

    LEETCODE_NO_SANITIZE static T gcdOf(T a, T b) { return std::gcd(a, b); }

    // O(1) -- every cell of [xLo, xHi] by [yLo, yHi] empty; needs xLo <= xHi and yLo <= yHi, else throws
    // invalid_argument
    DynamicSegTree2D(ll xLo, ll xHi, ll yLo, ll yHi)
        : xLo(xLo), xHi(xHi), yLo(yLo), yHi(yHi), xLeft(64, 0), xRight(64, 0), xTree(64, 0) {
        if (xLo > xHi || yLo > yHi) throw invalid_argument("DynamicSegTree2D: needs xLo <= xHi and yLo <= yHi");
        mx.assign(64, NO_MAX);
        gc.assign(64, T(0));
        xr.assign(64, T(0));
        an.assign(64, T(-1));
        yLeft.assign(64, 0), yRight.assign(64, 0);
    }

    // a new node is the next unused slot (already blank); a full array doubles
    LEETCODE_NO_SANITIZE int newX() {
        if (xUsed == (int)xLeft.size())
            xLeft.resize(2 * xUsed, 0), xRight.resize(2 * xUsed, 0), xTree.resize(2 * xUsed, 0);
        return xUsed++;
    }

    LEETCODE_NO_SANITIZE int newY() {
        if (yUsed == (int)yLeft.size()) {
            yLeft.resize(2 * (size_t)yUsed, 0), yRight.resize(2 * (size_t)yUsed, 0);
            mx.resize(2 * (size_t)yUsed, NO_MAX);
            gc.resize(2 * (size_t)yUsed, T(0));
            xr.resize(2 * (size_t)yUsed, T(0));
            an.resize(2 * (size_t)yUsed, T(-1));
        }
        return yUsed++;
    }

    // the y-node of the tree rooted at q that holds exactly y (0 if nothing was set there)
    LEETCODE_NO_SANITIZE int findY(int q, ll y) const {
        ll lo = yLo, hi = yHi;
        while (q && lo < hi) {
            ll mid = lo + (hi - lo) / 2;
            if (y <= mid) q = yLeft[q], hi = mid;
            else q = yRight[q], lo = mid + 1;
        }
        return q;
    }

    // the y-node holding exactly (x, y) (0 if nothing was set there)
    LEETCODE_NO_SANITIZE int findCell(ll x, ll y) const {
        int p = 1;
        ll lo = xLo, hi = xHi;
        while (p && lo < hi) {
            ll mid = lo + (hi - lo) / 2;
            if (x <= mid) p = xLeft[p], hi = mid;
            else p = xRight[p], lo = mid + 1;
        }
        return findY(xTree[p], y);
    }

    // cell (x, y) = v, then every node above it
    LEETCODE_NO_SANITIZE void setCell(ll x, ll y, T v) {
        int path[66], depth = 0;  // the x-nodes from the root down to the one for x alone
        int p = 1;
        for (ll lo = xLo, hi = xHi;;) {
            path[depth++] = p;
            if (lo == hi) break;
            ll mid = lo + (hi - lo) / 2;
            if (x <= mid) {
                if (!xLeft[p]) { int made = newX(); xLeft[p] = made; }
                p = xLeft[p], hi = mid;
            } else {
                if (!xRight[p]) { int made = newX(); xRight[p] = made; }
                p = xRight[p], lo = mid + 1;
            }
        }
        T vMax = v;  // this aggregate over row y of the x-node being written
        T vGcd = v;  // this aggregate over row y of the x-node being written
        T vXor = v;  // this aggregate over row y of the x-node being written
        T vAnd = v;  // this aggregate over row y of the x-node being written
        int below = 0;  // the x-node just written (a child of the next one up)
        for (int i = depth - 1; i >= 0; i--) {
            p = path[i];
            if (below) {
                // the other child: what does it hold at y?
                int other = findY(xTree[xLeft[p] == below ? xRight[p] : xLeft[p]], y);
                vMax = hotMax(vMax, mx[other]);
                vGcd = gcdOf(vGcd, gc[other]);
                vXor ^= xr[other];
                vAnd &= an[other];
            }
            below = p;
            if (!xTree[p]) { int made = newY(); xTree[p] = made; }
            int q = xTree[p], ypath[66], ydepth = 0;
            for (ll lo = yLo, hi = yHi; lo < hi;) {
                ypath[ydepth++] = q;
                ll mid = lo + (hi - lo) / 2;
                if (y <= mid) {
                    if (!yLeft[q]) { int made = newY(); yLeft[q] = made; }
                    q = yLeft[q], hi = mid;
                } else {
                    if (!yRight[q]) { int made = newY(); yRight[q] = made; }
                    q = yRight[q], lo = mid + 1;
                }
            }
            mx[q] = vMax;
            gc[q] = vGcd;
            xr[q] = vXor;
            an[q] = vAnd;
            for (int j = ydepth - 1; j >= 0; j--) {
                q = ypath[j];
                mx[q] = hotMax(mx[yLeft[q]], mx[yRight[q]]);
                gc[q] = gcdOf(gc[yLeft[q]], gc[yRight[q]]);
                xr[q] = xr[yLeft[q]] ^ xr[yRight[q]];
                an[q] = an[yLeft[q]] & an[yRight[q]];
            }
        }
    }

    // O(log U) -- the value at (x, y), NO_MAX if the cell is empty; needs xLo <= x <= xHi and yLo <= y <= yHi, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return T(mx[findCell(x, y)]);
    }

    // O(log^2 U) gcds -- the cell at (x, y) becomes v (it may go down as well as up); needs xLo <= x <= xHi and yLo
    // <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointAssign: needs xLo <= x <= xHi and yLo <= y <= yHi");
        setCell(x, y, v);
    }

    // O(log^2 U) gcds -- adds v to the cell at (x, y); an empty cell becomes v; needs xLo <= x <= xHi and yLo <= y <=
    // yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointAdd: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T cur = T(mx[findCell(x, y)]);
        setCell(x, y, cur == NO_MAX ? v : T(cur + v));
    }

    // O(log^2 U) gcds -- the cell at (x, y) becomes max(itself, v); an empty cell becomes v; needs xLo <= x <= xHi and
    // yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointChmax: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T cur = T(mx[findCell(x, y)]);
        if (cur == NO_MAX || v > cur) setCell(x, y, v);
    }

    // O(log^2 U) gcds -- the cell at (x, y) becomes min(itself, v); an empty cell becomes v; needs xLo <= x <= xHi and
    // yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointChmin: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T cur = T(mx[findCell(x, y)]);
        if (cur == NO_MAX || v < cur) setCell(x, y, v);
    }

    LEETCODE_NO_SANITIZE void maxOverY(int q, ll lo, ll hi, ll y1, ll y2, T& res) const {
        if (q && !(y1 <= lo && hi <= y2)) {
            ll mid = lo + (hi - lo) / 2;
            if (y1 <= mid) maxOverY(yLeft[q], lo, mid, y1, y2, res);
            if (y2 > mid) maxOverY(yRight[q], mid + 1, hi, y1, y2, res);
            return;
        }
        res = hotMax(res, mx[q]);
    }

    LEETCODE_NO_SANITIZE void maxOverX(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T& res) const {
        if (p && !(x1 <= lo && hi <= x2)) {
            ll mid = lo + (hi - lo) / 2;
            if (x1 <= mid) maxOverX(xLeft[p], lo, mid, x1, y1, x2, y2, res);
            if (x2 > mid) maxOverX(xRight[p], mid + 1, hi, x1, y1, x2, y2, res);
            return;
        }
        // this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
        maxOverY(xTree[p], yLo, yHi, y1, y2, res);
    }

    LEETCODE_NO_SANITIZE T maxOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = NO_MAX;
        maxOverX(1, xLo, xHi, x1, y1, x2, y2, res);
        return res;
    }

    // O(log^2 U) -- max of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (NO_MAX if there are none); needs xLo
    // <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectMax(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectMax: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return maxOf(x1, y1, x2, y2);
    }

    // O(1) -- max of every set cell (NO_MAX if there are none)
    LEETCODE_NO_SANITIZE T maxAll() const {
        return mx[xTree[1]];
    }

    // O(log^2 U) -- max of the set cells with x <= the given x and y <= the given y (NO_MAX if there are none); needs
    // xLo <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxLteLte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("maxLteLte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return maxOf(xLo, yLo, x, y);
    }

    // O(log^2 U) -- max of the set cells with x <= the given x and y >= the given y (NO_MAX if there are none); needs
    // xLo <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxLteGte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("maxLteGte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return maxOf(xLo, y, x, yHi);
    }

    // O(log^2 U) -- max of the set cells with x >= the given x and y <= the given y (NO_MAX if there are none); needs
    // xLo <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxGteLte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("maxGteLte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return maxOf(x, yLo, xHi, y);
    }

    // O(log^2 U) -- max of the set cells with x >= the given x and y >= the given y (NO_MAX if there are none); needs
    // xLo <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T maxGteGte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("maxGteGte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return maxOf(x, y, xHi, yHi);
    }

    LEETCODE_NO_SANITIZE void gcdOverY(int q, ll lo, ll hi, ll y1, ll y2, T& res) const {
        if (q && !(y1 <= lo && hi <= y2)) {
            ll mid = lo + (hi - lo) / 2;
            if (y1 <= mid) gcdOverY(yLeft[q], lo, mid, y1, y2, res);
            if (y2 > mid) gcdOverY(yRight[q], mid + 1, hi, y1, y2, res);
            return;
        }
        res = gcdOf(res, gc[q]);
    }

    LEETCODE_NO_SANITIZE void gcdOverX(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T& res) const {
        if (p && !(x1 <= lo && hi <= x2)) {
            ll mid = lo + (hi - lo) / 2;
            if (x1 <= mid) gcdOverX(xLeft[p], lo, mid, x1, y1, x2, y2, res);
            if (x2 > mid) gcdOverX(xRight[p], mid + 1, hi, x1, y1, x2, y2, res);
            return;
        }
        // this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
        gcdOverY(xTree[p], yLo, yHi, y1, y2, res);
    }

    LEETCODE_NO_SANITIZE T gcdOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = T(0);
        gcdOverX(1, xLo, xHi, x1, y1, x2, y2, res);
        return res;
    }

    // O(log^2 U + log U) -- gcd of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (0 if there are none); needs
    // xLo <=
    // x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectGcd(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectGcd: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return gcdOf(x1, y1, x2, y2);
    }

    // O(1) -- gcd of every set cell (0 if there are none)
    LEETCODE_NO_SANITIZE T gcdAll() const {
        return gcdOf(gc[xTree[1]], T(0));
    }

    LEETCODE_NO_SANITIZE void xorOverY(int q, ll lo, ll hi, ll y1, ll y2, T& res) const {
        if (q && !(y1 <= lo && hi <= y2)) {
            ll mid = lo + (hi - lo) / 2;
            if (y1 <= mid) xorOverY(yLeft[q], lo, mid, y1, y2, res);
            if (y2 > mid) xorOverY(yRight[q], mid + 1, hi, y1, y2, res);
            return;
        }
        res ^= xr[q];
    }

    LEETCODE_NO_SANITIZE void xorOverX(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T& res) const {
        if (p && !(x1 <= lo && hi <= x2)) {
            ll mid = lo + (hi - lo) / 2;
            if (x1 <= mid) xorOverX(xLeft[p], lo, mid, x1, y1, x2, y2, res);
            if (x2 > mid) xorOverX(xRight[p], mid + 1, hi, x1, y1, x2, y2, res);
            return;
        }
        // this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
        xorOverY(xTree[p], yLo, yHi, y1, y2, res);
    }

    LEETCODE_NO_SANITIZE T xorOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = T(0);
        xorOverX(1, xLo, xHi, x1, y1, x2, y2, res);
        return res;
    }

    // O(log^2 U) -- xor of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (0 if there are none); needs xLo <= x1 <=
    // x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectXor(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectXor: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return xorOf(x1, y1, x2, y2);
    }

    // O(1) -- xor of every set cell (0 if there are none)
    LEETCODE_NO_SANITIZE T xorAll() const {
        return xr[xTree[1]];
    }

    LEETCODE_NO_SANITIZE void andOverY(int q, ll lo, ll hi, ll y1, ll y2, T& res) const {
        if (q && !(y1 <= lo && hi <= y2)) {
            ll mid = lo + (hi - lo) / 2;
            if (y1 <= mid) andOverY(yLeft[q], lo, mid, y1, y2, res);
            if (y2 > mid) andOverY(yRight[q], mid + 1, hi, y1, y2, res);
            return;
        }
        res &= an[q];
    }

    LEETCODE_NO_SANITIZE void andOverX(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T& res) const {
        if (p && !(x1 <= lo && hi <= x2)) {
            ll mid = lo + (hi - lo) / 2;
            if (x1 <= mid) andOverX(xLeft[p], lo, mid, x1, y1, x2, y2, res);
            if (x2 > mid) andOverX(xRight[p], mid + 1, hi, x1, y1, x2, y2, res);
            return;
        }
        // this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
        andOverY(xTree[p], yLo, yHi, y1, y2, res);
    }

    LEETCODE_NO_SANITIZE T andOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = T(-1);
        andOverX(1, xLo, xHi, x1, y1, x2, y2, res);
        return res;
    }

    // O(log^2 U) -- AND of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (-1 (every bit set) if there are none);
    // needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectAnd(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectAnd: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return andOf(x1, y1, x2, y2);
    }

    // O(1) -- AND of every set cell (-1 (every bit set) if there are none)
    LEETCODE_NO_SANITIZE T andAll() const {
        return an[xTree[1]];
    }
};
