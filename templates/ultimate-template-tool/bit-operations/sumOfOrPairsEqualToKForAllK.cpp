// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfOrPairsEqualToKForAllK.cpp
#include <bits/stdc++.h>
using namespace std;

// c of size 2^B: c[k] = sum of arr1[i] * arr2[j] over every i and every j with i | j == k
// arr1.size() == arr2.size() == 2^B; exact whenever the answers fit in long long (works mod 2^64 inside, so no overflow
// in between matters)
// sumOfOrPairsEqualToKForAllK(vector<int>{1, 2}, vector<int>{3, 4}) -> {3, 18}   // c[1] = arr1[0]*arr2[1] +
// arr1[1]*arr2[0] + arr1[1]*arr2[1] = 4 + 6 + 8
// O(B * 2^B)
template <class T>
vector<long long> sumOfOrPairsEqualToKForAllK(const vector<T>& arr1, const vector<T>& arr2) {
    int n = (int)arr1.size();
    if (n == 0 || (n & (n - 1)) || (int)arr2.size() != n) {
        throw invalid_argument("sumOfOrPairsEqualToKForAllK: lengths " + to_string(arr1.size()) + " and "
            + to_string(arr2.size())
                               + " must be the same power of two");
    }
    vector<unsigned long long> fa(arr1.begin(), arr1.end()), fb(arr2.begin(), arr2.end());
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                fa[i] += fa[i ^ half];
            }
        }
    }
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                fb[i] += fb[i ^ half];
            }
        }
    }
    for (int i = 0; i < n; i++) {
        fa[i] *= fb[i];
    }
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                fa[i] -= fa[i ^ half];
            }
        }
    }
    return vector<long long>(fa.begin(), fa.end());
}
