// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/remove-only-set/template.cpp
// @operations: contains largestLtX largestLteX max min popInValRange popMax popMin remove smallestGtX smallestGteX
// @data-structure-type: remove-only-set
// @complexities:
//   contains: 1
//   largestLtX: α(N) amortized
//   largestLteX: α(N) amortized
//   max: α(N) amortized
//   min: α(N) amortized
//   popInValRange: α(N) amortized
//   popMax: α(N) amortized
//   popMin: α(N) amortized
//   remove: α(N) amortized
//   smallestGtX: α(N) amortized
//   smallestGteX: α(N) amortized
//   build: N
// @memory:
//   layout: none
//   node: par[1*N] lo[1*N] hi[1*N]
//   tags: none
//   other: present[1*N]
//   note: N = the range it covers: n, or max(values) - min(values) + 1. popInValRange costs α(N) per value they remove, and a value is only removed once, so O(N α(N)) over every call together
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// RemoveOnlySet s(10);                        // holds 0, 1, 2, ..., 9
// RemoveOnlySet s(vector<int>{1, 4, 7});      // holds 1, 4, 7
// RemoveOnlySet s(vector<int>{-50, 3, 99});   // any ints (negatives too); memory is max - min + 1
// A set that only ever loses values: nothing can be added back. smallestGteX / largestLteX jump to the nearest value
// still in it from any x, present or not.
// Union find underneath: each run of removed values is grouped with the value just after it, groups linked by size.
// Searches that find nothing return s.NONE: -1 when no value is negative (always, built from n), else min - 1.
struct RemoveOnlySet {
    int n = 0, cnt = 0, base = 0, NONE = -1;
    // each group: a run of removed values plus the present value right after it; its root knows both ends
    vector<int> par, lo, hi;
    vector<char> present;     // present[n] = 1: a stand-in that never leaves, so every group ends in something present

    // O(n) -- holds 0, 1, ..., n-1
    explicit RemoveOnlySet(int n) : n(n), present(n + 1, 1) { build(); }

    // O(max - min) -- holds just these values: any ints, duplicates are fine
    explicit RemoveOnlySet(const vector<int>& values) {
        if (!values.empty()) {
            auto [mn, mx] = minmax_element(values.begin(), values.end());
            base = *mn, n = *mx - *mn + 1;
            if (base < 0) NONE = base - 1;
        }
        present.assign(n + 1, 0);
        for (int x : values) present[x - base] = 1;
        present[n] = 1;
        build();
    }

    void build() {
        par.resize(n + 1), lo.resize(n + 1), hi.resize(n + 1);
        iota(par.begin(), par.end(), 0), iota(lo.begin(), lo.end(), 0), iota(hi.begin(), hi.end(), 0);
        int start = 0;
        for (int i = 0; i <= n; i++) {
            if (!present[i]) continue;
            for (int j = start; j < i; j++) par[j] = i;
            lo[i] = start;
            start = i + 1;
            if (i < n) cnt++;
        }
    }

    int find(int i) {
        while (par[i] != i) i = par[i] = par[par[i]];
        return i;
    }

    // O(1) -- true if x is in the set (any x is fine)
    bool contains(int x) {
        ll i = (ll)x - base;
        return i >= 0 && i < n && present[i];
    }

    // O(1) -- how many values are still in the set
    int size() { return cnt; }

    // O(α(N)) amortized -- remove x; returns 1 if it was there, else 0 (any x is fine)
    int remove(int x) {
        if (!contains(x)) return 0;
        int i = x - base;
        present[i] = 0;
        cnt--;
        int left = find(i), right = find(i + 1);
        if (hi[left] - lo[left] > hi[right] - lo[right]) par[right] = left, hi[left] = hi[right];
        else par[left] = right, lo[right] = lo[left];
        return 1;
    }

    // O(α(N)) amortized -- smallest value >= x; NONE if there is none (any x is fine)
    int smallestGteX(int x) {
        ll i = (ll)x - base;
        if (i >= n) return NONE;
        int found = hi[find((int)std::max(i, 0LL))];
        return found == n ? NONE : found + base;
    }

    // O(α(N)) amortized -- smallest value > x; NONE if there is none (any x is fine)
    int smallestGtX(int x) { return x == INT_MAX ? NONE : smallestGteX(x + 1); }

    // O(α(N)) amortized -- largest value <= x; NONE if there is none (any x is fine)
    int largestLteX(int x) {
        ll i = std::min((ll)x - base, (ll)n - 1);
        if (i < 0) return NONE;
        if (present[i]) return (int)i + base;
        int found = lo[find((int)i)] - 1;
        return found < 0 ? NONE : found + base;
    }

    // O(α(N)) amortized -- largest value < x; NONE if there is none (any x is fine)
    int largestLtX(int x) { return x == INT_MIN ? NONE : largestLteX(x - 1); }

    // O(α(N)) amortized -- the smallest value; out_of_range if empty
    int min() {
        if (!cnt) throw out_of_range("min: the set is empty");
        return smallestGteX(base);
    }

    // O(α(N)) amortized -- the largest value; out_of_range if empty
    int max() {
        if (!cnt) throw out_of_range("max: the set is empty");
        return largestLteX(base + n - 1);
    }

    // O(α(N)) amortized -- remove and return the smallest value; out_of_range if empty
    int popMin() {
        int x = min();
        remove(x);
        return x;
    }

    // O(α(N)) amortized -- remove and return the largest value; out_of_range if empty
    int popMax() {
        int x = max();
        remove(x);
        return x;
    }

    // O(α(N)) per value removed, amortized -- remove every value in [lo, hi] and return them in increasing order
    // (empty if lo > hi)
    vector<int> popInValRange(int lo, int hi) {
        vector<int> res;
        for (int x = smallestGteX(lo); x != NONE && x <= hi; x = smallestGtX(x)) remove(x), res.push_back(x);
        return res;
    }
};
