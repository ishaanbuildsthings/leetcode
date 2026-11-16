// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-seg-tree-sum-min-max-and/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: andAll maxAll maxGteGte maxGteLte maxLteGte maxLteLte minAll minGteGte minGteLte minLteGte minLteLte pointAdd pointAssign pointChmax pointChmin pointGet rectAnd rectMax rectMin rectSum sumAll
// @data-structure-type: seg-tree
// @input: online
// @empty-cells: yes
// @complexities:
//   andAll: 1
//   maxAll: 1
//   maxGteGte: log^2(U)
//   maxGteLte: log^2(U)
//   maxLteGte: log^2(U)
//   maxLteLte: log^2(U)
//   minAll: 1
//   minGteGte: log^2(U)
//   minGteLte: log^2(U)
//   minLteGte: log^2(U)
//   minLteLte: log^2(U)
//   pointAdd: log^2(U)
//   pointAssign: log^2(U)
//   pointChmax: log^2(U)
//   pointChmin: log^2(U)
//   pointGet: log(U)
//   rectAnd: log^2(U)
//   rectMax: log^2(U)
//   rectMin: log^2(U)
//   rectSum: log^2(U)
//   sumAll: 1
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[1*log^2(U)] mn[1*log^2(U)] mx[1*log^2(U)] an[1*log^2(U)]
//   tags: none
//   other: yLeft[1*log^2(U)] yRight[1*log^2(U)] xLeft[1*log(U)] xRight[1*log(U)] xTree[1*log(U)]
//   note: sizes are per update: it makes up to log U x-nodes, and a y-path of up to log U nodes in each x-node above the point

// Dynamic 2D segment tree (sum, min, max, AND): point updates and any-rectangle queries over any coordinate range
// [xLo, xHi] by [yLo, yHi] (as big as +-10^18, negative is fine), with nothing known up front. O(log^2 U) per op, U =
// the size of a coordinate range, and up to log^2 U new nodes per update: the heaviest option. When every point that
// will be updated can be listed before the first call, the points-known templates are much lighter. A segment tree
// over x whose nodes are made only where touched, each owning a segment tree over y made the same way. Rectangles are
// inclusive: x1..x2 by y1..y2. Every cell starts empty and queries only see cells that have been set: a min / max
// over no set cell is NO_MIN / NO_MAX; a sum over none is 0; an AND over none is -1 (every bit set).
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T). Coordinates are long
// long, with xHi - xLo and yHi - yLo below 2^63.
template <typename T>
struct DynamicSegTree2D {
    using ll = long long;
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no set cell gives
    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set cell gives
    ll xLo, xHi, yLo, yHi;
    // x-node 0 = nothing there, 1 = the root; xTree = an x-node's own y-tree (its root)
    vector<int> xLeft, xRight, xTree;
    vector<int> yLeft, yRight;  // y-node 0 = nothing there: its aggregates are what an untouched range gives
    vector<S> sm;
    vector<T> mn;
    vector<T> mx;
    vector<T> an;

    // O(1) -- every cell of [xLo, xHi] by [yLo, yHi] empty; needs xLo <= xHi and yLo <= yHi, else throws
    // invalid_argument
    DynamicSegTree2D(ll xLo, ll xHi, ll yLo, ll yHi)
        : xLo(xLo), xHi(xHi), yLo(yLo), yHi(yHi), xLeft(2, 0), xRight(2, 0), xTree(2, 0), yLeft(1, 0), yRight(1, 0) {
        if (xLo > xHi || yLo > yHi) throw invalid_argument("DynamicSegTree2D: needs xLo <= xHi and yLo <= yHi");
        sm.assign(1, S(0));
        mn.assign(1, NO_MIN);
        mx.assign(1, NO_MAX);
        an.assign(1, T(-1));
    }

    int newX() {
        xLeft.push_back(0), xRight.push_back(0), xTree.push_back(0);
        return (int)xLeft.size() - 1;
    }

    int newY() {
        yLeft.push_back(0), yRight.push_back(0);
        sm.push_back(S(0));
        mn.push_back(NO_MIN);
        mx.push_back(NO_MAX);
        an.push_back(T(-1));
        return (int)yLeft.size() - 1;
    }

    // the y-node of the tree rooted at q that holds exactly y (0 if nothing was set there)
    int findY(int q, ll y) const {
        ll lo = yLo, hi = yHi;
        while (q && lo < hi) {
            ll mid = lo + (hi - lo) / 2;
            if (y <= mid) q = yLeft[q], hi = mid;
            else q = yRight[q], lo = mid + 1;
        }
        return q;
    }

    // the y-node holding exactly (x, y) (0 if nothing was set there)
    int findCell(ll x, ll y) const {
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
    void setCell(ll x, ll y, T v) {
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
        T vMin = v;  // this aggregate over row y of the x-node being written
        T vMax = v;  // this aggregate over row y of the x-node being written
        T vAnd = v;  // this aggregate over row y of the x-node being written
        int below = 0;  // the x-node just written (a child of the next one up)
        for (int i = depth - 1; i >= 0; i--) {
            p = path[i];
            if (below) {
                // the other child: what does it hold at y?
                int other = findY(xTree[xLeft[p] == below ? xRight[p] : xLeft[p]], y);
                vSum += sm[other];
                vMin = min(vMin, mn[other]);
                vMax = max(vMax, mx[other]);
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
            sm[q] = vSum;
            mn[q] = vMin;
            mx[q] = vMax;
            an[q] = vAnd;
            for (int j = ydepth - 1; j >= 0; j--) {
                q = ypath[j];
                sm[q] = sm[yLeft[q]] + sm[yRight[q]];
                mn[q] = min(mn[yLeft[q]], mn[yRight[q]]);
                mx[q] = max(mx[yLeft[q]], mx[yRight[q]]);
                an[q] = an[yLeft[q]] & an[yRight[q]];
            }
        }
    }

    // O(log U) -- the value at (x, y), NO_MAX if the cell is empty; needs xLo <= x <= xHi and yLo <= y <= yHi, else
    // throws out_of_range
    T pointGet(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return T(mx[findCell(x, y)]);
    }

    // O(log^2 U) -- the cell at (x, y) becomes v (it may go down as well as up); needs xLo <= x <= xHi and yLo <= y <=
    // yHi, else throws out_of_range
    void pointAssign(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointAssign: needs xLo <= x <= xHi and yLo <= y <= yHi");
        setCell(x, y, v);
    }

    // O(log^2 U) -- adds v to the cell at (x, y); an empty cell becomes v; needs xLo <= x <= xHi and yLo <= y <= yHi,
    // else throws out_of_range
    void pointAdd(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointAdd: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T cur = T(mx[findCell(x, y)]);
        setCell(x, y, cur == NO_MAX ? v : T(cur + v));
    }

    // O(log^2 U) -- the cell at (x, y) becomes max(itself, v); an empty cell becomes v; needs xLo <= x <= xHi and yLo
    // <=
    // y <= yHi, else throws out_of_range
    void pointChmax(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointChmax: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T cur = T(mx[findCell(x, y)]);
        if (cur == NO_MAX || v > cur) setCell(x, y, v);
    }

    // O(log^2 U) -- the cell at (x, y) becomes min(itself, v); an empty cell becomes v; needs xLo <= x <= xHi and yLo
    // <=
    // y <= yHi, else throws out_of_range
    void pointChmin(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointChmin: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T cur = T(mx[findCell(x, y)]);
        if (cur == NO_MAX || v < cur) setCell(x, y, v);
    }

    void sumOverY(int q, ll lo, ll hi, ll y1, ll y2, S& res) const {
        if (q && !(y1 <= lo && hi <= y2)) {
            ll mid = lo + (hi - lo) / 2;
            if (y1 <= mid) sumOverY(yLeft[q], lo, mid, y1, y2, res);
            if (y2 > mid) sumOverY(yRight[q], mid + 1, hi, y1, y2, res);
            return;
        }
        res += sm[q];
    }

    void sumOverX(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, S& res) const {
        if (p && !(x1 <= lo && hi <= x2)) {
            ll mid = lo + (hi - lo) / 2;
            if (x1 <= mid) sumOverX(xLeft[p], lo, mid, x1, y1, x2, y2, res);
            if (x2 > mid) sumOverX(xRight[p], mid + 1, hi, x1, y1, x2, y2, res);
            return;
        }
        // this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
        sumOverY(xTree[p], yLo, yHi, y1, y2, res);
    }

    S sumOf(ll x1, ll y1, ll x2, ll y2) const {
        S res = S(0);
        sumOverX(1, xLo, xHi, x1, y1, x2, y2, res);
        return res;
    }

    // O(log^2 U) -- sum of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (0 if there are none); needs xLo <= x1 <=
    // x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range
    S rectSum(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectSum: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return sumOf(x1, y1, x2, y2);
    }

    // O(1) -- sum of every set cell (0 if there are none)
    S sumAll() const {
        return sm[xTree[1]];
    }

    void minOverY(int q, ll lo, ll hi, ll y1, ll y2, T& res) const {
        if (q && !(y1 <= lo && hi <= y2)) {
            ll mid = lo + (hi - lo) / 2;
            if (y1 <= mid) minOverY(yLeft[q], lo, mid, y1, y2, res);
            if (y2 > mid) minOverY(yRight[q], mid + 1, hi, y1, y2, res);
            return;
        }
        res = min(res, mn[q]);
    }

    void minOverX(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T& res) const {
        if (p && !(x1 <= lo && hi <= x2)) {
            ll mid = lo + (hi - lo) / 2;
            if (x1 <= mid) minOverX(xLeft[p], lo, mid, x1, y1, x2, y2, res);
            if (x2 > mid) minOverX(xRight[p], mid + 1, hi, x1, y1, x2, y2, res);
            return;
        }
        // this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
        minOverY(xTree[p], yLo, yHi, y1, y2, res);
    }

    T minOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = NO_MIN;
        minOverX(1, xLo, xHi, x1, y1, x2, y2, res);
        return res;
    }

    // O(log^2 U) -- min of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (NO_MIN if there are none); needs xLo
    // <= x1
    // <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range
    T rectMin(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectMin: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return minOf(x1, y1, x2, y2);
    }

    // O(1) -- min of every set cell (NO_MIN if there are none)
    T minAll() const {
        return mn[xTree[1]];
    }

    // O(log^2 U) -- min of the set cells with x <= the given x and y <= the given y (NO_MIN if there are none); needs
    // xLo
    // <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    T minLteLte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("minLteLte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return minOf(xLo, yLo, x, y);
    }

    // O(log^2 U) -- min of the set cells with x <= the given x and y >= the given y (NO_MIN if there are none); needs
    // xLo
    // <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    T minLteGte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("minLteGte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return minOf(xLo, y, x, yHi);
    }

    // O(log^2 U) -- min of the set cells with x >= the given x and y <= the given y (NO_MIN if there are none); needs
    // xLo
    // <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    T minGteLte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("minGteLte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return minOf(x, yLo, xHi, y);
    }

    // O(log^2 U) -- min of the set cells with x >= the given x and y >= the given y (NO_MIN if there are none); needs
    // xLo
    // <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    T minGteGte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("minGteGte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return minOf(x, y, xHi, yHi);
    }

    void maxOverY(int q, ll lo, ll hi, ll y1, ll y2, T& res) const {
        if (q && !(y1 <= lo && hi <= y2)) {
            ll mid = lo + (hi - lo) / 2;
            if (y1 <= mid) maxOverY(yLeft[q], lo, mid, y1, y2, res);
            if (y2 > mid) maxOverY(yRight[q], mid + 1, hi, y1, y2, res);
            return;
        }
        res = max(res, mx[q]);
    }

    void maxOverX(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T& res) const {
        if (p && !(x1 <= lo && hi <= x2)) {
            ll mid = lo + (hi - lo) / 2;
            if (x1 <= mid) maxOverX(xLeft[p], lo, mid, x1, y1, x2, y2, res);
            if (x2 > mid) maxOverX(xRight[p], mid + 1, hi, x1, y1, x2, y2, res);
            return;
        }
        // this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
        maxOverY(xTree[p], yLo, yHi, y1, y2, res);
    }

    T maxOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = NO_MAX;
        maxOverX(1, xLo, xHi, x1, y1, x2, y2, res);
        return res;
    }

    // O(log^2 U) -- max of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (NO_MAX if there are none); needs xLo
    // <= x1
    // <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range
    T rectMax(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectMax: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return maxOf(x1, y1, x2, y2);
    }

    // O(1) -- max of every set cell (NO_MAX if there are none)
    T maxAll() const {
        return mx[xTree[1]];
    }

    // O(log^2 U) -- max of the set cells with x <= the given x and y <= the given y (NO_MAX if there are none); needs
    // xLo
    // <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    T maxLteLte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("maxLteLte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return maxOf(xLo, yLo, x, y);
    }

    // O(log^2 U) -- max of the set cells with x <= the given x and y >= the given y (NO_MAX if there are none); needs
    // xLo
    // <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    T maxLteGte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("maxLteGte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return maxOf(xLo, y, x, yHi);
    }

    // O(log^2 U) -- max of the set cells with x >= the given x and y <= the given y (NO_MAX if there are none); needs
    // xLo
    // <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    T maxGteLte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("maxGteLte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return maxOf(x, yLo, xHi, y);
    }

    // O(log^2 U) -- max of the set cells with x >= the given x and y >= the given y (NO_MAX if there are none); needs
    // xLo
    // <= x <= xHi and yLo <= y <= yHi, else throws out_of_range
    T maxGteGte(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("maxGteGte: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return maxOf(x, y, xHi, yHi);
    }

    void andOverY(int q, ll lo, ll hi, ll y1, ll y2, T& res) const {
        if (q && !(y1 <= lo && hi <= y2)) {
            ll mid = lo + (hi - lo) / 2;
            if (y1 <= mid) andOverY(yLeft[q], lo, mid, y1, y2, res);
            if (y2 > mid) andOverY(yRight[q], mid + 1, hi, y1, y2, res);
            return;
        }
        res &= an[q];
    }

    void andOverX(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T& res) const {
        if (p && !(x1 <= lo && hi <= x2)) {
            ll mid = lo + (hi - lo) / 2;
            if (x1 <= mid) andOverX(xLeft[p], lo, mid, x1, y1, x2, y2, res);
            if (x2 > mid) andOverX(xRight[p], mid + 1, hi, x1, y1, x2, y2, res);
            return;
        }
        // this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
        andOverY(xTree[p], yLo, yHi, y1, y2, res);
    }

    T andOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = T(-1);
        andOverX(1, xLo, xHi, x1, y1, x2, y2, res);
        return res;
    }

    // O(log^2 U) -- AND of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (-1 (every bit set) if there are none);
    // needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range
    T rectAnd(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectAnd: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return andOf(x1, y1, x2, y2);
    }

    // O(1) -- AND of every set cell (-1 (every bit set) if there are none)
    T andAll() const {
        return an[xTree[1]];
    }
};
