// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/countXorPairsEqualToKForAllK.cpp
#include <bits/stdc++.h>
using namespace std;

// res of size 2^B: res[v] = number of pairs i < j with arr[i] ^ arr[j] == v values must be >= 0; B = number of bits in
// max(arr), so the vector is about 2 * max(arr) long
// countXorPairsEqualToKForAllK(vector<int>{1, 3, 2}) -> {0, 1, 1, 1}   // 1^3 = 2, 1^2 = 3, 3^2 = 1
// O(B * 2^B + N)
template <class T>
vector<long long> countXorPairsEqualToKForAllK(const vector<T>& arr) {
    long long mx = 0;
    for (auto x : arr) {
        if (x < 0) {
            throw invalid_argument("countXorPairsEqualToKForAllK: value " + to_string((long long)x) + " is negative");
        }
        mx = max(mx, (long long)x);
    }
    int n = 1 << (mx ? 64 - __builtin_clzll(mx) : 0);
    vector<long long> cnt(n, 0);
    for (auto x : arr) {
        cnt[x]++;
    }
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                auto x = cnt[i ^ half], y = cnt[i];
                cnt[i ^ half] = x + y;
                cnt[i] = x - y;
            }
        }
    }
    for (int i = 0; i < n; i++) {
        cnt[i] *= cnt[i];
    }
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                auto x = cnt[i ^ half], y = cnt[i];
                cnt[i ^ half] = x + y;
                cnt[i] = x - y;
            }
        }
    }
    cnt[0] -= (long long)n * (long long)arr.size();   // drop each i paired with itself (still scaled by n)
    for (int i = 0; i < n; i++) {
        cnt[i] /= 2LL * n;   // / n undoes the transform, / 2 counts each unordered pair once
    }
    return cnt;
}
