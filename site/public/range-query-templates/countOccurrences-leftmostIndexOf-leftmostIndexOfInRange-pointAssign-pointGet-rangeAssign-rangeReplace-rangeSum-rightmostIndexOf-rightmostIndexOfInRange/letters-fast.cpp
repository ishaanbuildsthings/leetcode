// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAssign-pointGet-rangeAssign-rangeReplace-rangeSum-rightmostIndexOf-rightmostIndexOfInRange/letters-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countOccurrences getAll leftmostIndexOf leftmostIndexOfInRange pointAssign pointGet rangeAssign rangeReplace rightmostIndexOf rightmostIndexOfInRange
// @data-structure-type: lazy-seg-tree
// @complexities:
//   countOccurrences: U*log(N)
//   getAll: N*log(N)
//   leftmostIndexOf: U*log(N)
//   leftmostIndexOfInRange: U*log(N)
//   pointAssign: U*log(N)
//   pointGet: log(N)
//   rangeAssign: U*log(N)
//   rangeReplace: U*log(N)
//   rightmostIndexOf: U*log(N)
//   rightmostIndexOfInRange: U*log(N)
//   build: N*U
// @memory:
//   layout: pow2-iterative
//   node: t[4*N] cnt[2*N*U] sm[4*N]
//   tags: mp[2*N*U]
//   other: none
//   note: U = valHi - valLo + 1 (every value ever in the array is in [valLo, valHi]); each tag is a whole map old value -> new value, so a push costs O(U); a map is kept only while pending (handed down, its memory is reused), so mp is far below 2*N*U in practice

// Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
// operations that make sense on characters are listed.
// Lazy seg tree whose tag is a value map (mass change, CF 911G): rangeReplace(l, r, x, y) turns every x in a[l..r]
// into y, and rangeAssign(l, r, v) sets a[l..r] = v, in O(U log N), U = valHi - valLo + 1: good when the values are
// few (911G: 1..100). A pending tag is a map old value -> new value for the whole segment, so any mix of changes
// composes into one map. Each node also keeps how many times each value appears below it and its sum, for
// countOccurrences / where x first / last appears / rangeSum. All indices 0-based, ranges inclusive [l, r]; searches
// return -1 when nothing qualifies.
// T: int, long long, char, ...: the values; valLo / valHi bound every value the array will ever hold

// FAST MODE drawbacks compared with letters.cpp:
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
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct ValueMapSeg {
    using S = long long;  // sums
    // leaves t[cap + i] hold a[i] - valLo (-1: padding past n); node k's pending map for its children is
    // rows[row[k] * U ..] (row[k] = -1: none). A map row exists only while pending: pushed down, it is reused
    // cnt[k * U + v]: how many leaves below internal node k hold v (its own map already applied)
    int n, cap, lg, U;
    T valLo;
    HotVector<int> t, row, rows, freeRows, gbuf, tmp;
    HotVector<int> cnt;
    HotVector<S> sm;

    // O(N*U) -- arr: the initial array; every value it will ever hold must be in [valLo, valHi]
    ValueMapSeg(const vector<T>& arr, T valLo, T valHi) : n((int)arr.size()), cap(1), lg(0),
        U(int(valHi - valLo) + 1), valLo(valLo) {
        while (cap < n) cap <<= 1, lg++;
        t.assign(2 * cap, -1), row.assign(cap, -1), tmp.assign(U, 0);
        cnt.assign((size_t)cap * U, 0);
        sm.assign(2 * cap, 0);
        for (int i = 0; i < n; i++) {
            t[cap + i] = off(arr[i]);
            sm[cap + i] = S(arr[i]);
        }
        for (int k = cap - 1; k >= 1; k--) pull(k);
    }

    // O(1) -- the length of the array
    LEETCODE_NO_SANITIZE int size() const { return n; }

    // O(logN) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        int k = cap + i, v = t[k];
        for (k >>= 1; k; k >>= 1)  // (a map higher up is newer: apply them bottom-up)
            if (row[k] >= 0) v = rows[(size_t)row[k] * U + v];
        return T(v + valLo);
    }

    // O(U*logN) -- a[i] = v; needs valLo <= v <= valHi; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, const T& v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        int o = off(v), k = cap + i;
        for (int h = lg; h >= 1; h--) push(k >> h);
        t[k] = o;
        sm[k] = S(v);
        for (k >>= 1; k; k >>= 1) pull(k);
    }

    // O(U*logN) -- every a[i] == x with l <= i <= r becomes y; needs valLo <= y <= valHi; needs 0 <= l <= r < size(),
    // else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeReplace(int l, int r, const T& x, const T& y) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReplace: needs 0 <= l <= r < size()");
        int b = off(y);
        long long a = (long long)x - (long long)valLo;
        if (a < 0 || a >= U || a == b) return;
        update(l, r, [&](int k) { applyRep(k, (int)a, b); });
    }

    // O(U*logN) -- a[l..r] = v; needs valLo <= v <= valHi; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, const T& v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAssign: needs 0 <= l <= r < size()");
        vector<int> g(U, off(v));
        update(l, r, [&](int k) { applyMap(k, g.data()); });
    }

    // O(N log N) -- the whole current array
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = pointGet(i);
        return out;
    }

    // O(U*logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countOccurrences(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countOccurrences: needs 0 <= l <= r < size()");
        long long a = (long long)x - (long long)valLo;
        if (a < 0 || a >= U) return 0;
        int res = 0;
        cover(l, r, [&](int k) { res += countOf(k, (int)a); });
        return res;
    }

    // O(U*logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    LEETCODE_NO_SANITIZE int leftmostIndexOf(const T& x) { return find(x, 0, n - 1, true); }

    // O(U*logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    LEETCODE_NO_SANITIZE int rightmostIndexOf(const T& x) { return find(x, 0, n - 1, false); }

    // O(U*logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostIndexOfInRange(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < size()");
        return find(x, l, r, true);
    }

    // O(U*logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostIndexOfInRange(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < size()");
        return find(x, l, r, false);
    }

    // O(U*logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeSum: needs 0 <= l <= r < size()");
        S res = 0;
        cover(l, r, [&](int k) { res += sm[k]; });
        return res;
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE int off(const T& v) const {  // v's index into a map
        long long o = (long long)v - (long long)valLo;
        if (o < 0 || o >= U) throw invalid_argument("value outside [valLo, valHi]");
        return (int)o;
    }

    LEETCODE_NO_SANITIZE void applyMap(int k, const int* g) {
        // node k's segment goes through map g (newer than anything below k)
        if (k >= cap) {
            if (t[k] >= 0) {
                t[k] = g[t[k]];
                sm[k] = S(t[k] + valLo);
            }
            return;
        }
        if (row[k] < 0) {
            row[k] = newRow();
            std::copy(g, g + U, &rows[(size_t)row[k] * U]);
        } else {
            int* m = &rows[(size_t)row[k] * U];
            for (int v = 0; v < U; v++) m[v] = g[m[v]];
        }
        int* c = &cnt[(size_t)k * U];
        fill(tmp.begin(), tmp.end(), 0);
        for (int v = 0; v < U; v++) if (c[v]) tmp[g[v]] += c[v];
        copy(tmp.begin(), tmp.end(), c);
        sm[k] = 0;
        for (int v = 0; v < U; v++) if (c[v]) sm[k] += S(c[v]) * S(v + valLo);
    }

    LEETCODE_NO_SANITIZE void applyRep(int k, int a, int b) {  // every a in node k's segment becomes b
        if (k >= cap) {
            if (t[k] == a) {
                t[k] = b;
                sm[k] = S(b + valLo);
            }
            return;
        }
        if (row[k] < 0) {
            row[k] = newRow();
            iota(&rows[(size_t)row[k] * U], &rows[(size_t)row[k] * U] + U, 0);
        }
        int* m = &rows[(size_t)row[k] * U];
        for (int v = 0; v < U; v++) if (m[v] == a) m[v] = b;
        int* c = &cnt[(size_t)k * U];
        sm[k] += S(b - a) * S(c[a]);
        c[b] += c[a], c[a] = 0;
    }

    LEETCODE_NO_SANITIZE void push(int k) {  // hand node k's pending map to its children (its row is free again)
        if (row[k] < 0) return;
        gbuf.assign(rows.begin() + (size_t)row[k] * U, rows.begin() + (size_t)(row[k] + 1) * U);
        freeRows.push_back(row[k]), row[k] = -1;
        applyMap(2 * k, gbuf.data()), applyMap(2 * k + 1, gbuf.data());
    }

    LEETCODE_NO_SANITIZE int newRow() {  // a map row (a freed one if there is one)
        if (!freeRows.empty()) {
            int r = freeRows.back();
            freeRows.pop_back();
            return r;
        }
        rows.resize(rows.size() + U);
        return int(rows.size() / U) - 1;
    }

    LEETCODE_NO_SANITIZE void pull(int k) {  // recompute internal node k from its children (k has no pending map)
        int* c = &cnt[(size_t)k * U];
        if (2 * k >= cap) {
            fill(c, c + U, 0);
            for (int j = 2 * k; j <= 2 * k + 1; j++) if (t[j] >= 0) c[t[j]]++;
        } else {
            const int* p = &cnt[(size_t)(2 * k) * U];
            const int* q = &cnt[(size_t)(2 * k + 1) * U];
            for (int v = 0; v < U; v++) c[v] = p[v] + q[v];
        }
        sm[k] = sm[2 * k] + sm[2 * k + 1];
    }

    LEETCODE_NO_SANITIZE void pushAbove(int l, int r) {
        // push every map above the leaves l..r - 1 (offset by cap) down to them
        for (int h = lg; h >= 1; h--) {
            if (((l >> h) << h) != l) push(l >> h);
            if (((r >> h) << h) != r) push((r - 1) >> h);
        }
    }

    template <class F>
    LEETCODE_NO_SANITIZE void update(int l, int r, F apply) {
        l += cap, r += cap + 1;
        pushAbove(l, r);
        for (int a = l, b = r; a < b; a >>= 1, b >>= 1) {
            if (a & 1) apply(a++);
            if (b & 1) apply(--b);
        }
        for (int h = 1; h <= lg; h++) {
            if (((l >> h) << h) != l) pull(l >> h);
            if (((r >> h) << h) != r) pull((r - 1) >> h);
        }
    }

    template <class F>
    LEETCODE_NO_SANITIZE void cover(int l, int r, F visit) {
        // visit the nodes that exactly cover a[l..r], every map above them pushed
        l += cap, r += cap + 1;
        pushAbove(l, r);
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) visit(l++);
            if (r & 1) visit(--r);
        }
    }

    LEETCODE_NO_SANITIZE int countOf(int k, int a) const { return k >= cap ? int(t[k] == a) : cnt[(size_t)k * U + a]; }

    LEETCODE_NO_SANITIZE int find(const T& x, int l, int r, bool left) {
        // the first (left) / last i in [l, r] with a[i] == x, or -1
        long long a = (long long)x - (long long)valLo;
        return a < 0 || a >= U ? -1 : walk(1, 0, cap - 1, l, r, (int)a, left);
    }

    LEETCODE_NO_SANITIZE int walk(int k, int nl, int nr, int l, int r, int a, bool left) {
        if (r < nl || nr < l || !countOf(k, a)) return -1;
        if (k >= cap) return nl;
        push(k);
        int m = (nl + nr) >> 1;
        int res = left ? walk(2 * k, nl, m, l, r, a, left) : walk(2 * k + 1, m + 1, nr, l, r, a, left);
        if (res != -1) return res;
        return left ? walk(2 * k + 1, m + 1, nr, l, r, a, left) : walk(2 * k, nl, m, l, r, a, left);
    }
};
