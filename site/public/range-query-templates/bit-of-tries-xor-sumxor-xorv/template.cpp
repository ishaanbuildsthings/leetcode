// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/bit-of-tries-xor-sumxor-xorv/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences countXorGtK countXorGteK countXorLtK countXorLteK getAll kthSmallest kthXor largestLtX largestLteX largestXorLtK largestXorLteK maxAll maxXorAgainstX maxXorWithVGtM maxXorWithVGteM maxXorWithVInValRange maxXorWithVLtM maxXorWithVLteM minAll minXorAgainstX minXorWithVGtM minXorWithVGteM minXorWithVInValRange minXorWithVLtM minXorWithVLteM pointAssign pointGet rangeMax rangeMin rangeSum rangeXorQuery size smallestGtX smallestGteX smallestXorGtK smallestXorGteK sumXor xorGtX xorGteX xorInValRange xorLtX xorLteX
// @data-structure-type: bit-of-tries
// @complexities:
//   countGtX: log(N)*log(U)
//   countGteX: log(N)*log(U)
//   countInValRange: log(N)*log(U)
//   countLtX: log(N)*log(U)
//   countLteX: log(N)*log(U)
//   countOccurrences: log(N)*log(U)
//   countXorGtK: log(N)*log(U)
//   countXorGteK: log(N)*log(U)
//   countXorLtK: log(N)*log(U)
//   countXorLteK: log(N)*log(U)
//   getAll: N
//   kthSmallest: log(N)*log(U)
//   kthXor: log(N)*log(U)
//   largestLtX: log(N)*log(U)
//   largestLteX: log(N)*log(U)
//   largestXorLtK: log(N)*log(U)
//   largestXorLteK: log(N)*log(U)
//   maxAll: log(N)*log(U)
//   maxXorAgainstX: log(N)*log(U)
//   maxXorWithVGtM: log(N)*log(U)
//   maxXorWithVGteM: log(N)*log(U)
//   maxXorWithVInValRange: log(N)*log(U)
//   maxXorWithVLtM: log(N)*log(U)
//   maxXorWithVLteM: log(N)*log(U)
//   minAll: log(N)*log(U)
//   minXorAgainstX: log(N)*log(U)
//   minXorWithVGtM: log(N)*log(U)
//   minXorWithVGteM: log(N)*log(U)
//   minXorWithVInValRange: log(N)*log(U)
//   minXorWithVLtM: log(N)*log(U)
//   minXorWithVLteM: log(N)*log(U)
//   pointAssign: log(N)*log(U)
//   pointGet: 1
//   rangeMax: log(N)*log(U)
//   rangeMin: log(N)*log(U)
//   rangeSum: log(N)*log(U)
//   rangeXorQuery: log(N)*log(U)
//   size: 1
//   smallestGtX: log(N)*log(U)
//   smallestGteX: log(N)*log(U)
//   smallestXorGtK: log(N)*log(U)
//   smallestXorGteK: log(N)*log(U)
//   sumXor: log(N)*log(U)
//   xorGtX: log(N)*log(U)
//   xorGteX: log(N)*log(U)
//   xorInValRange: log(N)*log(U)
//   xorLtX: log(N)*log(U)
//   xorLteX: log(N)*log(U)
//   build: N*log(N)*log(U)
// @memory:
//   layout: none
//   node: L[1*N*log(N)*log(U)] R[1*N*log(N)*log(U)] C[1*N*log(N)*log(U)] X[1*N*log(N)*log(U)]
//   tags: none
//   other: root[1*N] arr[1*N] F[1*N*log(U)]
//   note: BIT over positions, each BIT node a binary trie of its block's values (U = 2^bits); nodes are never freed, so each point assign adds up to 2 log N log U of them

// a[l..r] as a multiset, asked about v ^ x over its values v, with point assigns. A Fenwick tree (BIT) over positions:
// BIT node j is a binary trie (one level per bit, highest bit first) of the values a[j - lowbit(j) .. j - 1]. The values
// of a[l..r] are the BIT prefix of r + 1 minus the prefix of l, so a query walks those ~2 log N tries down together
// (adding the first prefix's counts, subtracting the second's). Values and every x must lie in [0, 2^bits); thresholds
// (k, m, lo, hi) can be any integers. 0-indexed, inclusive.
// sumXor: a Fenwick tree per bit counting the values with that bit set.
// XOR by value: every trie node also keeps the xor of the values below it.
// The plain order statistics (counts, k-th, min / max, predecessor / successor) are the same walks with x = 0.
// T: int, long long, ....
template <typename T>
struct BitXorTries {
    int B, n;
    long long top;
    vector<T> arr;
    vector<int> root;  // root[j] = BIT node j's trie (1-indexed)
    struct Node {  // a node's fields side by side: a walk reads them together
        int L = 0, R = 0, C = 0;
        long long X = 0;
    };
    vector<Node> nd;  // node 0 = empty
    vector<vector<int>> F;  //@sumxor  F[h] = Fenwick tree counting the values with bit h set
    struct Span {  // the tries whose counts add up to a[l..r]'s values: P minus N
        vector<int> P, N;
    };

    // O(N logN logU) -- arr: the initial values, each in [0, 2^bits) (bits = 30 holds values up to 1073741823);
    // U = 2^bits
    BitXorTries(const vector<T>& a, int bits)
        : B(bits), n((int)a.size()), top((1LL << bits) - 1), arr(a), root(n + 1), nd(1) {
        F.assign(B, vector<int>(n + 1));
        for (int j = 1; j <= n; j++) root[j] = newNode();
        for (int i = 0; i < n; i++) {
            if (a[i] < 0 || (long long)a[i] > top) throw invalid_argument("BitXorTries: needs 0 <= v < 2^bits");
            add(i, a[i], 1);
        }
    }

    // O(logN logU) -- a[i] = v (0 <= v < 2^bits); needs 0 <= i < size(), else throws out_of_range (invalid_argument
    // for v)
    void pointAssign(long long i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < size()");
        if (v < 0 || (long long)v > top) throw invalid_argument("pointAssign: needs 0 <= v < 2^bits");
        if (arr[i] == v) return;
        add(i, arr[i], -1);
        add(i, v, 1);
        arr[i] = v;
    }

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(long long i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < size()");
        return arr[i];
    }

    // O(N) -- the whole array (a copy)
    vector<T> getAll() const { return arr; }

    // O(1) -- the length of the array
    long long size() const { return n; }

    // O(logN logU) -- largest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long maxXorAgainstX(long long l, long long r, long long x) const {
        Span s = span("maxXorAgainstX", l, r);
        return extreme(s, B - 1, x, 1);
    }

    // O(logN logU) -- smallest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long minXorAgainstX(long long l, long long r, long long x) const {
        Span s = span("minXorAgainstX", l, r);
        return extreme(s, B - 1, x, 0);
    }

    // O(logN logU) -- the i-th smallest of v ^ x over the values v in a[l..r], 0-indexed: kthXor(l, r, x, 0) is the
    // smallest (copies count); needs 0 <= l <= r < size() and 0 <= i <= r - l, else throws out_of_range
    long long kthXor(long long l, long long r, long long x, long long i) const {
        Span s = span("kthXor", l, r);
        if (i < 0 || i > r - l) throw out_of_range("kthXor: needs 0 <= i <= r - l");
        return kthX(s, i + 1, x);
    }

    // O(logN logU) -- how many values v in a[l..r] have v ^ x < k (k is a VALUE, not a rank); needs 0 <= l <= r < size()
    long long countXorLtK(long long l, long long r, long long x, long long k) const {
        Span s = span("countXorLtK", l, r);
        return cntLt(s, r - l + 1, k, x);
    }

    // O(logN logU) -- how many values v in a[l..r] have v ^ x <= k (k is a VALUE, not a rank); needs
    // 0 <= l <= r < size()
    long long countXorLteK(long long l, long long r, long long x, long long k) const {
        Span s = span("countXorLteK", l, r);
        return cntLt(s, r - l + 1, k + 1, x);
    }

    // O(logN logU) -- how many values v in a[l..r] have v ^ x > k (k is a VALUE, not a rank); needs 0 <= l <= r < size()
    long long countXorGtK(long long l, long long r, long long x, long long k) const {
        Span s = span("countXorGtK", l, r);
        return r - l + 1 - cntLt(s, r - l + 1, k + 1, x);
    }

    // O(logN logU) -- how many values v in a[l..r] have v ^ x >= k (k is a VALUE, not a rank); needs
    // 0 <= l <= r < size()
    long long countXorGteK(long long l, long long r, long long x, long long k) const {
        Span s = span("countXorGteK", l, r);
        return r - l + 1 - cntLt(s, r - l + 1, k, x);
    }

    // O(logN logU) -- largest v ^ x < k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    optional<long long> largestXorLtK(long long l, long long r, long long x, long long k) const {
        Span s = span("largestXorLtK", l, r);
        long long c = cntLt(s, r - l + 1, k, x);
        if (!c) return nullopt;
        return kthX(s, c, x);
    }

    // O(logN logU) -- largest v ^ x <= k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    optional<long long> largestXorLteK(long long l, long long r, long long x, long long k) const {
        Span s = span("largestXorLteK", l, r);
        long long c = cntLt(s, r - l + 1, k + 1, x);
        if (!c) return nullopt;
        return kthX(s, c, x);
    }

    // O(logN logU) -- smallest v ^ x > k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    optional<long long> smallestXorGtK(long long l, long long r, long long x, long long k) const {
        Span s = span("smallestXorGtK", l, r);
        long long c = cntLt(s, r - l + 1, k + 1, x);
        if (c > r - l) return nullopt;
        return kthX(s, c + 1, x);
    }

    // O(logN logU) -- smallest v ^ x >= k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    optional<long long> smallestXorGteK(long long l, long long r, long long x, long long k) const {
        Span s = span("smallestXorGteK", l, r);
        long long c = cntLt(s, r - l + 1, k, x);
        if (c > r - l) return nullopt;
        return kthX(s, c + 1, x);
    }

    // O(logN logU) -- sum of v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size()
    long long sumXor(long long l, long long r, long long x) const {
        span("sumXor", l, r);
        long long cnt = r - l + 1, res = 0;
        for (int h = 0; h < B; h++) {
            long long ones = 0;
            for (long long j = r + 1; j; j &= j - 1) ones += F[h][j];
            for (long long j = l; j; j &= j - 1) ones -= F[h][j];
            res += (x >> h & 1 ? cnt - ones : ones) << h;
        }
        return res;
    }

    // O(logN logU) -- largest v ^ x over the values v < m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> maxXorWithVLtM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("maxXorWithVLtM", l, r), x, 0, m - 1, 1);
    }

    // O(logN logU) -- largest v ^ x over the values v <= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> maxXorWithVLteM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("maxXorWithVLteM", l, r), x, 0, m, 1);
    }

    // O(logN logU) -- largest v ^ x over the values v > m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> maxXorWithVGtM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("maxXorWithVGtM", l, r), x, m + 1, top, 1);
    }

    // O(logN logU) -- largest v ^ x over the values v >= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> maxXorWithVGteM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("maxXorWithVGteM", l, r), x, m, top, 1);
    }

    // O(logN logU) -- smallest v ^ x over the values v < m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> minXorWithVLtM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("minXorWithVLtM", l, r), x, 0, m - 1, 0);
    }

    // O(logN logU) -- smallest v ^ x over the values v <= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> minXorWithVLteM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("minXorWithVLteM", l, r), x, 0, m, 0);
    }

    // O(logN logU) -- smallest v ^ x over the values v > m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> minXorWithVGtM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("minXorWithVGtM", l, r), x, m + 1, top, 0);
    }

    // O(logN logU) -- smallest v ^ x over the values v >= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> minXorWithVGteM(long long l, long long r, long long x, long long m) const {
        return bestIn(span("minXorWithVGteM", l, r), x, m, top, 0);
    }

    // O(logN logU) -- largest v ^ x over the values v in a[l..r] with lo <= v <= hi, or nullopt; needs
    // 0 <= l <= r < size()
    optional<long long> maxXorWithVInValRange(long long l, long long r, long long x, long long lo, long long hi) const {
        return bestIn(span("maxXorWithVInValRange", l, r), x, lo, hi, 1);
    }

    // O(logN logU) -- smallest v ^ x over the values v in a[l..r] with lo <= v <= hi, or nullopt; needs
    // 0 <= l <= r < size()
    optional<long long> minXorWithVInValRange(long long l, long long r, long long x, long long lo, long long hi) const {
        return bestIn(span("minXorWithVInValRange", l, r), x, lo, hi, 0);
    }

    // ---- plain order statistics over a[l..r] (the same walks with x = 0) ----

    // O(logN logU) -- # of values < x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long countLtX(long long l, long long r, long long x) const {
        rangeCheck("countLtX", l, r);
        return lt(l, r, x);
    }

    // O(logN logU) -- # of values <= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long countLteX(long long l, long long r, long long x) const {
        rangeCheck("countLteX", l, r);
        return lt(l, r, x + 1);
    }

    // O(logN logU) -- # of values > x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long countGtX(long long l, long long r, long long x) const {
        rangeCheck("countGtX", l, r);
        return r - l + 1 - lt(l, r, x + 1);
    }

    // O(logN logU) -- # of values >= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long countGteX(long long l, long long r, long long x) const {
        rangeCheck("countGteX", l, r);
        return r - l + 1 - lt(l, r, x);
    }

    // O(logN logU) -- # of values v in a[l..r] with lowVal <= v <= highVal (0 if lowVal > highVal); needs 0 <= l <= r < size()
    long long countInValRange(long long l, long long r, long long lowVal, long long highVal) const {
        rangeCheck("countInValRange", l, r);
        return lowVal <= highVal ? lt(l, r, highVal + 1) - lt(l, r, lowVal) : 0;
    }

    // O(logN logU) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    long long countOccurrences(long long l, long long r, long long x) const {
        rangeCheck("countOccurrences", l, r);
        return lt(l, r, x + 1) - lt(l, r, x);
    }

    // O(logN logU) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and 1 <= k <= r - l + 1,
    // else throws out_of_range
    T kthSmallest(long long l, long long r, long long k) const {
        rangeCheck("kthSmallest", l, r);
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return (T)kth(l, r, k);
    }

    // O(logN logU) -- min of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMin(long long l, long long r) const {
        rangeCheck("rangeMin", l, r);
        return (T)kth(l, r, 1);
    }

    // O(logN logU) -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMax(long long l, long long r) const {
        rangeCheck("rangeMax", l, r);
        return (T)kth(l, r, r - l + 1);
    }

    // O(logN logU) -- smallest value >= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    optional<T> smallestGteX(long long l, long long r, long long x) const {
        rangeCheck("smallestGteX", l, r);
        long long c = lt(l, r, x);
        if (c == r - l + 1) return nullopt;
        return (T)kth(l, r, c + 1);
    }

    // O(logN logU) -- smallest value > x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    optional<T> smallestGtX(long long l, long long r, long long x) const {
        rangeCheck("smallestGtX", l, r);
        long long c = lt(l, r, x + 1);
        if (c == r - l + 1) return nullopt;
        return (T)kth(l, r, c + 1);
    }

    // O(logN logU) -- largest value <= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    optional<T> largestLteX(long long l, long long r, long long x) const {
        rangeCheck("largestLteX", l, r);
        long long c = lt(l, r, x + 1);
        if (!c) return nullopt;
        return (T)kth(l, r, c);
    }

    // O(logN logU) -- largest value < x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    optional<T> largestLtX(long long l, long long r, long long x) const {
        rangeCheck("largestLtX", l, r);
        long long c = lt(l, r, x);
        if (!c) return nullopt;
        return (T)kth(l, r, c);
    }

    // O(logN logU) -- min of the whole array; throws out_of_range if it is empty
    T minAll() const {
        if (!size()) throw out_of_range("minAll: the array is empty");
        return (T)kth(0, size() - 1, 1);
    }

    // O(logN logU) -- max of the whole array; throws out_of_range if it is empty
    T maxAll() const {
        if (!size()) throw out_of_range("maxAll: the array is empty");
        return (T)kth(0, size() - 1, size());
    }

    // O(logN logU) -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long rangeSum(long long l, long long r) const {
        rangeCheck("rangeSum", l, r);
        return sumAll(l, r);
    }

    // O(logN logU) -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long rangeXorQuery(long long l, long long r) const {
        rangeCheck("rangeXorQuery", l, r);
        return xorAll(l, r);
    }

    // O(logN logU) -- xor of the values < x in a[l..r] (copies count); needs 0 <= l <= r < size(), else throws out_of_range
    long long xorLtX(long long l, long long r, long long x) const {
        rangeCheck("xorLtX", l, r);
        return xorLt(l, r, x);
    }

    // O(logN logU) -- xor of the values <= x in a[l..r] (copies count); needs 0 <= l <= r < size(), else throws out_of_range
    long long xorLteX(long long l, long long r, long long x) const {
        rangeCheck("xorLteX", l, r);
        return xorLt(l, r, x + 1);
    }

    // O(logN logU) -- xor of the values > x in a[l..r] (copies count); needs 0 <= l <= r < size(), else throws out_of_range
    long long xorGtX(long long l, long long r, long long x) const {
        rangeCheck("xorGtX", l, r);
        return xorAll(l, r) ^ xorLt(l, r, x + 1);
    }

    // O(logN logU) -- xor of the values >= x in a[l..r] (copies count); needs 0 <= l <= r < size(), else throws out_of_range
    long long xorGteX(long long l, long long r, long long x) const {
        rangeCheck("xorGteX", l, r);
        return xorAll(l, r) ^ xorLt(l, r, x);
    }

    // O(logN logU) -- xor of the values v in a[l..r] with lowVal <= v <= highVal (copies count; 0 if lowVal > highVal); needs
    // 0 <= l <= r < size()
    long long xorInValRange(long long l, long long r, long long lowVal, long long highVal) const {
        rangeCheck("xorInValRange", l, r);
        return lowVal <= highVal ? xorLt(l, r, highVal + 1) ^ xorLt(l, r, lowVal) : 0;
    }

  private:
    int newNode() {
        nd.emplace_back();
        return (int)nd.size() - 1;
    }

    // d copies of v at index i (d = -1 removes one): every BIT node covering i, and the per-bit counts
    void add(long long i, long long v, int d) {
        for (long long j = i + 1; j <= n; j += j & -j) {
            int t = root[j];
            nd[t].C += d;
            nd[t].X ^= v;
            for (int h = B - 1; h >= 0; h--) {
                int bit = v >> h & 1;
                int c = bit ? nd[t].R : nd[t].L;
                if (!c) {
                    c = newNode();
                    (bit ? nd[t].R : nd[t].L) = c;
                }
                t = c;
                nd[t].C += d;
                nd[t].X ^= v;
            }
        }
        for (int h = 0; h < B; h++)
            if (v >> h & 1)
                for (long long j = i + 1; j <= n; j += j & -j) F[h][j] += d;
    }

    void rangeCheck(const char* name, long long l, long long r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range(string(name) + ": needs 0 <= l <= r < size()");
    }

    // checks 0 <= l <= r < size(); the tries of prefix r + 1 (P) and prefix l (N)
    Span span(const char* name, long long l, long long r) const {
        rangeCheck(name, l, r);
        return tries(l, r);
    }

    Span tries(long long l, long long r) const {  // the tries of prefix r + 1 (P) and prefix l (N)
        Span s;
        for (long long j = r + 1; j; j &= j - 1) s.P.push_back(root[j]);
        for (long long j = l; j; j &= j - 1) s.N.push_back(root[j]);
        return s;
    }

    long long lt(long long l, long long r, long long k) const { return cntLt(tries(l, r), r - l + 1, k, 0); }  // # < k

    long long kth(long long l, long long r, long long k) const { return kthX(tries(l, r), k, 0); }  // k-th smallest

    long long sumAll(long long l, long long r) const { return sumXor(l, r, 0); }

    long long xorOf(const Span& s) const {
        long long res = 0;
        for (int t : s.P) res ^= nd[t].X;
        for (int t : s.N) res ^= nd[t].X;
        return res;
    }

    long long xorAll(long long l, long long r) const { return xorOf(tries(l, r)); }

    long long xorLt(long long l, long long r, long long k) const {  // xor of the values < k in a[l..r]
        if (k <= 0) return 0;
        if (k > top) return xorAll(l, r);
        Span s = tries(l, r);
        long long res = 0;
        for (int h = B - 1; h >= 0 && !s.P.empty(); h--) {
            if (k >> h & 1) {
                res ^= xorOf(down(s, 0));
                s = down(s, 1);
            } else {
                s = down(s, 0);
            }
        }
        return res;
    }

    long long cnt(const Span& s) const {
        long long c = 0;
        for (int t : s.P) c += nd[t].C;
        for (int t : s.N) c -= nd[t].C;
        return c;
    }

    Span down(const Span& s, int bit) const {  // the children for v's bit = bit (empty ones dropped)
        Span o;
        for (int t : s.P) if (int c = bit ? nd[t].R : nd[t].L) o.P.push_back(c);
        for (int t : s.N) if (int c = bit ? nd[t].R : nd[t].L) o.N.push_back(c);
        return o;
    }

    // how many values v below s (all of them: total) have v ^ x < k
    long long cntLt(Span s, long long total, long long k, long long x) const {
        if (k <= 0) return 0;
        if (k > top) return total;
        long long res = 0;
        for (int h = B - 1; h >= 0 && !s.P.empty(); h--) {
            int xb = x >> h & 1;
            if (k >> h & 1) {  // every result with bit h = 0 is < k
                res += cnt(down(s, xb));
                s = down(s, xb ^ 1);
            } else {
                s = down(s, xb);
            }
        }
        return res;
    }

    // the k-th smallest (1-indexed) v ^ x over the values below s
    long long kthX(Span s, long long k, long long x) const {
        long long res = 0;
        for (int h = B - 1; h >= 0; h--) {
            int xb = x >> h & 1;
            Span z = down(s, xb);
            long long c = cnt(z);
            if (k <= c) {
                s = std::move(z);
            } else {
                k -= c;
                s = down(s, xb ^ 1);
                res |= 1LL << h;
            }
        }
        return res;
    }

    // bits h..0 of the largest (big = 1) / smallest v ^ x below s, which holds some value
    long long extreme(Span s, int h, long long x, int big) const {
        long long res = 0;
        for (; h >= 0; h--) {
            int p = (int)(x >> h & 1) ^ big;  // the child whose result bit is big
            Span u = down(s, p);
            if (cnt(u)) {
                s = std::move(u);
                res |= (long long)big << h;
            } else {
                s = down(s, p ^ 1);
                res |= (long long)(big ^ 1) << h;
            }
        }
        return res;
    }

    // the largest (big = 1) / smallest v ^ x over the values v below s with lo <= v <= hi, or nullopt. Walks down the
    // bits lo and hi share, then splits: below lo's side only the lower bound matters, below hi's only the upper one
    optional<long long> bestIn(Span s, long long x, long long lo, long long hi, int big) const {
        lo = max(lo, 0LL), hi = min(hi, top);
        if (lo > hi) return nullopt;
        int h = B - 1;
        long long res = 0;
        for (; h >= 0 && (lo >> h & 1) == (hi >> h & 1); h--) {
            int bit = lo >> h & 1;
            s = down(s, bit);
            if (!cnt(s)) return nullopt;
            res |= (long long)(bit ^ (x >> h & 1)) << h;
        }
        if (h < 0) return res;
        long long xb = x >> h & 1;
        auto c0 = oneSide(down(s, 0), h - 1, lo, x, big, 1, res | xb << h);
        auto c1 = oneSide(down(s, 1), h - 1, hi, x, big, 0, res | (xb ^ 1) << h);
        if (!c0 || !c1) return c0 ? c0 : c1;
        return big ? max(*c0, *c1) : min(*c0, *c1);
    }

    // below s: the best v ^ x whose bits h..0 are >= (lower = 1) / <= bound's bits h..0, or nullopt; res holds the
    // result's bits above h. Along the path that matches bound, each step off it (to the side the bound allows) is a
    // free subtree: take it at once if its result bit beats the path's, else remember the deepest one
    optional<long long> oneSide(Span s, int h, long long bound, long long x, int big, int lower, long long res) const {
        if (!cnt(s)) return nullopt;
        Span f;
        int fh = -2;
        long long fres = 0;
        for (; h >= 0; h--) {
            int xb = x >> h & 1, bb = bound >> h & 1;
            if (bb != lower) {  // a free side exists: v bit = lower
                Span c = down(s, lower);
                if (cnt(c)) {
                    long long cres = res | (long long)(lower ^ xb) << h;
                    if ((lower ^ xb) == big) return cres | extreme(std::move(c), h - 1, x, big);
                    f = std::move(c), fh = h, fres = cres;
                }
            }
            s = down(s, bb);
            if (!cnt(s)) break;
            res |= (long long)(bb ^ xb) << h;
        }
        if (h < 0) return res;  // v equal to bound below here: allowed (inclusive)
        if (fh == -2) return nullopt;
        return fres | extreme(std::move(f), fh - 1, x, big);
    }
};
