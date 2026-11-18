// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/3d-bit-sum/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: boxSum pointAdd pointAssign pointChmax pointChmin pointGet sumAll sumGteGteGte sumLteLteLte
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
//   sumGteGteGte: log(X)*log(Y)*log(Z)
//   sumLteLteLte: log(X)*log(Y)*log(Z)
//   build: X*Y*Z
// @memory:
//   layout: none
//   node: sm[1*X*Y*Z]
//   tags: none
//   other: vals[1*X*Y*Z]
//   note: the Fenwick tree is (X + 1) by (Y + 1) by (Z + 1), flat, 1-based

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

// 3D Fenwick tree (sum): point updates and any-box sums on an X x Y x Z grid, O(log X * log Y * log Z) each, with an
// eighth of a 3D segment tree's memory. A box is eight prefix queries added and subtracted. Every cell starts at 0.
// Coordinates are 0-based and boxes are inclusive: x1..x2, y1..y2, z1..z2.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T).
template <typename T>
struct Fenwick3D {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int X, Y, Z, SY, SZ;
    HotVector<S> sm;
    HotVector<T> vals;
    S total = 0;

    // O(X*Y*Z) -- X by Y by Z, every cell 0; needs X >= 1, Y >= 1 and Z >= 1, else throws invalid_argument
    Fenwick3D(int X, int Y, int Z) : X(X), Y(Y), Z(Z), SY(Y + 1), SZ(Z + 1) {
        if (X < 1 || Y < 1 || Z < 1) throw invalid_argument("Fenwick3D: needs X >= 1, Y >= 1 and Z >= 1");
        sm.assign((size_t)(X + 1) * SY * SZ, 0);
        vals.assign((size_t)X * Y * Z, T(0));
    }

    LEETCODE_NO_SANITIZE size_t cell(int x, int y, int z) const { return ((size_t)x * Y + y) * Z + z; }

    // cell (x, y, z) becomes v
    LEETCODE_NO_SANITIZE void setCell(int x, int y, int z, T v) {
        S d = S(v) - vals[cell(x, y, z)];
        vals[cell(x, y, z)] = v;
        total += d;
        for (int i = x + 1; i <= X; i += i & -i)
            for (int j = y + 1; j <= Y; j += j & -j)
                for (int k = z + 1; k <= Z; k += k & -k) sm[((size_t)i * SY + j) * SZ + k] += d;
    }

    // sum of the cells with all three coordinates below x, y, z
    LEETCODE_NO_SANITIZE S prefix(int x, int y, int z) const {
        S res = 0;
        for (int i = x; i > 0; i &= i - 1)
            for (int j = y; j > 0; j &= j - 1)
                for (int k = z; k > 0; k &= k - 1) res += sm[((size_t)i * SY + j) * SZ + k];
        return res;
    }

    // O(1) -- the value at (x, y, z); needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointGet: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        return vals[cell(x, y, z)];
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes v; needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointAssign: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        setCell(x, y, z, v);
    }

    // O(log X * log Y * log Z) -- adds v to the cell at (x, y, z); needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointAdd: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        setCell(x, y, z, T(vals[cell(x, y, z)] + v));
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes max(itself, v); needs 0 <= x < X, 0 <= y < Y and 0 <= z
    // < Z, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointChmax: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        if (v > vals[cell(x, y, z)]) setCell(x, y, z, v);
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes min(itself, v); needs 0 <= x < X, 0 <= y < Y and 0 <= z
    // < Z, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointChmin: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        if (v < vals[cell(x, y, z)]) setCell(x, y, z, v);
    }

    // O(log X * log Y * log Z) -- sum of the box x1..x2, y1..y2, z1..z2; needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and
    // 0 <= z1 <= z2 < Z, else throws out_of_range
    LEETCODE_NO_SANITIZE S boxSum(int x1, int y1, int z1, int x2, int y2, int z2) const {
        if (x1 < 0 || x1 > x2 || x2 >= X || y1 < 0 || y1 > y2 || y2 >= Y || z1 < 0 || z1 > z2 || z2 >= Z)
            throw out_of_range("boxSum: needs 0 <= x1 <= x2 < X, 0 <= y1 <= y2 < Y and 0 <= z1 <= z2 < Z");
        x2++, y2++, z2++;
        return prefix(x2, y2, z2) - prefix(x1, y2, z2) - prefix(x2, y1, z2) - prefix(x2, y2, z1)
             + prefix(x1, y1, z2) + prefix(x1, y2, z1) + prefix(x2, y1, z1) - prefix(x1, y1, z1);
    }

    // O(1) -- sum of the whole grid
    LEETCODE_NO_SANITIZE S sumAll() const {
        return total;
    }

    // O(log X * log Y * log Z) -- sum of the cells with all three coordinates <= x, y, z (one prefix query); needs 0 <=
    // x < X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumLteLteLte(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("sumLteLteLte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        return prefix(x + 1, y + 1, z + 1);
    }

    // O(log X * log Y * log Z) -- sum of the cells with all three coordinates >= x, y, z (a box query, eight prefix
    // queries); needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumGteGteGte(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("sumGteGteGte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        return boxSum(x, y, z, X - 1, Y - 1, Z - 1);
    }
};
