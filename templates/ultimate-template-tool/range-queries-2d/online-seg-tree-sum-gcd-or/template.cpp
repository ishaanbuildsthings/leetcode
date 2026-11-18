// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-seg-tree-sum-gcd-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: gcdAll orAll pointAdd pointAssign pointChmax pointChmin pointGet rectGcd rectOr rectSum sumAll sumGteGte sumGteLte sumLteGte sumLteLte
// @data-structure-type: seg-tree
// @input: online
// @complexities:
//   gcdAll: 1
//   orAll: 1
//   pointAdd: log^2(U)*log(U) ?
//   pointAssign: log^2(U)*log(U) ?
//   pointChmax: log^2(U)*log(U) ?
//   pointChmin: log^2(U)*log(U) ?
//   pointGet: log(U)
//   rectGcd: log^2(U)+log(U) ?
//   rectOr: log^2(U)
//   rectSum: log^2(U)
//   sumAll: 1
//   sumGteGte: log^2(U)
//   sumGteLte: log^2(U)
//   sumLteGte: log^2(U)
//   sumLteLte: log^2(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[1*log^2(U)] gc[1*log^2(U)] orr[1*log^2(U)]
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

// Dynamic 2D segment tree (sum, gcd, OR): point updates and any-rectangle queries over any coordinate range [xLo,
// xHi] by [yLo, yHi] (as big as +-10^18, negative is fine), with nothing known up front. O(log^2 U) per op, U = the
// size of a coordinate range, and up to log^2 U new nodes per update: the heaviest option. When every point that will
// be updated can be listed before the first call, the points-known templates are much lighter. A segment tree over x
// whose nodes are made only where touched, each owning a segment tree over y made the same way. Rectangles are
// inclusive: x1..x2 by y1..y2. Every cell starts at 0.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T). Coordinates are long
// long, with xHi - xLo and yHi - yLo below 2^63.
template <typename T>
struct DynamicSegTree2D {
    using ll = long long;
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    ll xLo, xHi, yLo, yHi;
    int xUsed = 2, yUsed = 1;  // how many x-nodes / y-nodes exist (the arrays are longer: they double when full)
    // x-node 0 = nothing there, 1 = the root; xTree = an x-node's own y-tree (its root)
    HotVector<int> xLeft, xRight, xTree;
    HotVector<int> yLeft, yRight;  // y-node 0 = nothing there: its aggregates are what an untouched range gives
    HotVector<S> sm;
    HotVector<T> gc;
    HotVector<T> orr;

    LEETCODE_NO_SANITIZE static T gcdOf(T a, T b) { return std::gcd(a, b); }

    // O(1) -- every cell of [xLo, xHi] by [yLo, yHi] 0; needs xLo <= xHi and yLo <= yHi, else throws invalid_argument
    DynamicSegTree2D(ll xLo, ll xHi, ll yLo, ll yHi)
        : xLo(xLo), xHi(xHi), yLo(yLo), yHi(yHi), xLeft(64, 0), xRight(64, 0), xTree(64, 0) {
        if (xLo > xHi || yLo > yHi) throw invalid_argument("DynamicSegTree2D: needs xLo <= xHi and yLo <= yHi");
        sm.assign(64, S(0));
        gc.assign(64, T(0));
        orr.assign(64, T(0));
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
            sm.resize(2 * (size_t)yUsed, S(0));
            gc.resize(2 * (size_t)yUsed, T(0));
            orr.resize(2 * (size_t)yUsed, T(0));
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
        S vSum = v;  // this aggregate over row y of the x-node being written
        T vGcd = v;  // this aggregate over row y of the x-node being written
        T vOr = v;  // this aggregate over row y of the x-node being written
        int below = 0;  // the x-node just written (a child of the next one up)
        for (int i = depth - 1; i >= 0; i--) {
            p = path[i];
            if (below) {
                // the other child: what does it hold at y?
                int other = findY(xTree[xLeft[p] == below ? xRight[p] : xLeft[p]], y);
                vSum += sm[other];
                vGcd = gcdOf(vGcd, gc[other]);
                vOr |= orr[other];
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
            sm[q] = vSum;
            gc[q] = vGcd;
            orr[q] = vOr;
            for (int j = ydepth - 1; j >= 0; j--) {
                q = ypath[j];
                sm[q] = sm[yLeft[q]] + sm[yRight[q]];
                gc[q] = gcdOf(gc[yLeft[q]], gc[yRight[q]]);
                orr[q] = orr[yLeft[q]] | orr[yRight[q]];
            }
        }
    }

    // O(log U) -- the value at (x, y); needs xLo <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return T(sm[findCell(x, y)]);
    }

    // O(log^2 U) gcds -- the cell at (x, y) becomes v (it may go down as well as up); needs xLo <= x <= xHi and yLo
    // <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointAssign: needs xLo <= x <= xHi and yLo <= y <= yHi");
        setCell(x, y, v);
    }

    // O(log^2 U) gcds -- adds v to the cell at (x, y); needs xLo <= x <= xHi and yLo <= y <= yHi, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointAdd: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T cur = T(sm[findCell(x, y)]);
        setCell(x, y, T(cur + v));
    }

    // O(log^2 U) gcds -- the cell at (x, y) becomes max(itself, v); needs xLo <= x <= xHi and yLo <= y <= yHi, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointChmax: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T cur = T(sm[findCell(x, y)]);
        if (v > cur) setCell(x, y, v);
    }

    // O(log^2 U) gcds -- the cell at (x, y) becomes min(itself, v); needs xLo <= x <= xHi and yLo <= y <= yHi, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointChmin: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T cur = T(sm[findCell(x, y)]);
        if (v < cur) setCell(x, y, v);
    }

    LEETCODE_NO_SANITIZE void sumOverY(int q, ll lo, ll hi, ll y1, ll y2, S& res) const {
        if (q && !(y1 <= lo && hi <= y2)) {
            ll mid = lo + (hi - lo) / 2;
            if (y1 <= mid) sumOverY(yLeft[q], lo, mid, y1, y2, res);
            if (y2 > mid) sumOverY(yRight[q], mid + 1, hi, y1, y2, res);
            return;
        }
        res += sm[q];
    }

    LEETCODE_NO_SANITIZE void sumOverX(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, S& res) const {
        if (p && !(x1 <= lo && hi <= x2)) {
            ll mid = lo + (hi - lo) / 2;
            if (x1 <= mid) sumOverX(xLeft[p], lo, mid, x1, y1, x2, y2, res);
            if (x2 > mid) sumOverX(xRight[p], mid + 1, hi, x1, y1, x2, y2, res);
            return;
        }
        // this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
        sumOverY(xTree[p], yLo, yHi, y1, y2, res);
    }

    LEETCODE_NO_SANITIZE S sumOf(ll x1, ll y1, ll x2, ll y2) const {
        S res = S(0);
        sumOverX(1, xLo, xHi, x1, y1, x2, y2, res);
        return res;
    }

    // O(log^2 U) -- sum of the cells with x1 <= x <= x2 and y1 <= y <= y2; needs xLo <= x1 <= x2 <= xHi and yLo <= y1
    // <=
    // y2 <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE S rectSum(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectSum: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return sumOf(x1, y1, x2, y2);
    }

    // O(1) -- sum of the whole range
    LEETCODE_NO_SANITIZE S sumAll() const {
        return sm[xTree[1]];
    }

    // O(log^2 U) -- sum of the set cells with x <= the given x and y <= the given y; needs xLo <= x <= xHi and yLo <= y
    // <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumLteLte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("sumLteLte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return sumOf(xLo, yLo, x, y);
    }

    // O(log^2 U) -- sum of the set cells with x <= the given x and y >= the given y; needs xLo <= x <= xHi and yLo <= y
    // <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumLteGte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("sumLteGte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return sumOf(xLo, y, x, yHi);
    }

    // O(log^2 U) -- sum of the set cells with x >= the given x and y <= the given y; needs xLo <= x <= xHi and yLo <= y
    // <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumGteLte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("sumGteLte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return sumOf(x, yLo, xHi, y);
    }

    // O(log^2 U) -- sum of the set cells with x >= the given x and y >= the given y; needs xLo <= x <= xHi and yLo <= y
    // <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumGteGte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("sumGteGte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return sumOf(x, y, xHi, yHi);
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

    // O(log^2 U + log U) -- gcd of the cells with x1 <= x <= x2 and y1 <= y <= y2; needs xLo <= x1 <= x2 <= xHi and yLo
    // <= y1 <= y2 <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectGcd(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectGcd: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return gcdOf(x1, y1, x2, y2);
    }

    // O(1) -- gcd of the whole range
    LEETCODE_NO_SANITIZE T gcdAll() const {
        return gcdOf(gc[xTree[1]], T(0));
    }

    LEETCODE_NO_SANITIZE void orOverY(int q, ll lo, ll hi, ll y1, ll y2, T& res) const {
        if (q && !(y1 <= lo && hi <= y2)) {
            ll mid = lo + (hi - lo) / 2;
            if (y1 <= mid) orOverY(yLeft[q], lo, mid, y1, y2, res);
            if (y2 > mid) orOverY(yRight[q], mid + 1, hi, y1, y2, res);
            return;
        }
        res |= orr[q];
    }

    LEETCODE_NO_SANITIZE void orOverX(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T& res) const {
        if (p && !(x1 <= lo && hi <= x2)) {
            ll mid = lo + (hi - lo) / 2;
            if (x1 <= mid) orOverX(xLeft[p], lo, mid, x1, y1, x2, y2, res);
            if (x2 > mid) orOverX(xRight[p], mid + 1, hi, x1, y1, x2, y2, res);
            return;
        }
        // this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
        orOverY(xTree[p], yLo, yHi, y1, y2, res);
    }

    LEETCODE_NO_SANITIZE T orOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = T(0);
        orOverX(1, xLo, xHi, x1, y1, x2, y2, res);
        return res;
    }

    // O(log^2 U) -- OR of the cells with x1 <= x <= x2 and y1 <= y <= y2; needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <=
    // y2 <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectOr(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectOr: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return orOf(x1, y1, x2, y2);
    }

    // O(1) -- OR of the whole range
    LEETCODE_NO_SANITIZE T orAll() const {
        return orr[xTree[1]];
    }
};
