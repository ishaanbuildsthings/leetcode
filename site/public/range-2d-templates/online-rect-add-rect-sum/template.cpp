// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-rect-add-rect-sum/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointAdd pointGet rectAdd rectSum sumAll sumGteGte sumGteLte sumLteGte sumLteLte
// @data-structure-type: BIT
// @input: online
// @model: area
// @complexities:
//   pointAdd: log^2(U)
//   pointGet: log^2(U)
//   rectAdd: log^2(U)
//   rectSum: log^2(U)
//   sumAll: 1
//   sumGteGte: log^2(U)
//   sumGteLte: log^2(U)
//   sumLteGte: log^2(U)
//   sumLteLte: log^2(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: s0[4*log^2(U)] sx[4*log^2(U)] sy[4*log^2(U)] sxy[4*log^2(U)]
//   tags: none
//   other: yLeft[4*log^2(U)] yRight[4*log^2(U)] xLeft[4*log(U)] xRight[4*log(U)] xTree[4*log(U)]
//   note: sizes are per update: a rect add is up to four marks, each making up to about log U x-nodes and log U y-nodes under each

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


// Rectangle add and rectangle sum over a huge coordinate range, nothing known up front: O(log^2 U) per operation, and
// up to about 4 log^2 U new nodes per rectAdd. A rect add is four point marks at its corners (+v, -v, -v, +v), and
// the sum of the cells with x <= X and y <= Y comes from four sums over the marks below and left of (X, Y): of d, d *
// x, d * y and d * x * y, which a dynamic tree over x whose every node owns a dynamic tree over y keeps (coordinates
// are counted from xLo and yLo). Every cell starts at 0, and sums are true area sums: a rect add of v on a 3 by 4
// rectangle adds 12 * v.
// T is any integer type (int, long long, ...); the four sums are kept in __int128, so coordinates up to about 10^9
// apart and values up to about 10^9 are fine, as long as every answer fits in T. Coordinates are long long.
template <typename T>
struct OnlineRectAddRectSum2D {
    using ll = long long;
    using L = __int128;
    ll xLo, xHi, yLo, yHi, W, H;  // (marks sit at 0..W by 0..H, counted from xLo and yLo)
    int xUsed = 2, yUsed = 1;  // how many x-nodes / y-nodes exist (the arrays are longer: they double when full)
    // x-node 0 = nothing there, 1 = the root; xTree = its own y-tree's root (0 = none)
    HotVector<int> xLeft, xRight, xTree;
    HotVector<int> yLeft, yRight;  // y-node 0 = nothing there
    HotVector<array<L, 4>> s;  // per y-node: the sums of d, d * x, d * y, d * x * y over the marks below it
    L total = 0;

    // O(1) -- every cell of [xLo, xHi] by [yLo, yHi] starts at 0; needs xLo <= xHi and yLo <= yHi, else throws
    // invalid_argument
    OnlineRectAddRectSum2D(ll xLo, ll xHi, ll yLo, ll yHi)
        : xLo(xLo), xHi(xHi), yLo(yLo), yHi(yHi), W(xHi - xLo), H(yHi - yLo),
          xLeft(64, 0), xRight(64, 0), xTree(64, 0) {
        if (xLo > xHi || yLo > yHi) throw invalid_argument("OnlineRectAddRectSum2D: needs xLo <= xHi and yLo <= yHi");
        yLeft.assign(64, 0), yRight.assign(64, 0), s.assign(64, array<L, 4>{0, 0, 0, 0});
    }

    // a new node is the next unused slot (already blank); a full array doubles
    LEETCODE_NO_SANITIZE int newX() {
        if (xUsed == (int)xLeft.size())
            xLeft.resize(2 * xUsed, 0), xRight.resize(2 * xUsed, 0), xTree.resize(2 * xUsed, 0);
        return xUsed++;
    }

    LEETCODE_NO_SANITIZE int newY() {
        if (yUsed == (int)yLeft.size()) {
            size_t n = 2 * (size_t)yUsed;
            yLeft.resize(n, 0), yRight.resize(n, 0), s.resize(n, array<L, 4>{0, 0, 0, 0});
        }
        return yUsed++;
    }

    // a mark of d at (x, y), counted from (xLo, yLo)
    LEETCODE_NO_SANITIZE void mark(ll x, ll y, L d) {
        L dx = d * x, dy = d * y, dxy = dx * y;
        int p = 1;
        for (ll lo = 0, hi = W;;) {
            if (!xTree[p]) { int made = newY(); xTree[p] = made; }
            int q = xTree[p];
            for (ll ylo = 0, yhi = H;;) {
                s[q][0] += d, s[q][1] += dx, s[q][2] += dy, s[q][3] += dxy;
                if (ylo == yhi) break;
                ll mid = ylo + (yhi - ylo) / 2;
                if (y <= mid) {
                    if (!yLeft[q]) { int made = newY(); yLeft[q] = made; }
                    q = yLeft[q], yhi = mid;
                } else {
                    if (!yRight[q]) { int made = newY(); yRight[q] = made; }
                    q = yRight[q], ylo = mid + 1;
                }
            }
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
    }

    // the y-tree rooted at q: adds its sums over y <= Y to acc
    LEETCODE_NO_SANITIZE void colsPrefix(int q, ll Y, array<L, 4>& acc) const {
        for (ll ylo = 0, yhi = H; q;) {
            if (yhi <= Y) {
                for (int i = 0; i < 4; i++) acc[i] += s[q][i];
                return;
            }
            ll mid = ylo + (yhi - ylo) / 2;
            if (Y <= mid) q = yLeft[q], yhi = mid;
            else {
                if (yLeft[q])
                    for (int i = 0; i < 4; i++) acc[i] += s[yLeft[q]][i];
                q = yRight[q], ylo = mid + 1;
            }
        }
    }

    // the sum of the cells with x <= X and y <= Y, counted from (xLo, yLo) (X, Y in -1..W, -1..H)
    LEETCODE_NO_SANITIZE L prefix(ll X, ll Y) const {
        if (X < 0 || Y < 0) return 0;
        array<L, 4> acc{0, 0, 0, 0};
        int p = 1;
        for (ll lo = 0, hi = W; p;) {
            if (hi <= X) {
                colsPrefix(xTree[p], Y, acc);
                break;
            }
            ll mid = lo + (hi - lo) / 2;
            if (X <= mid) p = xLeft[p], hi = mid;
            else {
                if (xLeft[p]) colsPrefix(xTree[xLeft[p]], Y, acc);
                p = xRight[p], lo = mid + 1;
            }
        }
        L a = acc[0], b = acc[1], c = acc[2], e = acc[3];
        return (L)(X + 1) * (Y + 1) * a - (L)(Y + 1) * b - (L)(X + 1) * c + e;
    }

    LEETCODE_NO_SANITIZE void add(ll x1, ll y1, ll x2, ll y2, T v) {
        total += (L)v * (x2 - x1 + 1) * (y2 - y1 + 1);
        ll a = x1 - xLo, b = x2 - xLo + 1, c = y1 - yLo, e = y2 - yLo + 1;
        mark(a, c, v);
        if (b <= W) mark(b, c, -(L)v);  // (a mark past the range never reaches a query)
        if (e <= H) mark(a, e, -(L)v);
        if (b <= W && e <= H) mark(b, e, v);
    }

    LEETCODE_NO_SANITIZE L sumOf(ll x1, ll y1, ll x2, ll y2) const {
        ll a = x1 - xLo - 1, b = x2 - xLo, c = y1 - yLo - 1, e = y2 - yLo;
        return prefix(b, e) - prefix(a, e) - prefix(b, c) + prefix(a, c);
    }

    // O(log^2 U) -- adds v to every cell with x1 <= x <= x2 and y1 <= y <= y2; needs xLo <= x1 <= x2 <= xHi and yLo <=
    // y1 <= y2 <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rectAdd(ll x1, ll y1, ll x2, ll y2, T v) {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectAdd: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        add(x1, y1, x2, y2, v);
    }

    // O(log^2 U) -- adds v to the cell (x, y); needs xLo <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointAdd: needs xLo <= x <= xHi and yLo <= y <= yHi");
        add(x, y, x, y, v);
    }

    // O(log^2 U) -- the value at (x, y); needs xLo <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return (T)sumOf(x, y, x, y);
    }

    // O(log^2 U) -- sum of the cells with x1 <= x <= x2 and y1 <= y <= y2; needs xLo <= x1 <= x2 <= xHi and yLo <= y1
    // <= y2 <= yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rectSum(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectSum: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return (T)sumOf(x1, y1, x2, y2);
    }

    // O(1) -- sum of every cell
    LEETCODE_NO_SANITIZE T sumAll() const { return (T)total; }

    // O(log^2 U) -- sum of the cells with x <= the given x and y <= the given y; needs xLo <= x <= xHi and yLo <= y <=
    // yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T sumLteLte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("sumLteLte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        x -= xLo, y -= yLo;
        return (T)(prefix(x, y));
    }

    // O(log^2 U) -- sum of the cells with x <= the given x and y >= the given y; needs xLo <= x <= xHi and yLo <= y <=
    // yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T sumLteGte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("sumLteGte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        x -= xLo, y -= yLo;
        return (T)(prefix(x, H) - prefix(x, y - 1));
    }

    // O(log^2 U) -- sum of the cells with x >= the given x and y <= the given y; needs xLo <= x <= xHi and yLo <= y <=
    // yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T sumGteLte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("sumGteLte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        x -= xLo, y -= yLo;
        return (T)(prefix(W, y) - prefix(x - 1, y));
    }

    // O(log^2 U) -- sum of the cells with x >= the given x and y >= the given y; needs xLo <= x <= xHi and yLo <= y <=
    // yHi, else throws out_of_range
    LEETCODE_NO_SANITIZE T sumGteGte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("sumGteGte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        x -= xLo, y -= yLo;
        return (T)(total - prefix(x - 1, H) - prefix(W, y - 1) + prefix(x - 1, y - 1));
    }
};
