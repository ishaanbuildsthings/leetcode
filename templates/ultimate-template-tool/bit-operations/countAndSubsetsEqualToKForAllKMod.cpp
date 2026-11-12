// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/countAndSubsetsEqualToKForAllKMod.cpp
#include <bits/stdc++.h>
using namespace std;

// res of size 2^B: res[v] = number of non-empty subsets (by position) whose AND is exactly v, mod mod values must be >=
// 0; B = number of bits in max(arr), so the vector is about 2 * max(arr) long; mod < 2^62
// countAndSubsetsEqualToKForAllKMod(vector<int>{1, 3}, 1'000'000'007) -> {0, 2, 0, 1}   // {1}, {1, 3} AND to 1; {3}
// ANDs to 3
// O(B * 2^B + N)
template <class T>
vector<long long> countAndSubsetsEqualToKForAllKMod(const vector<T>& arr, long long mod) {
    long long mx = 0;
    for (auto x : arr) {
        if (x < 0) {
            throw invalid_argument("countAndSubsetsEqualToKForAllKMod: value " + to_string((long long)x)
                + " is negative");
        }
        mx = max(mx, (long long)x);
    }
    int n = 1 << (mx ? 64 - __builtin_clzll(mx) : 0);
    vector<int> cnt(n, 0);
    for (auto x : arr) {
        cnt[x]++;
    }
    // cnt[m] = how many values have every bit of m
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                cnt[i ^ half] += cnt[i];
            }
        }
    }
    // res[m] = non-empty subsets whose AND has every bit of m
    vector<long long> pow2(arr.size() + 1, 1 % mod);
    for (size_t i = 1; i < pow2.size(); i++) {
        pow2[i] = pow2[i - 1] * 2 % mod;
    }
    vector<long long> res(n);
    for (int m = 0; m < n; m++) {
        res[m] = (pow2[cnt[m]] - 1 + mod) % mod;
    }
    // keep only the ones whose AND is exactly m
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                res[i ^ half] = (res[i ^ half] - res[i] + mod) % mod;
            }
        }
    }
    return res;
}
