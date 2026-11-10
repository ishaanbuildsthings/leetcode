// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-strided-updates-xor/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet stridedXorQuery
// @data-structure-type: sqrt
// @complexities:
//   getAll: N
//   pointAdd: 1*sqrt(N)
//   pointAssign: 1*sqrt(N)
//   pointChmax: 1*sqrt(N)
//   pointChmin: 1*sqrt(N)
//   pointGet: 1
//   stridedXorQuery: sqrt(N)
//   build: 1*N*sqrt(N)
// @memory:
//   layout: none
//   node: xorBlocks[1*N]
//   tags: none
//   other: A[1*N] offsets[1*N]
//   note: one list per stride, in which a strided query is a contiguous range. Steps above the cutoff walk their positions

// Strided queries with point updates: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r
// (the last position used may be below r). Fix a stride and split the array by position mod stride: a strided query
// is a contiguous range of one list, so small strides are ordinary range queries, and a big stride visits few
// positions, so it walks them. All indices 0-based, ranges inclusive.
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
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct StridedQueries {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, blockStrides = 0, blockSize = 1, numBlocks = 0, treeStrides = 0;
    HotVector<T> A;
    // offsets[step * (step - 1) / 2 + residue]: where that residue class starts in that stride's list
    HotVector<int> offsets;
    HotVector<T> xorBlocks;

    // O(build) -- arr: the initial array
    explicit StridedQueries(const vector<T>& arr) {
        n = (int)arr.size();
        A = arr;
        blockStrides = min(n, max(1, (int)sqrt((double)n)));
        blockSize = blockStrides;
        numBlocks = n / blockSize + 1;
        int strides = max(blockStrides, treeStrides);
        offsets.assign((size_t)strides * (strides + 1) / 2, 0);
        for (int step = 1; step <= strides; step++) {
            int used = 0;
            for (int residue = 0; residue < step; residue++) {
                offsets[step * (step - 1) / 2 + residue] = used;
                if (residue < n) used += (n - residue + step - 1) / step;
            }
        }
        xorBlocks.assign((size_t)blockStrides * numBlocks, 0);
        for (int step = 1; step <= blockStrides; step++) {
            size_t base = (size_t)(step - 1) * numBlocks;
            int index = 0;
            for (int residue = 0; residue < step; residue++) {
                for (int i = residue; i < n; i += step, index++) {
                    xorBlocks[base + index / blockSize] ^= A[i];
                }
            }
        }
    }

    // O(n) -- the whole array
    LEETCODE_NO_SANITIZE vector<T> getAll() const { return vector<T>(A.begin(), A.end()); }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return A[i];
    }

    // a[i] = v (overwrite); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        write(i, v);
    }

    // a[i] += v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        write(i, T(A[i] + v));
    }

    // a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        write(i, max(A[i], v));
    }

    // a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        write(i, min(A[i], v));
    }

    // a[l] ^ a[l + step] ^ ..., up to at most r; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T stridedXorQuery(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedXorQuery: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedXorQuery: needs step >= 1");
        int last = l + (r - l) / step * step;
        if (step > blockStrides) {
            T res = 0;
            for (int i = l; i <= last; i += step) res ^= A[i];
            return res;
        }
        int first = listIndex(step, l), final = listIndex(step, last);
        int firstBlock = first / blockSize, lastBlock = final / blockSize;
        T res = 0;
        if (firstBlock == lastBlock) {
            for (int i = l; i <= last; i += step) res ^= A[i];
            return res;
        }
        const T* blocks = xorBlocks.data() + (size_t)(step - 1) * numBlocks;
        int leftCount = (firstBlock + 1) * blockSize - first, rightCount = final - lastBlock * blockSize + 1;
        for (int k = 0, i = l; k < leftCount; k++, i += step) res ^= A[i];
        for (int block = firstBlock + 1; block < lastBlock; block++) res ^= blocks[block];
        for (int k = 0, i = last; k < rightCount; k++, i -= step) res ^= A[i];
        return res;
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE int listIndex(int step, int i) const {
        return offsets[step * (step - 1) / 2 + i % step] + i / step;
    }

    LEETCODE_NO_SANITIZE void write(int i, T v) {
        T xorDelta = A[i] ^ v;
        A[i] = v;
        for (int step = 1; step <= blockStrides; step++) {
            int block = listIndex(step, i) / blockSize;
            xorBlocks[(size_t)(step - 1) * numBlocks + block] ^= xorDelta;
        }
    }
};
