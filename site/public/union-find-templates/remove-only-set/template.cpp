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
//   note: popInValRange costs α(N) per value it removes, and a value is only removed once, so O(N α(N)) over every call together
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// RemoveOnlySet s(10);  // holds 0, 1, 2, ..., 9
// A set of 0..n-1 that only ever loses values: nothing can be added back. smallestGteX / largestLteX jump to the
// nearest value still in it from any x, present or not. Searches that find nothing return -1.
// Union find underneath: a removed value joins the group to its right, so each group is a run of removed values plus
// the one present value at its right end; the root keeps the group's two ends, and groups are linked by size.
struct RemoveOnlySet {
    int n, cnt;
    vector<int> par;
    vector<int> lo;        // at a root: the group's smallest value
    vector<int> hi;        // at a root: the group's largest value, the only one still present
    vector<char> present;  // present[n] = 1: a stand-in that never leaves, so every group has a right end

    // O(n) -- holds 0, 1, ..., n-1
    explicit RemoveOnlySet(int n) : n(n), cnt(n), par(n + 1), lo(n + 1), hi(n + 1), present(n + 1, 1) {
        iota(par.begin(), par.end(), 0), iota(lo.begin(), lo.end(), 0), iota(hi.begin(), hi.end(), 0);
    }

    int find(int i) {
        while (par[i] != i) i = par[i] = par[par[i]];
        return i;
    }

    // O(1) -- true if x is in the set (any x is fine)
    bool contains(int x) { return x >= 0 && x < n && present[x]; }

    // O(1) -- how many values are still in the set
    int size() { return cnt; }

    // O(α(N)) amortized -- remove x; returns 1 if it was there, else 0 (any x is fine)
    int remove(int x) {
        if (!contains(x)) return 0;
        present[x] = 0;
        cnt--;
        int left = find(x), right = find(x + 1);
        if (hi[left] - lo[left] > hi[right] - lo[right]) par[right] = left, hi[left] = hi[right];
        else par[left] = right, lo[right] = lo[left];
        return 1;
    }

    // O(α(N)) amortized -- smallest value >= x; -1 if there is none (any x is fine)
    int smallestGteX(int x) {
        if (x >= n) return -1;
        int found = hi[find(std::max(x, 0))];
        return found == n ? -1 : found;
    }

    // O(α(N)) amortized -- smallest value > x; -1 if there is none (any x is fine)
    int smallestGtX(int x) { return x >= n ? -1 : smallestGteX(x + 1); }

    // O(α(N)) amortized -- largest value <= x; -1 if there is none (any x is fine)
    int largestLteX(int x) {
        x = std::min(x, n - 1);
        if (x < 0) return -1;
        if (present[x]) return x;
        return lo[find(x)] - 1;
    }

    // O(α(N)) amortized -- largest value < x; -1 if there is none (any x is fine)
    int largestLtX(int x) { return x <= 0 ? -1 : largestLteX(x - 1); }

    // O(α(N)) amortized -- the smallest value; out_of_range if empty
    int min() {
        if (!cnt) throw out_of_range("min: the set is empty");
        return smallestGteX(0);
    }

    // O(α(N)) amortized -- the largest value; out_of_range if empty
    int max() {
        if (!cnt) throw out_of_range("max: the set is empty");
        return largestLteX(n - 1);
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
        for (int x = smallestGteX(lo); x != -1 && x <= hi; x = smallestGtX(x)) remove(x), res.push_back(x);
        return res;
    }
};
