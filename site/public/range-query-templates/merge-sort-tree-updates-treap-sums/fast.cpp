// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/merge-sort-tree-updates-treap-sums/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countGtX countGteX countInValRange countLtX countLteX getAll largestLtX largestLteX pointAdd pointAssign pointChmax pointChmin pointGet smallestGtX smallestGteX sumAbsDiffToX sumGtX sumGteX sumInValRange sumLtX sumLteX
// @data-structure-type: merge-sort-tree
// @fractional-cascading: no
// @complexities:
//   countGtX: log^2(N) expected
//   countGteX: log^2(N) expected
//   countInValRange: log^2(N) expected
//   countLtX: log^2(N) expected
//   countLteX: log^2(N) expected
//   getAll: N
//   largestLtX: log^2(N) expected
//   largestLteX: log^2(N) expected
//   pointAdd: log^2(N) expected
//   pointAssign: log^2(N) expected
//   pointChmax: log^2(N) expected
//   pointChmin: log^2(N) expected
//   pointGet: 1
//   smallestGtX: log^2(N) expected
//   smallestGteX: log^2(N) expected
//   sumAbsDiffToX: log^2(N) expected
//   sumGtX: log^2(N) expected
//   sumGteX: log^2(N) expected
//   sumInValRange: log^2(N) expected
//   sumLtX: log^2(N) expected
//   sumLteX: log^2(N) expected
//   build: N*log(N)
// @memory:
//   layout: none
//   node: key[1*N*log(N)] copies[1*N*log(N)] under[1*N*log(N)] leftChild[1*N*log(N)] rightChild[1*N*log(N)] priority[1*N*log(N)] subSum[1*N*log(N)]
//   tags: none
//   other: A[1*N] total[2*N] root[1*N]
//   note: no value range and nothing up front; each update makes at most log N new treap nodes and none are reused, so N counts updates too

// Merge sort tree with point updates: a segment tree over positions (bottom-up: node p >= n is a[p - n]), each
// inner node keeping its positions' values in a searchable structure (a treap keyed by value, copies counted, with subtree sizes / sums / xors). a[l..r] is O(log n) nodes, and a
// point update changes one value in each of the O(log n) nodes above it. All indices 0-based, ranges inclusive.
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

    // O(log^2(N) expected) -- # of i in [l, r] with lowVal <= a[i] <= highVal (0 if lowVal > highVal); needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE long long countInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countInValRange: needs 0 <= l <= r < n");
        if (lowVal > highVal) return 0;
        return countLess(l, r, highVal, false) - countLess(l, r, lowVal, true);
    }

    // O(log^2(N) expected) -- smallest a[i] >= x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGteX: needs 0 <= l <= r < n");
        return firstAtLeast(l, r, x, false);
    }

    // O(log^2(N) expected) -- smallest a[i] > x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGtX: needs 0 <= l <= r < n");
        return firstAtLeast(l, r, x, true);
    }

    // O(log^2(N) expected) -- largest a[i] <= x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLteX: needs 0 <= l <= r < n");
        return lastBelow(l, r, x, false);
    }

    // O(log^2(N) expected) -- largest a[i] < x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws out_of_range
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

    // O(log^2(N) expected) -- sum of a[i] with lowVal <= a[i] <= highVal in [l, r] (0 if lowVal > highVal); needs 0 <= l <= r < n, else throws out_of_range
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

    LEETCODE_NO_SANITIZE int buildTreap(const vector<T>& sortedVals) {  // a treap of sortedVals (sorted) in O(len): a Cartesian tree by priority
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

    LEETCODE_NO_SANITIZE optional<T> firstIn(int p, T x, bool strict) const {  // smallest value > x (strict) or >= x in node p
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

    LEETCODE_NO_SANITIZE optional<T> lastIn(int p, T x, bool strict) const {  // largest value < x (strict) or <= x in node p
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
