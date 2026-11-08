// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/xorConvolution.cpp
#include <bits/stdc++.h>
using namespace std;

// c of size 2^B: c[k] = sum of a[i] * b[j] over every i, j with i ^ j == k
// a.size() == b.size() == 2^B; exact while (sum of |a[i]|) * (sum of |b[j]|) fits in long long (e.g. counts up to
// 10^9 total), else use xorConvolutionMod
// xorConvolution(vector<int>{1, 2}, vector<int>{3, 4}) -> {11, 10}   // c[0] = a0*b0 + a1*b1, c[1] = a0*b1 + a1*b0
// O(B * 2^B)
template <class T>
vector<long long> xorConvolution(const vector<T>& a, const vector<T>& b) {
    int n = (int)a.size();
    if (n == 0 || (n & (n - 1)) || (int)b.size() != n) {
        throw invalid_argument("xorConvolution: lengths " + to_string(a.size()) + " and " + to_string(b.size())
                               + " must be the same power of two");
    }
    vector<long long> fa(a.begin(), a.end()), fb(b.begin(), b.end());
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
