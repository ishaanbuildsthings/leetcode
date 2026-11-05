// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/isRBS-pointAssign-pointGet/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll isRBS pointAssign pointGet
// @data-structure-type: seg-tree
// @letters: same
// @complexities:
//   getAll: N
//   isRBS: log(N)
//   pointAssign: log(N)
//   pointGet: 1
//   build: N
// @memory:
//   layout: pow2-iterative
//   node: sm[4*N] mp[4*N]
//   tags: none
//   other: s[1*N]
//   note: one (sum, min prefix sum) pair per node over 2 * size slots (size = next power of two >= n); s: the characters

// Bracket sequence with point writes: isRBS(l, r) asks whether s[l..r] is a regular (balanced) bracket sequence.
// With open = +1 and anything else = -1, s[l..r] is regular iff its total is 0 and no prefix of it dips below 0. Each
// seg tree node keeps (sum, min prefix sum) of its range; two halves combine as
//   sum = L.sum + R.sum,   minPre = min(L.minPre, L.sum + R.minPre)
// and a query folds the covering nodes left to right. Iterative over 2 * size slots (size = next power of two >= n).
// All indices 0-based, ranges inclusive. The values are the characters themselves.
// T: char (or any type: openChar is the one that opens).
// FAST MODE drawbacks compared with template.cpp:
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.
#ifdef __SSE2__
#include <immintrin.h>
#endif

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
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct BracketTree {
    int n, size;
    T openChar;
    HotVector<T> s;
    HotVector<int> sm, mp;  // per node: sum of its +-1s, min prefix sum (0 for the empty prefix)

    // O(N) -- brackets: the sequence, e.g. vector<char>(str.begin(), str.end()); openChar: the character that opens
    // ('(' unless you pass e.g. '['); every other character closes
    explicit BracketTree(const vector<T>& brackets, T openChar_ = T('('))
        : n((int)brackets.size()), size(1), openChar(openChar_), s(brackets) {
        while (size < n) size <<= 1;
        sm.assign(2 * size, 0), mp.assign(2 * size, 0);
        for (int i = 0; i < n; i++) setLeaf(i);
        for (int x = size - 1; x > 0; x--) pull(x);
    }

    // O(N) -- the whole sequence
    LEETCODE_NO_SANITIZE vector<T> getAll() const { return s; }

    // O(1) -- brackets[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return s[i];
    }

    // O(logN) -- brackets[i] = ch; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T ch) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        s[i] = ch;
        setLeaf(i);
        for (int x = (i + size) >> 1; x; x >>= 1) pull(x);
    }

    // O(logN) -- is brackets[l..r] a regular bracket sequence (balanced, never closing more than it opened)?; needs
    // 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE bool isRBS(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("isRBS: needs 0 <= l <= r < n");
        int ls = 0, lm = 0;  // (sum, min prefix) of the left part folded so far
        int rights[64], k = 0;  // the right side's nodes, folded in afterwards right to left
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) lm = min(lm, ls + mp[l]), ls += sm[l], l++;
            if (r & 1) rights[k++] = --r;
        }
        while (k--) lm = min(lm, ls + mp[rights[k]]), ls += sm[rights[k]];
        return ls == 0 && lm >= 0;
    }

    LEETCODE_NO_SANITIZE void setLeaf(int i) {
        int v = s[i] == openChar ? 1 : -1;
        sm[i + size] = v, mp[i + size] = min(v, 0);
    }

    LEETCODE_NO_SANITIZE void pull(int x) {
        sm[x] = sm[2 * x] + sm[2 * x + 1];
        mp[x] = min(mp[2 * x], sm[2 * x] + mp[2 * x + 1]);
    }
};
