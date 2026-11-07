// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostIndexOf-leftmostIndexOfInRange-rangeReplace-rightmostIndexOf-rightmostIndexOfInRange/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll leftmostIndexOf leftmostIndexOfInRange rangeReplace rightmostIndexOf rightmostIndexOfInRange
// @data-structure-type: position-trees
// @letters: same
// @complexities:
//   getAll: N*log(N)
//   leftmostIndexOf: log(N)
//   leftmostIndexOfInRange: log(N)
//   rangeReplace: log(N) amortized
//   rightmostIndexOf: log(N)
//   rightmostIndexOfInRange: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: L[1*N*log(N)] R[1*N*log(N)]
//   tags: none
//   other: roots[1*N] vals[1*N]
//   note: one dynamic seg tree over the positions per distinct value; at most about N log N nodes live at once (freed nodes are reused); values are hashed, so any values work

// One seg tree over the positions per value (mass change, CF 911G): rangeReplace(l, r, x, y) turns every x in a[l..r]
// into y in O(log N) amortized, for any values. Each distinct value keeps a seg tree over 0..n-1 holding the
// positions where it is; a change splits x's tree at [l, r] (O(log N) new nodes) and merges the cut part into y's
// tree (each step of a merge frees a node, so merges cost O(log N) amortized over the whole run). Also: where x first
// / last appears (in a range). All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing
// qualifies.
// T: any type with a hash (int, long long, char, ...)

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
struct PositionTrees {
    struct SafeHash {  // splitmix64 with a seed random per run (the default hash of an integer is easy to attack)
        size_t operator()(const T& x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    // node 0 = the empty tree; L / R: children
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        int L = 0, R = 0;
    };
    int n;
    HotVector<Node> nd;
    HotVector<int> roots, freeList;
    HotVector<T> vals;
    unordered_map<T, int, SafeHash> ids;

    // O(N log N) -- arr: the initial array
    PositionTrees(const vector<T>& arr) : n((int)arr.size()), nd(1) {
        nd.reserve(2 * n + 2);
        for (int i = 0; i < n; i++) {
            int k = id(arr[i]);
            roots[k] = insert(roots[k], i);
        }
    }

    // O(1) -- the length of the array
    LEETCODE_NO_SANITIZE int size() const { return n; }

    // O(logN) amortized -- every a[i] == x with l <= i <= r becomes y; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void rangeReplace(int l, int r, const T& x, const T& y) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReplace: needs 0 <= l <= r < size()");
        auto it = ids.find(x);
        if (it != ids.end() && x != y) moveTo(it->second, l, r, y);
    }

    // O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    LEETCODE_NO_SANITIZE int leftmostIndexOf(const T& x) const { return edgeOf(x, true); }

    // O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    LEETCODE_NO_SANITIZE int rightmostIndexOf(const T& x) const { return edgeOf(x, false); }

    // O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < size()");
        auto it = ids.find(x);
        return it == ids.end() ? -1 : firstIn(roots[it->second], 0, n - 1, l, r, true);
    }

    // O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < size()");
        auto it = ids.find(x);
        return it == ids.end() ? -1 : firstIn(roots[it->second], 0, n - 1, l, r, false);
    }

    // O(N log N) -- the whole current array
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out(n);
        vector<array<int, 3>> st;
        for (int k = 0; k < (int)roots.size(); k++) {
            if (!roots[k]) continue;
            st.push_back({roots[k], 0, n - 1});
            while (!st.empty()) {
                auto [t, lo, hi] = st.back();
                st.pop_back();
                if (lo == hi) {
                    out[lo] = vals[k];
                    continue;
                }
                int mid = (lo + hi) >> 1;
                if (nd[t].L) st.push_back({nd[t].L, lo, mid});
                if (nd[t].R) st.push_back({nd[t].R, mid + 1, hi});
            }
        }
        return out;
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE int id(const T& v) {  // v's index into vals / roots (a new one, with an empty tree, the first time v is seen)
        auto [it, fresh] = ids.try_emplace(v, (int)vals.size());
        if (fresh) vals.push_back(v), roots.push_back(0);
        return it->second;
    }

    LEETCODE_NO_SANITIZE int newNode() {  // an empty node (a freed one if there is one)
        if (!freeList.empty()) {
            int x = freeList.back();
            freeList.pop_back();
            nd[x] = Node();
            return x;
        }
        nd.emplace_back();
        return (int)nd.size() - 1;
    }

    LEETCODE_NO_SANITIZE int pull(int x) {  // recompute x from its children
        return x;
    }

    LEETCODE_NO_SANITIZE int insert(int t, int i) {  // t's tree with position i (not in it) added; returns the root
        if (!t) t = newNode();
        int root = t, lo = 0, hi = n - 1;
        while (true) {
            if (lo == hi) {
                return root;
            }
            int mid = (lo + hi) >> 1;
            bool left = i <= mid;
            if (!(left ? nd[t].L : nd[t].R)) {
                int c = newNode();
                (left ? nd[t].L : nd[t].R) = c;
            }
            t = left ? nd[t].L : nd[t].R;
            (left ? hi : lo) = left ? mid : mid + 1;
        }
    }

    // (t without the positions in [l, r], a tree of just those); no empty nodes are left behind
    LEETCODE_NO_SANITIZE pair<int, int> split(int t, int lo, int hi, int l, int r) {
        if (!t || r < lo || hi < l) return {t, 0};
        if (l <= lo && hi <= r) return {0, t};
        int mid = (lo + hi) >> 1;
        auto [a1, b1] = split(nd[t].L, lo, mid, l, r);
        auto [a2, b2] = split(nd[t].R, mid + 1, hi, l, r);
        int cut = 0;
        if (b1 || b2) {
            cut = newNode();
            nd[cut].L = b1, nd[cut].R = b2;
            pull(cut);
        }
        if (a1 || a2) {
            nd[t].L = a1, nd[t].R = a2;
            return {pull(t), cut};
        }
        freeList.push_back(t);
        return {0, cut};
    }

    LEETCODE_NO_SANITIZE int merge(int a, int b) {  // the union of two trees over disjoint positions; b's nodes that overlap a's are freed
        if (!a || !b) return a ? a : b;
        int l = merge(nd[a].L, nd[b].L);
        int r = merge(nd[a].R, nd[b].R);
        nd[a].L = l, nd[a].R = r;
        freeList.push_back(b);
        return pull(a);
    }

    LEETCODE_NO_SANITIZE void moveTo(int k, int l, int r, const T& y) {  // the positions in [l, r] of vals[k]'s tree go to y's
        auto [keep, cut] = split(roots[k], 0, n - 1, l, r);
        roots[k] = keep;
        if (!cut) return;
        int ky = id(y);
        int t = roots[ky] = merge(roots[ky], cut);
        (void)t;
    }

    LEETCODE_NO_SANITIZE int edgeOf(const T& x, bool left) const {  // the first (left) / last position of x, or -1
        auto it = ids.find(x);
        int t = it == ids.end() ? 0 : roots[it->second];
        if (!t) return -1;
        int lo = 0, hi = n - 1;
        while (lo < hi) {
            int mid = (lo + hi) >> 1;
            if (left ? nd[t].L : !nd[t].R) t = nd[t].L, hi = mid;
            else t = nd[t].R, lo = mid + 1;
        }
        return lo;
    }

    LEETCODE_NO_SANITIZE int firstIn(int t, int lo, int hi, int l, int r, bool left) const {  // the first (left) / last position in [l, r], or -1
        if (!t || r < lo || hi < l) return -1;
        if (lo == hi) return lo;
        int mid = (lo + hi) >> 1;
        int res = left ? firstIn(nd[t].L, lo, mid, l, r, left) : firstIn(nd[t].R, mid + 1, hi, l, r, left);
        if (res != -1) return res;
        return left ? firstIn(nd[t].R, mid + 1, hi, l, r, left) : firstIn(nd[t].L, lo, mid, l, r, left);
    }
};
