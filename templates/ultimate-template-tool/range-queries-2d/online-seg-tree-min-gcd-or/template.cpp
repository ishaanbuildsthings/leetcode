// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-seg-tree-min-gcd-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: gcdAll minAll minGteGte minGteLte minLteGte minLteLte orAll pointAdd pointAssign pointChmax pointChmin pointGet rectGcd rectMin rectOr
// @data-structure-type: seg-tree
// @input: online
// @empty-cells: yes
// @complexities:
//   gcdAll: 1
//   minAll: 1
//   minGteGte: log^2(U)
//   minGteLte: log^2(U)
//   minLteGte: log^2(U)
//   minLteLte: log^2(U)
//   orAll: 1
//   pointAdd: log^2(U)*log(U) ?
//   pointAssign: log^2(U)*log(U) ?
//   pointChmax: log^2(U)*log(U) ?
//   pointChmin: log^2(U)*log(U) ?
//   pointGet: log(U)
//   rectGcd: log^2(U)+log(U) ?
//   rectMin: log^2(U)
//   rectOr: log^2(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mn[1*log^2(U)] gc[1*log^2(U)] orr[1*log^2(U)]
//   tags: none
//   other: yLeft[1*log^2(U)] yRight[1*log^2(U)] xLeft[1*log(U)] xRight[1*log(U)] xTree[1*log(U)]
//   note: sizes are per update: it makes up to log U x-nodes, and a y-path of up to log U nodes in each x-node above the point

// Dynamic 2D segment tree (min, gcd, OR): point updates and any-rectangle queries over any coordinate range [xLo,
// xHi] by [yLo, yHi] (as big as +-10^18, negative is fine), with nothing known up front. O(log^2 U) per op, U = the
// size of a coordinate range, and up to log^2 U new nodes per update: the heaviest option. When every point that will
// be updated can be listed before the first call, the points-known templates are much lighter. A segment tree over x
// whose nodes are made only where touched, each owning a segment tree over y made the same way. Rectangles are
// inclusive: x1..x2 by y1..y2. Every cell starts empty and queries only see cells that have been set: a min / max
// over no set cell is NO_MIN; a gcd / OR over none is 0.
// T is any integer type (int, long long, ...). Coordinates are long long, with xHi - xLo and yHi - yLo below 2^63.
template <typename T>
struct DynamicSegTree2D {
    using ll = long long;
    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set cell gives
    ll xLo, xHi, yLo, yHi;
    // x-node 0 = nothing there, 1 = the root; xTree = an x-node's own y-tree (its root)
    vector<int> xLeft, xRight, xTree;
    vector<int> yLeft, yRight;  // y-node 0 = nothing there: its aggregates are what an untouched range gives
    vector<T> mn;
    vector<T> gc;
    vector<T> orr;

    static T gcdOf(T a, T b) { return std::gcd(a, b); }

    // O(1) -- every cell of [xLo, xHi] by [yLo, yHi] empty; needs xLo <= xHi and yLo <= yHi, else throws
    // invalid_argument
    DynamicSegTree2D(ll xLo, ll xHi, ll yLo, ll yHi)
        : xLo(xLo), xHi(xHi), yLo(yLo), yHi(yHi), xLeft(2, 0), xRight(2, 0), xTree(2, 0), yLeft(1, 0), yRight(1, 0) {
        if (xLo > xHi || yLo > yHi) throw invalid_argument("DynamicSegTree2D: needs xLo <= xHi and yLo <= yHi");
        mn.assign(1, NO_MIN);
        gc.assign(1, T(0));
        orr.assign(1, T(0));
    }

    int newX() {
        xLeft.push_back(0), xRight.push_back(0), xTree.push_back(0);
        return (int)xLeft.size() - 1;
    }

    int newY() {
        yLeft.push_back(0), yRight.push_back(0);
        mn.push_back(NO_MIN);
        gc.push_back(T(0));
        orr.push_back(T(0));
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
        T vMin = v;  // this aggregate over row y of the x-node being written
        T vGcd = v;  // this aggregate over row y of the x-node being written
        T vOr = v;  // this aggregate over row y of the x-node being written
        int below = 0;  // the x-node just written (a child of the next one up)
        for (int i = depth - 1; i >= 0; i--) {
            p = path[i];
            if (below) {
                // the other child: what does it hold at y?
                int other = findY(xTree[xLeft[p] == below ? xRight[p] : xLeft[p]], y);
                vMin = min(vMin, mn[other]);
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
            mn[q] = vMin;
            gc[q] = vGcd;
            orr[q] = vOr;
            for (int j = ydepth - 1; j >= 0; j--) {
                q = ypath[j];
                mn[q] = min(mn[yLeft[q]], mn[yRight[q]]);
                gc[q] = gcdOf(gc[yLeft[q]], gc[yRight[q]]);
                orr[q] = orr[yLeft[q]] | orr[yRight[q]];
            }
        }
    }

    // O(log U) -- the value at (x, y), NO_MIN if the cell is empty; needs xLo <= x <= xHi and yLo <= y <= yHi, else
    // throws out_of_range
    T pointGet(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi");
        return T(mn[findCell(x, y)]);
    }

    // O(log^2 U) gcds -- the cell at (x, y) becomes v (it may go down as well as up); needs xLo <= x <= xHi and yLo
    // <= y
    // <= yHi, else throws out_of_range
    void pointAssign(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointAssign: needs xLo <= x <= xHi and yLo <= y <= yHi");
        setCell(x, y, v);
    }

    // O(log^2 U) gcds -- adds v to the cell at (x, y); an empty cell becomes v; needs xLo <= x <= xHi and yLo <= y <=
    // yHi, else throws out_of_range
    void pointAdd(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointAdd: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T cur = T(mn[findCell(x, y)]);
        setCell(x, y, cur == NO_MIN ? v : T(cur + v));
    }

    // O(log^2 U) gcds -- the cell at (x, y) becomes max(itself, v); an empty cell becomes v; needs xLo <= x <= xHi and
    // yLo <= y <= yHi, else throws out_of_range
    void pointChmax(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointChmax: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T cur = T(mn[findCell(x, y)]);
        if (cur == NO_MIN || v > cur) setCell(x, y, v);
    }

    // O(log^2 U) gcds -- the cell at (x, y) becomes min(itself, v); an empty cell becomes v; needs xLo <= x <= xHi and
    // yLo <= y <= yHi, else throws out_of_range
    void pointChmin(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi)
            throw out_of_range("pointChmin: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T cur = T(mn[findCell(x, y)]);
        if (cur == NO_MIN || v < cur) setCell(x, y, v);
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

    void gcdOverY(int q, ll lo, ll hi, ll y1, ll y2, T& res) const {
        if (q && !(y1 <= lo && hi <= y2)) {
            ll mid = lo + (hi - lo) / 2;
            if (y1 <= mid) gcdOverY(yLeft[q], lo, mid, y1, y2, res);
            if (y2 > mid) gcdOverY(yRight[q], mid + 1, hi, y1, y2, res);
            return;
        }
        res = gcdOf(res, gc[q]);
    }

    void gcdOverX(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T& res) const {
        if (p && !(x1 <= lo && hi <= x2)) {
            ll mid = lo + (hi - lo) / 2;
            if (x1 <= mid) gcdOverX(xLeft[p], lo, mid, x1, y1, x2, y2, res);
            if (x2 > mid) gcdOverX(xRight[p], mid + 1, hi, x1, y1, x2, y2, res);
            return;
        }
        // this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
        gcdOverY(xTree[p], yLo, yHi, y1, y2, res);
    }

    T gcdOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = T(0);
        gcdOverX(1, xLo, xHi, x1, y1, x2, y2, res);
        return res;
    }

    // O(log^2 U + log U) -- gcd of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (0 if there are none); needs
    // xLo <=
    // x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range
    T rectGcd(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectGcd: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return gcdOf(x1, y1, x2, y2);
    }

    // O(1) -- gcd of every set cell (0 if there are none)
    T gcdAll() const {
        return gcdOf(gc[xTree[1]], T(0));
    }

    void orOverY(int q, ll lo, ll hi, ll y1, ll y2, T& res) const {
        if (q && !(y1 <= lo && hi <= y2)) {
            ll mid = lo + (hi - lo) / 2;
            if (y1 <= mid) orOverY(yLeft[q], lo, mid, y1, y2, res);
            if (y2 > mid) orOverY(yRight[q], mid + 1, hi, y1, y2, res);
            return;
        }
        res |= orr[q];
    }

    void orOverX(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T& res) const {
        if (p && !(x1 <= lo && hi <= x2)) {
            ll mid = lo + (hi - lo) / 2;
            if (x1 <= mid) orOverX(xLeft[p], lo, mid, x1, y1, x2, y2, res);
            if (x2 > mid) orOverX(xRight[p], mid + 1, hi, x1, y1, x2, y2, res);
            return;
        }
        // this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
        orOverY(xTree[p], yLo, yHi, y1, y2, res);
    }

    T orOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = T(0);
        orOverX(1, xLo, xHi, x1, y1, x2, y2, res);
        return res;
    }

    // O(log^2 U) -- OR of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (0 if there are none); needs xLo <= x1
    // <= x2
    // <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range
    T rectOr(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectOr: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        return orOf(x1, y1, x2, y2);
    }

    // O(1) -- OR of every set cell (0 if there are none)
    T orAll() const {
        return orr[xTree[1]];
    }
};
