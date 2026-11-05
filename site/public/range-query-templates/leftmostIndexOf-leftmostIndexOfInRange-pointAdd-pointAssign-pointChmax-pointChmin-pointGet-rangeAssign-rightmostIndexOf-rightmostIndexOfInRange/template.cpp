// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostIndexOf-leftmostIndexOfInRange-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rightmostIndexOf-rightmostIndexOfInRange/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll leftmostIndexOf leftmostIndexOfInRange pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rightmostIndexOf rightmostIndexOfInRange
// @data-structure-type: interval-map
// @letters: same
// @complexities:
//   getAll: N
//   leftmostIndexOf: log(N)
//   leftmostIndexOfInRange: log(N)
//   pointAdd: log(N) amortized
//   pointAssign: log(N) amortized
//   pointChmax: log(N) amortized
//   pointChmin: log(N) amortized
//   pointGet: log(N)
//   rangeAssign: log(N) amortized
//   rightmostIndexOf: log(N)
//   rightmostIndexOfInRange: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: runs[1*N] byVal[1*N]
//   tags: none
//   other: none
//   note: one entry per run of equal values (at most N, usually far fewer), in the run map and in its value's set

// "Where is x's first / last copy, in the whole array or inside a[l..r]?" with RANGE ASSIGN and point updates. All
// indices 0-based, ranges inclusive; -1 when there is no such index. The array is kept as runs of one value: an
// ordered map start -> value, and per value the ordered set of its runs' starts. An assign splits the runs at l and
// r + 1, deletes the runs inside and adds one, so it adds at most 3 runs and pays for every run it later deletes
// (O(log N) amortized). x's first index in [l, r] is l if the run holding l has x, else the start of x's next run.
// T: int, long long, char, ... (any type usable as a std::map key).
template <typename T>
struct IntervalMap {
    int n;
    map<int, T> runs;          // run start -> its value; a run lasts until the next start
    map<T, set<int>> byVal;    // value -> the starts of its runs

    // O(N log N) -- arr: the initial array (equal neighbours become one run)
    explicit IntervalMap(const vector<T>& arr) : n((int)arr.size()) {
        for (int i = 0; i < n; i++)
            if (i == 0 || !(arr[i] == arr[i - 1])) runs.emplace_hint(runs.end(), i, arr[i]), byVal[arr[i]].insert(i);
    }

    // O(logN) amortized -- a[i] = x for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAssign(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        if (l > r) return;
        split(l), split(r + 1);
        auto it = runs.find(l);
        while (it != runs.end() && it->first <= r) {  // (the runs inside [l, r], each deleted once)
            auto p = byVal.find(it->second);
            p->second.erase(it->first);
            if (p->second.empty()) byVal.erase(p);
            it = runs.erase(it);
        }
        runs.emplace_hint(it, l, x);
        byVal[x].insert(l);
    }

    // O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    int leftmostIndexOf(const T& x) const {
        auto p = byVal.find(x);
        return p == byVal.end() ? -1 : *p->second.begin();
    }

    // O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    int rightmostIndexOf(const T& x) const {
        auto p = byVal.find(x);
        return p == byVal.end() ? -1 : end(*p->second.rbegin());
    }

    // O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < n, else throws
    // out_of_range
    int leftmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < n");
        auto p = byVal.find(x);
        if (p == byVal.end() || l > r) return -1;
        auto j = p->second.upper_bound(l);  // x's next run after l; the one before it starts at or before l
        if (j != p->second.begin() && end(*prev(j)) >= l) return l;
        return j != p->second.end() && *j <= r ? *j : -1;
    }

    // O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < n, else throws
    // out_of_range
    int rightmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < n");
        auto p = byVal.find(x);
        if (p == byVal.end() || l > r) return -1;
        auto j = p->second.upper_bound(r);  // x's last run starting at or before r is the one before
        if (j == p->second.begin()) return -1;
        int e = min(end(*prev(j)), r);
        return e >= l ? e : -1;
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return prev(runs.upper_bound(i))->second;
    }

    // O(N) -- the whole array
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(n);
        for (auto it = runs.begin(); it != runs.end(); ++it) {
            int e = next(it) == runs.end() ? n : next(it)->first;
            out.insert(out.end(), e - it->first, it->second);
        }
        return out;
    }

    // O(logN) amortized -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        rangeAssign(i, i, v);
    }

    // O(logN) amortized -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        rangeAssign(i, i, pointGet(i) + delta);
    }

    // O(logN) amortized -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (pointGet(i) < v) rangeAssign(i, i, v);
    }

    // O(logN) amortized -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) rangeAssign(i, i, v);
    }

    // ---- internals ----

    int end(int s) const {  // the last index of the run starting at s
        auto it = next(runs.find(s));
        return (it == runs.end() ? n : it->first) - 1;
    }

    void split(int i) {  // make a run start at i (nothing if one does, or i == n)
        if (i >= n) return;
        auto it = runs.upper_bound(i);
        auto b = prev(it);
        if (b->first == i) return;
        runs.emplace_hint(it, i, b->second);
        byVal[b->second].insert(i);
    }
};
