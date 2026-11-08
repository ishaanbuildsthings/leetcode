// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/countPairsByAnd.cpp
#include <bits/stdc++.h>
using namespace std;

// res of size 2^B: res[v] = number of pairs i < j with arr[i] & arr[j] == v
// values must be >= 0; B = number of bits in max(arr), so the vector is about 2 * max(arr) long
// countPairsByAnd(vector<int>{1, 3, 2}) -> {1, 1, 1, 0}   // 1&2 = 0, 1&3 = 1, 3&2 = 2
// O(B * 2^B + N)
template <class T>
vector<long long> countPairsByAnd(const vector<T>& arr) {
    long long mx = 0;
    for (auto x : arr) {
        if (x < 0) {
            throw invalid_argument("countPairsByAnd: value " + to_string((long long)x) + " is negative");
        }
        mx = max(mx, (long long)x);
    }
    int n = 1 << (mx ? 64 - __builtin_clzll(mx) : 0);
    vector<long long> cnt(n, 0);
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
    // res[m] = pairs whose AND has every bit of m
    vector<long long> res(n);
    for (int m = 0; m < n; m++) {
        res[m] = cnt[m] * (cnt[m] - 1) / 2;
    }
    // keep only the ones whose AND is exactly m
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                res[i ^ half] -= res[i];
            }
        }
    }
    return res;
}
