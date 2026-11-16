// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/3d-seg-tree-min-max/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: boxMax boxMin maxAll maxGteGteGte maxLteLteLte minAll minGteGteGte minLteLteLte pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: seg-tree
// @input: grid-3d
// @empty-cells: yes
// @complexities:
//   boxMax: log(X)*log(Y)*log(Z)
//   boxMin: log(X)*log(Y)*log(Z)
//   maxAll: 1
//   maxGteGteGte: log(X)*log(Y)*log(Z)
//   maxLteLteLte: log(X)*log(Y)*log(Z)
//   minAll: 1
//   minGteGteGte: log(X)*log(Y)*log(Z)
//   minLteLteLte: log(X)*log(Y)*log(Z)
//   pointAdd: log(X)*log(Y)*log(Z)
//   pointAssign: log(X)*log(Y)*log(Z)
//   pointChmax: log(X)*log(Y)*log(Z)
//   pointChmin: log(X)*log(Y)*log(Z)
//   pointGet: 1
//   build: X*Y*Z
// @memory:
//   layout: 2n-iterative
//   node: mn[8*X*Y*Z] mx[8*X*Y*Z]
//   tags: none
//   other: none
//   note: one flat array per aggregate, 2X x-nodes by 2Y y-nodes by 2Z z-nodes

// 3D segment tree (min, max): point updates and any-box queries on an X x Y x Z grid, O(log X * log Y * log Z) each.
// A bottom-up tree over x whose every node is a tree over y whose every node is a tree over z, in one flat array per
// aggregate (8 * X * Y * Z entries each, so the three sides have to be small: compress coordinates first).
// Coordinates are 0-based and boxes are inclusive: x1..x2, y1..y2, z1..z2. Every cell starts empty and queries only
// see set cells: a min / max over no set cell is NO_MIN / NO_MAX.
// T is any integer type (int, long long, ...).
template <typename T>
struct SegTree3D {
    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no set cell gives
    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set cell gives
    int X, Y, Z, SY, SZ;  // SY = 2Y y-nodes per x-node, SZ = 2Z z-nodes per y-node
    vector<T> mn;
    vector<T> mx;

    // O(X*Y*Z) -- X by Y by Z, every cell empty; needs X >= 1, Y >= 1 and Z >= 1, else throws invalid_argument
    SegTree3D(int X, int Y, int Z) : X(X), Y(Y), Z(Z), SY(2 * Y), SZ(2 * Z) {
        if (X < 1 || Y < 1 || Z < 1) throw invalid_argument("SegTree3D: needs X >= 1, Y >= 1 and Z >= 1");
        mn.assign((size_t)8 * X * Y * Z, NO_MIN);
        mx.assign((size_t)8 * X * Y * Z, NO_MAX);
    }

    size_t at(int px, int py, int pz) const { return ((size_t)px * SY + py) * SZ + pz; }

    // cell (x, y, z) = v, then every node above it
    void setCell(int x, int y, int z, T v) {
        for (int px = x + X; px >= 1; px >>= 1)
            for (int py = y + Y; py >= 1; py >>= 1)
                for (int pz = z + Z; pz >= 1; pz >>= 1) {
                    size_t i = at(px, py, pz);
                    if (px < X) mn[i] = min(mn[at(2 * px, py, pz)], mn[at(2 * px + 1, py, pz)]);
                    else if (py < Y) mn[i] = min(mn[at(px, 2 * py, pz)], mn[at(px, 2 * py + 1, pz)]);
                    else if (pz < Z) mn[i] = min(mn[at(px, py, 2 * pz)], mn[at(px, py, 2 * pz + 1)]);
                    else mn[i] = v;
                    if (px < X) mx[i] = max(mx[at(2 * px, py, pz)], mx[at(2 * px + 1, py, pz)]);
                    else if (py < Y) mx[i] = max(mx[at(px, 2 * py, pz)], mx[at(px, 2 * py + 1, pz)]);
                    else if (pz < Z) mx[i] = max(mx[at(px, py, 2 * pz)], mx[at(px, py, 2 * pz + 1)]);
                    else mx[i] = v;
                }
    }

    // O(1) -- the value at (x, y, z), NO_MAX if the cell is empty; needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else
    // throws out_of_range
    T pointGet(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointGet: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        return T(mx[at(x + X, y + Y, z + Z)]);
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes v (it may go down as well as up); needs 0 <= x < X, 0
    // <=
    // y < Y and 0 <= z < Z, else throws out_of_range
    void pointAssign(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointAssign: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        setCell(x, y, z, v);
    }

    // O(log X * log Y * log Z) -- adds v to the cell at (x, y, z); an empty cell becomes v; needs 0 <= x < X, 0 <= y
    // < Y
    // and 0 <= z < Z, else throws out_of_range
    void pointAdd(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointAdd: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        T cur = T(mx[at(x + X, y + Y, z + Z)]);
        setCell(x, y, z, cur == NO_MAX ? v : T(cur + v));
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes max(itself, v); an empty cell becomes v; needs 0 <= x <
    // X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    void pointChmax(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointChmax: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        T cur = T(mx[at(x + X, y + Y, z + Z)]);
        if (cur == NO_MAX || v > cur) setCell(x, y, z, v);
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes min(itself, v); an empty cell becomes v; needs 0 <= x <
    // X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    void pointChmin(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointChmin: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        T cur = T(mx[at(x + X, y + Y, z + Z)]);
        if (cur == NO_MAX || v < cur) setCell(x, y, z, v);
    }

    T minOverZ(int px, int py, int z1, int z2) const {
        T res = NO_MIN;
        for (int lz = z1 + Z, rz = z2 + Z + 1; lz < rz; lz >>= 1, rz >>= 1) {
            if (lz & 1) res = min(res, mn[at(px, py, lz++)]);
            if (rz & 1) res = min(res, mn[at(px, py, --rz)]);
        }
        return res;
    }

    T minOverYZ(int px, int y1, int z1, int y2, int z2) const {
        T res = NO_MIN;
        for (int ly = y1 + Y, ry = y2 + Y + 1; ly < ry; ly >>= 1, ry >>= 1) {
            if (ly & 1) res = min(res, minOverZ(px, ly++, z1, z2));
            if (ry & 1) res = min(res, minOverZ(px, --ry, z1, z2));
        }
        return res;
    }

    T minOf(int x1, int y1, int z1, int x2, int y2, int z2) const {
        T res = NO_MIN;
        for (int lx = x1 + X, rx = x2 + X + 1; lx < rx; lx >>= 1, rx >>= 1) {
            if (lx & 1) res = min(res, minOverYZ(lx++, y1, z1, y2, z2));
            if (rx & 1) res = min(res, minOverYZ(--rx, y1, z1, y2, z2));
        }
        return res;
    }

    // O(log X * log Y * log Z) -- min of the set cells in the box x1..x2, y1..y2, z1..z2 (NO_MIN if there are none);
    // needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z, else throws out_of_range
    T boxMin(int x1, int y1, int z1, int x2, int y2, int z2) const {
        if (x1 < 0 || x1 > x2 || x2 >= X || y1 < 0 || y1 > y2 || y2 >= Y || z1 < 0 || z1 > z2 || z2 >= Z)
            throw out_of_range("boxMin: needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z");
        return minOf(x1, y1, z1, x2, y2, z2);
    }

    // O(1) -- min of every set cell (NO_MIN if there are none)
    T minAll() const {
        return mn[at(1, 1, 1)];
    }

    // O(log X * log Y * log Z) -- min of the set cells with all three coordinates <= x, y, z (NO_MIN if there are
    // none);
    // needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    T minLteLteLte(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("minLteLteLte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        return minOf(0, 0, 0, x, y, z);
    }

    // O(log X * log Y * log Z) -- min of the set cells with all three coordinates >= x, y, z (NO_MIN if there are
    // none);
    // needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    T minGteGteGte(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("minGteGteGte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        return minOf(x, y, z, X - 1, Y - 1, Z - 1);
    }

    T maxOverZ(int px, int py, int z1, int z2) const {
        T res = NO_MAX;
        for (int lz = z1 + Z, rz = z2 + Z + 1; lz < rz; lz >>= 1, rz >>= 1) {
            if (lz & 1) res = max(res, mx[at(px, py, lz++)]);
            if (rz & 1) res = max(res, mx[at(px, py, --rz)]);
        }
        return res;
    }

    T maxOverYZ(int px, int y1, int z1, int y2, int z2) const {
        T res = NO_MAX;
        for (int ly = y1 + Y, ry = y2 + Y + 1; ly < ry; ly >>= 1, ry >>= 1) {
            if (ly & 1) res = max(res, maxOverZ(px, ly++, z1, z2));
            if (ry & 1) res = max(res, maxOverZ(px, --ry, z1, z2));
        }
        return res;
    }

    T maxOf(int x1, int y1, int z1, int x2, int y2, int z2) const {
        T res = NO_MAX;
        for (int lx = x1 + X, rx = x2 + X + 1; lx < rx; lx >>= 1, rx >>= 1) {
            if (lx & 1) res = max(res, maxOverYZ(lx++, y1, z1, y2, z2));
            if (rx & 1) res = max(res, maxOverYZ(--rx, y1, z1, y2, z2));
        }
        return res;
    }

    // O(log X * log Y * log Z) -- max of the set cells in the box x1..x2, y1..y2, z1..z2 (NO_MAX if there are none);
    // needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z, else throws out_of_range
    T boxMax(int x1, int y1, int z1, int x2, int y2, int z2) const {
        if (x1 < 0 || x1 > x2 || x2 >= X || y1 < 0 || y1 > y2 || y2 >= Y || z1 < 0 || z1 > z2 || z2 >= Z)
            throw out_of_range("boxMax: needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z");
        return maxOf(x1, y1, z1, x2, y2, z2);
    }

    // O(1) -- max of every set cell (NO_MAX if there are none)
    T maxAll() const {
        return mx[at(1, 1, 1)];
    }

    // O(log X * log Y * log Z) -- max of the set cells with all three coordinates <= x, y, z (NO_MAX if there are
    // none);
    // needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    T maxLteLteLte(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("maxLteLteLte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        return maxOf(0, 0, 0, x, y, z);
    }

    // O(log X * log Y * log Z) -- max of the set cells with all three coordinates >= x, y, z (NO_MAX if there are
    // none);
    // needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    T maxGteGteGte(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("maxGteGteGte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        return maxOf(x, y, z, X - 1, Y - 1, Z - 1);
    }
};
