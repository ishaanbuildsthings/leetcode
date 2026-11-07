// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-offline-order-stats-mex/fast.cpp
// @operations: append countGtX countGteX countInValRange countLtX countLteX countOccurrences getAll kthSmallest largestLtX largestLteX maxAll minAll pointGet pop rangeMax rangeMex rangeMin size smallestGtX smallestGteX
// @data-structure-type: persistent
// @values: offline
// @complexities:
//   append: log(N)
//   countGtX: log(N)
//   countGteX: log(N)
//   countInValRange: log(N)
//   countLtX: log(N)
//   countLteX: log(N)
//   countOccurrences: log(N)
//   getAll: N
//   kthSmallest: log(N)
//   largestLtX: log(N)
//   largestLteX: log(N)
//   pointGet: 1
//   pop: 1
//   rangeMax: log(N)
//   rangeMex: log(N)
//   rangeMin: log(N)
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   size: 1
//   minAll: log(N)
//   maxAll: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: L[1*N*log(N)] R[1*N*log(N)] C[1*N*log(N)]
//   tags: none
//   other: root[1*N] arr[1*N] srt[1*N] mexRoot[1*N] ML[1*N*log(N)] MR[1*N*log(N)] MN[1*N*log(N)]
//   note: N = every value ever added (initial array plus each append); each adds one root-to-leaf path of log N nodes over the compressed values (and one in the mex tree)

// An array that grows: append(v) appends, and queries on any a[l..r] can come in between. Every value that will
// ever be added is given up front (only to compress them: nothing is added until you push it), so the persistent seg
// tree is over compressed ranks and costs are log N, never log U: version p holds a[0..p-1], a[l..r] is version r + 1
// minus version l, and each append adds one version. Query arguments (x, lowVal, ...) can be anything. 0-indexed.
// rangeMex: a second persistent tree, over the values 0..(# of distinct values) + 1, holding each value's last index.
// T: int, long long, ....
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
struct PersistentOfflineOrderStats {
    int n = 0, m;
    long long klo, khi;            // the tree is over ranks 0..m-1
    HotVector<T> arr, srt;            // srt: sorted distinct values
    HotVector<int> root;     // node 0 = the empty tree
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        int L = 0;
        int R = 0;
        int C = 0;
    };
    HotVector<Node> nd;  // node 0 = the empty tree
    int mexHi;                     // mex <= (# of distinct values) < this
    HotVector<int> mexRoot;
    struct MexNode {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        int ML = 0;
        int MR = 0;
        int MN = -1;
    };
    HotVector<MexNode> mnd;  // node 0 = the empty tree

    // O(N log N) -- arr: the initial array (may be empty), 0-indexed; allValuesThatWillEverBeInsertedForOfflineCompression: every value append will
    // ever get (any order, duplicates fine; arr's own values are included for you). N = # of distinct values
    PersistentOfflineOrderStats(const vector<T>& a, vector<T> allValuesThatWillEverBeInsertedForOfflineCompression)
        : srt(move(allValuesThatWillEverBeInsertedForOfflineCompression)), root(1, 0), nd(1) {
        srt.insert(srt.end(), a.begin(), a.end());
        sort(srt.begin(), srt.end());
        srt.erase(unique(srt.begin(), srt.end()), srt.end());
        m = (int)srt.size();
        klo = 0, khi = max(m - 1, 0);
        mexHi = min(m, 1 << 30) + 1;
        mexRoot.assign(1, 0), mnd.assign(1, MexNode{});
        for (const T& v : a) append(v);
    }

    // O(logN) -- append v (one of the values given to the constructor, else throws invalid_argument): it becomes a[n],
    // and n grows by 1
    LEETCODE_NO_SANITIZE void append(T v) {
        int k = lb(v);
        if (k == m || srt[k] != v) throw invalid_argument("append: v was not in the values given to the constructor");
        root.push_back(ins(root.back(), k, v));
        int prev = mexRoot.back();
        mexRoot.push_back(T(0) <= v && (long long)v <= mexHi ? mexSet(prev, 0, mexHi, int(v), n) : prev);
        arr.push_back(v), n++;
    }

    // O(1) -- remove a[n-1] and return it: the newest version is dropped (its nodes stay allocated); needs n >= 1,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE T pop() {
        if (n < 1) throw out_of_range("pop: needs n >= 1");
        root.pop_back();
        mexRoot.pop_back();
        T v = arr.back();
        arr.pop_back(), n--;
        return v;
    }

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return arr[i];
    }

    // O(N) -- the whole array (a copy)
    LEETCODE_NO_SANITIZE vector<T> getAll() const { return arr; }

    // O(1) -- the current length of the array
    LEETCODE_NO_SANITIZE int size() const { return (int)arr.size(); }

    // O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countOccurrences(int l, int r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countOccurrences: needs 0 <= l <= r < size()");
        return countInValRange(l, r, x, x);
    }

    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE int countInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countInValRange: needs 0 <= l <= r < size()");
        if (highVal < lowVal) return 0;
        return countBelow(l, r, ub(highVal)) - countBelow(l, r, lb(lowVal));
    }

    // O(logN) -- # of values < x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countLtX: needs 0 <= l <= r < size()");
        return countBelow(l, r, lb(x));
    }

    // O(logN) -- # of values <= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countLteX: needs 0 <= l <= r < size()");
        return countBelow(l, r, ub(x));
    }

    // O(logN) -- # of values > x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countGtX: needs 0 <= l <= r < size()");
        return r - l + 1 - countBelow(l, r, ub(x));
    }

    // O(logN) -- # of values >= x in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countGteX: needs 0 <= l <= r < size()");
        return r - l + 1 - countBelow(l, r, lb(x));
    }

    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and 1 <= k <= r - l + 1,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE T kthSmallest(int l, int r, int k) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("kthSmallest: needs 0 <= l <= r < size()");
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }

    // O(logN) -- min of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(int l, int r) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMin: needs 0 <= l <= r < size()");
        return kth(l, r, 1);
    }

    // O(logN) -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(int l, int r) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMax: needs 0 <= l <= r < size()");
        return kth(l, r, r - l + 1);
    }

    // O(logN) -- smallest value >= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("smallestGteX: needs 0 <= l <= r < size()");
        int c = countBelow(l, r, lb(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- smallest value > x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> smallestGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("smallestGtX: needs 0 <= l <= r < size()");
        int c = countBelow(l, r, ub(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logN) -- largest value <= x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("largestLteX: needs 0 <= l <= r < size()");
        int c = countBelow(l, r, ub(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- largest value < x in a[l..r], or nullopt; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE optional<T> largestLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("largestLtX: needs 0 <= l <= r < size()");
        int c = countBelow(l, r, lb(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logN) -- smallest integer >= 0 that is not in a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int rangeMex(int l, int r) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMex: needs 0 <= l <= r < size()");
        return mexFrom(l, r, 0);
    }

    LEETCODE_NO_SANITIZE int lb(const T& v) const { return int(lower_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    LEETCODE_NO_SANITIZE int ub(const T& v) const { return int(upper_bound(srt.begin(), srt.end(), v) - srt.begin()); }

    // O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto minAll() {
        if (size() < 1) throw out_of_range("minAll: needs n >= 1");
        return rangeMin(0, size() - 1);
    }

    // O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto maxAll() {
        if (size() < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, size() - 1);
    }

    // ---- internals ----

    // copy of version node with one more value (key = its compressed rank)
    LEETCODE_NO_SANITIZE int ins(int node, long long key, T v) {
        vector<pair<int, bool>> path;
        long long nl = klo, nh = khi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (key <= mid) path.push_back({node, true}), node = nd[node].L, nh = mid;
            else path.push_back({node, false}), node = nd[node].R, nl = mid + 1;
        }
        Node n;
        n.L = 0, n.R = 0, n.C = nd[node].C + 1;
        nd.push_back(n);
        int cur = (int)nd.size() - 1;
        for (int k = (int)path.size() - 1; k >= 0; k--) {
            auto [old, left] = path[k];
            int lc = left ? cur : nd[old].L, rc = left ? nd[old].R : cur;
            Node n;
            n.L = lc, n.R = rc, n.C = nd[lc].C + nd[rc].C;
            nd.push_back(n);
            cur = (int)nd.size() - 1;
        }
        return cur;
    }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1: walk version r + 1 minus version l
    LEETCODE_NO_SANITIZE T kth(long long l, long long r, long long k) const {
        int a = root[r + 1], b = root[l];
        long long nl = klo, nh = khi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = nd[nd[a].L].C - nd[nd[b].L].C;
            if (k <= c) a = nd[a].L, b = nd[b].L, nh = mid;
            else k -= c, a = nd[a].R, b = nd[b].R, nl = mid + 1;
        }
        return srt[nl];
    }

    // # of i in [l, r] whose compressed rank is < x
    LEETCODE_NO_SANITIZE long long countBelow(long long l, long long r, long long x) const {
        if (x <= klo) return 0;
        if (x > khi) return r - l + 1;
        int a = root[r + 1], b = root[l];
        long long nl = klo, nh = khi, res = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (x <= mid) a = nd[a].L, b = nd[b].L, nh = mid;
            // the whole left half is below x
            else res += nd[nd[a].L].C - nd[nd[b].L].C, a = nd[a].R, b = nd[b].R, nl = mid + 1;
        }
        return res;
    }

    // copy of node with value v's last index set to i
    LEETCODE_NO_SANITIZE int mexSet(int node, int nl, int nh, int v, int i) {
        int l = mnd[node].ML, r = mnd[node].MR, x;
        if (nl == nh) x = i;
        else {
            int mid = (nl + nh) >> 1;
            if (v <= mid) l = mexSet(l, nl, mid, v, i);
            else r = mexSet(r, mid + 1, nh, v, i);
            x = min(mnd[l].MN, mnd[r].MN);
        }
        MexNode n;
        n.ML = nl == nh ? 0 : l, n.MR = nl == nh ? 0 : r, n.MN = x;
        mnd.push_back(n);
        return (int)mnd.size() - 1;
    }

    // smallest value >= s that is not in a[l..r]: the leftmost value >= s whose last index (as of r) is < l
    LEETCODE_NO_SANITIZE int mexFrom(int l, int r, int s) const {
        auto go = [&](auto&& self, int t, int nl, int nh) -> int {
            if (nh < s || mnd[t].MN >= l) return -1;  // nothing allowed here, or every value here is in a[l..r]
            if (!t) return max(nl, s);            // no value here was ever seen
            if (nl == nh) return nl;
            int mid = (nl + nh) >> 1, res = self(self, mnd[t].ML, nl, mid);
            return res >= 0 ? res : self(self, mnd[t].MR, mid + 1, nh);
        };
        return go(go, mexRoot[r + 1], 0, mexHi);
    }
};
