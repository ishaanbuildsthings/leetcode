// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/countORSubsetsEqualToKForAllK.cpp
#include <bits/stdc++.h>
using namespace std;

// res of size 2^B: res[v] = number of non-empty subsets (by position) whose OR is exactly v, exact values must be >= 0;
// B = number of bits in max(arr), so the vector is about 2 * max(arr) long; the counts reach 2^N - 1, so more than 62
// values throws overflow_error (then use countORSubsetsEqualToKForAllKMod)
// countORSubsetsEqualToKForAllK(vector<int>{1, 2, 3}) -> {0, 1, 1, 5}   // 5 of the 7 subsets OR to 3
// O(B * 2^B + N)
template <class T>
vector<long long> countORSubsetsEqualToKForAllK(const vector<T>& arr) {
    if (arr.size() > 62) {
        throw overflow_error(
            "countORSubsetsEqualToKForAllK: more than 62 values, so the counts don't fit in long long; "
            "use countORSubsetsEqualToKForAllKMod");
    }
    long long mx = 0;
    for (auto x : arr) {
        if (x < 0) {
            throw invalid_argument("countORSubsetsEqualToKForAllK: value " + to_string((long long)x) + " is negative");
        }
        mx = max(mx, (long long)x);
    }
    int n = 1 << (mx ? 64 - __builtin_clzll(mx) : 0);
    vector<int> cnt(n, 0);
    for (auto x : arr) {
        cnt[x]++;
    }
    // cnt[m] = how many values are submasks of m
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                cnt[i] += cnt[i ^ half];
            }
        }
    }
    // res[m] = non-empty subsets whose OR is a submask of m
    vector<long long> res(n);
    for (int m = 0; m < n; m++) {
        res[m] = (1LL << cnt[m]) - 1;
    }
    // keep only the ones whose OR is exactly m
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                res[i] -= res[i ^ half];
            }
        }
    }
    return res;
}
