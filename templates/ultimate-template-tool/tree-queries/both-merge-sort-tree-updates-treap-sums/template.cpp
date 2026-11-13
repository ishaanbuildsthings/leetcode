// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-merge-sort-tree-updates-treap-sums/template.cpp
// The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/merge-sort-tree-updates-treap-sums/fast.cpp
// @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeChmax edgeChmin edgeGet edgePathCountGtX edgePathCountGteX edgePathCountInValRange edgePathCountLtX edgePathCountLteX edgePathLargestLtX edgePathLargestLteX edgePathSmallestGtX edgePathSmallestGteX edgePathSumAbsDiffToX edgePathSumGtX edgePathSumGteX edgePathSumInValRange edgePathSumLtX edgePathSumLteX edgeSubtreeCountGtX edgeSubtreeCountGteX edgeSubtreeCountInValRange edgeSubtreeCountLtX edgeSubtreeCountLteX edgeSubtreeLargestLtX edgeSubtreeLargestLteX edgeSubtreeSmallestGtX edgeSubtreeSmallestGteX edgeSubtreeSumAbsDiffToX edgeSubtreeSumGtX edgeSubtreeSumGteX edgeSubtreeSumInValRange edgeSubtreeSumLtX edgeSubtreeSumLteX isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodePathCountGtX nodePathCountGteX nodePathCountInValRange nodePathCountLtX nodePathCountLteX nodePathLargestLtX nodePathLargestLteX nodePathSmallestGtX nodePathSmallestGteX nodePathSumAbsDiffToX nodePathSumGtX nodePathSumGteX nodePathSumInValRange nodePathSumLtX nodePathSumLteX nodeSubtreeCountGtX nodeSubtreeCountGteX nodeSubtreeCountInValRange nodeSubtreeCountLtX nodeSubtreeCountLteX nodeSubtreeLargestLtX nodeSubtreeLargestLteX nodeSubtreeSmallestGtX nodeSubtreeSmallestGteX nodeSubtreeSumAbsDiffToX nodeSubtreeSumGtX nodeSubtreeSumGteX nodeSubtreeSumInValRange nodeSubtreeSumLtX nodeSubtreeSumLteX parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: merge-sort-tree
// @complexities:
//   countAtDepthInSubtree: log(N)
//   depth: 1
//   edgeAdd: log^2(N) expected
//   edgeAssign: log^2(N) expected
//   edgeChmax: log^2(N) expected
//   edgeChmin: log^2(N) expected
//   edgeGet: 1
//   edgePathCountGtX: log^3(N) expected
//   edgePathCountGteX: log^3(N) expected
//   edgePathCountInValRange: log^3(N) expected
//   edgePathCountLtX: log^3(N) expected
//   edgePathCountLteX: log^3(N) expected
//   edgePathLargestLtX: log^3(N) expected
//   edgePathLargestLteX: log^3(N) expected
//   edgePathSmallestGtX: log^3(N) expected
//   edgePathSmallestGteX: log^3(N) expected
//   edgePathSumAbsDiffToX: log^3(N) expected
//   edgePathSumGtX: log^3(N) expected
//   edgePathSumGteX: log^3(N) expected
//   edgePathSumInValRange: log^3(N) expected
//   edgePathSumLtX: log^3(N) expected
//   edgePathSumLteX: log^3(N) expected
//   edgeSubtreeCountGtX: log^2(N) expected
//   edgeSubtreeCountGteX: log^2(N) expected
//   edgeSubtreeCountInValRange: log^2(N) expected
//   edgeSubtreeCountLtX: log^2(N) expected
//   edgeSubtreeCountLteX: log^2(N) expected
//   edgeSubtreeLargestLtX: log^2(N) expected
//   edgeSubtreeLargestLteX: log^2(N) expected
//   edgeSubtreeSmallestGtX: log^2(N) expected
//   edgeSubtreeSmallestGteX: log^2(N) expected
//   edgeSubtreeSumAbsDiffToX: log^2(N) expected
//   edgeSubtreeSumGtX: log^2(N) expected
//   edgeSubtreeSumGteX: log^2(N) expected
//   edgeSubtreeSumInValRange: log^2(N) expected
//   edgeSubtreeSumLtX: log^2(N) expected
//   edgeSubtreeSumLteX: log^2(N) expected
//   isAncestor: 1
//   isOnPath: log(N)
//   kthAncestor: log(N)
//   kthNodeOnPath: log(N)
//   lca: log(N)
//   lcaRootedAt: log(N)
//   median: log(N)
//   nextNodeOnPath: log(N)
//   nodeAdd: log^2(N) expected
//   nodeAssign: log^2(N) expected
//   nodeChmax: log^2(N) expected
//   nodeChmin: log^2(N) expected
//   nodeGet: 1
//   nodePathCountGtX: log^3(N) expected
//   nodePathCountGteX: log^3(N) expected
//   nodePathCountInValRange: log^3(N) expected
//   nodePathCountLtX: log^3(N) expected
//   nodePathCountLteX: log^3(N) expected
//   nodePathLargestLtX: log^3(N) expected
//   nodePathLargestLteX: log^3(N) expected
//   nodePathSmallestGtX: log^3(N) expected
//   nodePathSmallestGteX: log^3(N) expected
//   nodePathSumAbsDiffToX: log^3(N) expected
//   nodePathSumGtX: log^3(N) expected
//   nodePathSumGteX: log^3(N) expected
//   nodePathSumInValRange: log^3(N) expected
//   nodePathSumLtX: log^3(N) expected
//   nodePathSumLteX: log^3(N) expected
//   nodeSubtreeCountGtX: log^2(N) expected
//   nodeSubtreeCountGteX: log^2(N) expected
//   nodeSubtreeCountInValRange: log^2(N) expected
//   nodeSubtreeCountLtX: log^2(N) expected
//   nodeSubtreeCountLteX: log^2(N) expected
//   nodeSubtreeLargestLtX: log^2(N) expected
//   nodeSubtreeLargestLteX: log^2(N) expected
//   nodeSubtreeSmallestGtX: log^2(N) expected
//   nodeSubtreeSmallestGteX: log^2(N) expected
//   nodeSubtreeSumAbsDiffToX: log^2(N) expected
//   nodeSubtreeSumGtX: log^2(N) expected
//   nodeSubtreeSumGteX: log^2(N) expected
//   nodeSubtreeSumInValRange: log^2(N) expected
//   nodeSubtreeSumLtX: log^2(N) expected
//   nodeSubtreeSumLteX: log^2(N) expected
//   parent: 1
//   parentRootedAt: log(N)
//   pathIntersection: log(N)
//   pathNodes: K+log(N)
//   subtreeSize: 1
//   subtreeSizeRootedAt: log(N)
//   unweightedDist: log(N)
//   unweightedDistBetweenPaths: log(N)
//   unweightedDistToPath: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: key[2*N*log(N)] copies[2*N*log(N)] under[2*N*log(N)] leftChild[2*N*log(N)] rightChild[2*N*log(N)] priority[2*N*log(N)] subSum[2*N*log(N)]
//   tags: none
//   other: A[2*N] total[4*N] root[2*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: no value range and nothing up front; each update makes at most log N new treap nodes and none are reused, so N counts updates too
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.

// Merge sort tree with point updates: a segment tree over positions (bottom-up: node p >= n is a[p - n]), each inner
// node keeping its positions' values in a searchable structure (a treap keyed by value, copies counted, with subtree
// sizes / sums / xors). a[l..r] is O(log n) nodes, and a point update changes one value in each of the O(log n) nodes
// above it. All indices 0-based, ranges inclusive.
// T: int, long long, ...; sums are kept in S (long long for small T).
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
struct MergeSortTreeUpdates {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    HotVector<T> A;
    HotVector<S> total;  // total[p]: sum of node p's values
    HotVector<T> key;  // treap nodes, shared by every seg node (node 0 = the empty tree); a removed node isn't reused
    HotVector<int> copies, under, leftChild, rightChild;  // copies of the key, values in the subtree, children
    HotVector<unsigned> priority;
    HotVector<S> subSum;  // sum of the subtree's values
    HotVector<int> root;  // root[p]: node p's treap
    unsigned long long rngState;

    // O(build) -- arr: the initial array
    explicit MergeSortTreeUpdates(const vector<T>& arr) {
        n = (int)arr.size();
        A = arr;
        key.assign(1, T(0));
        copies.assign(1, 0);
        under.assign(1, 0);
        leftChild.assign(1, 0);
        rightChild.assign(1, 0);
        priority.assign(1, 0);
        subSum.assign(1, 0);
        root.assign(max(n, 1), 0);
        rngState = chrono::steady_clock::now().time_since_epoch().count() | 1;
        vector<vector<T>> sortedVals(2 * n);  // node p's values, sorted (freed once its parent has them)
        for (int i = 0; i < n; i++) sortedVals[n + i] = {A[i]};
        for (int p = n - 1; p >= 1; p--) {
            vector<T>& left = sortedVals[2 * p];
            vector<T>& right = sortedVals[2 * p + 1];
            sortedVals[p].resize(left.size() + right.size());
            merge(left.begin(), left.end(), right.begin(), right.end(), sortedVals[p].begin());
            vector<T>().swap(left);
            vector<T>().swap(right);
            root[p] = buildTreap(sortedVals[p]);
        }
        buildTotals();
    }

    // O(n) -- the whole array
    LEETCODE_NO_SANITIZE vector<T> getAll() const { return vector<T>(A.begin(), A.end()); }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return A[i];
    }

    // O(log^2(N) expected) -- a[i] = v (overwrite); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        write(i, v, "pointAssign");
    }

    // O(log^2(N) expected) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        write(i, T(A[i] + v), "pointAdd");
    }

    // O(log^2(N) expected) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        write(i, max(A[i], v), "pointChmax");
    }

    // O(log^2(N) expected) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        write(i, min(A[i], v), "pointChmin");
    }

    // O(log^2(N) expected) -- # of i in [l, r] with a[i] < x; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLtX: needs 0 <= l <= r < n");
        return countLess(l, r, x, true);
    }

    // O(log^2(N) expected) -- # of i in [l, r] with a[i] <= x; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLteX: needs 0 <= l <= r < n");
        return countLess(l, r, x, false);
    }

    // O(log^2(N) expected) -- # of i in [l, r] with a[i] > x; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGtX: needs 0 <= l <= r < n");
        return (r - l + 1) - countLess(l, r, x, false);
    }

    // O(log^2(N) expected) -- # of i in [l, r] with a[i] >= x; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGteX: needs 0 <= l <= r < n");
        return (r - l + 1) - countLess(l, r, x, true);
    }

    // O(log^2(N) expected) -- # of i in [l, r] with lowVal <= a[i] <= highVal (0 if lowVal > highVal); needs 0 <= l <=
    // r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countInValRange: needs 0 <= l <= r < n");
        if (lowVal > highVal) return 0;
        return countLess(l, r, highVal, false) - countLess(l, r, lowVal, true);
    }

    // O(log^2(N) expected) -- smallest a[i] >= x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGteX: needs 0 <= l <= r < n");
        return firstAtLeast(l, r, x, false);
    }

    // O(log^2(N) expected) -- smallest a[i] > x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGtX: needs 0 <= l <= r < n");
        return firstAtLeast(l, r, x, true);
    }

    // O(log^2(N) expected) -- largest a[i] <= x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLteX: needs 0 <= l <= r < n");
        return lastBelow(l, r, x, false);
    }

    // O(log^2(N) expected) -- largest a[i] < x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLtX: needs 0 <= l <= r < n");
        return lastBelow(l, r, x, true);
    }

    // O(log^2(N) expected) -- sum of a[i] < x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLtX: needs 0 <= l <= r < n");
        return sumLess(l, r, x, true);
    }

    // O(log^2(N) expected) -- sum of a[i] <= x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLteX: needs 0 <= l <= r < n");
        return sumLess(l, r, x, false);
    }

    // O(log^2(N) expected) -- sum of a[i] > x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumGtX: needs 0 <= l <= r < n");
        return sumAll(l, r) - sumLess(l, r, x, false);
    }

    // O(log^2(N) expected) -- sum of a[i] >= x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumGteX: needs 0 <= l <= r < n");
        return sumAll(l, r) - sumLess(l, r, x, true);
    }

    // O(log^2(N) expected) -- sum of a[i] with lowVal <= a[i] <= highVal in [l, r] (0 if lowVal > highVal); needs 0 <=
    // l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumInValRange: needs 0 <= l <= r < n");
        if (lowVal > highVal) return 0;
        return sumLess(l, r, highVal, false) - sumLess(l, r, lowVal, true);
    }

    // O(log^2(N) expected) -- sum of |a[i] - x| over [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S sumAbsDiffToX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumAbsDiffToX: needs 0 <= l <= r < n");
        long long below = countLess(l, r, x, true);
        S belowSum = sumLess(l, r, x, true), total = sumAll(l, r);
        return S(x) * below - belowSum + (total - belowSum) - S(x) * ((r - l + 1) - below);
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE void buildTotals() {  // the sum / xor of every node's values
        total.assign(2 * n, 0);
        for (int i = 0; i < n; i++) total[n + i] = A[i];
        for (int p = n - 1; p >= 1; p--) total[p] = total[2 * p] + total[2 * p + 1];
    }

    template <class F>
    LEETCODE_NO_SANITIZE void forNodes(int l, int r, F f) const {  // the O(log n) nodes that cover a[l..r]
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) f(l++);
            if (r & 1) f(--r);
        }
    }

    LEETCODE_NO_SANITIZE long long countLess(int l, int r, T x, bool strict) const {
        // # of values < x (strict) or <= x in a[l..r]
        long long res = 0;
        forNodes(l, r, [&](int p) {
            if (p >= n) res += strict ? A[p - n] < x : !(x < A[p - n]);
            else res += countBelow(p, x, strict);
        });
        return res;
    }

    LEETCODE_NO_SANITIZE optional<T> firstAtLeast(int l, int r, T x, bool strict) const {
        // smallest value > x (strict) or >= x
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

    LEETCODE_NO_SANITIZE optional<T> lastBelow(int l, int r, T x, bool strict) const {
        // largest value < x (strict) or <= x
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

    LEETCODE_NO_SANITIZE S sumLess(int l, int r, T x, bool strict) const {
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

    LEETCODE_NO_SANITIZE S sumAll(int l, int r) const {
        S res = 0;
        forNodes(l, r, [&](int p) { res += p >= n ? S(A[p - n]) : total[p]; });
        return res;
    }

    LEETCODE_NO_SANITIZE void write(int i, T v, [[maybe_unused]] const char* op) {
        T old = A[i];
        if (old == v) return;
        for (int p = (i + n) >> 1; p >= 1; p >>= 1) {
            eraseValue(p, old);
            insertValue(p, v);
            total[p] += S(v) - S(old);
        }
        A[i] = v;
    }

    LEETCODE_NO_SANITIZE unsigned nextRandom() {
        rngState ^= rngState << 7;
        rngState ^= rngState >> 9;
        return unsigned(rngState);
    }

    LEETCODE_NO_SANITIZE int newNode(T v, int count) {
        key.push_back(v);
        copies.push_back(count);
        under.push_back(0);
        leftChild.push_back(0);
        rightChild.push_back(0);
        priority.push_back(nextRandom());
        subSum.push_back(0);
        pull((int)key.size() - 1);
        return (int)key.size() - 1;
    }

    LEETCODE_NO_SANITIZE void pull(int t) {
        under[t] = under[leftChild[t]] + under[rightChild[t]] + copies[t];
        subSum[t] = subSum[leftChild[t]] + subSum[rightChild[t]] + S(key[t]) * copies[t];
    }

    LEETCODE_NO_SANITIZE int buildTreap(const vector<T>& sortedVals) {
        // a treap of sortedVals (sorted) in O(len): a Cartesian tree by priority
        vector<int> stack;
        for (size_t k = 0; k < sortedVals.size();) {
            size_t next = k;
            while (next < sortedVals.size() && !(sortedVals[k] < sortedVals[next])) next++;
            int t = newNode(sortedVals[k], int(next - k)), last = 0;
            k = next;
            while (!stack.empty() && priority[stack.back()] < priority[t]) {
                last = stack.back();
                stack.pop_back();
            }
            leftChild[t] = last;
            if (!stack.empty()) rightChild[stack.back()] = t;
            stack.push_back(t);
        }
        if (stack.empty()) return 0;
        pullAll(stack[0]);
        return stack[0];
    }

    LEETCODE_NO_SANITIZE void pullAll(int t) {  // (recursion depth = the treap's height, O(log n) expected)
        if (!t) return;
        pullAll(leftChild[t]);
        pullAll(rightChild[t]);
        pull(t);
    }

    LEETCODE_NO_SANITIZE pair<int, int> split(int t, T v, bool orEqual) {  // (keys < v, or <= v if orEqual; the rest)
        if (!t) return {0, 0};
        if (orEqual ? !(v < key[t]) : key[t] < v) {
            auto [low, high] = split(rightChild[t], v, orEqual);
            rightChild[t] = low;
            pull(t);
            return {t, high};
        }
        auto [low, high] = split(leftChild[t], v, orEqual);
        leftChild[t] = high;
        pull(t);
        return {low, t};
    }

    LEETCODE_NO_SANITIZE int join(int a, int b) {  // every key of a is below every key of b
        if (!a || !b) return a | b;
        if (priority[a] > priority[b]) {
            rightChild[a] = join(rightChild[a], b);
            pull(a);
            return a;
        }
        leftChild[b] = join(a, leftChild[b]);
        pull(b);
        return b;
    }

    LEETCODE_NO_SANITIZE void insertValue(int p, T v) {
        auto [low, rest] = split(root[p], v, false);
        auto [same, high] = split(rest, v, true);
        if (same) {
            copies[same]++;
            pull(same);
        } else {
            same = newNode(v, 1);
        }
        root[p] = join(join(low, same), high);
    }

    LEETCODE_NO_SANITIZE void eraseValue(int p, T v) {  // v is in node p
        auto [low, rest] = split(root[p], v, false);
        auto [same, high] = split(rest, v, true);
        if (--copies[same] == 0) same = 0;
        else pull(same);
        root[p] = join(join(low, same), high);
    }

    LEETCODE_NO_SANITIZE long long countBelow(int p, T x, bool strict) const {
        long long res = 0;
        for (int t = root[p]; t;) {
            if (strict ? key[t] < x : !(x < key[t])) {
                res += under[leftChild[t]] + copies[t];
                t = rightChild[t];
            } else {
                t = leftChild[t];
            }
        }
        return res;
    }

    LEETCODE_NO_SANITIZE S sumBelow(int p, T x, bool strict) const {
        S res = 0;
        for (int t = root[p]; t;) {
            if (strict ? key[t] < x : !(x < key[t])) {
                res += subSum[leftChild[t]] + S(key[t]) * copies[t];
                t = rightChild[t];
            } else {
                t = leftChild[t];
            }
        }
        return res;
    }

    LEETCODE_NO_SANITIZE optional<T> firstIn(int p, T x, bool strict) const {
        // smallest value > x (strict) or >= x in node p
        optional<T> best;
        for (int t = root[p]; t;) {
            if (strict ? x < key[t] : !(key[t] < x)) {
                best = key[t];
                t = leftChild[t];
            } else {
                t = rightChild[t];
            }
        }
        return best;
    }

    LEETCODE_NO_SANITIZE optional<T> lastIn(int p, T x, bool strict) const {
        // largest value < x (strict) or <= x in node p
        optional<T> best;
        for (int t = root[p]; t;) {
            if (strict ? key[t] < x : !(x < key[t])) {
                best = key[t];
                t = rightChild[t];
            } else {
                t = leftChild[t];
            }
        }
        return best;
    }
};

// Tree tree(edges, root, vals);
//
// edges: the tree's n - 1 edges with their weights, vector<vector<int>> (vector<vector<long long>> works too). Whether
//        nodes are 0..n-1 or 1..n is detected automatically from the edge list (smallest label is 0 -> 0..n-1,
//        otherwise 1..n; with no edges, from root)
//   {{a, b, w}, ...}     e.g. {{0, 1, 5}, {1, 2, 7}}
// root: the root node (required), e.g. 0 or 1.
// vals: the node values, vector<T> (T = long long, or int; the weights are kept as T too), vals[node] is node's value
//   nodes 0..n-1: size n        e.g. n = 3: {10, 20, 30}         node 0 -> 10
//   nodes 1..n:   size n + 1    e.g. n = 3: {0, 10, 20, 30}      vals[0] is ignored, node 1 -> 10
//
//   Tree<long long> tree({{0, 1, 5}, {1, 2, 7}}, 0, {10, 20, 30});       // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2, 5}, {2, 3, 7}}, 1, {0, 10, 20, 30});    // nodes 1..3, rooted at 1
//
// The node... ops act on the node values and the edge... ops on the edge weights: the two never affect each other. For
// nodes, a path a..b includes both a and b. For edges, a path a..b covers the edges between a and b and a subtree the
// edges below node; an edge is named by its two ends in either order, a search that finds an edge returns its lower end
// (the end farther from the root), and a query with no edges to look at (a path a..a, a leaf's subtree) says what it
// returns. Nodes go in and come out with your labels, -1 means "none", and a label that is not in the tree throws
// out_of_range. Nothing recurses, so a 10^6-node chain is fine.
//
// How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
// stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above
// (MergeSortTreeUpdates) sit over those positions: nodeSeg holds each node's value at its position, edgeSeg each edge's
// weight at its lower end's position (the root's holds no edge). A subtree is one range, and a path a..b is O(log n)
// ranges, one per chain it crosses.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    MergeSortTreeUpdates<T> nodeSeg;  // the node values, in position order
    MergeSortTreeUpdates<T> edgeSeg;  // each edge's weight, at its lower end's position

    // O(n * log n) -- builds the layout and the two range structures; throws invalid_argument when the edges are not
    // one tree on nodes 0..n-1 or 1..n, an edge has no weight, or vals has the wrong size
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root, const vector<T>& vals)
        : nodeSeg(layout(edges, root, vals)), edgeSeg(weights(edges)) {}

    // lays the tree out (fills the arrays above) and returns the values in position order
    template <typename E> vector<T> layout(const vector<vector<E>>& edges, int root, const vector<T>& vals) {
        this->root = root;
        n = (int)edges.size() + 1;
        long long least = root;
        if (!edges.empty()) {
            least = LLONG_MAX;
            for (const auto& e : edges) {
                if (e.size() != 2 && e.size() != 3)
                    throw invalid_argument("Tree: every edge needs 2 or 3 numbers, {a, b} or {a, b, w}");
                least = min({least, (long long)e[0], (long long)e[1]});
            }
        }
        if (least != 0 && least != 1)
            throw invalid_argument("Tree: nodes must be labeled 0..n-1 or 1..n, but the smallest label is " +
                                   to_string(least));
        lo = (int)least, hi = lo + n - 1;
        string nodes = to_string(lo) + ".." + to_string(hi);
        if (root < lo || root > hi)
            throw invalid_argument("Tree: root must be one of the nodes " + nodes + ", got " + to_string(root));
        int size = hi + 1;

        // the neighbors of v are adj[start[v] .. start[v + 1])
        vector<int> start(size + 1, 0), adj(2 * (n - 1));
        for (const auto& e : edges) {
            if ((long long)e[0] > hi || (long long)e[1] > hi)
                throw invalid_argument("Tree: " + to_string(n - 1) + " edges means the nodes are " + nodes +
                                       ", got the edge (" + to_string(e[0]) + ", " + to_string(e[1]) + ")");
            start[e[0] + 1]++, start[e[1] + 1]++;
        }
        for (int v = 0; v < size; v++) start[v + 1] += start[v];
        vector<int> at(start.begin(), start.end() - 1);
        for (const auto& e : edges) {
            int a = (int)e[0], b = (int)e[1];
            adj[at[a]++] = b, adj[at[b]++] = a;
        }

        // parents and depths, top down (par is -2 until a node is reached)
        par.assign(size, -2), dep.assign(size, 0);
        vector<int> bfs(n);
        int reached = 0;
        par[root] = -1, bfs[reached++] = root;
        for (int i = 0; i < reached; i++) {
            int v = bfs[i];
            for (int k = start[v]; k < start[v + 1]; k++) {
                int u = adj[k];
                if (par[u] == -2) par[u] = v, dep[u] = dep[v] + 1, bfs[reached++] = u;
            }
        }
        if (reached != n)
            throw invalid_argument("Tree: the edges do not form one tree (some node cannot be reached from root)");

        // subtree sizes bottom up, then each node's heavy child (the one with the biggest subtree)
        sz.assign(size, 1);
        for (int i = n - 1; i > 0; i--) sz[par[bfs[i]]] += sz[bfs[i]];
        vector<int> heavy(size, -1);
        for (int i = 1; i < n; i++) {
            int v = bfs[i], p = par[v];
            if (heavy[p] == -1 || sz[v] > sz[heavy[p]]) heavy[p] = v;
        }

        // positions: a preorder that always steps into the heavy child first, so a heavy chain is one stretch
        head.assign(size, 0), pos.assign(size, 0), order.assign(n, 0);
        vector<int> todo = {root};
        todo.reserve(n);
        head[root] = root;
        int t = 0;
        while (!todo.empty()) {
            int v = todo.back();
            todo.pop_back();
            pos[v] = t, order[t++] = v;
            int h = heavy[v], p = par[v];
            for (int k = start[v]; k < start[v + 1]; k++) {
                int u = adj[k];
                if (u != p && u != h) head[u] = u, todo.push_back(u);
            }
            if (h != -1) head[h] = head[v], todo.push_back(h);  // pushed last, so it is popped next
        }

        int maxDep = dep[bfs[n - 1]];
        depthStart.assign(maxDep + 2, 0), depthPos.assign(n, 0);
        for (int i = 0; i < n; i++) depthStart[dep[bfs[i]] + 1]++;
        for (int d = 0; d <= maxDep; d++) depthStart[d + 1] += depthStart[d];
        vector<int> slot(depthStart.begin(), depthStart.end() - 1);
        for (int i = 0; i < n; i++) depthPos[slot[dep[order[i]]]++] = i;
        if ((int)vals.size() != hi + 1)
            throw invalid_argument("Tree: vals[node] is node's value, so nodes " + nodes + " need vals.size() = " +
                                   to_string(hi + 1) + ", got " + to_string(vals.size()));
        vector<T> inOrder(n);
        for (int i = 0; i < n; i++) inOrder[i] = vals[order[i]];
        return inOrder;
    }

    // each edge's weight, at its lower end's position (the layout is built by the time this runs)
    template <typename E> vector<T> weights(const vector<vector<E>>& edges) {
        for (const auto& e : edges)
            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");
        // (position 0 is the root's: it holds no edge and is never read)
        vector<T> inOrder(n, edges.empty() ? T(0) : (T)edges[0][2]);
        for (const auto& e : edges) {
            int a = (int)e[0], b = (int)e[1];
            inOrder[par[a] == b ? pos[a] : pos[b]] = (T)e[2];
        }
        return inOrder;
    }

    // O(1) -- val(node)
    LEETCODE_NO_SANITIZE auto nodeGet(int node) {
        if (node < lo || node > hi) bad("nodeGet");
        return nodeSeg.pointGet(pos[node]);
    }

    // O(log^2 n) -- val(node) = x
    LEETCODE_NO_SANITIZE void nodeAssign(int node, T x) {
        if (node < lo || node > hi) bad("nodeAssign");
        nodeSeg.pointAssign(pos[node], x);
    }

    // O(log^2 n) -- val(node) += x
    LEETCODE_NO_SANITIZE void nodeAdd(int node, T x) {
        if (node < lo || node > hi) bad("nodeAdd");
        nodeSeg.pointAdd(pos[node], x);
    }

    // O(log^2 n) -- val(node) = max(val, x)
    LEETCODE_NO_SANITIZE void nodeChmax(int node, T x) {
        if (node < lo || node > hi) bad("nodeChmax");
        nodeSeg.pointChmax(pos[node], x);
    }

    // O(log^2 n) -- val(node) = min(val, x)
    LEETCODE_NO_SANITIZE void nodeChmin(int node, T x) {
        if (node < lo || node > hi) bad("nodeChmin");
        nodeSeg.pointChmin(pos[node], x);
    }

    // O(log^3 n) -- how many node values on the path a..b are < x
    LEETCODE_NO_SANITIZE auto nodePathCountLtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountLtX");
        using R = decltype(nodeSeg.countLtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.countLtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.countLtX(l, r, x);
        res += v;
        return res;
    }

    // O(log^3 n) -- how many node values on the path a..b are <= x
    LEETCODE_NO_SANITIZE auto nodePathCountLteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountLteX");
        using R = decltype(nodeSeg.countLteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.countLteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.countLteX(l, r, x);
        res += v;
        return res;
    }

    // O(log^3 n) -- how many node values on the path a..b are > x
    LEETCODE_NO_SANITIZE auto nodePathCountGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountGtX");
        using R = decltype(nodeSeg.countGtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.countGtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.countGtX(l, r, x);
        res += v;
        return res;
    }

    // O(log^3 n) -- how many node values on the path a..b are >= x
    LEETCODE_NO_SANITIZE auto nodePathCountGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountGteX");
        using R = decltype(nodeSeg.countGteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.countGteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.countGteX(l, r, x);
        res += v;
        return res;
    }

    // O(log^3 n) -- how many node values on the path a..b are in [low, high]
    LEETCODE_NO_SANITIZE auto nodePathCountInValRange(int a, int b, T low, T high) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountInValRange");
        using R = decltype(nodeSeg.countInValRange(0, 0, low, high));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.countInValRange(pos[head[a]], pos[a], low, high);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.countInValRange(l, r, low, high);
        res += v;
        return res;
    }

    // O(log^3 n) -- sum of the node values on the path a..b that are < x
    LEETCODE_NO_SANITIZE auto nodePathSumLtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumLtX");
        using R = decltype(nodeSeg.sumLtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.sumLtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.sumLtX(l, r, x);
        res += v;
        return res;
    }

    // O(log^3 n) -- sum of the node values on the path a..b that are <= x
    LEETCODE_NO_SANITIZE auto nodePathSumLteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumLteX");
        using R = decltype(nodeSeg.sumLteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.sumLteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.sumLteX(l, r, x);
        res += v;
        return res;
    }

    // O(log^3 n) -- sum of the node values on the path a..b that are > x
    LEETCODE_NO_SANITIZE auto nodePathSumGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumGtX");
        using R = decltype(nodeSeg.sumGtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.sumGtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.sumGtX(l, r, x);
        res += v;
        return res;
    }

    // O(log^3 n) -- sum of the node values on the path a..b that are >= x
    LEETCODE_NO_SANITIZE auto nodePathSumGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumGteX");
        using R = decltype(nodeSeg.sumGteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.sumGteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.sumGteX(l, r, x);
        res += v;
        return res;
    }

    // O(log^3 n) -- sum of the node values on the path a..b in [low, high]
    LEETCODE_NO_SANITIZE auto nodePathSumInValRange(int a, int b, T low, T high) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumInValRange");
        using R = decltype(nodeSeg.sumInValRange(0, 0, low, high));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.sumInValRange(pos[head[a]], pos[a], low, high);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.sumInValRange(l, r, low, high);
        res += v;
        return res;
    }

    // O(log^3 n) -- sum of |val - x| over the node values on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathSumAbsDiffToX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSumAbsDiffToX");
        using R = decltype(nodeSeg.sumAbsDiffToX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.sumAbsDiffToX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.sumAbsDiffToX(l, r, x);
        res += v;
        return res;
    }

    // O(log^3 n) -- smallest of the node values on the path a..b that is >= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathSmallestGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSmallestGteX");
        using R = decltype(nodeSeg.smallestGteX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.smallestGteX(pos[head[a]], pos[a], x);
            if (v && (!res || *v < *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.smallestGteX(l, r, x);
        if (v && (!res || *v < *res)) res = v;
        return res;
    }

    // O(log^3 n) -- smallest of the node values on the path a..b that is > x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathSmallestGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSmallestGtX");
        using R = decltype(nodeSeg.smallestGtX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.smallestGtX(pos[head[a]], pos[a], x);
            if (v && (!res || *v < *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.smallestGtX(l, r, x);
        if (v && (!res || *v < *res)) res = v;
        return res;
    }

    // O(log^3 n) -- largest of the node values on the path a..b that is <= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathLargestLteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLargestLteX");
        using R = decltype(nodeSeg.largestLteX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.largestLteX(pos[head[a]], pos[a], x);
            if (v && (!res || *v > *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.largestLteX(l, r, x);
        if (v && (!res || *v > *res)) res = v;
        return res;
    }

    // O(log^3 n) -- largest of the node values on the path a..b that is < x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodePathLargestLtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLargestLtX");
        using R = decltype(nodeSeg.largestLtX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.largestLtX(pos[head[a]], pos[a], x);
            if (v && (!res || *v > *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.largestLtX(l, r, x);
        if (v && (!res || *v > *res)) res = v;
        return res;
    }

    // O(log^2 n) -- how many node values in node's subtree are < x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountLtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountLtX");
        int l = pos[node];
        return nodeSeg.countLtX(l, l + sz[node] - 1, x);
    }

    // O(log^2 n) -- how many node values in node's subtree are <= x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountLteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountLteX");
        int l = pos[node];
        return nodeSeg.countLteX(l, l + sz[node] - 1, x);
    }

    // O(log^2 n) -- how many node values in node's subtree are > x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountGtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountGtX");
        int l = pos[node];
        return nodeSeg.countGtX(l, l + sz[node] - 1, x);
    }

    // O(log^2 n) -- how many node values in node's subtree are >= x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountGteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountGteX");
        int l = pos[node];
        return nodeSeg.countGteX(l, l + sz[node] - 1, x);
    }

    // O(log^2 n) -- how many node values in node's subtree are in [low, high]
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountInValRange(int node, T low, T high) {
        if (node < lo || node > hi) bad("nodeSubtreeCountInValRange");
        int l = pos[node];
        return nodeSeg.countInValRange(l, l + sz[node] - 1, low, high);
    }

    // O(log^2 n) -- sum of the node values in node's subtree that are < x
    LEETCODE_NO_SANITIZE auto nodeSubtreeSumLtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeSumLtX");
        int l = pos[node];
        return nodeSeg.sumLtX(l, l + sz[node] - 1, x);
    }

    // O(log^2 n) -- sum of the node values in node's subtree that are <= x
    LEETCODE_NO_SANITIZE auto nodeSubtreeSumLteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeSumLteX");
        int l = pos[node];
        return nodeSeg.sumLteX(l, l + sz[node] - 1, x);
    }

    // O(log^2 n) -- sum of the node values in node's subtree that are > x
    LEETCODE_NO_SANITIZE auto nodeSubtreeSumGtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeSumGtX");
        int l = pos[node];
        return nodeSeg.sumGtX(l, l + sz[node] - 1, x);
    }

    // O(log^2 n) -- sum of the node values in node's subtree that are >= x
    LEETCODE_NO_SANITIZE auto nodeSubtreeSumGteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeSumGteX");
        int l = pos[node];
        return nodeSeg.sumGteX(l, l + sz[node] - 1, x);
    }

    // O(log^2 n) -- sum of the node values in node's subtree in [low, high]
    LEETCODE_NO_SANITIZE auto nodeSubtreeSumInValRange(int node, T low, T high) {
        if (node < lo || node > hi) bad("nodeSubtreeSumInValRange");
        int l = pos[node];
        return nodeSeg.sumInValRange(l, l + sz[node] - 1, low, high);
    }

    // O(log^2 n) -- sum of |val - x| over the node values in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeSumAbsDiffToX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeSumAbsDiffToX");
        int l = pos[node];
        return nodeSeg.sumAbsDiffToX(l, l + sz[node] - 1, x);
    }

    // O(log^2 n) -- smallest of the node values in node's subtree that is >= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeSmallestGteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeSmallestGteX");
        int l = pos[node];
        return nodeSeg.smallestGteX(l, l + sz[node] - 1, x);
    }

    // O(log^2 n) -- smallest of the node values in node's subtree that is > x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeSmallestGtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeSmallestGtX");
        int l = pos[node];
        return nodeSeg.smallestGtX(l, l + sz[node] - 1, x);
    }

    // O(log^2 n) -- largest of the node values in node's subtree that is <= x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeLargestLteX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeLargestLteX");
        int l = pos[node];
        return nodeSeg.largestLteX(l, l + sz[node] - 1, x);
    }

    // O(log^2 n) -- largest of the node values in node's subtree that is < x (nullopt if none)
    LEETCODE_NO_SANITIZE auto nodeSubtreeLargestLtX(int node, T x) {
        if (node < lo || node > hi) bad("nodeSubtreeLargestLtX");
        int l = pos[node];
        return nodeSeg.largestLtX(l, l + sz[node] - 1, x);
    }

    // the position that holds the edge a - b: its lower end's (a and b in either order)
    LEETCODE_NO_SANITIZE int edgeAt(const char* name, int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad(name);
        if (par[a] == b) return pos[a];
        if (par[b] == a) return pos[b];
        throw out_of_range(string(name) + ": needs an edge between a and b");
    }

    // O(1) -- weight(a - b); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE auto edgeGet(int a, int b) {
        return edgeSeg.pointGet(edgeAt("edgeGet", a, b));
    }

    // O(log^2 n) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeAssign(int a, int b, T w) {
        edgeSeg.pointAssign(edgeAt("edgeAssign", a, b), w);
    }

    // O(log^2 n) -- weight(a - b) += w; a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeAdd(int a, int b, T w) {
        edgeSeg.pointAdd(edgeAt("edgeAdd", a, b), w);
    }

    // O(log^2 n) -- weight(a - b) = max(weight, w); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeChmax(int a, int b, T w) {
        edgeSeg.pointChmax(edgeAt("edgeChmax", a, b), w);
    }

    // O(log^2 n) -- weight(a - b) = min(weight, w); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeChmin(int a, int b, T w) {
        edgeSeg.pointChmin(edgeAt("edgeChmin", a, b), w);
    }

    // O(log^3 n) -- how many edge weights on the path a..b are < x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountLtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountLtX");
        using R = decltype(edgeSeg.countLtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.countLtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.countLtX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log^3 n) -- how many edge weights on the path a..b are <= x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountLteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountLteX");
        using R = decltype(edgeSeg.countLteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.countLteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.countLteX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log^3 n) -- how many edge weights on the path a..b are > x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountGtX");
        using R = decltype(edgeSeg.countGtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.countGtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.countGtX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log^3 n) -- how many edge weights on the path a..b are >= x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountGteX");
        using R = decltype(edgeSeg.countGteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.countGteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.countGteX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log^3 n) -- how many edge weights on the path a..b are in [low, high]; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountInValRange(int a, int b, T low, T high) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountInValRange");
        using R = decltype(edgeSeg.countInValRange(0, 0, low, high));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.countInValRange(pos[head[a]], pos[a], low, high);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.countInValRange(l + 1, r, low, high);
            res += v;
        }
        return res;
    }

    // O(log^3 n) -- sum of the edge weights on the path a..b that are < x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathSumLtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumLtX");
        using R = decltype(edgeSeg.sumLtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.sumLtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.sumLtX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log^3 n) -- sum of the edge weights on the path a..b that are <= x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathSumLteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumLteX");
        using R = decltype(edgeSeg.sumLteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.sumLteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.sumLteX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log^3 n) -- sum of the edge weights on the path a..b that are > x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathSumGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumGtX");
        using R = decltype(edgeSeg.sumGtX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.sumGtX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.sumGtX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log^3 n) -- sum of the edge weights on the path a..b that are >= x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathSumGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumGteX");
        using R = decltype(edgeSeg.sumGteX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.sumGteX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.sumGteX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log^3 n) -- sum of the edge weights on the path a..b in [low, high]; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathSumInValRange(int a, int b, T low, T high) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumInValRange");
        using R = decltype(edgeSeg.sumInValRange(0, 0, low, high));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.sumInValRange(pos[head[a]], pos[a], low, high);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.sumInValRange(l + 1, r, low, high);
            res += v;
        }
        return res;
    }

    // O(log^3 n) -- sum of |weight - x| over the edge weights on the path a..b; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathSumAbsDiffToX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSumAbsDiffToX");
        using R = decltype(edgeSeg.sumAbsDiffToX(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.sumAbsDiffToX(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.sumAbsDiffToX(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(log^3 n) -- smallest of the edge weights on the path a..b that is >= x (nullopt if none); nullopt when a == b
    // (no edges)
    LEETCODE_NO_SANITIZE auto edgePathSmallestGteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSmallestGteX");
        using R = decltype(edgeSeg.smallestGteX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.smallestGteX(pos[head[a]], pos[a], x);
            if (v && (!res || *v < *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.smallestGteX(l + 1, r, x);
            if (v && (!res || *v < *res)) res = v;
        }
        return res;
    }

    // O(log^3 n) -- smallest of the edge weights on the path a..b that is > x (nullopt if none); nullopt when a == b
    // (no edges)
    LEETCODE_NO_SANITIZE auto edgePathSmallestGtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSmallestGtX");
        using R = decltype(edgeSeg.smallestGtX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.smallestGtX(pos[head[a]], pos[a], x);
            if (v && (!res || *v < *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.smallestGtX(l + 1, r, x);
            if (v && (!res || *v < *res)) res = v;
        }
        return res;
    }

    // O(log^3 n) -- largest of the edge weights on the path a..b that is <= x (nullopt if none); nullopt when a == b
    // (no edges)
    LEETCODE_NO_SANITIZE auto edgePathLargestLteX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLargestLteX");
        using R = decltype(edgeSeg.largestLteX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.largestLteX(pos[head[a]], pos[a], x);
            if (v && (!res || *v > *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.largestLteX(l + 1, r, x);
            if (v && (!res || *v > *res)) res = v;
        }
        return res;
    }

    // O(log^3 n) -- largest of the edge weights on the path a..b that is < x (nullopt if none); nullopt when a == b (no
    // edges)
    LEETCODE_NO_SANITIZE auto edgePathLargestLtX(int a, int b, T x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLargestLtX");
        using R = decltype(edgeSeg.largestLtX(0, 0, x));
        R res = R();
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.largestLtX(pos[head[a]], pos[a], x);
            if (v && (!res || *v > *res)) res = v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.largestLtX(l + 1, r, x);
            if (v && (!res || *v > *res)) res = v;
        }
        return res;
    }

    // O(log^2 n) -- how many edge weights in node's subtree are < x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountLtX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountLtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.countLtX(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.countLtX(l, r, x);
    }

    // O(log^2 n) -- how many edge weights in node's subtree are <= x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountLteX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountLteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.countLteX(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.countLteX(l, r, x);
    }

    // O(log^2 n) -- how many edge weights in node's subtree are > x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountGtX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountGtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.countGtX(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.countGtX(l, r, x);
    }

    // O(log^2 n) -- how many edge weights in node's subtree are >= x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountGteX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountGteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.countGteX(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.countGteX(l, r, x);
    }

    // O(log^2 n) -- how many edge weights in node's subtree are in [low, high]; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountInValRange(int node, T low, T high) {
        if (node < lo || node > hi) bad("edgeSubtreeCountInValRange");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.countInValRange(0, 0, low, high));
        if (l > r) return R(0);
        return edgeSeg.countInValRange(l, r, low, high);
    }

    // O(log^2 n) -- sum of the edge weights in node's subtree that are < x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSumLtX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeSumLtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.sumLtX(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.sumLtX(l, r, x);
    }

    // O(log^2 n) -- sum of the edge weights in node's subtree that are <= x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSumLteX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeSumLteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.sumLteX(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.sumLteX(l, r, x);
    }

    // O(log^2 n) -- sum of the edge weights in node's subtree that are > x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSumGtX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeSumGtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.sumGtX(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.sumGtX(l, r, x);
    }

    // O(log^2 n) -- sum of the edge weights in node's subtree that are >= x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSumGteX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeSumGteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.sumGteX(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.sumGteX(l, r, x);
    }

    // O(log^2 n) -- sum of the edge weights in node's subtree in [low, high]; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSumInValRange(int node, T low, T high) {
        if (node < lo || node > hi) bad("edgeSubtreeSumInValRange");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.sumInValRange(0, 0, low, high));
        if (l > r) return R(0);
        return edgeSeg.sumInValRange(l, r, low, high);
    }

    // O(log^2 n) -- sum of |weight - x| over the edge weights in node's subtree; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSumAbsDiffToX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeSumAbsDiffToX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.sumAbsDiffToX(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.sumAbsDiffToX(l, r, x);
    }

    // O(log^2 n) -- smallest of the edge weights in node's subtree that is >= x (nullopt if none); nullopt when node is
    // a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSmallestGteX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeSmallestGteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.smallestGteX(0, 0, x));
        if (l > r) return R();
        return edgeSeg.smallestGteX(l, r, x);
    }

    // O(log^2 n) -- smallest of the edge weights in node's subtree that is > x (nullopt if none); nullopt when node is
    // a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeSmallestGtX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeSmallestGtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.smallestGtX(0, 0, x));
        if (l > r) return R();
        return edgeSeg.smallestGtX(l, r, x);
    }

    // O(log^2 n) -- largest of the edge weights in node's subtree that is <= x (nullopt if none); nullopt when node is
    // a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeLargestLteX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeLargestLteX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.largestLteX(0, 0, x));
        if (l > r) return R();
        return edgeSeg.largestLteX(l, r, x);
    }

    // O(log^2 n) -- largest of the edge weights in node's subtree that is < x (nullopt if none); nullopt when node is a
    // leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeLargestLtX(int node, T x) {
        if (node < lo || node > hi) bad("edgeSubtreeLargestLtX");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.largestLtX(0, 0, x));
        if (l > r) return R();
        return edgeSeg.largestLtX(l, r, x);
    }

    [[noreturn]] void bad(const char* name) const {
        throw out_of_range(string(name) + ": needs " + to_string(lo) + " <= node <= " + to_string(hi));
    }

    LEETCODE_NO_SANITIZE int lcaOf(int a, int b) const {
        while (head[a] != head[b]) {
            if (dep[head[a]] > dep[head[b]]) a = par[head[a]];
            else b = par[head[b]];
        }
        return dep[a] < dep[b] ? a : b;
    }

    // the node k steps above node (k <= its depth): a whole chain at a time
    LEETCODE_NO_SANITIZE int kthOf(int node, int k) const {
        while (true) {
            int h = head[node], d = pos[node] - pos[h];
            if (k <= d) return order[pos[node] - k];
            k -= d + 1;
            node = par[h];
        }
    }

    LEETCODE_NO_SANITIZE int distOf(int a, int b) const { return dep[a] + dep[b] - 2 * dep[lcaOf(a, b)]; }

    // of the three pairwise lcas two are equal and the third, the deeper one, is the median
    LEETCODE_NO_SANITIZE int medianOf(int a, int b, int c) const {
        int x = lcaOf(a, b), y = lcaOf(a, c), z = lcaOf(b, c);
        if (dep[y] > dep[x]) x = y;
        return dep[z] > dep[x] ? z : x;
    }

    LEETCODE_NO_SANITIZE bool above(int a, int b) const { return pos[a] <= pos[b] && pos[b] < pos[a] + sz[a]; }

    LEETCODE_NO_SANITIZE bool onPath(int a, int b, int node) const {
        return above(lcaOf(a, b), node) && (above(node, a) || above(node, b));
    }

    // the neighbor of a on the way to b (a != b): the child holding b when b is below a, else a's parent
    LEETCODE_NO_SANITIZE int nextOf(int a, int b) const {
        return above(a, b) ? kthOf(b, dep[b] - dep[a] - 1) : par[a];
    }

    LEETCODE_NO_SANITIZE int lowerPos(int s, int e, int x) const {  // first index in [s, e) with depthPos >= x
        while (s < e) {
            int m = (s + e) >> 1;
            if (depthPos[m] < x) s = m + 1;
            else e = m;
        }
        return s;
    }

    // O(log n) -- lowest common ancestor of a and b
    LEETCODE_NO_SANITIZE int lca(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("lca");
        return lcaOf(a, b);
    }

    // O(log n) -- number of edges on the path a..b
    LEETCODE_NO_SANITIZE int unweightedDist(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("unweightedDist");
        return distOf(a, b);
    }

    // O(1) -- edges from the root to node (the root is depth 0)
    LEETCODE_NO_SANITIZE int depth(int node) const {
        if (node < lo || node > hi) bad("depth");
        return dep[node];
    }

    // O(1) -- node's parent (-1 for the root)
    LEETCODE_NO_SANITIZE int parent(int node) const {
        if (node < lo || node > hi) bad("parent");
        return par[node];
    }

    // O(log n) -- the node k steps above node (k = 0 is node itself; -1 if that is past the root); needs k >= 0
    LEETCODE_NO_SANITIZE int kthAncestor(int node, int k) const {
        if (node < lo || node > hi) bad("kthAncestor");
        if (k < 0) throw out_of_range("kthAncestor: needs k >= 0");
        return k <= dep[node] ? kthOf(node, k) : -1;
    }

    // O(1) -- is a an ancestor of b? (true when a == b)
    LEETCODE_NO_SANITIZE bool isAncestor(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("isAncestor");
        return above(a, b);
    }

    // O(1) -- number of nodes in node's subtree (node included)
    LEETCODE_NO_SANITIZE int subtreeSize(int node) const {
        if (node < lo || node > hi) bad("subtreeSize");
        return sz[node];
    }

    // O(log n) -- number of nodes in node's subtree at depth d (the root is depth 0); 0 when there are none
    LEETCODE_NO_SANITIZE int countAtDepthInSubtree(int node, int d) const {
        if (node < lo || node > hi) bad("countAtDepthInSubtree");
        if (d < 0 || d + 1 >= (int)depthStart.size()) return 0;
        int s = depthStart[d], e = depthStart[d + 1], l = pos[node];
        return lowerPos(s, e, l + sz[node]) - lowerPos(s, e, l);
    }

    // O(log n) -- lca of a and b if the tree were rooted at r instead
    LEETCODE_NO_SANITIZE int lcaRootedAt(int r, int a, int b) const {
        if (r < lo || r > hi || a < lo || a > hi || b < lo || b > hi) bad("lcaRootedAt");
        return medianOf(a, b, r);
    }

    // O(log n) -- node's parent if the tree were rooted at r (-1 when node == r)
    LEETCODE_NO_SANITIZE int parentRootedAt(int r, int node) const {
        if (r < lo || r > hi || node < lo || node > hi) bad("parentRootedAt");
        return node == r ? -1 : nextOf(node, r);
    }

    // O(log n) -- size of node's subtree if the tree were rooted at r
    LEETCODE_NO_SANITIZE int subtreeSizeRootedAt(int r, int node) const {
        if (r < lo || r > hi || node < lo || node > hi) bad("subtreeSizeRootedAt");
        if (node == r) return n;
        // r hangs below node: everything but the child holding r
        if (above(node, r)) return n - sz[kthOf(r, dep[r] - dep[node] - 1)];
        return sz[node];
    }

    // O(log n) -- the kth node walking a -> b (k = 0 is a, k = unweightedDist(a, b) is b; -1 if k is past b); needs
    // k >= 0
    LEETCODE_NO_SANITIZE int kthNodeOnPath(int a, int b, int k) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("kthNodeOnPath");
        if (k < 0) throw out_of_range("kthNodeOnPath: needs k >= 0");
        int c = lcaOf(a, b), up = dep[a] - dep[c], total = up + dep[b] - dep[c];
        if (k > total) return -1;
        return k <= up ? kthOf(a, k) : kthOf(b, total - k);
    }

    // O(log n) -- the neighbor of a one step toward b (-1 if a == b)
    LEETCODE_NO_SANITIZE int nextNodeOnPath(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nextNodeOnPath");
        return a == b ? -1 : nextOf(a, b);
    }

    // O(log n) -- does the path a..b pass through node? (a and b count)
    LEETCODE_NO_SANITIZE bool isOnPath(int a, int b, int node) const {
        if (a < lo || a > hi || b < lo || b > hi || node < lo || node > hi) bad("isOnPath");
        return onPath(a, b, node);
    }

    // O(log n) -- fewest edges from node to any node on the path a..b (0 if node is on it)
    LEETCODE_NO_SANITIZE int unweightedDistToPath(int a, int b, int node) const {
        if (a < lo || a > hi || b < lo || b > hi || node < lo || node > hi) bad("unweightedDistToPath");
        return distOf(node, medianOf(a, b, node));
    }

    // O(log n) -- fewest edges between any node on path a..b and any node on path c..d (0 if they share a node)
    LEETCODE_NO_SANITIZE int unweightedDistBetweenPaths(int a, int b, int c, int d) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi || d < lo || d > hi)
            bad("unweightedDistBetweenPaths");
        int p = medianOf(a, b, c);  // where c's side meets the path a..b
        if (p != medianOf(a, b, d)) return 0;  // c and d meet it at different nodes, so c..d runs along it
        return distOf(p, medianOf(c, d, p));
    }

    // O(log n) -- the one node that lies on all three paths between a, b and c
    LEETCODE_NO_SANITIZE int median(int a, int b, int c) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi) bad("median");
        return medianOf(a, b, c);
    }

    // O(log n) -- the shared part of paths a..b and c..d as its two end nodes {p, q}, p first walking a -> b; p == q
    // if they share one node; {-1, -1} if they share none
    LEETCODE_NO_SANITIZE pair<int, int> pathIntersection(int a, int b, int c, int d) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi || d < lo || d > hi) bad("pathIntersection");
        int p = medianOf(a, b, c), q = medianOf(a, b, d);  // where c's side and d's side meet the path a..b
        if (p == q) return onPath(c, d, p) ? pair<int, int>{p, p} : pair<int, int>{-1, -1};
        return distOf(a, p) < distOf(a, q) ? pair<int, int>{p, q} : pair<int, int>{q, p};
    }

    // O(K + log n) -- every node on the path a..b, in order from a (K = how many)
    LEETCODE_NO_SANITIZE vector<int> pathNodes(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("pathNodes");
        int c = lcaOf(a, b), up = dep[a] - dep[c], len = up + dep[b] - dep[c] + 1;
        vector<int> out(len);
        int* p = out.data();
        for (int i = 0; a != c; a = par[a]) p[i++] = a;
        p[up] = c;
        for (int i = len - 1; b != c; b = par[b]) p[i--] = b;
        return out;
    }
};
