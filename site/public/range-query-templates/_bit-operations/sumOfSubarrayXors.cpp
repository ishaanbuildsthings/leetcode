// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfSubarrayXors.cpp
#include <bits/stdc++.h>
using namespace std;

// sum over every non-empty subarray of the XOR of all its values values must be >= 0; B = number of bits in max(arr)
// Each bit is counted on its own: a subarray has bit b exactly when the prefix XORs at its two ends differ in bit b
// Exact: throws overflow_error if the answer doesn't fit in long long (then use sumOfSubarrayXorsMod)
// sumOfSubarrayXors(vector<int>{1, 2, 3}) -> 10   // [1] [2] [3] [1,2] [2,3] [1,2,3] -> 1 + 2 + 3 + 3 + 1 + 0
// O(N * B)
template <class T>
long long sumOfSubarrayXors(const vector<T>& arr) {
    long long mx = 0;
    for (auto x : arr) {
        if (x < 0) {
            throw invalid_argument("sumOfSubarrayXors: value " + to_string((long long)x) + " is negative");
        }
        mx = max(mx, (long long)x);
    }
    long long n = arr.size();
    vector<long long> prefix(n + 1, 0);
    for (long long i = 0; i < n; i++) {
        prefix[i + 1] = prefix[i] ^ (long long)arr[i];
    }
    __int128 total = 0;
    for (int b = 0; b < (mx ? 64 - __builtin_clzll(mx) : 0); b++) {
        long long ones = 0;
        for (long long p : prefix) {
            ones += p >> b & 1;
        }
        long long ways = ones * (n + 1 - ones);
        total += (__int128)ways << b;
    }
    if (total > LLONG_MAX) {
        throw overflow_error("sumOfSubarrayXors: the answer doesn't fit in long long; use sumOfSubarrayXorsMod");
    }
    return (long long)total;
}
