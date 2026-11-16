// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/3d-bit-corner-max-gtegtegte/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: maxAll maxGteGteGte pointChmax
// @data-structure-type: BIT
// @input: grid-3d
// @empty-cells: yes
// @complexities:
//   maxAll: 1
//   maxGteGteGte: log(X)*log(Y)*log(Z)
//   pointChmax: log(X)*log(Y)*log(Z)
//   build: X*Y*Z
// @memory:
//   layout: none
//   node: tGteGteGte[1*X*Y*Z]
//   tags: none
//   other: none
//   note: one Fenwick tree per corner direction, (X + 1) by (Y + 1) by (Z + 1), flat; the >= direction is the same tree with every axis mirrored

// 3D corner max with a Fenwick tree: pointChmax at a cell and the max over every cell whose three coordinates are all
// <= (or all >=) the given ones, O(log X * log Y * log Z) each, with an eighth of a 3D segment tree's memory per
// direction. This works because values only move one way: a cell can only go up; for a cell that can move both ways,
// or for boxes that aren't corners, use the 3D segment tree. Every cell starts empty and queries only see set cells.
// Coordinates are 0-based. A max over no set cell is NO_MAX.
// T is any integer type (int, long long, ...).
template <typename T>
struct CornerMaxFenwick3D {
    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no set cell gives
    int X, Y, Z, SY, SZ;
    T top = NO_MAX;
    vector<T> tGteGteGte;

    // O(X*Y*Z) -- X by Y by Z, every cell empty; needs X >= 1, Y >= 1 and Z >= 1, else throws invalid_argument
    CornerMaxFenwick3D(int X, int Y, int Z) : X(X), Y(Y), Z(Z), SY(Y + 1), SZ(Z + 1) {
        if (X < 1 || Y < 1 || Z < 1) throw invalid_argument("CornerMaxFenwick3D: needs X >= 1, Y >= 1 and Z >= 1");
        tGteGteGte.assign((size_t)(X + 1) * SY * SZ, NO_MAX);
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes max(itself, v); an empty cell becomes v; needs 0 <= x <
    // X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    void pointChmax(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointChmax: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        top = max(top, v);
        for (int i = X - x; i <= X; i += i & -i)
            for (int j = Y - y; j <= Y; j += j & -j)
                for (int k = Z - z; k <= Z; k += k & -k) {
                    size_t at = ((size_t)i * SY + j) * SZ + k;
                    tGteGteGte[at] = max(tGteGteGte[at], v);
                }
    }

    // O(log X * log Y * log Z) -- max of the set cells with all three coordinates >= x, y, z (NO_MAX if there are
    // none);
    // needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    T maxGteGteGte(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("maxGteGteGte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        T res = NO_MAX;
        for (int i = X - x; i > 0; i &= i - 1)
            for (int j = Y - y; j > 0; j &= j - 1)
                for (int k = Z - z; k > 0; k &= k - 1) res = max(res, tGteGteGte[((size_t)i * SY + j) * SZ + k]);
        return res;
    }

    // O(1) -- max of every set cell (NO_MAX if there are none)
    T maxAll() const {
        return top;
    }
};
