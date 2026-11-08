// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/andConvolution.cpp
#include <bits/stdc++.h>
using namespace std;

// c of size 2^B: c[k] = sum of a[i] * b[j] over every i, j with i & j == k
// a.size() == b.size() == 2^B; exact whenever the answers fit in long long (works mod 2^64 inside, so no overflow
// in between matters)
// andConvolution(vector<int>{1, 2}, vector<int>{3, 4}) -> {13, 8}   // c[0] = a0*b0 + a0*b1 + a1*b0 = 3 + 4 + 6
// O(B * 2^B)
template <class T>
vector<long long> andConvolution(const vector<T>& a, const vector<T>& b) {
    int n = (int)a.size();
    if (n == 0 || (n & (n - 1)) || (int)b.size() != n) {
        throw invalid_argument("andConvolution: lengths " + to_string(a.size()) + " and " + to_string(b.size())
                               + " must be the same power of two");
    }
    vector<unsigned long long> fa(a.begin(), a.end()), fb(b.begin(), b.end());
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                fa[i ^ half] += fa[i];
            }
        }
    }
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                fb[i ^ half] += fb[i];
            }
        }
    }
    for (int i = 0; i < n; i++) {
        fa[i] *= fb[i];
    }
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                fa[i ^ half] -= fa[i];
            }
        }
    }
    return vector<long long>(fa.begin(), fa.end());
}
