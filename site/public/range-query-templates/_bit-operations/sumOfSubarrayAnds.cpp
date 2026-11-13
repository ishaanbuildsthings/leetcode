// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfSubarrayANDs.cpp
#include <bits/stdc++.h>
using namespace std;

// sum over every non-empty subarray of the AND of all its values values must be >= 0; B = number of bits in max(arr)
// Each bit is counted on its own: a subarray has bit b exactly when it sits inside a run of values that all have bit b
// Exact: throws overflow_error if the answer doesn't fit in long long (then use sumOfSubarrayANDsMod)
// sumOfSubarrayANDs(vector<int>{1, 2, 3}) -> 8   // [1] [2] [3] [1,2] [2,3] [1,2,3] -> 1 + 2 + 3 + 0 + 2 + 0
// O(N * B)
template <class T>
long long sumOfSubarrayANDs(const vector<T>& arr) {
    long long mx = 0;
    for (auto x : arr) {
        if (x < 0) {
            throw invalid_argument("sumOfSubarrayANDs: value " + to_string((long long)x) + " is negative");
        }
        mx = max(mx, (long long)x);
    }
    __int128 total = 0;
    for (int b = 0; b < (mx ? 64 - __builtin_clzll(mx) : 0); b++) {
        long long ways = 0, length = 0;
        for (auto x : arr) {
            length = ((long long)x >> b & 1) ? length + 1 : 0;
            ways += length;
        }
        total += (__int128)ways << b;
    }
    if (total > LLONG_MAX) {
        throw overflow_error("sumOfSubarrayANDs: the answer doesn't fit in long long; use sumOfSubarrayANDsMod");
    }
    return (long long)total;
}
