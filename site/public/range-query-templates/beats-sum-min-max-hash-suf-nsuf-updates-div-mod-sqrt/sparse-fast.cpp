// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/beats-sum-min-max-hash-suf-nsuf-updates-div-mod-sqrt/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: isPalindrome leftmostGtX leftmostGteX leftmostLtX leftmostLteX maxSuffixSum minSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorDiv rangeFloorSqrt rangeHash rangeHashReversed rangeMax rangeMin rangeMod rangeSum rangesEqual rightmostGtX rightmostGteX rightmostLtX rightmostLteX rightmostSuffixSumGtX rightmostSuffixSumGteX rightmostSuffixSumLtX rightmostSuffixSumLteX
// @data-structure-type: beats
// @complexities:
//   isPalindrome: log(U)
//   leftmostGtX: log(U)
//   leftmostGteX: log(U)
//   leftmostLtX: log(U)
//   leftmostLteX: log(U)
//   maxSuffixSum: log(U)
//   minSuffixSum: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeFloorDiv: log(U)*log(U) amortized
//   rangeFloorSqrt: log(U)*log(log(U)) amortized
//   rangeHash: log(U)
//   rangeHashReversed: log(U)
//   rangeMax: log(U)
//   rangeMin: log(U)
//   rangeMod: log(U)*log(U) amortized
//   rangeSum: log(U)
//   rangesEqual: log(U)
//   rightmostGtX: log(U)
//   rightmostGteX: log(U)
//   rightmostLtX: log(U)
//   rightmostLteX: log(U)
//   rightmostSuffixSumGtX: log(U)
//   rightmostSuffixSumGteX: log(U)
//   rightmostSuffixSumLtX: log(U)
//   rightmostSuffixSumLteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[4*log(U)] mn[4*log(U)] mx[4*log(U)] fh[4*log(U)] bh[4*log(U)] suf[4*log(U)] nsuf[4*log(U)]
//   tags: none
//   other: PW[1*log(U)] GS[1*log(U)] children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates), amortized for the shrink walks; node data per field, children L / R

// Shrink segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; range updates (rangeFloorDiv, rangeMod, rangeFloorSqrt) and range queries in O(logU), U =
// hi - lo + 1; each node keeps its sum, its min, its max, its forward / backward hash (and B^size), its best suffix
// sum, its min suffix sum over its range. Ranges inclusive [l, r]; searches return lo - 1 when nothing qualifies. The
// root covers 2^D >= U positions from lo (the ones past hi are zeros nobody reads), so a node of level s covers 2^s
// positions; children are created on demand as blocks of zeros, right before anything descends past a node. mod /
// floor div / floor sqrt walk down every node whose max still changes.
// T: int, long long, ...; sums are kept in S (long long for small T).
// FAST MODE drawbacks compared with sparse.cpp:
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
struct SparseShrinkSegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        U64 fh = 0;
        U64 bh = 0;
        S sm = 0;
        S suf = 0;
        S nsuf = 0;
        T mn = T(0);
        T mx = T(0);
        int L = 0;
        int R = 0;
    };
    HotVector<Node> nd{Node{}};  // node 0: none; node 1 is the root
    HotVector<U64> PW, GS;  // PW[s] = B^(2^s), GS[s] = 1 + B + ... + B^(2^s - 1): per level

    LEETCODE_NO_SANITIZE static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
    // range hashes: mod the prime 2^61 - 1, with a base picked at random each run (so no test can be built against it)
    static constexpr unsigned long long HP = (1ULL << 61) - 1;
    LEETCODE_NO_SANITIZE static unsigned long long HB() {
        static unsigned long long b = (1ULL << 40) + rnd() % (HP - (1ULL << 41));
        return b;
    }
    LEETCODE_NO_SANITIZE static unsigned long long hmul(unsigned long long a, unsigned long long b) {
        __uint128_t c = (__uint128_t)a * b;
        unsigned long long r = (unsigned long long)(c & HP) + (unsigned long long)(c >> 61);
        r = (r & HP) + (r >> 61);
        return r >= HP ? r - HP : r;
    }
    LEETCODE_NO_SANITIZE static unsigned long long hadd(unsigned long long a, unsigned long long b) {
        return a + b >= HP ? a + b - HP : a + b;
    }
    LEETCODE_NO_SANITIZE static unsigned long long hraw(T v) {
        // v as a residue (what an add changes a hash by, per position)
        long long r = (long long)v % (long long)HP;
        return r < 0 ? (unsigned long long)(r + (long long)HP) : (unsigned long long)r;
    }
    LEETCODE_NO_SANITIZE static unsigned long long hval(T v) {
        // the hash of value v: v + an offset random per run, so no common value is 0
        static unsigned long long off = 1 + rnd() % (HP - 1);
        return hadd(hraw(v), off);
    }

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseShrinkSegTree(long long lo, long long hi) : first(lo), last(hi),
        D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        PW.assign(1, HB()), GS.assign(1, 1);
        for (int k = 0; k < D; k++) GS.push_back(hadd(hmul(GS[k], PW[k]), GS[k])), PW.push_back(hmul(PW[k], PW[k]));
        newZero(D);
    }

    // O(logN) -- is a[l..r] a palindrome (its two hashes agree); needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE bool isPalindrome(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("isPalindrome: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 f = 0, b = 0, p = 1;
        for (int i = 0; i < c; i++) {
            f = hadd(hmul(f, PW[ls[i]]), nd[ns[i]].fh), b = hadd(hmul(nd[ns[i]].bh, p), b), p = hmul(p, PW[ls[i]]);
        }
        return f == b;
    }

    // O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostGtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostGtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mx > x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].L].mx > x) t = nd[t].L;
                else t = nd[t].R, tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the first i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostGteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostGteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mx >= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].L].mx >= x) t = nd[t].L;
                else t = nd[t].R, tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the first i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostLtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostLtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mn < x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].L].mn < x) t = nd[t].L;
                else t = nd[t].R, tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the first i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostLteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostLteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mn <= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].L].mn <= x) t = nd[t].L;
                else t = nd[t].R, tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logN) -- max of a[i] + ... + a[r] over i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE S maxSuffixSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("maxSuffixSum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = nd[ns[c - 1]].suf, acc = nd[ns[c - 1]].sm;
        for (int i = c - 2; i >= 0; i--) res = max(res, acc + nd[ns[i]].suf), acc += nd[ns[i]].sm;
        return res;
    }

    // O(logN) -- min of a[i] + ... + a[r] over i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE S minSuffixSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("minSuffixSum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = nd[ns[c - 1]].nsuf, acc = nd[ns[c - 1]].sm;
        for (int i = c - 2; i >= 0; i--) res = min(res, acc + nd[ns[i]].nsuf), acc += nd[ns[i]].sm;
        return res;
    }

    // O(logU) -- a[i] += v; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAdd: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, T(leaf(x) + v)), up(path);
    }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAssign: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, v), up(path);
    }

    // O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmax: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, max(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmin: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, min(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) {
        if (i < first || i > last) throw out_of_range("pointGet: needs lo <= i <= hi");
        int path[64];
        return leaf(leafOf(i, path));
    }

    // amortized O(logU * logU) -- a[i] //= x for i in [l, r] (values >= 0; x >= 2, x = 1 does nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeFloorDiv(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rangeFloorDiv: needs lo <= l <= r <= hi");
        if (x >= 2)
            update(1, D, first, l, r, [&](int t, int s, long long) {
                shrink(t, s, T(1), [x](T v) { return T(v / x); });
            });
    }

    // amortized O(logU * loglogU) -- a[i] = floor(sqrt(a[i])) for i in [l, r] (values >= 0); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeFloorSqrt(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeFloorSqrt: needs lo <= l <= r <= hi");
        update(1, D, first, l, r, [&](int t, int s, long long) {
            shrink(t, s, T(2), isqrtT);
        });
    }

    // O(logN) -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE U64 rangeHash(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeHash: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 res = 0;
        for (int i = 0; i < c; i++) res = hadd(hmul(res, PW[ls[i]]), nd[ns[i]].fh);
        return res;
    }

    // O(logN) -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs lo <= l <= r <= hi,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE U64 rangeHashReversed(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeHashReversed: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 res = 0, p = 1;
        for (int i = 0; i < c; i++) res = hadd(hmul(nd[ns[i]].bh, p), res), p = hmul(p, PW[ls[i]]);  // (in front)
        return res;
    }

    // O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeMax: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = numeric_limits<T>::lowest();
        for (int i = 0; i < c; i++) res = max(res, nd[ns[i]].mx);
        return res;
    }

    // O(logU) -- min of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeMin: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = numeric_limits<T>::max();
        for (int i = 0; i < c; i++) res = min(res, nd[ns[i]].mn);
        return res;
    }

    // amortized O(logU * logU) -- a[i] %= x for i in [l, r] (values >= 0, x >= 1); needs lo <= l <= r <= hi, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE void rangeMod(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rangeMod: needs lo <= l <= r <= hi");
        if (x >= 1)
            update(1, D, first, l, r, [&](int t, int s, long long) {
                shrink(t, s, x, [x](T v) { return T(v % x); });
            });
    }

    // O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        S res = S(0);
        for (int i = 0; i < c; i++) res += nd[ns[i]].sm;
        return res;
    }

    // O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    // lo <= l1 <= r1 <= hi and lo <= l2 <= r2 <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE bool rangesEqual(long long l1, long long r1, long long l2, long long r2) {
        if (l1 < first || l1 > r1 || r1 > last || l2 < first || l2 > r2 || r2 > last)
            throw out_of_range("rangesEqual: needs lo <= l1 <= r1 <= hi and lo <= l2 <= r2 <= hi");
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }

    // O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostGtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostGtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mx > x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].R].mx > x) t = nd[t].R, tl += 1LL << s;
                else t = nd[t].L;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the last i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostGteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostGteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mx >= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].R].mx >= x) t = nd[t].R, tl += 1LL << s;
                else t = nd[t].L;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the last i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostLtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostLtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mn < x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].R].mn < x) t = nd[t].R, tl += 1LL << s;
                else t = nd[t].L;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the last i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostLteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostLteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mn <= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].R].mn <= x) t = nd[t].R, tl += 1LL << s;
                else t = nd[t].L;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- last i in [l, r] with a[i] + ... + a[r] > x, or lo - 1 (a walk pruned by best suffix sums); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostSuffixSumGtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostSuffixSumGtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + nd[t].suf > S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + nd[nd[t].R].suf > S(x)) t = nd[t].R, tl += 1LL << s;
                    else acc += nd[nd[t].R].sm, t = nd[t].L;
                }
                return tl;
            }
            acc += nd[t].sm;
        }
        return first - 1;
    }

    // O(logU) -- last i in [l, r] with a[i] + ... + a[r] >= x, or lo - 1 (a walk pruned by best suffix sums); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostSuffixSumGteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostSuffixSumGteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + nd[t].suf >= S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + nd[nd[t].R].suf >= S(x)) t = nd[t].R, tl += 1LL << s;
                    else acc += nd[nd[t].R].sm, t = nd[t].L;
                }
                return tl;
            }
            acc += nd[t].sm;
        }
        return first - 1;
    }

    // O(logU) -- last i in [l, r] with a[i] + ... + a[r] < x, or lo - 1 (a walk pruned by min suffix sums); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostSuffixSumLtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostSuffixSumLtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + nd[t].nsuf < S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + nd[nd[t].R].nsuf < S(x)) t = nd[t].R, tl += 1LL << s;
                    else acc += nd[nd[t].R].sm, t = nd[t].L;
                }
                return tl;
            }
            acc += nd[t].sm;
        }
        return first - 1;
    }

    // O(logU) -- last i in [l, r] with a[i] + ... + a[r] <= x, or lo - 1 (a walk pruned by min suffix sums); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostSuffixSumLteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostSuffixSumLteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + nd[t].nsuf <= S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + nd[nd[t].R].nsuf <= S(x)) t = nd[t].R, tl += 1LL << s;
                    else acc += nd[nd[t].R].sm, t = nd[t].L;
                }
                return tl;
            }
            acc += nd[t].sm;
        }
        return first - 1;
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE int newZero(int s) {  // a new node: a block of 2^s zeros
        U64 h = hmul(hval(T(0)), GS[s]);
        Node n;
        n.L = 0, n.R = 0, n.sm = S(0), n.mn = T(0), n.mx = T(0), n.fh = h, n.bh = h, n.suf = S(0), n.nsuf = S(0);
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    LEETCODE_NO_SANITIZE void kids(int x, int s) {  // create node x's children (blocks of zeros) if it has none yet
        if (nd[x].L) return;
        int a = newZero(s - 1), b = newZero(s - 1);
        nd[x].L = a, nd[x].R = b;
    }

    // the nodes covering a[l..r] left to right: ns, their levels ls, their first indices ts
    LEETCODE_NO_SANITIZE int cover(long long l, long long r, int* ns, int* ls, long long* ts) {
        int c = 0;
        collect(1, D, first, l, r, ns, ls, ts, c);
        return c;
    }

    LEETCODE_NO_SANITIZE int cover(long long l, long long r, int* ns, int* ls) {
        long long ts[128];
        return cover(l, r, ns, ls, ts);
    }

    LEETCODE_NO_SANITIZE void collect(int x, int s, long long tl, long long l, long long r, int* ns, int* ls,
        long long* ts, int& c) {
        if (l <= tl && tl + (1LL << s) - 1 <= r) {
            ns[c] = x, ls[c] = s, ts[c++] = tl;
            return;
        }
        kids(x, s);
        long long m = tl + (1LL << (s - 1));
        if (l < m) collect(nd[x].L, s - 1, tl, l, r, ns, ls, ts, c);
        if (r >= m) collect(nd[x].R, s - 1, m, l, r, ns, ls, ts, c);
    }

    template <class F>  // f(node, level, first index) on every node covering a[l..r], then pull up
    LEETCODE_NO_SANITIZE void update(int x, int s, long long tl, long long l, long long r, const F& f) {
        if (l <= tl && tl + (1LL << s) - 1 <= r) {
            f(x, s, tl);
            return;
        }
        kids(x, s);
        long long m = tl + (1LL << (s - 1));
        if (l < m) update(nd[x].L, s - 1, tl, l, r, f);
        if (r >= m) update(nd[x].R, s - 1, m, l, r, f);
        pull(x, s);
    }

    LEETCODE_NO_SANITIZE int leafOf(long long i, int* path) {
        // the leaf holding a[i]; path: the nodes above it top-down, every tag pushed
        int x = 1;
        long long tl = first;
        for (int s = D; s > 0; s--) {
            kids(x, s);
            path[D - s] = x;
            if (i >= tl + (1LL << (s - 1))) tl += 1LL << (s - 1), x = nd[x].R;
            else x = nd[x].L;
        }
        return x;
    }

    LEETCODE_NO_SANITIZE void up(const int* path) {
        // recompute the nodes of path, deepest first (path[k] has level D - k)
        for (int k = D - 1; k >= 0; k--) pull(path[k], D - k);
    }

    // floor(sqrt(v)) for v >= 0, exact for every 64-bit value
    LEETCODE_NO_SANITIZE static T isqrtT(T v) {
        T r = (T)sqrtl((long double)v);
        while (r > 0 && (__int128)r * r > v) r--;
        while ((__int128)(r + 1) * (r + 1) <= v) r++;
        return r;
    }

    template <class F>
    LEETCODE_NO_SANITIZE void shrink(int x, int s, T lim, const F& f) {
        // every value v >= lim under node x (level s) becomes f(v)
        if (nd[x].mx < lim) return;
        if (s == 0) { setLeaf(x, f(nd[x].mx)); return; }
        kids(x, s);
        shrink(nd[x].L, s - 1, lim, f), shrink(nd[x].R, s - 1, lim, f);
        pull(x, s);
    }

    LEETCODE_NO_SANITIZE void setLeaf(int p, T v) {  // leaf p holds v alone
        nd[p].sm = S(v), nd[p].mn = v, nd[p].mx = v, nd[p].fh = hval(v), nd[p].bh = hval(v), nd[p].suf = S(v),
            nd[p].nsuf = S(v);
    }

    LEETCODE_NO_SANITIZE T leaf(int p) const { return T(nd[p].sm); }  // the value at leaf p

    LEETCODE_NO_SANITIZE void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = nd[x].L, b = nd[x].R;
        nd[x].suf = max(nd[b].suf, nd[b].sm + nd[a].suf);
        nd[x].nsuf = min(nd[b].nsuf, nd[b].sm + nd[a].nsuf);
        nd[x].sm = nd[a].sm + nd[b].sm;
        nd[x].mn = min(nd[a].mn, nd[b].mn);
        nd[x].mx = max(nd[a].mx, nd[b].mx);
        nd[x].fh = hadd(hmul(nd[a].fh, PW[s - 1]), nd[b].fh), nd[x].bh = hadd(hmul(nd[b].bh, PW[s - 1]), nd[a].bh);
    }
};
