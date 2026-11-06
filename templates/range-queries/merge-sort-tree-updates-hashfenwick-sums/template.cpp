// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/merge-sort-tree-updates-hashfenwick-sums/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countGtX countGteX countInValRange countLtX countLteX getAll largestLtX largestLteX pointAdd pointAssign pointChmax pointChmin pointGet smallestGtX smallestGteX sumAbsDiffToX sumGtX sumGteX sumInValRange sumLtX sumLteX
// @data-structure-type: merge-sort-tree
// @fractional-cascading: no
// @complexities:
//   countGtX: log(N)*log(U)
//   countGteX: log(N)*log(U)
//   countInValRange: log(N)*log(U)
//   countLtX: log(N)*log(U)
//   countLteX: log(N)*log(U)
//   getAll: N
//   largestLtX: log(N)*log(U)
//   largestLteX: log(N)*log(U)
//   pointAdd: log(N)*log(U)
//   pointAssign: log(N)*log(U)
//   pointChmax: log(N)*log(U)
//   pointChmin: log(N)*log(U)
//   pointGet: 1
//   smallestGtX: log(N)*log(U)
//   smallestGteX: log(N)*log(U)
//   sumAbsDiffToX: log(N)*log(U)
//   sumGtX: log(N)*log(U)
//   sumGteX: log(N)*log(U)
//   sumInValRange: log(N)*log(U)
//   sumLtX: log(N)*log(U)
//   sumLteX: log(N)*log(U)
//   build: N*log(N)*log(U)
// @memory:
//   layout: none
//   node: slotKey[2*N*log(N)*log(U)] slotCount[2*N*log(N)*log(U)] slotSum[2*N*log(N)*log(U)]
//   tags: none
//   other: A[1*N] total[2*N] nodeSize[2*N]
//   note: every value must stay in [valLo, valHi] (U = its size); the hash table is kept at most half full, and N counts updates too (each adds up to log N log U keys)

// Merge sort tree with point updates: a segment tree over positions (bottom-up: node p >= n is a[p - n]), each
// inner node keeping its positions' values in a searchable structure (a Fenwick tree over the whole value range [valLo, valHi], stored sparsely in one hash table). a[l..r] is O(log n) nodes, and a
// point update changes one value in each of the O(log n) nodes above it. All indices 0-based, ranges inclusive.
// Every value a[i] ever holds must be in [valLo, valHi]; query arguments can be anything.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct MergeSortTreeUpdates {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr unsigned long long EMPTY = ~0ULL;
    int n;
    vector<T> A;
    vector<S> total;  // total[p]: sum of node p's values
    long long lo, hi, span;  // values live in [lo, hi]; span = hi - lo + 1 Fenwick slots per node
    // one open-addressing hash table for every node's Fenwick tree: key (node << 32) | slot
    vector<unsigned long long> slotKey;
    vector<int> slotCount;
    vector<S> slotSum;
    size_t used = 0;
    unsigned long long seed;
    vector<int> nodeSize;  // nodeSize[p]: how many positions node p covers

    // O(build) -- arr: the initial array. Every value a[i] ever holds must be in [valLo, valHi]
    MergeSortTreeUpdates(const vector<T>& arr, T valLo, T valHi) {
        n = (int)arr.size();
        A = arr;
        if (valLo > valHi || (long long)valHi - (long long)valLo >= (1LL << 32) - 1)
            throw out_of_range("MergeSortTreeUpdates: needs valLo <= valHi and valHi - valLo < 2^32 - 1");
        lo = valLo, hi = valHi, span = hi - lo + 1;
        for (int i = 0; i < n; i++)
            if ((long long)A[i] < lo || (long long)A[i] > hi) throw out_of_range("MergeSortTreeUpdates: every a[i] must be in [valLo, valHi]");
        seed = mix(chrono::steady_clock::now().time_since_epoch().count());
        nodeSize.assign(2 * n, 1);
        for (int p = n - 1; p >= 1; p--) nodeSize[p] = nodeSize[2 * p] + nodeSize[2 * p + 1];
        for (int i = 0; i < n; i++)
            for (int p = (i + n) >> 1; p >= 1; p >>= 1) add(p, A[i], 1);
        buildTotals();
    }

    // O(n) -- the whole array
    vector<T> getAll() const { return vector<T>(A.begin(), A.end()); }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return A[i];
    }

    // O(log(N)*log(U)) -- a[i] = v (overwrite); needs 0 <= i < n and the new value in [valLo, valHi], else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        write(i, v, "pointAssign");
    }

    // O(log(N)*log(U)) -- a[i] += v; needs 0 <= i < n and the new value in [valLo, valHi], else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        write(i, T(A[i] + v), "pointAdd");
    }

    // O(log(N)*log(U)) -- a[i] = max(a[i], v); needs 0 <= i < n and the new value in [valLo, valHi], else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        write(i, max(A[i], v), "pointChmax");
    }

    // O(log(N)*log(U)) -- a[i] = min(a[i], v); needs 0 <= i < n and the new value in [valLo, valHi], else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        write(i, min(A[i], v), "pointChmin");
    }

    // O(log(N)*log(U)) -- # of i in [l, r] with a[i] < x; needs 0 <= l <= r < n, else throws out_of_range
    long long countLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLtX: needs 0 <= l <= r < n");
        return countLess(l, r, x, true);
    }

    // O(log(N)*log(U)) -- # of i in [l, r] with a[i] <= x; needs 0 <= l <= r < n, else throws out_of_range
    long long countLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLteX: needs 0 <= l <= r < n");
        return countLess(l, r, x, false);
    }

    // O(log(N)*log(U)) -- # of i in [l, r] with a[i] > x; needs 0 <= l <= r < n, else throws out_of_range
    long long countGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGtX: needs 0 <= l <= r < n");
        return (r - l + 1) - countLess(l, r, x, false);
    }

    // O(log(N)*log(U)) -- # of i in [l, r] with a[i] >= x; needs 0 <= l <= r < n, else throws out_of_range
    long long countGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGteX: needs 0 <= l <= r < n");
        return (r - l + 1) - countLess(l, r, x, true);
    }

    // O(log(N)*log(U)) -- # of i in [l, r] with lowVal <= a[i] <= highVal (0 if lowVal > highVal); needs 0 <= l <= r < n, else throws out_of_range
    long long countInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countInValRange: needs 0 <= l <= r < n");
        if (lowVal > highVal) return 0;
        return countLess(l, r, highVal, false) - countLess(l, r, lowVal, true);
    }

    // O(log(N)*log(U)) -- smallest a[i] >= x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws out_of_range
    optional<T> smallestGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGteX: needs 0 <= l <= r < n");
        return firstAtLeast(l, r, x, false);
    }

    // O(log(N)*log(U)) -- smallest a[i] > x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws out_of_range
    optional<T> smallestGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGtX: needs 0 <= l <= r < n");
        return firstAtLeast(l, r, x, true);
    }

    // O(log(N)*log(U)) -- largest a[i] <= x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws out_of_range
    optional<T> largestLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLteX: needs 0 <= l <= r < n");
        return lastBelow(l, r, x, false);
    }

    // O(log(N)*log(U)) -- largest a[i] < x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws out_of_range
    optional<T> largestLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLtX: needs 0 <= l <= r < n");
        return lastBelow(l, r, x, true);
    }

    // O(log(N)*log(U)) -- sum of a[i] < x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLtX: needs 0 <= l <= r < n");
        return sumLess(l, r, x, true);
    }

    // O(log(N)*log(U)) -- sum of a[i] <= x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLteX: needs 0 <= l <= r < n");
        return sumLess(l, r, x, false);
    }

    // O(log(N)*log(U)) -- sum of a[i] > x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumGtX: needs 0 <= l <= r < n");
        return sumAll(l, r) - sumLess(l, r, x, false);
    }

    // O(log(N)*log(U)) -- sum of a[i] >= x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumGteX: needs 0 <= l <= r < n");
        return sumAll(l, r) - sumLess(l, r, x, true);
    }

    // O(log(N)*log(U)) -- sum of a[i] with lowVal <= a[i] <= highVal in [l, r] (0 if lowVal > highVal); needs 0 <= l <= r < n, else throws out_of_range
    S sumInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumInValRange: needs 0 <= l <= r < n");
        if (lowVal > highVal) return 0;
        return sumLess(l, r, highVal, false) - sumLess(l, r, lowVal, true);
    }

    // O(log(N)*log(U)) -- sum of |a[i] - x| over [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumAbsDiffToX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumAbsDiffToX: needs 0 <= l <= r < n");
        long long below = countLess(l, r, x, true);
        S belowSum = sumLess(l, r, x, true), total = sumAll(l, r);
        return S(x) * below - belowSum + (total - belowSum) - S(x) * ((r - l + 1) - below);
    }

    // ---- internals ----

    void buildTotals() {  // the sum / xor of every node's values
        total.assign(2 * n, 0);
        for (int i = 0; i < n; i++) total[n + i] = A[i];
        for (int p = n - 1; p >= 1; p--) total[p] = total[2 * p] + total[2 * p + 1];
    }

    template <class F>
    void forNodes(int l, int r, F f) const {  // the O(log n) nodes that cover a[l..r]
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) f(l++);
            if (r & 1) f(--r);
        }
    }

    long long countLess(int l, int r, T x, bool strict) const {  // # of values < x (strict) or <= x in a[l..r]
        long long res = 0;
        forNodes(l, r, [&](int p) {
            if (p >= n) res += strict ? A[p - n] < x : !(x < A[p - n]);
            else res += countBelow(p, x, strict);
        });
        return res;
    }

    optional<T> firstAtLeast(int l, int r, T x, bool strict) const {  // smallest value > x (strict) or >= x
        optional<T> best;
        forNodes(l, r, [&](int p) {
            optional<T> got;
            if (p >= n) {
                if (strict ? x < A[p - n] : !(A[p - n] < x)) got = A[p - n];
            } else {
                got = firstIn(p, x, strict);
            }
            if (got && (!best || *got < *best)) best = got;
        });
        return best;
    }

    optional<T> lastBelow(int l, int r, T x, bool strict) const {  // largest value < x (strict) or <= x
        optional<T> best;
        forNodes(l, r, [&](int p) {
            optional<T> got;
            if (p >= n) {
                if (strict ? A[p - n] < x : !(x < A[p - n])) got = A[p - n];
            } else {
                got = lastIn(p, x, strict);
            }
            if (got && (!best || *best < *got)) best = got;
        });
        return best;
    }

    S sumLess(int l, int r, T x, bool strict) const {
        S res = 0;
        forNodes(l, r, [&](int p) {
            if (p >= n) {
                if (strict ? A[p - n] < x : !(x < A[p - n])) res += A[p - n];
            } else {
                res += sumBelow(p, x, strict);
            }
        });
        return res;
    }

    S sumAll(int l, int r) const {
        S res = 0;
        forNodes(l, r, [&](int p) { res += p >= n ? S(A[p - n]) : total[p]; });
        return res;
    }

    void write(int i, T v, [[maybe_unused]] const char* op) {
        T old = A[i];
        if (old == v) return;
        if ((long long)v < lo || (long long)v > hi) throw out_of_range(string(op) + ": the new value must be in [valLo, valHi]");
        for (int p = (i + n) >> 1; p >= 1; p >>= 1) {
            eraseValue(p, old);
            insertValue(p, v);
            total[p] += S(v) - S(old);
        }
        A[i] = v;
    }

    static unsigned long long mix(unsigned long long z) {  // splitmix64
        z += 0x9e3779b97f4a7c15ULL;
        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
        z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
        return z ^ (z >> 31);
    }

    long long find(unsigned long long k) const {  // the slot holding key k, or -1
        size_t mask = slotKey.size() - 1, at = mix(k ^ seed) & mask;
        while (slotKey[at] != EMPTY) {
            if (slotKey[at] == k) return (long long)at;
            at = (at + 1) & mask;
        }
        return -1;
    }

    size_t findOrAdd(unsigned long long k) {
        if (2 * (used + 1) > slotKey.size()) grow();
        size_t mask = slotKey.size() - 1, at = mix(k ^ seed) & mask;
        while (slotKey[at] != EMPTY && slotKey[at] != k) at = (at + 1) & mask;
        if (slotKey[at] == EMPTY) {
            slotKey[at] = k;
            used++;
        }
        return at;
    }

    void grow() {
        size_t capacity = max<size_t>(1024, 2 * slotKey.size());
        vector<unsigned long long> oldKey = std::move(slotKey);
        vector<int> oldCount = std::move(slotCount);
        vector<S> oldSum = std::move(slotSum);
        slotKey.assign(capacity, EMPTY);
        slotCount.assign(capacity, 0);
        slotSum.assign(capacity, 0);
        size_t mask = capacity - 1;
        for (size_t k = 0; k < oldKey.size(); k++) {
            if (oldKey[k] != EMPTY) {
                size_t at = mix(oldKey[k] ^ seed) & mask;
                while (slotKey[at] != EMPTY) at = (at + 1) & mask;
                slotKey[at] = oldKey[k];
                slotCount[at] = oldCount[k];
                slotSum[at] = oldSum[k];
            }
        }
    }

    void add(int p, T v, int delta) {  // delta copies of v into node p's Fenwick tree
        unsigned long long base = (unsigned long long)p << 32;
        for (long long j = (long long)v - lo + 1; j <= span; j += j & -j) {
            size_t at = findOrAdd(base | (unsigned long long)j);
            slotCount[at] += delta;
            slotSum[at] += S(v) * delta;
        }
    }

    void insertValue(int p, T v) { add(p, v, 1); }

    void eraseValue(int p, T v) { add(p, v, -1); }

    long long countBelow(int p, T x, bool strict) const {  // over node p's values < x (strict) or <= x
        long long k = (long long)x - lo + (strict ? 0 : 1);
        if (k <= 0) return 0;
        if (k > span) k = span;
        long long res = 0;
        unsigned long long base = (unsigned long long)p << 32;
        for (long long j = k; j > 0; j &= j - 1) {
            long long at = find(base | (unsigned long long)j);
            if (at >= 0) res += slotCount[at];
        }
        return res;
    }

    S sumBelow(int p, T x, bool strict) const {  // over node p's values < x (strict) or <= x
        long long k = (long long)x - lo + (strict ? 0 : 1);
        if (k <= 0) return 0;
        if (k > span) k = span;
        S res = 0;
        unsigned long long base = (unsigned long long)p << 32;
        for (long long j = k; j > 0; j &= j - 1) {
            long long at = find(base | (unsigned long long)j);
            if (at >= 0) res += slotSum[at];
        }
        return res;
    }

    T kth(int p, long long k) const {  // node p's k-th smallest value (1-indexed; 1 <= k <= nodeSize[p])
        unsigned long long base = (unsigned long long)p << 32;
        long long pos = 0, step = 1;
        while (step * 2 <= span) step *= 2;
        for (; step; step >>= 1) {
            if (pos + step > span) continue;
            long long at = find(base | (unsigned long long)(pos + step));
            int here = at >= 0 ? slotCount[at] : 0;
            if (here < k) {
                pos += step;
                k -= here;
            }
        }
        return T(lo + pos);
    }

    optional<T> firstIn(int p, T x, bool strict) const {  // smallest value > x (strict) or >= x in node p
        long long below = countBelow(p, x, !strict);
        if (below >= nodeSize[p]) return nullopt;
        return kth(p, below + 1);
    }

    optional<T> lastIn(int p, T x, bool strict) const {  // largest value < x (strict) or <= x in node p
        long long below = countBelow(p, x, strict);
        if (below == 0) return nullopt;
        return kth(p, below);
    }
};
