// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumSubmasksForAllMasks.cpp
#include <bits/stdc++.h>
using namespace std;

// res[mask] = the sum of arr's values that are submasks of mask (v & mask == v), for every mask below 2^B
// B = number of bits in max(arr), so res has 2^B entries (about 2 * max(arr)); values must be >= 0
// sumSubmasksForAllMasks(vector<long long>{1, 2, 3}) -> {0, 1, 2, 6}   // res[3] = 1 + 2 + 3
// O(B * 2^B + N)
// results must fit in long long
template <class T>
vector<long long> sumSubmasksForAllMasks(const vector<T>& arr) {
    T mx = 0;
    for (const T& v : arr) {
        if (v < 0) throw invalid_argument("sumSubmasksForAllMasks: a value is negative");
        mx = max(mx, v);
    }
    int bits = 0;
    while (bits < 62 && (T(1) << bits) <= mx) bits++;
    int n = 1 << bits;
    vector<long long> res(n);
    for (const T& v : arr) res[(size_t)v] += (long long)v;
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                res[i] += res[i ^ half];
            }
        }
    }
    return res;
}
