// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/maxTwoGroupANDSum.cpp
#include <bits/stdc++.h>
using namespace std;

// max of AND(A) + AND(B) over every split of arr into two non-empty groups A and B (each value in exactly one)
// Why it works: bits that every value has land in both ANDs whatever the split, so they count twice; set them aside.
// Then no bit can be in both ANDs, so the rest of the answer is AND(A) | AND(B): go from the highest bit down and keep
// each bit if some split still has every kept bit in AND(A) or in AND(B). Each value must sit in the group whose kept
// bits it all has, so the kept bits a value is missing must all belong to the other group: merge them (union-find over
// bits). With 2 or more merged groups of bits a split always exists (put one group of bits on each side; every value
// goes opposite the bits it misses); with 1 it exists only if some value has every kept bit.
// Values must be >= 0 (any size); needs at least 2 values.
// maxTwoGroupANDSum(vector<int>{3, 3, 4, 4}) -> 7   // {3, 3} and {4, 4}: 3 + 4
// O(N * B), B = number of bits in max(arr)
template <class T>
unsigned long long maxTwoGroupANDSum(const vector<T>& arr) {
    int n = (int)arr.size();
    if (n < 2) throw invalid_argument("maxTwoGroupANDSum: needs at least 2 values");
    unsigned long long common = ~0ULL, mx = 0;
    for (const T& v : arr) {
        if (v < 0) throw invalid_argument("maxTwoGroupANDSum: values must be >= 0");
        common &= (unsigned long long)v;
    }
    vector<unsigned long long> vals(n);
    for (int i = 0; i < n; i++) vals[i] = (unsigned long long)arr[i] & ~common, mx = max(mx, vals[i]);
    int bits = mx ? 64 - __builtin_clzll(mx) : 0;
    int parent[64];
    iota(parent, parent + 64, 0);
    auto find = [&](int b) {
        while (parent[b] != b) b = parent[b] = parent[parent[b]];
        return b;
    };
    vector<int> missing(n, -1);  // a kept bit the value lacks (any one: they are all merged), or -1 if it has them all
    unsigned long long kept = 0;
    int groups = 0, roots[64];
    bool seen[64] = {};
    for (int t = bits - 1; t >= 0; t--) {
        int full = 0, nr = 0;
        for (int i = 0; i < n; i++) {
            if (vals[i] >> t & 1) {
                if (missing[i] == -1) full++;
            } else if (missing[i] != -1) {
                int r = find(missing[i]);
                if (!seen[r]) seen[r] = true, roots[nr++] = r;
            }
        }
        for (int k = 0; k < nr; k++) seen[roots[k]] = false;
        int newGroups = groups - nr + 1;  // t merges with the groups of every value that lacks it
        if (newGroups >= 2 || full) {
            kept |= 1ULL << t;
            groups = newGroups;
            for (int k = 0; k < nr; k++) parent[roots[k]] = t;
            for (int i = 0; i < n; i++)
                if (missing[i] == -1 && !(vals[i] >> t & 1)) missing[i] = t;
        }
    }
    return 2 * common + kept;
}
