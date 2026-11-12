// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfXorPairsEqualToKForAllK.cpp
#include <bits/stdc++.h>
using namespace std;

// c of size 2^B: c[k] = sum of arr1[i] * arr2[j] over every i and every j with i ^ j == k
// arr1.size() == arr2.size() == 2^B; exact while (sum of |arr1[i]|) * (sum of |arr2[j]|) fits in long long (e.g. counts
// up to 10^9 total), else use sumOfXorPairsEqualToKForAllKMod
// sumOfXorPairsEqualToKForAllK(vector<int>{1, 2}, vector<int>{3, 4}) -> {11, 10}   // c[0] = arr1[0]*arr2[0] +
// arr1[1]*arr2[1], c[1] = arr1[0]*arr2[1] + arr1[1]*arr2[0]
// O(B * 2^B)
template <class T>
vector<long long> sumOfXorPairsEqualToKForAllK(const vector<T>& arr1, const vector<T>& arr2) {
    int n = (int)arr1.size();
    if (n == 0 || (n & (n - 1)) || (int)arr2.size() != n) {
        throw invalid_argument("sumOfXorPairsEqualToKForAllK: lengths " + to_string(arr1.size()) + " and "
            + to_string(arr2.size())
                               + " must be the same power of two");
    }
    vector<long long> fa(arr1.begin(), arr1.end()), fb(arr2.begin(), arr2.end());
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                auto x = fa[i ^ half], y = fa[i];
                fa[i ^ half] = x + y;
                fa[i] = x - y;
            }
        }
    }
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                auto x = fb[i ^ half], y = fb[i];
                fb[i ^ half] = x + y;
                fb[i] = x - y;
            }
        }
    }
    for (int i = 0; i < n; i++) {
        fa[i] *= fb[i];
    }
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                auto x = fa[i ^ half], y = fa[i];
                fa[i ^ half] = x + y;
                fa[i] = x - y;
            }
        }
    }
    for (int i = 0; i < n; i++) {
        fa[i] /= n;
    }
    return fa;
}
