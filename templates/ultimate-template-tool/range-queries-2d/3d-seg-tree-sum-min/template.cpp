// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/3d-seg-tree-sum-min/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: boxMin boxSum minAll minGteGteGte minLteLteLte pointAdd pointAssign pointChmax pointChmin pointGet sumAll
// @data-structure-type: seg-tree
// @input: grid-3d
// @empty-cells: yes
// @complexities:
//   boxMin: log(X)*log(Y)*log(Z)
//   boxSum: log(X)*log(Y)*log(Z)
//   minAll: 1
//   minGteGteGte: log(X)*log(Y)*log(Z)
//   minLteLteLte: log(X)*log(Y)*log(Z)
//   pointAdd: log(X)*log(Y)*log(Z)
//   pointAssign: log(X)*log(Y)*log(Z)
//   pointChmax: log(X)*log(Y)*log(Z)
//   pointChmin: log(X)*log(Y)*log(Z)
//   pointGet: 1
//   sumAll: 1
//   build: X*Y*Z
// @memory:
//   layout: 2n-iterative
//   node: sm[8*X*Y*Z] mn[8*X*Y*Z]
//   tags: none
//   other: none
//   note: one flat array per aggregate, 2X x-nodes by 2Y y-nodes by 2Z z-nodes

// 3D segment tree (sum, min): point updates and any-box queries on an X x Y x Z grid, O(log X * log Y * log Z) each.
// A bottom-up tree over x whose every node is a tree over y whose every node is a tree over z, in one flat array per
// aggregate (8 * X * Y * Z entries each, so the three sides have to be small: compress coordinates first).
// Coordinates are 0-based and boxes are inclusive: x1..x2, y1..y2, z1..z2. Every cell starts empty and queries only
// see set cells: a min / max over no set cell is NO_MIN; a sum over none is 0.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T).
template <typename T>
struct SegTree3D {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set cell gives
    int X, Y, Z, SY, SZ;  // SY = 2Y y-nodes per x-node, SZ = 2Z z-nodes per y-node
    vector<S> sm;
    vector<T> mn;

    // O(X*Y*Z) -- X by Y by Z, every cell empty; needs X >= 1, Y >= 1 and Z >= 1, else throws invalid_argument
    SegTree3D(int X, int Y, int Z) : X(X), Y(Y), Z(Z), SY(2 * Y), SZ(2 * Z) {
        if (X < 1 || Y < 1 || Z < 1) throw invalid_argument("SegTree3D: needs X >= 1, Y >= 1 and Z >= 1");
        sm.assign((size_t)8 * X * Y * Z, S(0));
        mn.assign((size_t)8 * X * Y * Z, NO_MIN);
    }

    size_t at(int px, int py, int pz) const { return ((size_t)px * SY + py) * SZ + pz; }

    // cell (x, y, z) = v, then every node above it
    void setCell(int x, int y, int z, T v) {
        for (int px = x + X; px >= 1; px >>= 1)
            for (int py = y + Y; py >= 1; py >>= 1)
                for (int pz = z + Z; pz >= 1; pz >>= 1) {
                    size_t i = at(px, py, pz);
                    if (px < X) sm[i] = sm[at(2 * px, py, pz)] + sm[at(2 * px + 1, py, pz)];
                    else if (py < Y) sm[i] = sm[at(px, 2 * py, pz)] + sm[at(px, 2 * py + 1, pz)];
                    else if (pz < Z) sm[i] = sm[at(px, py, 2 * pz)] + sm[at(px, py, 2 * pz + 1)];
                    else sm[i] = v;
                    if (px < X) mn[i] = min(mn[at(2 * px, py, pz)], mn[at(2 * px + 1, py, pz)]);
                    else if (py < Y) mn[i] = min(mn[at(px, 2 * py, pz)], mn[at(px, 2 * py + 1, pz)]);
                    else if (pz < Z) mn[i] = min(mn[at(px, py, 2 * pz)], mn[at(px, py, 2 * pz + 1)]);
                    else mn[i] = v;
                }
    }

    // O(1) -- the value at (x, y, z), NO_MIN if the cell is empty; needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else
    // throws out_of_range
    T pointGet(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointGet: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        return T(mn[at(x + X, y + Y, z + Z)]);
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
        T cur = T(mn[at(x + X, y + Y, z + Z)]);
        setCell(x, y, z, cur == NO_MIN ? v : T(cur + v));
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes max(itself, v); an empty cell becomes v; needs 0 <= x <
    // X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    void pointChmax(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointChmax: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        T cur = T(mn[at(x + X, y + Y, z + Z)]);
        if (cur == NO_MIN || v > cur) setCell(x, y, z, v);
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes min(itself, v); an empty cell becomes v; needs 0 <= x <
    // X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    void pointChmin(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointChmin: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        T cur = T(mn[at(x + X, y + Y, z + Z)]);
        if (cur == NO_MIN || v < cur) setCell(x, y, z, v);
    }

    S sumOverZ(int px, int py, int z1, int z2) const {
        S res = S(0);
        for (int lz = z1 + Z, rz = z2 + Z + 1; lz < rz; lz >>= 1, rz >>= 1) {
            if (lz & 1) res += sm[at(px, py, lz++)];
            if (rz & 1) res += sm[at(px, py, --rz)];
        }
        return res;
    }

    S sumOverYZ(int px, int y1, int z1, int y2, int z2) const {
        S res = S(0);
        for (int ly = y1 + Y, ry = y2 + Y + 1; ly < ry; ly >>= 1, ry >>= 1) {
            if (ly & 1) res += sumOverZ(px, ly++, z1, z2);
            if (ry & 1) res += sumOverZ(px, --ry, z1, z2);
        }
        return res;
    }

    S sumOf(int x1, int y1, int z1, int x2, int y2, int z2) const {
        S res = S(0);
        for (int lx = x1 + X, rx = x2 + X + 1; lx < rx; lx >>= 1, rx >>= 1) {
            if (lx & 1) res += sumOverYZ(lx++, y1, z1, y2, z2);
            if (rx & 1) res += sumOverYZ(--rx, y1, z1, y2, z2);
        }
        return res;
    }

    // O(log X * log Y * log Z) -- sum of the set cells in the box x1..x2, y1..y2, z1..z2 (0 if there are none); needs 0
    // <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z, else throws out_of_range
    S boxSum(int x1, int y1, int z1, int x2, int y2, int z2) const {
        if (x1 < 0 || x1 > x2 || x2 >= X || y1 < 0 || y1 > y2 || y2 >= Y || z1 < 0 || z1 > z2 || z2 >= Z)
            throw out_of_range("boxSum: needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z");
        return sumOf(x1, y1, z1, x2, y2, z2);
    }

    // O(1) -- sum of every set cell (0 if there are none)
    S sumAll() const {
        return sm[at(1, 1, 1)];
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
};
