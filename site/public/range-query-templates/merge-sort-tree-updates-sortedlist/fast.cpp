// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/merge-sort-tree-updates-sortedlist/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countGtX countGteX countInValRange countLtX countLteX getAll largestLtX largestLteX pointAdd pointAssign pointChmax pointChmin pointGet smallestGtX smallestGteX
// @data-structure-type: merge-sort-tree
// @fractional-cascading: no
// @complexities:
//   countGtX: log^2(N)
//   countGteX: log^2(N)
//   countInValRange: log^2(N)
//   countLtX: log^2(N)
//   countLteX: log^2(N)
//   getAll: N
//   largestLtX: log^2(N)
//   largestLteX: log^2(N)
//   pointAdd: log^2(N) amortized
//   pointAssign: log^2(N) amortized
//   pointChmax: log^2(N) amortized
//   pointChmin: log^2(N) amortized
//   pointGet: 1
//   smallestGtX: log^2(N)
//   smallestGteX: log^2(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: vals[1*N*log(N)]
//   tags: none
//   other: A[1*N]
//   note: no value range and nothing up front; buckets hold 256 to 512 values, so an update also moves up to 512 values in each of its log N nodes

// Merge sort tree with point updates: a segment tree over positions (bottom-up: node p >= n is a[p - n]), each
// inner node keeping its positions' values in a searchable structure (sorted buckets of 256 to 512 values, with a Fenwick tree over the bucket sizes). a[l..r] is O(log n) nodes, and a
// point update changes one value in each of the O(log n) nodes above it. All indices 0-based, ranges inclusive.
// Counts and nearest values only: sums and xors need the treap or offline versions.
// T: int, long long, ...; sums are kept in S (long long for small T).
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
struct MergeSortTreeUpdates {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    HotVector<T> A;
    static constexpr int LOAD = 256;  // buckets hold LOAD to 2 * LOAD values
    HotVector<vector<vector<T>>> buckets;  // buckets[p]: node p's values sorted, cut into buckets
    HotVector<vector<T>> maxes;  // maxes[p][b]: the last value of node p's bucket b
    HotVector<vector<int>> sizes;  // sizes[p]: Fenwick tree over node p's bucket sizes (1-indexed)

    // O(build) -- arr: the initial array
    explicit MergeSortTreeUpdates(const vector<T>& arr) {
        n = (int)arr.size();
        A = arr;
        buckets.resize(max(n, 1));
        maxes.resize(max(n, 1));
        sizes.resize(max(n, 1));
        vector<vector<T>> sortedVals(2 * n);  // node p's values, sorted (freed once its parent has them)
        for (int i = 0; i < n; i++) sortedVals[n + i] = {A[i]};
        for (int p = n - 1; p >= 1; p--) {
            vector<T>& left = sortedVals[2 * p];
            vector<T>& right = sortedVals[2 * p + 1];
            sortedVals[p].resize(left.size() + right.size());
            merge(left.begin(), left.end(), right.begin(), right.end(), sortedVals[p].begin());
            vector<T>().swap(left);
            vector<T>().swap(right);
            auto& bs = buckets[p];
            for (size_t k = 0; k < sortedVals[p].size(); k += LOAD)
                bs.emplace_back(sortedVals[p].begin() + k, sortedVals[p].begin() + min(sortedVals[p].size(), k + LOAD));
            reindex(p);
        }
    }

    // O(n) -- the whole array
    LEETCODE_NO_SANITIZE vector<T> getAll() const { return vector<T>(A.begin(), A.end()); }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return A[i];
    }

    // O(log^2(N) amortized) -- a[i] = v (overwrite); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        write(i, v, "pointAssign");
    }

    // O(log^2(N) amortized) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        write(i, T(A[i] + v), "pointAdd");
    }

    // O(log^2(N) amortized) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        write(i, max(A[i], v), "pointChmax");
    }

    // O(log^2(N) amortized) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        write(i, min(A[i], v), "pointChmin");
    }

    // O(log^2(N)) -- # of i in [l, r] with a[i] < x; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLtX: needs 0 <= l <= r < n");
        return countLess(l, r, x, true);
    }

    // O(log^2(N)) -- # of i in [l, r] with a[i] <= x; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLteX: needs 0 <= l <= r < n");
        return countLess(l, r, x, false);
    }

    // O(log^2(N)) -- # of i in [l, r] with a[i] > x; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGtX: needs 0 <= l <= r < n");
        return (r - l + 1) - countLess(l, r, x, false);
    }

    // O(log^2(N)) -- # of i in [l, r] with a[i] >= x; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGteX: needs 0 <= l <= r < n");
        return (r - l + 1) - countLess(l, r, x, true);
    }

    // O(log^2(N)) -- # of i in [l, r] with lowVal <= a[i] <= highVal (0 if lowVal > highVal); needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countInValRange: needs 0 <= l <= r < n");
        if (lowVal > highVal) return 0;
        return countLess(l, r, highVal, false) - countLess(l, r, lowVal, true);
    }

    // O(log^2(N)) -- smallest a[i] >= x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGteX: needs 0 <= l <= r < n");
        return firstAtLeast(l, r, x, false);
    }

    // O(log^2(N)) -- smallest a[i] > x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGtX: needs 0 <= l <= r < n");
        return firstAtLeast(l, r, x, true);
    }

    // O(log^2(N)) -- largest a[i] <= x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLteX: needs 0 <= l <= r < n");
        return lastBelow(l, r, x, false);
    }

    // O(log^2(N)) -- largest a[i] < x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLtX: needs 0 <= l <= r < n");
        return lastBelow(l, r, x, true);
    }

    // ---- internals ----

    template <class F>
    LEETCODE_NO_SANITIZE void forNodes(int l, int r, F f) const {  // the O(log n) nodes that cover a[l..r]
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) f(l++);
            if (r & 1) f(--r);
        }
    }

    LEETCODE_NO_SANITIZE long long countLess(int l, int r, T x, bool strict) const {  // # of values < x (strict) or <= x in a[l..r]
        long long res = 0;
        forNodes(l, r, [&](int p) {
            if (p >= n) res += strict ? A[p - n] < x : !(x < A[p - n]);
            else res += countBelow(p, x, strict);
        });
        return res;
    }

    LEETCODE_NO_SANITIZE optional<T> firstAtLeast(int l, int r, T x, bool strict) const {  // smallest value > x (strict) or >= x
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

    LEETCODE_NO_SANITIZE optional<T> lastBelow(int l, int r, T x, bool strict) const {  // largest value < x (strict) or <= x
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

    LEETCODE_NO_SANITIZE void write(int i, T v, [[maybe_unused]] const char* op) {
        T old = A[i];
        if (old == v) return;
        for (int p = (i + n) >> 1; p >= 1; p >>= 1) {
            eraseValue(p, old);
            insertValue(p, v);
        }
        A[i] = v;
    }

    LEETCODE_NO_SANITIZE void reindex(int p) {  // maxes and the size Fenwick tree of node p, from its buckets
        const auto& bs = buckets[p];
        int count = (int)bs.size();
        maxes[p].resize(count);
        sizes[p].assign(count + 1, 0);
        for (int j = 1; j <= count; j++) {
            maxes[p][j - 1] = bs[j - 1].back();
            sizes[p][j] += (int)bs[j - 1].size();
            int up = j + (j & -j);
            if (up <= count) sizes[p][up] += sizes[p][j];
        }
    }

    LEETCODE_NO_SANITIZE int before(int p, int b) const {  // # of node p's values in its buckets 0 .. b - 1
        int res = 0;
        for (int j = b; j > 0; j &= j - 1) res += sizes[p][j];
        return res;
    }

    LEETCODE_NO_SANITIZE void bump(int p, int b, int delta) {
        int count = (int)sizes[p].size() - 1;
        for (int j = b + 1; j <= count; j += j & -j) sizes[p][j] += delta;
    }

    LEETCODE_NO_SANITIZE long long countBelow(int p, T x, bool strict) const {
        const auto& m = maxes[p];
        int b = int((strict ? lower_bound(m.begin(), m.end(), x) : upper_bound(m.begin(), m.end(), x)) - m.begin());
        if (b == (int)m.size()) return before(p, b);
        const auto& bucket = buckets[p][b];
        auto it = strict ? lower_bound(bucket.begin(), bucket.end(), x) : upper_bound(bucket.begin(), bucket.end(), x);
        return before(p, b) + int(it - bucket.begin());
    }

    LEETCODE_NO_SANITIZE optional<T> firstIn(int p, T x, bool strict) const {  // smallest value > x (strict) or >= x in node p
        const auto& m = maxes[p];
        int b = int((strict ? upper_bound(m.begin(), m.end(), x) : lower_bound(m.begin(), m.end(), x)) - m.begin());
        if (b == (int)m.size()) return nullopt;
        const auto& bucket = buckets[p][b];
        return *(strict ? upper_bound(bucket.begin(), bucket.end(), x) : lower_bound(bucket.begin(), bucket.end(), x));
    }

    LEETCODE_NO_SANITIZE optional<T> lastIn(int p, T x, bool strict) const {  // largest value < x (strict) or <= x in node p
        const auto& m = maxes[p];
        int b = int((strict ? lower_bound(m.begin(), m.end(), x) : upper_bound(m.begin(), m.end(), x)) - m.begin());
        if (b < (int)m.size()) {
            const auto& bucket = buckets[p][b];
            auto it = strict ? lower_bound(bucket.begin(), bucket.end(), x) : upper_bound(bucket.begin(), bucket.end(), x);
            if (it != bucket.begin()) return *prev(it);
        }
        if (b == 0) return nullopt;
        return buckets[p][b - 1].back();
    }

    LEETCODE_NO_SANITIZE void insertValue(int p, T v) {
        auto& bs = buckets[p];
        const auto& m = maxes[p];
        int b = int(lower_bound(m.begin(), m.end(), v) - m.begin());
        if (b == (int)bs.size()) b--;
        vector<T>& bucket = bs[b];
        bucket.insert(upper_bound(bucket.begin(), bucket.end(), v), v);
        if ((int)bucket.size() > 2 * LOAD) {  // split it in two
            vector<T> upper(bucket.begin() + LOAD, bucket.end());
            bucket.resize(LOAD);
            bs.insert(bs.begin() + b + 1, std::move(upper));
            reindex(p);
        } else {
            maxes[p][b] = bucket.back();
            bump(p, b, 1);
        }
    }

    LEETCODE_NO_SANITIZE void eraseValue(int p, T v) {  // v is in node p
        auto& bs = buckets[p];
        const auto& m = maxes[p];
        int b = int(lower_bound(m.begin(), m.end(), v) - m.begin());
        vector<T>& bucket = bs[b];
        bucket.erase(lower_bound(bucket.begin(), bucket.end(), v));
        if (bucket.empty()) {
            bs.erase(bs.begin() + b);
            reindex(p);
        } else {
            maxes[p][b] = bucket.back();
            bump(p, b, -1);
        }
    }
};
