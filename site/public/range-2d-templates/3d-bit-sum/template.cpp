// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/3d-bit-sum/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: boxSum pointAdd pointAssign pointChmax pointChmin pointGet sumAll
// @data-structure-type: BIT
// @input: grid-3d
// @complexities:
//   boxSum: log(X)*log(Y)*log(Z)
//   pointAdd: log(X)*log(Y)*log(Z)
//   pointAssign: log(X)*log(Y)*log(Z)
//   pointChmax: log(X)*log(Y)*log(Z)
//   pointChmin: log(X)*log(Y)*log(Z)
//   pointGet: 1
//   sumAll: 1
//   build: X*Y*Z
// @memory:
//   layout: none
//   node: sm[1*X*Y*Z]
//   tags: none
//   other: vals[1*X*Y*Z]
//   note: the Fenwick tree is (X + 1) by (Y + 1) by (Z + 1), flat, 1-based

// 3D Fenwick tree (sum): point updates and any-box sums on an X x Y x Z grid, O(log X * log Y * log Z) each, with an
// eighth of a 3D segment tree's memory. A box is eight prefix queries added and subtracted. Every cell starts at 0.
// Coordinates are 0-based and boxes are inclusive: x1..x2, y1..y2, z1..z2.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T).
template <typename T>
struct Fenwick3D {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int X, Y, Z, SY, SZ;
    vector<S> sm;
    vector<T> vals;
    S total = 0;

    // O(X*Y*Z) -- X by Y by Z, every cell 0; needs X >= 1, Y >= 1 and Z >= 1, else throws invalid_argument
    Fenwick3D(int X, int Y, int Z) : X(X), Y(Y), Z(Z), SY(Y + 1), SZ(Z + 1) {
        if (X < 1 || Y < 1 || Z < 1) throw invalid_argument("Fenwick3D: needs X >= 1, Y >= 1 and Z >= 1");
        sm.assign((size_t)(X + 1) * SY * SZ, 0);
        vals.assign((size_t)X * Y * Z, T(0));
    }

    size_t cell(int x, int y, int z) const { return ((size_t)x * Y + y) * Z + z; }

    // cell (x, y, z) becomes v
    void setCell(int x, int y, int z, T v) {
        S d = S(v) - vals[cell(x, y, z)];
        vals[cell(x, y, z)] = v;
        total += d;
        for (int i = x + 1; i <= X; i += i & -i)
            for (int j = y + 1; j <= Y; j += j & -j)
                for (int k = z + 1; k <= Z; k += k & -k) sm[((size_t)i * SY + j) * SZ + k] += d;
    }

    // sum of the cells with all three coordinates below x, y, z
    S prefix(int x, int y, int z) const {
        S res = 0;
        for (int i = x; i > 0; i &= i - 1)
            for (int j = y; j > 0; j &= j - 1)
                for (int k = z; k > 0; k &= k - 1) res += sm[((size_t)i * SY + j) * SZ + k];
        return res;
    }

    // O(1) -- the value at (x, y, z); needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    T pointGet(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointGet: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        return vals[cell(x, y, z)];
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes v; needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else
    // throws out_of_range
    void pointAssign(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointAssign: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        setCell(x, y, z, v);
    }

    // O(log X * log Y * log Z) -- adds v to the cell at (x, y, z); needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else
    // throws out_of_range
    void pointAdd(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointAdd: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        setCell(x, y, z, T(vals[cell(x, y, z)] + v));
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes max(itself, v); needs 0 <= x < X, 0 <= y < Y and 0 <=
    // z <
    // Z, else throws out_of_range
    void pointChmax(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointChmax: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        if (v > vals[cell(x, y, z)]) setCell(x, y, z, v);
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes min(itself, v); needs 0 <= x < X, 0 <= y < Y and 0 <=
    // z <
    // Z, else throws out_of_range
    void pointChmin(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointChmin: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        if (v < vals[cell(x, y, z)]) setCell(x, y, z, v);
    }

    // O(log X * log Y * log Z) -- sum of the box x1..x2, y1..y2, z1..z2; needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y
    // and 0
    // <= z1 <= z2 < Z, else throws out_of_range
    S boxSum(int x1, int y1, int z1, int x2, int y2, int z2) const {
        if (x1 < 0 || x1 > x2 || x2 >= X || y1 < 0 || y1 > y2 || y2 >= Y || z1 < 0 || z1 > z2 || z2 >= Z)
            throw out_of_range("boxSum: needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z");
        x2++, y2++, z2++;
        return prefix(x2, y2, z2) - prefix(x1, y2, z2) - prefix(x2, y1, z2) - prefix(x2, y2, z1)
             + prefix(x1, y1, z2) + prefix(x1, y2, z1) + prefix(x2, y1, z1) - prefix(x1, y1, z1);
    }

    // O(1) -- sum of the whole grid
    S sumAll() const {
        return total;
    }
};
