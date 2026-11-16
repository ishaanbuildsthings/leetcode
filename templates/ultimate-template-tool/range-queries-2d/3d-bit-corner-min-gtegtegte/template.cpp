// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/3d-bit-corner-min-gtegtegte/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: minAll minGteGteGte pointChmin
// @data-structure-type: BIT
// @input: grid-3d
// @empty-cells: yes
// @complexities:
//   minAll: 1
//   minGteGteGte: log(X)*log(Y)*log(Z)
//   pointChmin: log(X)*log(Y)*log(Z)
//   build: X*Y*Z
// @memory:
//   layout: none
//   node: tGteGteGte[1*X*Y*Z]
//   tags: none
//   other: none
//   note: one Fenwick tree per corner direction, (X + 1) by (Y + 1) by (Z + 1), flat; the >= direction is the same tree with every axis mirrored

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
LEETCODE_NO_SANITIZE_INLINE A hotMin(A a, A b) { return b < a ? b : a; }

// 3D corner min with a Fenwick tree: pointChmin at a cell and the min over every cell whose three coordinates are all
// <= (or all >=) the given ones, O(log X * log Y * log Z) each, with an eighth of a 3D segment tree's memory per
// direction. This works because values only move one way: a cell can only go down; for a cell that can move both
// ways, or for boxes that aren't corners, use the 3D segment tree. Every cell starts empty and queries only see set
// cells. Coordinates are 0-based. A min over no set cell is NO_MIN.
// T is any integer type (int, long long, ...).
template <typename T>
struct CornerMinFenwick3D {
    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set cell gives
    int X, Y, Z, SY, SZ;
    T top = NO_MIN;
    HotVector<T> tGteGteGte;

    // O(X*Y*Z) -- X by Y by Z, every cell empty; needs X >= 1, Y >= 1 and Z >= 1, else throws invalid_argument
    CornerMinFenwick3D(int X, int Y, int Z) : X(X), Y(Y), Z(Z), SY(Y + 1), SZ(Z + 1) {
        if (X < 1 || Y < 1 || Z < 1) throw invalid_argument("CornerMinFenwick3D: needs X >= 1, Y >= 1 and Z >= 1");
        tGteGteGte.assign((size_t)(X + 1) * SY * SZ, NO_MIN);
    }

    // O(log X * log Y * log Z) -- the cell at (x, y, z) becomes min(itself, v); an empty cell becomes v; needs 0 <= x <
    // X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int x, int y, int z, T v) {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("pointChmin: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        top = hotMin(top, v);
        for (int i = X - x; i <= X; i += i & -i)
            for (int j = Y - y; j <= Y; j += j & -j)
                for (int k = Z - z; k <= Z; k += k & -k) {
                    size_t at = ((size_t)i * SY + j) * SZ + k;
                    tGteGteGte[at] = hotMin(tGteGteGte[at], v);
                }
    }

    // O(log X * log Y * log Z) -- min of the set cells with all three coordinates >= x, y, z (NO_MIN if there are
    // none);
    // needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z, else throws out_of_range
    LEETCODE_NO_SANITIZE T minGteGteGte(int x, int y, int z) const {
        if (x < 0 || x >= X || y < 0 || y >= Y || z < 0 || z >= Z)
            throw out_of_range("minGteGteGte: needs 0 <= x < X, 0 <= y < Y and 0 <= z < Z");
        T res = NO_MIN;
        for (int i = X - x; i > 0; i &= i - 1)
            for (int j = Y - y; j > 0; j &= j - 1)
                for (int k = Z - z; k > 0; k &= k - 1) res = hotMin(res, tGteGteGte[((size_t)i * SY + j) * SZ + k]);
        return res;
    }

    // O(1) -- min of every set cell (NO_MIN if there are none)
    LEETCODE_NO_SANITIZE T minAll() const {
        return top;
    }
};
