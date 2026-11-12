// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/allDistinct-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: allDistinct getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
// @data-structure-type: seg-tree
// @letters: same
// @complexities:
//   allDistinct: log(N)
//   getAll: N
//   pointAdd: log(N) amortized
//   pointAssign: log(N) amortized
//   pointChmax: log(N) amortized
//   pointChmin: log(N) amortized
//   pointGet: log(N)
//   rangeAssign: log(N) amortized
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[2*N]
//   tags: none
//   other: end[1*N] val[1*N] starts[1*N] chains[1*N]
//   note: the array is kept as runs of equal values; tree is a min tree with one leaf per run start; starts and chains are std::sets; the build is O(N): integer values group in a salted hash map (other types use std::map, O(N log N))

// "Are all values in a[l..r] distinct?" with range assign. All indices 0-based, ranges inclusive [l, r].
// The array is kept as runs: run s covers s..end[s], all holding val[s] (at first every element is its own run; an
// assign makes l..r one run). starts holds every run start, chains[v] the starts of the runs holding v.
// tree is a min tree over positions with one leaf per run start s: s + 1 if the run is longer than 1 (a repeat right
// there), else the start of the next run holding the same value (n if none); every other leaf is n.
// a[l..r] has a repeat iff the run holding l repeats inside l..r, or some run starting in l+1..r has its leaf <= r.
// An assign removes the runs it covers (each one was made by an earlier op, so that is O(1) amortized of them) and
// changes O(1) leaves per run added or removed.
// T: any type usable as a std::map key.
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
struct DistinctTree {
    struct SaltedHash {  // splitmix64 with a per-run salt, so no fixed input makes the hash map slow
        size_t operator()(unsigned long long x) const {
            static const unsigned long long salt = chrono::steady_clock::now().time_since_epoch().count();
            x += salt + 0x9e3779b97f4a7c15ULL;
            x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
            x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
            return x ^ (x >> 31);
        }
    };
    // integer values: a hash map (O(1) expected per lookup, so the build is O(N)); others (pairs, strings): std::map
    using Chains = conditional_t<is_integral_v<T>, unordered_map<T, set<int>, SaltedHash>, map<T, set<int>>>;
    int n;
    HotVector<int> tree;          // min tree; leaves are tree[n + i]
    HotVector<int> end;           // end[s] = last index of the run starting at s
    HotVector<T> val;             // val[s] = the value of the run starting at s
    set<int> starts;           // every run start
    Chains chains;   // value -> starts of the runs holding it

    // O(N log N) -- one std::map lookup per element (starts arrive in increasing order, so each set insert is an
    // amortized O(1) hint insert at the end)
    explicit DistinctTree(const vector<T>& arr)
        : n((int)arr.size()), tree(2 * arr.size(), (int)arr.size()), end(arr.size()), val(arr) {
        for (int i = 0; i < n; i++) {
            end[i] = i;
            starts.emplace_hint(starts.end(), i);
            set<int>& s = chains[arr[i]];
            s.emplace_hint(s.end(), i);
        }
        for (auto& [v, s] : chains) {
            int prev = -1;
            for (int i : s) {
                if (prev != -1) tree[n + prev] = i;
                prev = i;
            }
        }
        for (int x = n - 1; x > 0; x--) tree[x] = min(tree[2 * x], tree[2 * x + 1]);
    }

    // O(logN) -- leaf of position i = v
    LEETCODE_NO_SANITIZE void setLeaf(int i, int v) {
        int p = i + n;
        tree[p] = v;
        for (p >>= 1; p; p >>= 1) tree[p] = min(tree[2 * p], tree[2 * p + 1]);
    }

    // O(logN) -- the leaf run s should have: s + 1 if it is longer than 1, else its value's next run start (or n)
    LEETCODE_NO_SANITIZE void refresh(int s) {
        if (end[s] > s) return setLeaf(s, s + 1);
        const set<int>& c = chains.find(val[s])->second;
        auto it = c.upper_bound(s);
        setLeaf(s, it == c.end() ? n : *it);
    }

    // O(logN) -- the start of the run holding i
    LEETCODE_NO_SANITIZE int runOf(int i) const { return *prev(starts.upper_bound(i)); }

    // O(logN) -- make a run start at x (0 < x < n)
    LEETCODE_NO_SANITIZE void split(int x) {
        int p = runOf(x);
        if (p == x) return;
        end[x] = end[p], val[x] = val[p], end[p] = x - 1;
        starts.insert(x);
        chains.find(val[x])->second.insert(x);
        refresh(p);
        refresh(x);
    }

    // O(logN) -- true iff no value repeats inside a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE bool allDistinct(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("allDistinct: needs 0 <= l <= r < n");
        int p = runOf(l);  // the run holding l
        if (end[p] > l) {
            if (l < r) return false;
        } else {
            const set<int>& c = chains.find(val[p])->second;
            auto it = c.upper_bound(p);
            if (it != c.end() && *it <= r) return false;
        }
        for (int lo = l + 1 + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if ((lo & 1) && tree[lo++] <= r) return false;
            if ((hi & 1) && tree[--hi] <= r) return false;
        }
        return true;
    }

    // O(logN) amortized -- a[i] = v for every i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, const T& v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        split(l);
        if (r + 1 < n) split(r + 1);
        for (auto it = starts.lower_bound(l); it != starts.end() && *it <= r;) {  // drop every run inside l..r
            int s = *it;
            auto cit = chains.find(val[s]);
            set<int>& c = cit->second;
            auto jt = c.find(s);
            int q = jt == c.begin() ? -1 : *prev(jt);
            c.erase(jt);
            if (c.empty()) chains.erase(cit);
            else if (q != -1 && end[q] == q) refresh(q);
            if (s != l) {
                it = starts.erase(it);
                setLeaf(s, n);
            } else {
                ++it;
            }
        }
        end[l] = r, val[l] = v;
        set<int>& c = chains[v];
        auto jt = c.insert(l).first;
        if (jt != c.begin() && end[*prev(jt)] == *prev(jt)) refresh(*prev(jt));
        refresh(l);
    }

    // O(logN) amortized -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        rangeAssign(i, i, v);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return val[runOf(i)];
    }

    // O(N) -- the whole array (a copy)
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out;
        out.reserve(n);
        for (int s : starts) out.insert(out.end(), end[s] - s + 1, val[s]);
        return out;
    }

    // O(logN) amortized -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, const T& delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        rangeAssign(i, i, pointGet(i) + delta);
    }

    // O(logN) amortized -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) rangeAssign(i, i, v);
    }

    // O(logN) amortized -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) rangeAssign(i, i, v);
    }
};
