// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfPairOrsMod.cpp
#include <bits/stdc++.h>
using namespace std;

// sum over every pair i < j of the OR of arr[i] and arr[j], mod mod (mod < 2^62)
// values must be >= 0; B = number of bits in max(arr)
// Each bit is counted on its own: a pair has bit b unless neither has it
// sumOfPairOrsMod(vector<int>{1, 2, 3}, 1'000'000'007) -> 9   // 1|2 + 1|3 + 2|3 = 3 + 3 + 3
// O(N * B)
template <class T>
long long sumOfPairOrsMod(const vector<T>& arr, long long mod) {
    long long mx = 0;
    for (auto x : arr) {
        if (x < 0) {
            throw invalid_argument("sumOfPairOrsMod: value " + to_string((long long)x) + " is negative");
        }
        mx = max(mx, (long long)x);
    }
    long long n = arr.size();
    long long total = 0;
    for (int b = 0; b < (mx ? 64 - __builtin_clzll(mx) : 0); b++) {
        long long zeros = n;
        for (auto x : arr) {
            zeros -= (long long)x >> b & 1;
        }
        long long ways = n * (n - 1) / 2 - zeros * (zeros - 1) / 2;
        total = (long long)((total + (__int128)(ways % mod) * (((__int128)1 << b) % mod)) % mod);
    }
    return total % mod;
}
