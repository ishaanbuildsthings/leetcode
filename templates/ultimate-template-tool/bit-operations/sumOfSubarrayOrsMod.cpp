// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfSubarrayOrsMod.cpp
#include <bits/stdc++.h>
using namespace std;

// sum over every non-empty subarray of the OR of all its values, mod mod (mod < 2^62)
// values must be >= 0; B = number of bits in max(arr)
// Each bit is counted on its own: a subarray has bit b unless it sits inside a run of values that all lack bit b
// sumOfSubarrayOrsMod(vector<int>{1, 2, 3}, 1'000'000'007) -> 15   // [1] [2] [3] [1,2] [2,3] [1,2,3] -> 1 + 2 + 3 + 3
// + 3 + 3
// O(N * B)
template <class T>
long long sumOfSubarrayOrsMod(const vector<T>& arr, long long mod) {
    long long mx = 0;
    for (auto x : arr) {
        if (x < 0) {
            throw invalid_argument("sumOfSubarrayOrsMod: value " + to_string((long long)x) + " is negative");
        }
        mx = max(mx, (long long)x);
    }
    long long n = arr.size();
    long long total = 0;
    for (int b = 0; b < (mx ? 64 - __builtin_clzll(mx) : 0); b++) {
        long long ways = n * (n + 1) / 2, length = 0;
        for (auto x : arr) {
            length = ((long long)x >> b & 1) ? 0 : length + 1;
            ways -= length;
        }
        total = (long long)((total + (__int128)(ways % mod) * (((__int128)1 << b) % mod)) % mod);
    }
    return total % mod;
}
