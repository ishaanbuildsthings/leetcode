// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/countSubmasksForAllMasks.cpp
#include <bits/stdc++.h>
using namespace std;

// res[mask] = how many of arr's values are submasks of mask (v & mask == v), for every mask below 2^B
// B = number of bits in max(arr), so res has 2^B entries (about 2 * max(arr)); values must be >= 0
// countSubmasksForAllMasks(vector<long long>{1, 2, 3}) -> {0, 1, 1, 3}   // res[3] = 3: 1, 2 and 3 all fit inside 3
// O(B * 2^B + N)
// results must fit in long long
template <class T>
vector<long long> countSubmasksForAllMasks(const vector<T>& arr) {
    T mx = 0;
    for (const T& v : arr) {
        if (v < 0) throw invalid_argument("countSubmasksForAllMasks: a value is negative");
        mx = max(mx, v);
    }
    int bits = 0;
    while (bits < 62 && (T(1) << bits) <= mx) bits++;
    int n = 1 << bits;
    vector<long long> res(n);
    for (const T& v : arr) res[(size_t)v] += 1;
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                res[i] += res[i ^ half];
            }
        }
    }
    return res;
}
