// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/3d-seg-tree-max/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: boxMax maxAll maxGteGteGte maxLteLteLte pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: seg-tree
// @input: grid-3d
// @empty-cells: yes
// @complexities:
//   boxMax: log(X)*log(Y)*log(Z)
//   maxAll: 1
//   maxGteGteGte: log(X)*log(Y)*log(Z)
//   maxLteLteLte: log(X)*log(Y)*log(Z)
//   pointAdd: log(X)*log(Y)*log(Z)
//   pointAssign: log(X)*log(Y)*log(Z)
//   pointChmax: log(X)*log(Y)*log(Z)
//   pointChmin: log(X)*log(Y)*log(Z)
//   pointGet: 1
//   build: X*Y*Z
// @memory:
//   layout: 2n-iterative
//   node: mx[8*X*Y*Z]
//   tags: none
//   other: none
//   note: one flat array per aggregate, 2X x-nodes by 2Y y-nodes by 2Z z-nodes

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

// 3D segment tree (max): point updates and any-box queries on an X x Y x Z grid, O(log X * log Y * log Z) each. A
// bottom-up tree over x whose every node is a tree over y whose every node is a tree over z, in one flat array per
// aggregate (8 * X * Y * Z entries each, so the three sides have to be small: compress coordinates first).
// Coordinates are 0-based and boxes are inclusive: x1..x2, y1..y2, z1..z2. Every cell starts empty and queries only
// see set cells: a min / max over no set cell is NO_MAX.
// T is any integer type (int, long long, ...).
template <typename T>
struct SegTree3D {
    static constexpr T NO_MAX = numeric_limits<T>::lowest();  // the smallest value T can hold: a max over no set cell
    int X, Y, Z, SY, SZ;  // SY = 2Y y-nodes per x-node, SZ = 2Z z-nodes per y-node
    HotVector<T> mx;

    // O(X*Y*Z) -- X by Y by Z, every cell empty; needs X >= 1, Y >= 1 and Z >= 1, else throws invalid_argument
    SegTree3D(int X, int Y, int Z) : X(X), Y(Y), Z(Z), SY(2 * Y), SZ(2 * Z) {
        if (X < 1 || Y < 1 || Z < 1) throw invalid_argument("SegTree3D: needs X >= 1, Y >= 1 and Z >= 1");
        mx.assign((size_t)8 * X * Y * Z, NO_MAX);
    }

    LEETCODE_NO_SANITIZE size_t at(int px, int py, int pz) const { return ((size_t)px * SY + py) * SZ + pz; }

    // cell (x, y, z) = v, then every node above it
    LEETCODE_NO_SANITIZE void setCell(int x, int y, int z, T v) {
        for (int px = x + X; px >= 1; px >>= 1)
            for (int py = y + Y; py >= 1; py >>= 1)
                for (int pz = z + Z; pz >= 1; pz >>= 1) {
                    size_t i = at(px, py, pz);
                    if (px < X) mx[i] = hotMax(mx[at(2 * px, py, pz)], mx[at(2 * px + 1, py, pz)]);
                    else if (py < Y) mx[i] = hotMax(mx[at(px, 2 * py, pz)], mx[at(px, 2 * py + 1, pz)]);
                    else if (pz < Z) mx[i] = hotMax(mx[at(px, py, 2 * pz)], mx[at(px, py, 2 * pz + 1)]);
                    else mx[i] = v;
                }
    }

    // O(1) -- the value at (x, y, z), NO_MAX, automatically the smallest value of your type T, if the cell is empty;
    // needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointGet: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        return T(mx[at(x + X, y + Y, z + Z)]);
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes v (it may go down as well as up); needs 0 <= x < X, 0
    // <= y < Y and 0 <= z < Z, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointAssign: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        setCell(x, y, z, v);
    }

    // O(log X * log Y * log Z) -- adds v to the cell at (x, y, z); an empty cell becomes v; needs 0 <= x < X, 0 <= y <
    // Y and 0 <= z < Z, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointAdd: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        T cur = T(mx[at(x + X, y + Y, z + Z)]);
        setCell(x, y, z, cur == NO_MAX ? v : T(cur + v));
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes max(itself, v); an empty cell becomes v; needs 0 <= x <
    // X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointChmax: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        T cur = T(mx[at(x + X, y + Y, z + Z)]);
        if (cur == NO_MAX || v > cur) setCell(x, y, z, v);
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes min(itself, v); an empty cell becomes v; needs 0 <= x <
    // X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointChmin: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        T cur = T(mx[at(x + X, y + Y, z + Z)]);
        if (cur == NO_MAX || v < cur) setCell(x, y, z, v);
    }

    LEETCODE_NO_SANITIZE T maxOverZ(int px, int py, int z1, int z2) const {
        T res = NO_MAX;
        for (int lz = z1 + Z, rz = z2 + Z + 1; lz < rz; lz >>= 1, rz >>= 1) {
            if (lz & 1) res = hotMax(res, mx[at(px, py, lz++)]);
            if (rz & 1) res = hotMax(res, mx[at(px, py, --rz)]);
        }
        return res;
    }

    LEETCODE_NO_SANITIZE T maxOverYZ(int px, int y1, int z1, int y2, int z2) const {
        T res = NO_MAX;
        for (int ly = y1 + Y, ry = y2 + Y + 1; ly < ry; ly >>= 1, ry >>= 1) {
            if (ly & 1) res = hotMax(res, maxOverZ(px, ly++, z1, z2));
            if (ry & 1) res = hotMax(res, maxOverZ(px, --ry, z1, z2));
        }
        return res;
    }

    LEETCODE_NO_SANITIZE T maxOf(int x1, int y1, int z1, int x2, int y2, int z2) const {
        T res = NO_MAX;
        for (int lx = x1 + X, rx = x2 + X + 1; lx < rx; lx >>= 1, rx >>= 1) {
            if (lx & 1) res = hotMax(res, maxOverYZ(lx++, y1, z1, y2, z2));
            if (rx & 1) res = hotMax(res, maxOverYZ(--rx, y1, z1, y2, z2));
        }
        return res;
    }

    // O(log X * log Y * log Z) -- max of the set cells in the box x1..x2, y1..y2, z1..z2 (NO_MAX, automatically the
    // smallest value of your type T, if there are none); needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 <
    // Z, else throws out_of_range
    LEETCODE_NO_SANITIZE T boxMax(int x1, int y1, int z1, int x2, int y2, int z2) const {
        if (x1 < 0 || x1 > x2 || x2 >= X || y1 < 0 || y1 > y2 || y2 >= Y || z1 < 0 || z1 > z2 || z2 >= Z)
            throw out_of_range("boxMax: needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z");
        return maxOf(x1, y1, z1, x2, y2, z2);
    }

    // O(1) -- max of every set cell (NO_MAX, automatically the smallest value of your type T, if there are none)
    LEETCODE_NO_SANITIZE T maxAll() const {
        return mx[at(1, 1, 1)];
    }

    // O(log X * log Y * log Z) -- max of the set cells with all three coordinates <= x, y, z (NO_MAX, automatically the
    // smallest value of your type T, if there are none); needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T maxLteLteLte(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("maxLteLteLte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        return maxOf(0, 0, 0, x, y, z);
    }

    // O(log X * log Y * log Z) -- max of the set cells with all three coordinates >= x, y, z (NO_MAX, automatically the
    // smallest value of your type T, if there are none); needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T maxGteGteGte(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("maxGteGteGte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        return maxOf(x, y, z, X - 1, Y - 1, Z - 1);
    }
};
