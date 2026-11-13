// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfPairORs.cpp
#include <bits/stdc++.h>
using namespace std;

// sum over every pair i < j of the OR of arr[i] and arr[j] values must be >= 0; B = number of bits in max(arr)
// Each bit is counted on its own: a pair has bit b unless neither has it
// Exact: throws overflow_error if the answer doesn't fit in long long (then use sumOfPairORsMod)
// sumOfPairORs(vector<int>{1, 2, 3}) -> 9   // 1|2 + 1|3 + 2|3 = 3 + 3 + 3
// O(N * B)
template <class T>
long long sumOfPairORs(const vector<T>& arr) {
    long long mx = 0;
    for (auto x : arr) {
        if (x < 0) {
            throw invalid_argument("sumOfPairORs: value " + to_string((long long)x) + " is negative");
        }
        mx = max(mx, (long long)x);
    }
    long long n = arr.size();
    __int128 total = 0;
    for (int b = 0; b < (mx ? 64 - __builtin_clzll(mx) : 0); b++) {
        long long zeros = n;
        for (auto x : arr) {
            zeros -= (long long)x >> b & 1;
        }
        long long ways = n * (n - 1) / 2 - zeros * (zeros - 1) / 2;
        total += (__int128)ways << b;
    }
    if (total > LLONG_MAX) {
        throw overflow_error("sumOfPairORs: the answer doesn't fit in long long; use sumOfPairORsMod");
    }
    return (long long)total;
}
