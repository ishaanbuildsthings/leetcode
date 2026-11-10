// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/persistent-trie-xor-mex-sumxor-sums-xorv/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append countGtX countGteX countInValRange countLtX countLteX countOccurrences countXorGtK countXorGteK countXorLtK countXorLteK getAll kthSmallest kthXor largestLtX largestLteX largestXorLtK largestXorLteK maxAll maxXorAgainstX maxXorWithVGtM maxXorWithVGteM maxXorWithVInValRange maxXorWithVLtM maxXorWithVLteM mexXor minAll minXorAgainstX minXorWithVGtM minXorWithVGteM minXorWithVInValRange minXorWithVLtM minXorWithVLteM pointGet pop rangeMax rangeMex rangeMin rangeSum rangeXorQuery size smallestGtX smallestGteX smallestXorGtK smallestXorGteK sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK sumXor xorGtX xorGteX xorInValRange xorLtX xorLteX
// @data-structure-type: persistent-trie
// @complexities:
//   append: log(U)
//   countGtX: log(U)
//   countGteX: log(U)
//   countInValRange: log(U)
//   countLtX: log(U)
//   countLteX: log(U)
//   countOccurrences: log(U)
//   countXorGtK: log(U)
//   countXorGteK: log(U)
//   countXorLtK: log(U)
//   countXorLteK: log(U)
//   getAll: N
//   kthSmallest: log(U)
//   kthXor: log(U)
//   largestLtX: log(U)
//   largestLteX: log(U)
//   largestXorLtK: log(U)
//   largestXorLteK: log(U)
//   maxAll: log(U)
//   maxXorAgainstX: log(U)
//   maxXorWithVGtM: log(U)
//   maxXorWithVGteM: log(U)
//   maxXorWithVInValRange: log(U)
//   maxXorWithVLtM: log(U)
//   maxXorWithVLteM: log(U)
//   mexXor: log(U)
//   minAll: log(U)
//   minXorAgainstX: log(U)
//   minXorWithVGtM: log(U)
//   minXorWithVGteM: log(U)
//   minXorWithVInValRange: log(U)
//   minXorWithVLtM: log(U)
//   minXorWithVLteM: log(U)
//   pointGet: 1
//   pop: 1
//   rangeMax: log(U)
//   rangeMex: log(U)
//   rangeMin: log(U)
//   rangeSum: log(U)
//   rangeXorQuery: log(U)
//   size: 1
//   smallestGtX: log(U)
//   smallestGteX: log(U)
//   smallestXorGtK: log(U)
//   smallestXorGteK: log(U)
//   sumAbsDiffToX: log(U)
//   sumGtX: log(U)
//   sumGteX: log(U)
//   sumInValRange: log(U)
//   sumKthLargestRange: log(U)
//   sumKthSmallestRange: log(U)
//   sumLargestK: log(U)
//   sumLtX: log(U)
//   sumLteX: log(U)
//   sumSmallestK: log(U)
//   sumXor: log(U)
//   xorGtX: log(U)
//   xorGteX: log(U)
//   xorInValRange: log(U)
//   xorLtX: log(U)
//   xorLteX: log(U)
//   build: N*log(U)
// @memory:
//   layout: none
//   node: L[1*N*log(U)] R[1*N*log(U)] C[1*N*log(U)] M[1*N*log(U)] S[1*N*log(U)] X[1*N*log(U)]
//   tags: none
//   other: root[1*N] arr[1*N] P[1*N*log(U)]
//   note: N = every value ever added (initial array plus each append); each adds one root-to-leaf path of log U + 1 nodes, U = 2^bits

// a[l..r] as a multiset, asked about v ^ x over its values v. A persistent binary trie over the values: one level per
// bit, highest bit first, and version p holds a[0..p-1], so the values of a[l..r] are version r + 1 minus version l
// (walk both, subtract counts). Each append adds one version. Values and every x must lie in [0, 2^bits); thresholds
// (k, m, lo, hi) can be any integers. 0-indexed, inclusive.
// mexXor: every node also keeps the smallest "last index" over the values below it (as of its version; -1 if some
// value below never appeared), so a subtree is complete inside a[l..r] exactly when that is >= l.
// sumXor: prefix counts of how many values have each bit set.
// Sums: every node also keeps the sum of the values below it.
// XOR by value: every node also keeps the xor of the values below it.
// The plain order statistics (counts, k-th, min / max, predecessor / successor) are the same walks with x = 0.
// T: int, long long, ....
template <typename T>
struct PersistentXorTrie {
    int B;
    long long top;
    vector<T> arr;
    vector<int> root;  // root[p] = version holding a[0..p-1]
    struct Node {  // a node's fields side by side: a walk reads them together
        int L = 0, R = 0, C = 0;
        int M = -1;
        long long S = 0;
        long long X = 0;
    };
    vector<Node> nd;  // node 0 = the empty trie
    vector<int> P;  // P[p * B + h] = how many of a[0..p-1] have bit h set

    // O(N log U) -- arr: the initial values (may be empty), each in [0, 2^bits) (bits = 30 holds values up to
    // 1073741823); U = 2^bits
    PersistentXorTrie(const vector<T>& a, int bits) : B(bits), top((1LL << bits) - 1), root{0}, nd(1) {
        P.assign(B, 0);
        nd.reserve(1 + a.size() * (B + 1));
        for (const T& v : a) append(v);
    }

    // O(logU) -- append v (0 <= v < 2^bits): it becomes a[n], and n grows by 1; throws invalid_argument outside that
    void append(T v) {
        if (v < 0 || (long long)v > top) throw invalid_argument("append: needs 0 <= v < 2^bits");
        root.push_back(ins(root.back(), (long long)v, (int)arr.size()));
        size_t base = P.size() - B;
        for (int h = 0; h < B; h++) P.push_back(P[base + h] + (int)((long long)v >> h & 1));
        arr.push_back(v);
    }

    // O(1) -- remove a[n-1] and return it (its nodes stay allocated); throws out_of_range if the array is empty
    T pop() {
        if (arr.empty()) throw out_of_range("pop: the array is empty");
        root.pop_back();
        P.resize(P.size() - B);
        T v = arr.back();
        arr.pop_back();
        return v;
    }

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(long long i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return arr[i];
    }

    // O(N) -- the whole array (a copy)
    vector<T> getAll() const { return arr; }

    // O(1) -- the current length of the array
    long long size() const { return (long long)arr.size(); }

    // O(logU) -- largest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long maxXorAgainstX(long long l, long long r, long long x) const {
        rangeCheck("maxXorAgainstX", l, r);
        return extreme(root[r + 1], root[l], B - 1, x, 1);
    }

    // O(logU) -- smallest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long minXorAgainstX(long long l, long long r, long long x) const {
        rangeCheck("minXorAgainstX", l, r);
        return extreme(root[r + 1], root[l], B - 1, x, 0);
    }

    // O(logU) -- the i-th smallest of v ^ x over the values v in a[l..r], 0-indexed: kthXor(l, r, x, 0) is the
    // smallest (copies count); needs 0 <= l <= r < size() and 0 <= i <= r - l, else throws out_of_range
    long long kthXor(long long l, long long r, long long x, long long i) const {
        rangeCheck("kthXor", l, r);
        if (i < 0 || i > r - l) throw out_of_range("kthXor: needs 0 <= i <= r - l");
        return kthX(l, r, i + 1, x);
    }

    // O(logU) -- how many values v in a[l..r] have v ^ x < k (k is a VALUE, not a rank); needs 0 <= l <= r < size()
    long long countXorLtK(long long l, long long r, long long x, long long k) const {
        rangeCheck("countXorLtK", l, r);
        return cntLt(l, r, k, x);
    }

    // O(logU) -- how many values v in a[l..r] have v ^ x <= k (k is a VALUE, not a rank); needs 0 <= l <= r < size()
    long long countXorLteK(long long l, long long r, long long x, long long k) const {
        rangeCheck("countXorLteK", l, r);
        return cntLt(l, r, k + 1, x);
    }

    // O(logU) -- how many values v in a[l..r] have v ^ x > k (k is a VALUE, not a rank); needs 0 <= l <= r < size()
    long long countXorGtK(long long l, long long r, long long x, long long k) const {
        rangeCheck("countXorGtK", l, r);
        return r - l + 1 - cntLt(l, r, k + 1, x);
    }

    // O(logU) -- how many values v in a[l..r] have v ^ x >= k (k is a VALUE, not a rank); needs 0 <= l <= r < size()
    long long countXorGteK(long long l, long long r, long long x, long long k) const {
        rangeCheck("countXorGteK", l, r);
        return r - l + 1 - cntLt(l, r, k, x);
    }

    // O(logU) -- largest v ^ x < k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    optional<long long> largestXorLtK(long long l, long long r, long long x, long long k) const {
        rangeCheck("largestXorLtK", l, r);
        long long c = cntLt(l, r, k, x);
        if (!c) return nullopt;
        return kthX(l, r, c, x);
    }

    // O(logU) -- largest v ^ x <= k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    optional<long long> largestXorLteK(long long l, long long r, long long x, long long k) const {
        rangeCheck("largestXorLteK", l, r);
        long long c = cntLt(l, r, k + 1, x);
        if (!c) return nullopt;
        return kthX(l, r, c, x);
    }

    // O(logU) -- smallest v ^ x > k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    optional<long long> smallestXorGtK(long long l, long long r, long long x, long long k) const {
        rangeCheck("smallestXorGtK", l, r);
        long long c = cntLt(l, r, k + 1, x);
        if (c > r - l) return nullopt;
        return kthX(l, r, c + 1, x);
    }

    // O(logU) -- smallest v ^ x >= k over the values v in a[l..r] (k is a VALUE, not a rank), or nullopt; needs
    // 0 <= l <= r < size()
    optional<long long> smallestXorGteK(long long l, long long r, long long x, long long k) const {
        rangeCheck("smallestXorGteK", l, r);
        long long c = cntLt(l, r, k, x);
        if (c > r - l) return nullopt;
        return kthX(l, r, c + 1, x);
    }

    // O(logU) -- smallest integer >= 0 that is not v ^ x for any value v in a[l..r] (2^bits if every one is); needs
    // 0 <= l <= r < size()
    long long mexXor(long long l, long long r, long long x) const {
        rangeCheck("mexXor", l, r);
        int a = root[r + 1];
        if (nd[a].M >= l) return top + 1;
        long long res = 0;
        for (int h = B - 1; h >= 0; h--) {
            bool xb = x >> h & 1;
            int z = xb ? nd[a].R : nd[a].L, o = xb ? nd[a].L : nd[a].R;  // result bit 0 / 1
            if (nd[z].M >= l) {  // every result with bit h = 0 (and these higher bits) is taken
                res |= 1LL << h;
                a = o;
            } else {
                a = z;
            }
            if (!a) break;
        }
        return res;
    }

    // O(logU) -- sum of v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size()
    long long sumXor(long long l, long long r, long long x) const {
        rangeCheck("sumXor", l, r);
        size_t hi = (size_t)(r + 1) * B, lo = (size_t)l * B;
        long long n = r - l + 1, res = 0;
        for (int h = 0; h < B; h++) {
            long long ones = P[hi + h] - P[lo + h];
            res += (x >> h & 1 ? n - ones : ones) << h;
        }
        return res;
    }

    // O(logU) -- largest v ^ x over the values v < m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> maxXorWithVLtM(long long l, long long r, long long x, long long m) const {
        rangeCheck("maxXorWithVLtM", l, r);
        return bestIn(l, r, x, 0, m - 1, 1);
    }

    // O(logU) -- largest v ^ x over the values v <= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> maxXorWithVLteM(long long l, long long r, long long x, long long m) const {
        rangeCheck("maxXorWithVLteM", l, r);
        return bestIn(l, r, x, 0, m, 1);
    }

    // O(logU) -- largest v ^ x over the values v > m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> maxXorWithVGtM(long long l, long long r, long long x, long long m) const {
        rangeCheck("maxXorWithVGtM", l, r);
        return bestIn(l, r, x, m + 1, top, 1);
    }

    // O(logU) -- largest v ^ x over the values v >= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> maxXorWithVGteM(long long l, long long r, long long x, long long m) const {
        rangeCheck("maxXorWithVGteM", l, r);
        return bestIn(l, r, x, m, top, 1);
    }

    // O(logU) -- smallest v ^ x over the values v < m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> minXorWithVLtM(long long l, long long r, long long x, long long m) const {
        rangeCheck("minXorWithVLtM", l, r);
        return bestIn(l, r, x, 0, m - 1, 0);
    }

    // O(logU) -- smallest v ^ x over the values v <= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> minXorWithVLteM(long long l, long long r, long long x, long long m) const {
        rangeCheck("minXorWithVLteM", l, r);
        return bestIn(l, r, x, 0, m, 0);
    }

    // O(logU) -- smallest v ^ x over the values v > m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> minXorWithVGtM(long long l, long long r, long long x, long long m) const {
        rangeCheck("minXorWithVGtM", l, r);
        return bestIn(l, r, x, m + 1, top, 0);
    }

    // O(logU) -- smallest v ^ x over the values v >= m in a[l..r], or nullopt; needs 0 <= l <= r < size()
    optional<long long> minXorWithVGteM(long long l, long long r, long long x, long long m) const {
        rangeCheck("minXorWithVGteM", l, r);
        return bestIn(l, r, x, m, top, 0);
    }

    // O(logU) -- largest v ^ x over the values v in a[l..r] with lo <= v <= hi, or nullopt; needs 0 <= l <= r < size()
    optional<long long> maxXorWithVInValRange(long long l, long long r, long long x, long long lo, long long hi) const {
        rangeCheck("maxXorWithVInValRange", l, r);
        return bestIn(l, r, x, lo, hi, 1);
    }

    // O(logU) -- smallest v ^ x over the values v in a[l..r] with lo <= v <= hi, or nullopt; needs 0 <= l <= r < size()
    optional<long long> minXorWithVInValRange(long long l, long long r, long long x, long long lo, long long hi) const {
        rangeCheck("minXorWithVInValRange", l, r);
        return bestIn(l, r, x, lo, hi, 0);
    }

    // ---- plain order statistics over a[l..r] (the same walks with x = 0) ----

    // O(logU) -- # of values < x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long countLtX(long long l, long long r, long long x) const {
        rangeCheck("countLtX", l, r);
        return lt(l, r, x);
    }

    // O(logU) -- # of values <= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long countLteX(long long l, long long r, long long x) const {
        rangeCheck("countLteX", l, r);
        return lt(l, r, x + 1);
    }

    // O(logU) -- # of values > x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long countGtX(long long l, long long r, long long x) const {
        rangeCheck("countGtX", l, r);
        return r - l + 1 - lt(l, r, x + 1);
    }

    // O(logU) -- # of values >= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long countGteX(long long l, long long r, long long x) const {
        rangeCheck("countGteX", l, r);
        return r - l + 1 - lt(l, r, x);
    }

    // O(logU) -- # of values v in a[l..r] with lowVal <= v <= highVal (0 if lowVal > highVal); needs 0 <= l <= r <
    // size()
    long long countInValRange(long long l, long long r, long long lowVal, long long highVal) const {
        rangeCheck("countInValRange", l, r);
        return lowVal <= highVal ? lt(l, r, highVal + 1) - lt(l, r, lowVal) : 0;
    }

    // O(logU) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    long long countOccurrences(long long l, long long r, long long x) const {
        rangeCheck("countOccurrences", l, r);
        return lt(l, r, x + 1) - lt(l, r, x);
    }

    // O(logU) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and 1 <= k <= r - l + 1,
    // else throws out_of_range
    T kthSmallest(long long l, long long r, long long k) const {
        rangeCheck("kthSmallest", l, r);
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return (T)kth(l, r, k);
    }

    // O(logU) -- min of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMin(long long l, long long r) const {
        rangeCheck("rangeMin", l, r);
        return (T)kth(l, r, 1);
    }

    // O(logU) -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMax(long long l, long long r) const {
        rangeCheck("rangeMax", l, r);
        return (T)kth(l, r, r - l + 1);
    }

    // O(logU) -- smallest value >= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    optional<T> smallestGteX(long long l, long long r, long long x) const {
        rangeCheck("smallestGteX", l, r);
        long long c = lt(l, r, x);
        if (c == r - l + 1) return nullopt;
        return (T)kth(l, r, c + 1);
    }

    // O(logU) -- smallest value > x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    optional<T> smallestGtX(long long l, long long r, long long x) const {
        rangeCheck("smallestGtX", l, r);
        long long c = lt(l, r, x + 1);
        if (c == r - l + 1) return nullopt;
        return (T)kth(l, r, c + 1);
    }

    // O(logU) -- largest value <= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    optional<T> largestLteX(long long l, long long r, long long x) const {
        rangeCheck("largestLteX", l, r);
        long long c = lt(l, r, x + 1);
        if (!c) return nullopt;
        return (T)kth(l, r, c);
    }

    // O(logU) -- largest value < x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    optional<T> largestLtX(long long l, long long r, long long x) const {
        rangeCheck("largestLtX", l, r);
        long long c = lt(l, r, x);
        if (!c) return nullopt;
        return (T)kth(l, r, c);
    }

    // O(logU) -- min of the whole array; throws out_of_range if it is empty
    T minAll() const {
        if (!size()) throw out_of_range("minAll: the array is empty");
        return (T)kth(0, size() - 1, 1);
    }

    // O(logU) -- max of the whole array; throws out_of_range if it is empty
    T maxAll() const {
        if (!size()) throw out_of_range("maxAll: the array is empty");
        return (T)kth(0, size() - 1, size());
    }

    // O(logU) -- smallest integer >= 0 that is not in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long rangeMex(long long l, long long r) const { return mexXor(l, r, 0); }

    // O(logU) -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long rangeSum(long long l, long long r) const {
        rangeCheck("rangeSum", l, r);
        return sumAll(l, r);
    }

    // O(logU) -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long rangeXorQuery(long long l, long long r) const {
        rangeCheck("rangeXorQuery", l, r);
        return xorAll(l, r);
    }

    // O(logU) -- sum of the values < x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long sumLtX(long long l, long long r, long long x) const {
        rangeCheck("sumLtX", l, r);
        return sumLt(l, r, x);
    }

    // O(logU) -- sum of the values <= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long sumLteX(long long l, long long r, long long x) const {
        rangeCheck("sumLteX", l, r);
        return sumLt(l, r, x + 1);
    }

    // O(logU) -- sum of the values > x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long sumGtX(long long l, long long r, long long x) const {
        rangeCheck("sumGtX", l, r);
        return sumAll(l, r) - sumLt(l, r, x + 1);
    }

    // O(logU) -- sum of the values >= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long sumGteX(long long l, long long r, long long x) const {
        rangeCheck("sumGteX", l, r);
        return sumAll(l, r) - sumLt(l, r, x);
    }

    // O(logU) -- sum of the values v in a[l..r] with lowVal <= v <= highVal (0 if lowVal > highVal); needs
    // 0 <= l <= r < size()
    long long sumInValRange(long long l, long long r, long long lowVal, long long highVal) const {
        rangeCheck("sumInValRange", l, r);
        return lowVal <= highVal ? sumLt(l, r, highVal + 1) - sumLt(l, r, lowVal) : 0;
    }

    // O(logU) -- sum of the k smallest values in a[l..r]; needs 0 <= l <= r < size() and 0 <= k <= r - l + 1, else
    // throws out_of_range
    long long sumSmallestK(long long l, long long r, long long k) const {
        rangeCheck("sumSmallestK", l, r);
        if (k < 0 || k > r - l + 1) throw out_of_range("sumSmallestK: needs 0 <= k <= r - l + 1");
        return sumKth(l, r, k);
    }

    // O(logU) -- sum of the k largest values in a[l..r]; needs 0 <= l <= r < size() and 0 <= k <= r - l + 1, else
    // throws out_of_range
    long long sumLargestK(long long l, long long r, long long k) const {
        rangeCheck("sumLargestK", l, r);
        if (k < 0 || k > r - l + 1) throw out_of_range("sumLargestK: needs 0 <= k <= r - l + 1");
        return sumAll(l, r) - sumKth(l, r, r - l + 1 - k);
    }

    // O(logU) -- sum of the kFrom-th .. kTo-th smallest values in a[l..r] (1-indexed, inclusive); needs
    // 0 <= l <= r < size() and 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    long long sumKthSmallestRange(long long l, long long r, long long kFrom, long long kTo) const {
        rangeCheck("sumKthSmallestRange", l, r);
        if (kFrom < 1 || kFrom > kTo || kTo > r - l
            + 1) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumKth(l, r, kTo) - sumKth(l, r, kFrom - 1);
    }

    // O(logU) -- sum of the kFrom-th .. kTo-th largest values in a[l..r] (1-indexed, inclusive); needs
    // 0 <= l <= r < size() and 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    long long sumKthLargestRange(long long l, long long r, long long kFrom, long long kTo) const {
        rangeCheck("sumKthLargestRange", l, r);
        long long n = r - l + 1;
        if (kFrom < 1 || kFrom > kTo
            || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumKth(l, r, n - kFrom + 1) - sumKth(l, r, n - kTo);
    }

    // O(logU) -- sum of |a[i] - x| over i in [l, r]; needs 0 <= l <= r < size(), else throws out_of_range
    long long sumAbsDiffToX(long long l, long long r, long long x) const {
        rangeCheck("sumAbsDiffToX", l, r);
        long long c = lt(l, r, x), s = sumLt(l, r, x);
        return x * c - s + (sumAll(l, r) - s) - x * (r - l + 1 - c);
    }

    // O(logU) -- xor of the values < x in a[l..r] (copies count); needs 0 <= l <= r < size(), else throws out_of_range
    long long xorLtX(long long l, long long r, long long x) const {
        rangeCheck("xorLtX", l, r);
        return xorLt(l, r, x);
    }

    // O(logU) -- xor of the values <= x in a[l..r] (copies count); needs 0 <= l <= r < size(), else throws out_of_range
    long long xorLteX(long long l, long long r, long long x) const {
        rangeCheck("xorLteX", l, r);
        return xorLt(l, r, x + 1);
    }

    // O(logU) -- xor of the values > x in a[l..r] (copies count); needs 0 <= l <= r < size(), else throws out_of_range
    long long xorGtX(long long l, long long r, long long x) const {
        rangeCheck("xorGtX", l, r);
        return xorAll(l, r) ^ xorLt(l, r, x + 1);
    }

    // O(logU) -- xor of the values >= x in a[l..r] (copies count); needs 0 <= l <= r < size(), else throws out_of_range
    long long xorGteX(long long l, long long r, long long x) const {
        rangeCheck("xorGteX", l, r);
        return xorAll(l, r) ^ xorLt(l, r, x);
    }

    // O(logU) -- xor of the values v in a[l..r] with lowVal <= v <= highVal (copies count; 0 if lowVal > highVal);
    // needs
    // 0 <= l <= r < size()
    long long xorInValRange(long long l, long long r, long long lowVal, long long highVal) const {
        rangeCheck("xorInValRange", l, r);
        return lowVal <= highVal ? xorLt(l, r, highVal + 1) ^ xorLt(l, r, lowVal) : 0;
    }

  private:
    void rangeCheck(const char* name, long long l, long long r) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range(string(name) + ": needs 0 <= l <= r < size()");
    }

    int child(int t, int bit) const { return bit ? nd[t].R : nd[t].L; }

    // copy of version node with one more copy of v, the value at index i
    int ins(int node, long long v, int i) {
        vector<int> path(B);
        for (int h = B - 1; h >= 0; h--) {
            path[h] = node;
            node = child(node, v >> h & 1);
        }
        Node leaf;
        leaf.C = nd[node].C + 1;
        leaf.M = i;
        leaf.S = nd[node].S + v;
        leaf.X = nd[node].X ^ v;
        int cur = (int)nd.size();
        nd.push_back(leaf);
        for (int h = 0; h < B; h++) {
            Node up = nd[path[h]];
            if (v >> h & 1) up.R = cur; else up.L = cur;
            up.C = nd[up.L].C + nd[up.R].C;
            up.M = min(nd[up.L].M, nd[up.R].M);
            up.S = nd[up.L].S + nd[up.R].S;
            up.X = nd[up.L].X ^ nd[up.R].X;
            cur = (int)nd.size();
            nd.push_back(up);
        }
        return cur;
    }

    // # of values < k in a[l..r]
    long long lt(long long l, long long r, long long k) const { return cntLt(l, r, k, 0); }

    // k-th smallest (1-indexed)
    long long kth(long long l, long long r, long long k) const { return kthX(l, r, k, 0); }

    long long sumAll(long long l, long long r) const { return nd[root[r + 1]].S - nd[root[l]].S; }

    long long sumLt(long long l, long long r, long long k) const {  // sum of the values < k in a[l..r]
        if (k <= 0) return 0;
        if (k > top) return sumAll(l, r);
        int a = root[r + 1], b = root[l];
        long long res = 0;
        for (int h = B - 1; h >= 0 && a; h--) {
            if (k >> h & 1) {
                res += nd[nd[a].L].S - nd[nd[b].L].S;
                a = nd[a].R, b = nd[b].R;
            } else {
                a = nd[a].L, b = nd[b].L;
            }
        }
        return res;
    }

    long long sumKth(long long l, long long r, long long k) const {  // sum of the k smallest values in a[l..r]
        if (k <= 0) return 0;
        int a = root[r + 1], b = root[l];
        long long res = 0, v = 0;
        for (int h = B - 1; h >= 0; h--) {
            long long c = nd[nd[a].L].C - nd[nd[b].L].C;
            if (k <= c) {
                a = nd[a].L, b = nd[b].L;
            } else {
                k -= c;
                res += nd[nd[a].L].S - nd[nd[b].L].S;
                a = nd[a].R, b = nd[b].R;
                v |= 1LL << h;
            }
        }
        return res + k * v;  // the last k all equal the k-th smallest
    }

    long long xorAll(long long l, long long r) const { return nd[root[r + 1]].X ^ nd[root[l]].X; }

    long long xorLt(long long l, long long r, long long k) const {  // xor of the values < k in a[l..r]
        if (k <= 0) return 0;
        if (k > top) return xorAll(l, r);
        int a = root[r + 1], b = root[l];
        long long res = 0;
        for (int h = B - 1; h >= 0 && a; h--) {
            if (k >> h & 1) {
                res ^= nd[nd[a].L].X ^ nd[nd[b].L].X;
                a = nd[a].R, b = nd[b].R;
            } else {
                a = nd[a].L, b = nd[b].L;
            }
        }
        return res;
    }


    // how many values v in a[l..r] have v ^ x < k
    long long cntLt(long long l, long long r, long long k, long long x) const {
        if (k <= 0) return 0;
        if (k > top) return r - l + 1;
        int a = root[r + 1], b = root[l];
        long long res = 0;
        for (int h = B - 1; h >= 0; h--) {
            int xb = x >> h & 1;
            if (k >> h & 1) {  // every result with bit h = 0 is < k
                res += nd[child(a, xb)].C - nd[child(b, xb)].C;
                a = child(a, xb ^ 1), b = child(b, xb ^ 1);
            } else {
                a = child(a, xb), b = child(b, xb);
            }
            if (!a) break;
        }
        return res;
    }

    // the k-th smallest (1-indexed) v ^ x over the values v in a[l..r]
    long long kthX(long long l, long long r, long long k, long long x) const {
        int a = root[r + 1], b = root[l];
        long long res = 0;
        for (int h = B - 1; h >= 0; h--) {
            int xb = x >> h & 1;
            long long c = nd[child(a, xb)].C - nd[child(b, xb)].C;
            if (k <= c) {
                a = child(a, xb), b = child(b, xb);
            } else {
                k -= c;
                a = child(a, xb ^ 1), b = child(b, xb ^ 1);
                res |= 1LL << h;
            }
        }
        return res;
    }

    // bits h..0 of the largest (big = 1) / smallest v ^ x below the node pair (a, b), which holds some value
    long long extreme(int a, int b, int h, long long x, int big) const {
        long long res = 0;
        for (; h >= 0; h--) {
            int p = (int)(x >> h & 1) ^ big;  // the child whose result bit is big
            int ua = child(a, p), ub = child(b, p);
            if (nd[ua].C != nd[ub].C) {
                a = ua, b = ub;
                res |= (long long)big << h;
            } else {
                a = child(a, p ^ 1), b = child(b, p ^ 1);
                res |= (long long)(big ^ 1) << h;
            }
        }
        return res;
    }

    // the largest (big = 1) / smallest v ^ x over the values v in a[l..r] with lo <= v <= hi, or nullopt. Walks down
    // the bits lo and hi share, then splits: below lo's side only the lower bound matters, below hi's only the upper
    // one
    optional<long long> bestIn(long long l, long long r, long long x, long long lo, long long hi, int big) const {
        lo = max(lo, 0LL), hi = min(hi, top);
        if (lo > hi) return nullopt;
        int a = root[r + 1], b = root[l], h = B - 1;
        long long res = 0;
        for (; h >= 0 && (lo >> h & 1) == (hi >> h & 1); h--) {
            int bit = lo >> h & 1;
            a = child(a, bit), b = child(b, bit);
            if (nd[a].C == nd[b].C) return nullopt;
            res |= (long long)(bit ^ (x >> h & 1)) << h;
        }
        if (h < 0) return res;
        long long xb = x >> h & 1;
        auto c0 = oneSide(child(a, 0), child(b, 0), h - 1, lo, x, big, 1, res | xb << h);
        auto c1 = oneSide(child(a, 1), child(b, 1), h - 1, hi, x, big, 0, res | (xb ^ 1) << h);
        if (!c0 || !c1) return c0 ? c0 : c1;
        return big ? max(*c0, *c1) : min(*c0, *c1);
    }

    // below the node pair (a, b): the best v ^ x whose bits h..0 are >= (lower = 1) / <= bound's bits h..0, or nullopt;
    // res holds the result's bits above h. Along the path that matches bound, each step off it (to the side the bound
    // allows) is a free subtree: take it at once if its result bit beats the path's, else remember the deepest one
    optional<long long> oneSide(int a, int b, int h, long long bound, long long x, int big, int lower,
        long long res) const {
        if (nd[a].C == nd[b].C) return nullopt;
        int fa = -1, fb = 0, fh = 0;
        long long fres = 0;
        for (; h >= 0; h--) {
            int xb = x >> h & 1, bb = bound >> h & 1;
            if (bb != lower) {  // a free side exists: v bit = lower
                int ca = child(a, lower), cb = child(b, lower);
                if (nd[ca].C != nd[cb].C) {
                    long long cres = res | (long long)(lower ^ xb) << h;
                    if ((lower ^ xb) == big) return cres | extreme(ca, cb, h - 1, x, big);
                    fa = ca, fb = cb, fh = h, fres = cres;
                }
            }
            a = child(a, bb), b = child(b, bb);
            if (nd[a].C == nd[b].C) break;
            res |= (long long)(bb ^ xb) << h;
        }
        if (h < 0) return res;  // v equal to bound below here: allowed (inclusive)
        if (fa < 0) return nullopt;
        return fres | extreme(fa, fb, fh - 1, x, big);
    }
};
