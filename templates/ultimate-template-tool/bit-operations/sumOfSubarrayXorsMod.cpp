// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfSubarrayXorsMod.cpp
#include <bits/stdc++.h>
using namespace std;

// sum over every non-empty subarray of the XOR of all its values, mod mod (mod < 2^62)
// values must be >= 0; B = number of bits in max(arr)
// Each bit is counted on its own: a subarray has bit b exactly when the prefix XORs at its two ends differ in bit b
// sumOfSubarrayXorsMod(vector<int>{1, 2, 3}, 1'000'000'007) -> 10   // [1] [2] [3] [1,2] [2,3] [1,2,3] -> 1 + 2 + 3 + 3
// + 1 + 0
// O(N * B)
template <class T>
long long sumOfSubarrayXorsMod(const vector<T>& arr, long long mod) {
    long long mx = 0;
    for (auto x : arr) {
        if (x < 0) {
            throw invalid_argument("sumOfSubarrayXorsMod: value " + to_string((long long)x) + " is negative");
        }
        mx = max(mx, (long long)x);
    }
    long long n = arr.size();
    vector<long long> prefix(n + 1, 0);
    for (long long i = 0; i < n; i++) {
        prefix[i + 1] = prefix[i] ^ (long long)arr[i];
    }
    long long total = 0;
    for (int b = 0; b < (mx ? 64 - __builtin_clzll(mx) : 0); b++) {
        long long ones = 0;
        for (long long p : prefix) {
            ones += p >> b & 1;
        }
        long long ways = ones * (n + 1 - ones);
        total = (long long)((total + (__int128)(ways % mod) * (((__int128)1 << b) % mod)) % mod);
    }
    return total % mod;
}
