// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/seg-tree-sum-min-hash-pre-suf-best-alt/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll hashAll isPalindrome leftmostLtX leftmostLteX leftmostPrefixSumGtX leftmostPrefixSumGteX longestPalCenteredAtI longestPalCenteredAtIPlusOne maxAltSubseqSum maxPrefixSum maxSubarraySum maxSuffixSum minAll pointAdd pointAssign pointChmax pointChmin pointGet rangeHash rangeHashReversed rangeMin rangeSum rangesEqual rightmostLtX rightmostLteX rightmostSuffixSumGtX rightmostSuffixSumGteX sumAll
// @data-structure-type: seg-tree
// @complexities:
//   getAll: N
//   isPalindrome: log(N)
//   leftmostLtX: log(N)
//   leftmostLteX: log(N)
//   leftmostPrefixSumGtX: log(N)
//   leftmostPrefixSumGteX: log(N)
//   maxAltSubseqSum: log(N)
//   maxPrefixSum: log(N)
//   maxSubarraySum: log(N)
//   maxSuffixSum: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeHash: log(N)
//   rangeHashReversed: log(N)
//   rangeMin: log(N)
//   rangeSum: log(N)
//   rangesEqual: log(N)
//   rightmostLtX: log(N)
//   rightmostLteX: log(N)
//   rightmostSuffixSumGtX: log(N)
//   rightmostSuffixSumGteX: log(N)
//   longestPalCenteredAtI: log^2(N)
//   longestPalCenteredAtIPlusOne: log^2(N)
//   hashAll: log(N)
//   sumAll: log(N)
//   minAll: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: sm[2*N] mn[2*N] fh[2*N] bh[2*N] pre[2*N] suf[2*N] best[2*N] a00[2*N] a01[2*N] a10[2*N] a11[2*N]
//   tags: none
//   other: PW[1*log(N)]
//   note: leaves [n, 2n) hold each value's own aggregates; hash powers are per level (a covering node of level s has 2^s leaves)

// Segment tree with composable aggregates (2N iterative): point updates and range queries in O(logN); each node keeps
// its sum, its min, its forward / backward hash (and B^size), its best prefix sum, its best suffix sum, its best
// subarray sum, its best alternating (+ - + ...) subsequence sum for each start / end sign over its range. All
// indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing qualifies. Leaves tree[n..2n); a node
// used by a query or update is a perfect subtree of 2^s leaves (s = its level); an update rewrites a leaf, then its
// ancestors.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)
    int n, h;
    vector<S> sm;
    vector<T> mn;
    vector<U64> fh;
    vector<U64> bh;
    vector<S> pre;
    vector<S> suf;
    vector<S> best;
    vector<S> a00;
    vector<S> a01;
    vector<S> a10;
    vector<S> a11;
    vector<U64> PW;  // PW[s] = B^(2^s): per level

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
    // range hashes: mod the prime 2^61 - 1, with a base picked at random each run (so no test can be built against it)
    static constexpr unsigned long long HP = (1ULL << 61) - 1;
    static unsigned long long HB() {
        static unsigned long long b = (1ULL << 40) + rnd() % (HP - (1ULL << 41));
        return b;
    }
    static unsigned long long hmul(unsigned long long a, unsigned long long b) {
        __uint128_t c = (__uint128_t)a * b;
        unsigned long long r = (unsigned long long)(c & HP) + (unsigned long long)(c >> 61);
        r = (r & HP) + (r >> 61);
        return r >= HP ? r - HP : r;
    }
    static unsigned long long hadd(unsigned long long a, unsigned long long b) {
        return a + b >= HP ? a + b - HP : a + b;
    }
    static unsigned long long hraw(T v) {  // v as a residue (what an add changes a hash by, per position)
        long long r = (long long)v % (long long)HP;
        return r < 0 ? (unsigned long long)(r + (long long)HP) : (unsigned long long)r;
    }
    static unsigned long long hval(T v) {  // the hash of value v: v + an offset random per run, so no common value is 0
        static unsigned long long off = 1 + rnd() % (HP - 1);
        return hadd(hraw(v), off);
    }

    // O(N) -- arr: the initial array (non-empty)
    explicit SegTree(const vector<T>& arr) : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0) {
        sm.assign(2 * n, 0);
        mn.assign(2 * n, T(0));
        fh.assign(2 * n, 0);
        bh.assign(2 * n, 0);
        pre.assign(2 * n, 0);
        suf.assign(2 * n, 0);
        best.assign(2 * n, 0);
        a00.assign(2 * n, 0);
        a01.assign(2 * n, 0);
        a10.assign(2 * n, 0);
        a11.assign(2 * n, 0);
        for (int i = 0; i < n; i++) setLeaf(n + i, arr[i]);
        PW.assign(1, HB());
        while ((int)PW.size() <= h) PW.push_back(hmul(PW.back(), PW.back()));
        for (int x = n - 1; x > 0; x--) {
            int s = 0;
            for (int y = x; y < n; y <<= 1) s++;  // (x's level: down its left edge to the leaves)
            pull(x, s);
        }
    }

    // O(N) -- the whole array
    vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = leaf(n + i);
        return out;
    }

    // O(logN) -- is a[l..r] a palindrome (its two hashes agree); needs 0 <= l <= r < n, else throws out_of_range
    bool isPalindrome(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("isPalindrome: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 f = 0, b = 0, p = 1;
        for (int i = 0; i < c; i++) {
            f = hadd(hmul(f, PW[ls[i]]), fh[ns[i]]), b = hadd(hmul(bh[ns[i]], p), b), p = hmul(p, PW[ls[i]]);
        }
        return f == b;
    }

    // O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    int leftmostLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostLtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mn[t] < x)) continue;
            while (t < n) t = mn[2 * t] < x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    int leftmostLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostLteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mn[t] <= x)) continue;
            while (t < n) t = mn[2 * t] <= x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (a walk pruned by best prefix sums); needs
    // 0 <= l <= r < n, else throws out_of_range
    int leftmostPrefixSumGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostPrefixSumGtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (acc + pre[t] > S(x)) {
                while (t < n) {
                    if (acc + pre[2 * t] > S(x)) t = 2 * t;
                    else acc += sm[2 * t], t = 2 * t + 1;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1 (a walk pruned by best prefix sums); needs
    // 0 <= l <= r < n, else throws out_of_range
    int leftmostPrefixSumGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostPrefixSumGteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (acc + pre[t] >= S(x)) {
                while (t < n) {
                    if (acc + pre[2 * t] >= S(x)) t = 2 * t;
                    else acc += sm[2 * t], t = 2 * t + 1;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // O(logN) -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]; needs 0 <= l <= r < n, else
    // throws out_of_range
    S maxAltSubseqSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("maxAltSubseqSum: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        array<S, 4> a{a00[ns[0]], a01[ns[0]], a10[ns[0]], a11[ns[0]]};
        for (int i = 1; i < c; i++) a = altJoin(a, {a00[ns[i]], a01[ns[i]], a10[ns[i]], a11[ns[i]]});
        return max(a[0], a[1]);
    }

    // O(logN) -- max of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    S maxPrefixSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("maxPrefixSum: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = pre[ns[0]], acc = sm[ns[0]];
        for (int i = 1; i < c; i++) res = max(res, acc + pre[ns[i]]), acc += sm[ns[i]];
        return res;
    }

    // O(logN) -- max sum of a non-empty contiguous subarray of a[l..r]; needs 0 <= l <= r < n, else throws
    // out_of_range
    S maxSubarraySum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("maxSubarraySum: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = best[ns[0]], q = suf[ns[0]];  // (q: the best sum ending at the right edge so far)
        for (int i = 1; i < c; i++) {
            int t = ns[i];
            res = max({res, best[t], q + pre[t]}), q = max(suf[t], sm[t] + q);
        }
        return res;
    }

    // O(logN) -- max of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    S maxSuffixSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("maxSuffixSum: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = suf[ns[c - 1]], acc = sm[ns[c - 1]];
        for (int i = c - 2; i >= 0; i--) res = max(res, acc + suf[ns[i]]), acc += sm[ns[i]];
        return res;
    }

    // O(logN) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, T(leaf(p) + v)), rebuild(p);
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, v), rebuild(p);
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, max(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, min(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n;
        return leaf(p);
    }

    // O(logN) -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    // 0 <= l <= r < n, else throws out_of_range
    U64 rangeHash(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeHash: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 res = 0;
        for (int i = 0; i < c; i++) res = hadd(hmul(res, PW[ls[i]]), fh[ns[i]]);
        return res;
    }

    // O(logN) -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs 0 <= l <= r < n, else
    // throws out_of_range
    U64 rangeHashReversed(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeHashReversed: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 res = 0, p = 1;
        for (int i = 0; i < c; i++) res = hadd(hmul(bh[ns[i]], p), res), p = hmul(p, PW[ls[i]]);  // (in front)
        return res;
    }

    // O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeMin(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMin: needs 0 <= l <= r < n");
        T res = numeric_limits<T>::max();
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res = min(res, mn[lo++]);
            if (hi & 1) res = min(res, mn[--hi]);
        }
        return res;
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        S res = S(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res += sm[lo++];
            if (hi & 1) res += sm[--hi];
        }
        return res;
    }

    // O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    // 0 <= l1 <= r1 < n and 0 <= l2 <= r2 < n, else throws out_of_range
    bool rangesEqual(int l1, int r1, int l2, int r2) {
        if (l1 < 0 || l1 > r1 || r1 >= n || l2 < 0 || l2 > r2 || r2 >= n)
            throw out_of_range("rangesEqual: needs 0 <= l1 <= r1 < n and 0 <= l2 <= r2 < n");
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }

    // O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    int rightmostLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostLtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mn[t] < x)) continue;
            while (t < n) t = mn[2 * t + 1] < x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    int rightmostLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostLteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mn[t] <= x)) continue;
            while (t < n) t = mn[2 * t + 1] <= x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (a walk pruned by best suffix sums); needs
    // 0 <= l <= r < n, else throws out_of_range
    int rightmostSuffixSumGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostSuffixSumGtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (acc + suf[t] > S(x)) {
                while (t < n) {
                    if (acc + suf[2 * t + 1] > S(x)) t = 2 * t + 1;
                    else acc += sm[2 * t + 1], t = 2 * t;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // O(logN) -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1 (a walk pruned by best suffix sums); needs
    // 0 <= l <= r < n, else throws out_of_range
    int rightmostSuffixSumGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostSuffixSumGteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (acc + suf[t] >= S(x)) {
                while (t < n) {
                    if (acc + suf[2 * t + 1] >= S(x)) t = 2 * t + 1;
                    else acc += sm[2 * t + 1], t = 2 * t;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // O(log^2(N)) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)): a binary search on
    // its radius, log N calls of isPalindrome; needs 0 <= i < n, else throws out_of_range
    pair<long long, long long> longestPalCenteredAtI(long long i) {
        long long len = n;
        if (i < 0 || i >= len) throw out_of_range("longestPalCenteredAtI: needs 0 <= i < n");
        long long lo = 0, hi = min(i, len - 1 - i);
        while (lo < hi) {
            long long mid = (lo + hi + 1) / 2;
            if (isPalindrome(i - mid, i + mid)) lo = mid;
            else hi = mid - 1;
        }
        return {i - lo, i + lo};
    }

    // O(log^2(N)) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1, i), the empty
    // range, when there is none (so also for i = n - 1): a binary search on its radius, log N calls of isPalindrome;
    // needs 0 <= i < n, else throws out_of_range
    pair<long long, long long> longestPalCenteredAtIPlusOne(long long i) {
        long long len = n;
        if (i < 0 || i >= len) throw out_of_range("longestPalCenteredAtIPlusOne: needs 0 <= i < n");
        long long lo = 0, hi = min(i + 1, len - 1 - i);
        while (lo < hi) {
            long long mid = (lo + hi + 1) / 2;
            if (isPalindrome(i - mid + 1, i + mid)) lo = mid;
            else hi = mid - 1;
        }
        return {i - lo + 1, i + lo};
    }

    // O(log(N)) -- hash of the whole array a[0..n-1]: the same base and mod as rangeHash (shared by every structure
    // this run, so it compares with another one's hashes); needs n >= 1, else throws out_of_range
    auto hashAll() {
        if (n < 1) throw out_of_range("hashAll: needs n >= 1");
        return rangeHash(0, n - 1);
    }

    // O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

    // O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else throws out_of_range
    auto minAll() {
        if (n < 1) throw out_of_range("minAll: needs n >= 1");
        return rangeMin(0, n - 1);
    }

    // ---- internals ----

    // A's part, then B's: the best alternating sums by (start sign, end sign) = (++, +-, -+, --)
    static array<S, 4> altJoin(const array<S, 4>& A, const array<S, 4>& B) {
        return {max({A[0], B[0], A[0] + B[2], A[1] + B[0]}), max({A[1], B[1], A[0] + B[3], A[1] + B[1]}),
                max({A[2], B[2], A[2] + B[2], A[3] + B[0]}), max({A[3], B[3], A[2] + B[3], A[3] + B[1]})};
    }

    void setLeaf(int p, T v) {  // leaf p holds v alone
        sm[p] = S(v), mn[p] = v, fh[p] = hval(v), bh[p] = hval(v), pre[p] = S(v), suf[p] = S(v), best[p] = S(v),
        a00[p] = S(v), a01[p] = NEG, a10[p] = NEG, a11[p] = -S(v);
    }

    T leaf(int p) const { return T(sm[p]); }  // the value at leaf p

    void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = 2 * x, b = 2 * x + 1;
        pre[x] = max(pre[a], sm[a] + pre[b]);
        suf[x] = max(suf[b], sm[b] + suf[a]);
        best[x] = max({best[a], best[b], suf[a] + pre[b]});
        sm[x] = sm[a] + sm[b];
        mn[x] = min(mn[a], mn[b]);
        fh[x] = hadd(hmul(fh[a], PW[s - 1]), fh[b]), bh[x] = hadd(hmul(bh[b], PW[s - 1]), bh[a]);
        array<S, 4> c = altJoin({a00[a], a01[a], a10[a], a11[a]}, {a00[b], a01[b], a10[b], a11[b]});
        a00[x] = c[0], a01[x] = c[1], a10[x] = c[2], a11[x] = c[3];
    }

    void rebuild(int p) {  // recompute every ancestor of leaf p
        for (int s = 1; p > 1; s++) p >>= 1, pull(p, s);
    }

    int cover(int l, int r, int* ns, int* ls) {  // the nodes covering a[l..r] left to right (ns) and their levels (ls)
        int c = 0, rc = 0, rn[32], rl[32];
        for (int lo = l + n, hi = r + n + 1, s = 0; lo < hi; lo >>= 1, hi >>= 1, s++) {
            if (lo & 1) ns[c] = lo++, ls[c++] = s;
            if (hi & 1) rn[rc] = --hi, rl[rc++] = s;
        }
        while (rc) rc--, ns[c] = rn[rc], ls[c++] = rl[rc];
        return c;
    }
};
