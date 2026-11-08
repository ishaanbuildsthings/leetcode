// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/xorConvolutionMod.cpp
#include <bits/stdc++.h>
using namespace std;

// c of size 2^B: c[k] = sum of a[i] * b[j] over every i, j with i ^ j == k, mod mod (mod must be odd, < 2^62)
// a.size() == b.size() == 2^B
// xorConvolutionMod(vector<int>{1, 2}, vector<int>{3, 4}, 7) -> {4, 3}   // 11 % 7, 10 % 7
// O(B * 2^B + log(MOD))
template <class T>
vector<long long> xorConvolutionMod(const vector<T>& a, const vector<T>& b, long long mod) {
    int n = (int)a.size();
    if (n == 0 || (n & (n - 1)) || (int)b.size() != n) {
        throw invalid_argument("xorConvolutionMod: lengths " + to_string(a.size()) + " and " + to_string(b.size())
                               + " must be the same power of two");
    }
    if (mod % 2 == 0) {
        throw invalid_argument("xorConvolutionMod: mod " + to_string(mod) + " is even, so 2^B has no inverse");
    }
    vector<long long> fa(n), fb(n);
    for (int i = 0; i < n; i++) {
        fa[i] = ((long long)a[i] % mod + mod) % mod;
        fb[i] = ((long long)b[i] % mod + mod) % mod;
    }
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                long long x = fa[i ^ half], y = fa[i];
                fa[i ^ half] = (x + y) % mod;
                fa[i] = (x - y + mod) % mod;
            }
        }
    }
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                long long x = fb[i ^ half], y = fb[i];
                fb[i ^ half] = (x + y) % mod;
                fb[i] = (x - y + mod) % mod;
            }
        }
    }
    for (int i = 0; i < n; i++) {
        fa[i] = (long long)((__int128)fa[i] * fb[i] % mod);
    }
    for (int half = 1; half < n; half <<= 1) {
        for (int i = 0; i < n; i++) {
            if (i & half) {
                long long x = fa[i ^ half], y = fa[i];
                fa[i ^ half] = (x + y) % mod;
                fa[i] = (x - y + mod) % mod;
            }
        }
    }
    // inverse of n mod mod, by the extended Euclidean algorithm (mod is odd and n is a power of two)
    long long oldR = n % mod, r = mod, oldS = 1, s = 0;
    while (r) {
        long long q = oldR / r;
        oldR -= q * r;
        swap(oldR, r);
        oldS -= q * s;
        swap(oldS, s);
    }
    long long invN = (oldS % mod + mod) % mod;
    for (int i = 0; i < n; i++) {
        fa[i] = (long long)((__int128)fa[i] * invN % mod);
    }
    return fa;
}
