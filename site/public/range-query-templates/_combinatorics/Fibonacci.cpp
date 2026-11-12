// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/combinatorics/Fibonacci.cpp
#include <bits/stdc++.h>
using namespace std;
// by ishaanbuildsthings

// returns a list of all fibs <= n example: n=10 -> [0, 1, 1, 2, 3, 5, 8]
// O(log(n)) time and space
vector<long long> getFibList(long long n) {
    if (n < 0) {
        return {};
    }
    vector<long long> fibs = {0};
    if (n >= 1) {
        fibs.push_back(1);
    }
    while (fibs.size() >= 2 && fibs.back() <= n - fibs[fibs.size() - 2]) {
        fibs.push_back(fibs.back() + fibs[fibs.size() - 2]);
    }
    return fibs;
}

// O(1) time: only 93 fibonacci numbers fit in a long long, so this walks them
// (the 5x^2 +- 4 perfect square test overflows __int128 from x around 6e18, F92 included)
bool isFib(long long x) {
    if (x < 0) {
        return false;
    }
    unsigned long long a = 0, b = 1;  // unsigned: F93 still fits, and that is as far as a gets
    while (a < (unsigned long long)x) {
        unsigned long long next = a + b;
        a = b;
        b = next;
    }
    return a == (unsigned long long)x;
}

// gets the xth fibonacci number
// getXthFib(1) -> 0
// getXthFib(2) -> 1
// getXthFib(3) -> 1
// getXthFib(10) -> 34
// x is 1-indexed: needs x >= 1
// O(log(x)), overflows past x = 94
unsigned long long getXthFib(long long x) {
    if (x < 1) throw invalid_argument("getXthFib: x is 1-indexed, needs x >= 1");
    auto fibPair = [](auto&& self, long long k) -> pair<unsigned long long, unsigned long long> {
        if (k == 0) {
            return {0, 1};
        }
        auto [a, b] = self(self, k >> 1);
        unsigned long long even = a * (2 * b - a);
        unsigned long long odd = a * a + b * b;
        if (k & 1) {
            return {odd, even + odd};
        }
        return {even, odd};
    };
    return fibPair(fibPair, x - 1).first;
}

// same as above with mod, any mod that fits in a long long
long long getXthFibMod(long long x, long long mod) {
    if (x < 1) throw invalid_argument("getXthFibMod: x is 1-indexed, needs x >= 1");
    auto fibPair = [&](auto&& self, long long k) -> pair<long long, long long> {
        if (k == 0) {
            return {0, 1 % mod};
        }
        auto [a, b] = self(self, k >> 1);
        long long even = (__int128)a * (((__int128)2 * b - a + mod) % mod) % mod;
        long long odd = ((__int128)a * a + (__int128)b * b) % mod;
        if (k & 1) {
            return {odd, (long long)(((__int128)even + odd) % mod)};
        }
        return {even, odd};
    };
    return fibPair(fibPair, x - 1).first;
}