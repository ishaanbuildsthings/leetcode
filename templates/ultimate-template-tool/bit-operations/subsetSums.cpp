// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/subsetSums.cpp
#include <bits/stdc++.h>
using namespace std;

// g where g[mask] = sum of f[sub] over every submask sub of mask (sub & mask == sub), the zeta transform / SOS DP
// f.size() must be a power of two, 2^B; results must fit in long long
// subsetSums(vector<int>{1, 2, 3, 4}) -> {1, 3, 4, 10}   // g[3] = f[0] + f[1] + f[2] + f[3]
// Count of array values that are submasks of each mask: subsetSums(counts), counts[x] = occurrences of x
// O(B * 2^B)
template <class T>
vector<long long> subsetSums(const vector<T>& f) {
    int n = (int)f.size();
    if (n == 0 || (n & (n - 1))) {
        throw invalid_argument("subsetSums: length " + to_string(n) + " is not a power of two");
    }
    vector<long long> g(f.begin(), f.end());
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                g[i] += g[i ^ half];
            }
        }
    }
    return g;
}
