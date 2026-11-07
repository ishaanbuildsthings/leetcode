// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sqrt-strided-updates-xor-min-gcd-and-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet stridedAndQuery stridedGcd stridedMin stridedOrQuery stridedXorQuery
// @data-structure-type: sqrt
// @complexities:
//   getAll: N
//   pointAdd: 1*sqrt(N)+4*sqrt(NlogN)+sqrt(N/logN)*log(U) ?
//   pointAssign: 1*sqrt(N)+4*sqrt(NlogN)+sqrt(N/logN)*log(U) ?
//   pointChmax: 1*sqrt(N)+4*sqrt(NlogN)+sqrt(N/logN)*log(U) ?
//   pointChmin: 1*sqrt(N)+4*sqrt(NlogN)+sqrt(N/logN)*log(U) ?
//   pointGet: 1
//   stridedAndQuery: sqrt(NlogN)
//   stridedGcd: sqrt(NlogN)+log(U) ?
//   stridedMin: sqrt(NlogN)
//   stridedOrQuery: sqrt(NlogN)
//   stridedXorQuery: sqrt(N)
//   build: 1*N*sqrt(N)+8*N*sqrt(N/logN)+N*sqrt(N/logN)*log(U) ?
// @memory:
//   layout: none
//   node: xorBlocks[1*N] minTree[2*N*sqrt(N/logN)] gcdTree[2*N*sqrt(N/logN)] andTree[2*N*sqrt(N/logN)] orTree[2*N*sqrt(N/logN)]
//   tags: none
//   other: A[1*N] offsets[1*N]
//   note: one list per stride, in which a strided query is a contiguous range. Steps above the cutoff walk their positions

// Strided queries with point updates: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r
// (the last position used may be below r). Fix a stride and split the array by position mod stride: a strided query
// is a contiguous range of one list, so small strides are ordinary range queries, and a big stride visits few
// positions, so it walks them. All indices 0-based, ranges inclusive.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct StridedQueries {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, blockStrides = 0, blockSize = 1, numBlocks = 0, treeStrides = 0;
    vector<T> A;
    vector<int> offsets;  // offsets[step * (step - 1) / 2 + residue]: where that residue class starts in that stride's list
    vector<T> xorBlocks;
    vector<T> minTree;
    vector<T> gcdTree;
    vector<T> andTree;
    vector<T> orTree;

    // O(build) -- arr: the initial array. cutoff: seg trees are kept for steps up to it (more memory and slower
    // updates, faster big-step queries); leave it out for sqrt(n / log n)
    explicit StridedQueries(const vector<T>& arr, int cutoff = -1) {
        n = (int)arr.size();
        A = arr;
        blockStrides = max(1, min(n, (int)sqrt((double)n)));
        blockSize = blockStrides;
        numBlocks = n / blockSize + 1;
        treeStrides = cutoff != -1 ? cutoff : max(1, min(n, (int)sqrt(n / max(1.0, log2(n + 1.0)))));
        if (treeStrides < 0 || treeStrides > n) throw out_of_range("StridedQueries: needs 0 <= cutoff <= n");
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
        minTree.assign((size_t)treeStrides * 2 * n, T(0));
        for (int step = 1; step <= treeStrides; step++) {
            T* tree = minTree.data() + (size_t)(step - 1) * 2 * n;
            int index = n;
            for (int residue = 0; residue < step; residue++) {
                for (int i = residue; i < n; i += step) tree[index++] = A[i];
            }
            for (int node = n - 1; node >= 1; node--) tree[node] = min(tree[2 * node], tree[2 * node + 1]);
        }
        gcdTree.assign((size_t)treeStrides * 2 * n, T(0));
        for (int step = 1; step <= treeStrides; step++) {
            T* tree = gcdTree.data() + (size_t)(step - 1) * 2 * n;
            int index = n;
            for (int residue = 0; residue < step; residue++) {
                for (int i = residue; i < n; i += step) tree[index++] = A[i];
            }
            for (int node = n - 1; node >= 1; node--) tree[node] = std::gcd(tree[2 * node], tree[2 * node + 1]);
        }
        andTree.assign((size_t)treeStrides * 2 * n, T(0));
        for (int step = 1; step <= treeStrides; step++) {
            T* tree = andTree.data() + (size_t)(step - 1) * 2 * n;
            int index = n;
            for (int residue = 0; residue < step; residue++) {
                for (int i = residue; i < n; i += step) tree[index++] = A[i];
            }
            for (int node = n - 1; node >= 1; node--) tree[node] = (tree[2 * node] & tree[2 * node + 1]);
        }
        orTree.assign((size_t)treeStrides * 2 * n, T(0));
        for (int step = 1; step <= treeStrides; step++) {
            T* tree = orTree.data() + (size_t)(step - 1) * 2 * n;
            int index = n;
            for (int residue = 0; residue < step; residue++) {
                for (int i = residue; i < n; i += step) tree[index++] = A[i];
            }
            for (int node = n - 1; node >= 1; node--) tree[node] = (tree[2 * node] | tree[2 * node + 1]);
        }
    }

    // O(n) -- the whole array
    vector<T> getAll() const { return vector<T>(A.begin(), A.end()); }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return A[i];
    }

    // a[i] = v (overwrite); needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        write(i, v);
    }

    // a[i] += v; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        write(i, T(A[i] + v));
    }

    // a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        write(i, max(A[i], v));
    }

    // a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        write(i, min(A[i], v));
    }

    // a[l] ^ a[l + step] ^ ..., up to at most r; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    T stridedXorQuery(int l, int r, int step) {
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

    // min of a[l], a[l + step], ..., up to at most r; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    T stridedMin(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedMin: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedMin: needs step >= 1");
        int last = l + (r - l) / step * step;
        if (step > treeStrides) {
            T res = A[l];
            for (int i = l + step; i <= last; i += step) res = min(res, A[i]);
            return res;
        }
        const T* tree = minTree.data() + (size_t)(step - 1) * 2 * n;
        int low = n + listIndex(step, l), high = n + listIndex(step, last) + 1;
        T res = A[l];  // (every aggregate here keeps a value it has already seen)
        while (low < high) {
            if (low & 1) res = min(res, tree[low++]);
            if (high & 1) res = min(res, tree[--high]);
            low /= 2, high /= 2;
        }
        return res;
    }

    // gcd of a[l], a[l + step], ..., up to at most r; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    T stridedGcd(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedGcd: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedGcd: needs step >= 1");
        int last = l + (r - l) / step * step;
        if (step > treeStrides) {
            T res = A[l];
            for (int i = l + step; i <= last; i += step) res = std::gcd(res, A[i]);
            return res;
        }
        const T* tree = gcdTree.data() + (size_t)(step - 1) * 2 * n;
        int low = n + listIndex(step, l), high = n + listIndex(step, last) + 1;
        T res = A[l];  // (every aggregate here keeps a value it has already seen)
        while (low < high) {
            if (low & 1) res = std::gcd(res, tree[low++]);
            if (high & 1) res = std::gcd(res, tree[--high]);
            low /= 2, high /= 2;
        }
        return res;
    }

    // a[l] & a[l + step] & ..., up to at most r; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    T stridedAndQuery(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedAndQuery: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedAndQuery: needs step >= 1");
        int last = l + (r - l) / step * step;
        if (step > treeStrides) {
            T res = A[l];
            for (int i = l + step; i <= last; i += step) res = (res & A[i]);
            return res;
        }
        const T* tree = andTree.data() + (size_t)(step - 1) * 2 * n;
        int low = n + listIndex(step, l), high = n + listIndex(step, last) + 1;
        T res = A[l];  // (every aggregate here keeps a value it has already seen)
        while (low < high) {
            if (low & 1) res = (res & tree[low++]);
            if (high & 1) res = (res & tree[--high]);
            low /= 2, high /= 2;
        }
        return res;
    }

    // a[l] | a[l + step] | ..., up to at most r; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    T stridedOrQuery(int l, int r, int step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("stridedOrQuery: needs 0 <= l <= r < n");
        if (step < 1) throw out_of_range("stridedOrQuery: needs step >= 1");
        int last = l + (r - l) / step * step;
        if (step > treeStrides) {
            T res = A[l];
            for (int i = l + step; i <= last; i += step) res = (res | A[i]);
            return res;
        }
        const T* tree = orTree.data() + (size_t)(step - 1) * 2 * n;
        int low = n + listIndex(step, l), high = n + listIndex(step, last) + 1;
        T res = A[l];  // (every aggregate here keeps a value it has already seen)
        while (low < high) {
            if (low & 1) res = (res | tree[low++]);
            if (high & 1) res = (res | tree[--high]);
            low /= 2, high /= 2;
        }
        return res;
    }

    // ---- internals ----

    int listIndex(int step, int i) const { return offsets[step * (step - 1) / 2 + i % step] + i / step; }

    void write(int i, T v) {
        T xorDelta = A[i] ^ v;
        A[i] = v;
        for (int step = 1; step <= blockStrides; step++) {
            int block = listIndex(step, i) / blockSize;
            xorBlocks[(size_t)(step - 1) * numBlocks + block] ^= xorDelta;
        }
        for (int step = 1; step <= treeStrides; step++) {
            int leaf = n + listIndex(step, i);
            {
                T* tree = minTree.data() + (size_t)(step - 1) * 2 * n;
                tree[leaf] = v;
                for (int node = leaf / 2; node >= 1; node /= 2) {
                    T merged = min(tree[2 * node], tree[2 * node + 1]);
                    if (merged == tree[node]) break;  // (nothing above can change either)
                    tree[node] = merged;
                }
            }
            {
                T* tree = gcdTree.data() + (size_t)(step - 1) * 2 * n;
                tree[leaf] = v;
                for (int node = leaf / 2; node >= 1; node /= 2) {
                    T merged = std::gcd(tree[2 * node], tree[2 * node + 1]);
                    if (merged == tree[node]) break;  // (nothing above can change either)
                    tree[node] = merged;
                }
            }
            {
                T* tree = andTree.data() + (size_t)(step - 1) * 2 * n;
                tree[leaf] = v;
                for (int node = leaf / 2; node >= 1; node /= 2) {
                    T merged = (tree[2 * node] & tree[2 * node + 1]);
                    if (merged == tree[node]) break;  // (nothing above can change either)
                    tree[node] = merged;
                }
            }
            {
                T* tree = orTree.data() + (size_t)(step - 1) * 2 * n;
                tree[leaf] = v;
                for (int node = leaf / 2; node >= 1; node /= 2) {
                    T merged = (tree[2 * node] | tree[2 * node + 1]);
                    if (merged == tree[node]) break;  // (nothing above can change either)
                    tree[node] = merged;
                }
            }
        }
    }
};
