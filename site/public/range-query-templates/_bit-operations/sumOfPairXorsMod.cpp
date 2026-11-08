// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfPairXorsMod.cpp
#include <bits/stdc++.h>
using namespace std;

// sum over every pair i < j of the XOR of arr[i] and arr[j], mod mod (mod < 2^62)
// values must be >= 0; B = number of bits in max(arr)
// Each bit is counted on its own: a pair has bit b exactly when one of the two has it
// sumOfPairXorsMod(vector<int>{1, 2, 3}, 1'000'000'007) -> 6   // 1^2 + 1^3 + 2^3 = 3 + 2 + 1
// O(N * B)
template <class T>
long long sumOfPairXorsMod(const vector<T>& arr, long long mod) {
    long long mx = 0;
    for (auto x : arr) {
        if (x < 0) {
            throw invalid_argument("sumOfPairXorsMod: value " + to_string((long long)x) + " is negative");
        }
        mx = max(mx, (long long)x);
    }
    long long n = arr.size();
    long long total = 0;
    for (int b = 0; b < (mx ? 64 - __builtin_clzll(mx) : 0); b++) {
        long long ones = 0;
        for (auto x : arr) {
            ones += (long long)x >> b & 1;
        }
        long long ways = ones * (n - ones);
        total = (long long)((total + (__int128)(ways % mod) * (((__int128)1 << b) % mod)) % mod);
    }
    return total % mod;
}
