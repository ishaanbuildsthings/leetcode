// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/isRBS-pointAssign-pointGet-rangeAssign/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll isRBS pointAssign pointGet rangeAssign
// @data-structure-type: lazy-seg-tree
// @letters: same
// @complexities:
//   getAll: N
//   isRBS: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeAssign: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: sm[4*N] mn[4*N]
//   tags: asg[4*N]
//   other: none
//   note: the characters aren't stored: a node's +-1s say them

// Bracket sequence with RANGE ASSIGN: isRBS(l, r) asks whether s[l..r] is a regular (balanced) bracket sequence. With
// open = +1 and close = -1, s[l..r] is regular iff its total is 0 and no prefix of it dips below 0. Each node keeps
// (sum, min prefix sum) of its range, prefixes including the empty one; two halves combine as sum = L.sum + R.sum,
// minPre = min(L.minPre, L.sum + R.minPre). An assigned node of k slots is all +k or all -k. Recursive lazy tree over
// 4N slots; the characters themselves are not stored (a +1 reads back as openChar, a -1 as closeChar). All indices
// 0-based, ranges inclusive.
// T: char (or any type: openChar / closeChar are the ones that open / close).
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
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct LazyBracketTree {
    int n;
    T oc, cc;
    HotVector<int> sm, mn;  // per node: sum of its +-1s, min prefix sum (the empty prefix counts)
    HotVector<signed char> asg;  // pending assign: +1 / -1, 0 for none

    // O(N) -- brackets: the sequence, e.g. vector<char>(str.begin(), str.end()); openChar / closeChar: the characters
    // that open / close ('(' / ')' unless you pass e.g. '[' / ']'); a character that isn't openChar counts as (and
    // reads back as) closeChar
    explicit LazyBracketTree(const vector<T>& brackets, T openChar = T('('), T closeChar = T(')'))
        : n((int)brackets.size()), oc(openChar), cc(closeChar) {
        sm.assign(4 * max(1, n), 0);
        mn.assign(4 * max(1, n), 0);
        asg.assign(4 * max(1, n), 0);
        if (n) build(1, 0, n - 1, brackets);
    }

    // O(N) -- the whole sequence, as characters
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        vector<T> out;
        out.reserve(n);
        if (n) collect(1, 0, n - 1, out);
        return out;
    }

    // O(logN) -- is brackets[l..r] a regular bracket sequence (balanced, never closing more than it opened)?; needs
    // 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE bool isRBS(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("isRBS: needs 0 <= l <= r < n");
        int s = 0, m = 0;
        fold(1, 0, n - 1, l, r, s, m);
        return s == 0 && m >= 0;
    }

    // O(logN) -- brackets[i] = ch; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T ch) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        set(1, 0, n - 1, i, ch == oc ? 1 : -1);
    }

    // O(logN) -- brackets[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int x = 1, lo = 0, hi = n - 1;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            push(x, lo, mid, hi);
            if (i <= mid) x = 2 * x, hi = mid;
            else x = 2 * x + 1, lo = mid + 1;
        }
        return sm[x] > 0 ? oc : cc;
    }

    // O(logN) -- brackets[i] = ch for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, T ch) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        update(1, 0, n - 1, l, r, ch == oc ? 1 : -1);
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE void build(int x, int lo, int hi, const vector<T>& s) {
        if (lo == hi) {
            int v = s[lo] == oc ? 1 : -1;
            sm[x] = v, mn[x] = min(v, 0);
            return;
        }
        int mid = (lo + hi) / 2;
        build(2 * x, lo, mid, s), build(2 * x + 1, mid + 1, hi, s);
        pull(x);
    }

    LEETCODE_NO_SANITIZE void pull(int x) {
        int l = 2 * x, r = 2 * x + 1;
        sm[x] = sm[l] + sm[r], mn[x] = min(mn[l], sm[l] + mn[r]);
    }

    LEETCODE_NO_SANITIZE void assign(int x, int k, int v) {  // node x (k slots) becomes all v (+1 or -1)
        int t = v * k;
        sm[x] = t, mn[x] = min(t, 0), asg[x] = v;
    }

    LEETCODE_NO_SANITIZE void push(int x, int lo, int mid, int hi) {  // hand x's pending tags to its children
        if (asg[x]) assign(2 * x, mid - lo + 1, asg[x]), assign(2 * x + 1, hi - mid, asg[x]), asg[x] = 0;
    }

    LEETCODE_NO_SANITIZE void update(int x, int lo, int hi, int l, int r, int v) {  // v: assign +-1, or 0 for a flip
        if (l <= lo && hi <= r) {
            assign(x, hi - lo + 1, v);
            return;
        }
        int mid = (lo + hi) / 2;
        push(x, lo, mid, hi);
        if (l <= mid) update(2 * x, lo, mid, l, r, v);
        if (r > mid) update(2 * x + 1, mid + 1, hi, l, r, v);
        pull(x);
    }

    LEETCODE_NO_SANITIZE void set(int x, int lo, int hi, int i, int v) {
        if (lo == hi) {
            sm[x] = v, mn[x] = min(v, 0);
            return;
        }
        int mid = (lo + hi) / 2;
        push(x, lo, mid, hi);
        if (i <= mid) set(2 * x, lo, mid, i, v);
        else set(2 * x + 1, mid + 1, hi, i, v);
        pull(x);
    }

    // s, m: sum and min prefix of everything left of this part; this part gets folded in
    LEETCODE_NO_SANITIZE void fold(int x, int lo, int hi, int l, int r, int& s, int& m) {
        if (l <= lo && hi <= r) {
            m = min(m, s + mn[x]), s += sm[x];
            return;
        }
        int mid = (lo + hi) / 2;
        push(x, lo, mid, hi);
        if (l <= mid) fold(2 * x, lo, mid, l, r, s, m);
        if (r > mid) fold(2 * x + 1, mid + 1, hi, l, r, s, m);
    }

    LEETCODE_NO_SANITIZE void collect(int x, int lo, int hi, vector<T>& out) {
        if (lo == hi) {
            out.push_back(sm[x] > 0 ? oc : cc);
            return;
        }
        int mid = (lo + hi) / 2;
        push(x, lo, mid, hi);
        collect(2 * x, lo, mid, out), collect(2 * x + 1, mid + 1, hi, out);
    }
};
