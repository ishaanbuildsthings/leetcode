// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/supersetSums.cpp
#include <bits/stdc++.h>
using namespace std;

// g where g[mask] = sum of f[sup] over every supermask sup of mask (sup & mask == mask), SOS DP over supersets
// f.size() must be a power of two, 2^B; results must fit in long long
// supersetSums(vector<int>{1, 2, 3, 4}) -> {10, 6, 7, 4}   // g[1] = f[1] + f[3]
// Count of array values that have every bit of each mask: supersetSums(counts), counts[x] = occurrences of x
// O(B * 2^B)
template <class T>
vector<long long> supersetSums(const vector<T>& f) {
    int n = (int)f.size();
    if (n == 0 || (n & (n - 1))) {
        throw invalid_argument("supersetSums: length " + to_string(n) + " is not a power of two");
    }
    vector<long long> g(f.begin(), f.end());
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                g[i ^ half] += g[i];
            }
        }
    }
    return g;
}
