#include <bits/stdc++.h>
using namespace std;
// by ishaanbuildsthings

// returns a list of all fibs <= n
// example: n=10 -> [0, 1, 1, 2, 3, 5, 8]
// O(log(n)) time and space
vector<long long> getFibList(long long n) {
    vector<long long> fibs = {0};
    if (n >= 1) {
        fibs.push_back(1);
    }
    while (fibs.size() >= 2 && fibs.back() <= n - fibs[fibs.size() - 2]) {
        fibs.push_back(fibs.back() + fibs[fibs.size() - 2]);
    }
    return fibs;
}

// O(1) time
// x is fibonacci number exactly when 5x^2 + 4 or 5x^2 - 4 is a perfect square
bool isFib(long long x) {
    if (x < 0) {
        return false;
    }
    auto isSquare = [](__int128 value) {
        if (value < 0) {
            return false;
        }
        __int128 root = (__int128)sqrtl((long double)value);
        while (root * root > value) {
            root--;
        }
        while ((root + 1) * (root + 1) <= value) {
            root++;
        }
        return root * root == value;
    };
    __int128 base = (__int128)5 * x * x;
    return isSquare(base + 4) || isSquare(base - 4);
}

// gets the xth fibonacci number
// getXthFib(1) -> 0
// getXthFib(2) -> 1
// getXthFib(3) -> 1
// getXthFib(10) -> 34
// O(log(x)), overflows past x = 94
unsigned long long getXthFib(long long x) {
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

// same as above with mod
long long getXthFibMod(long long x, long long mod) {
    auto fibPair = [&](auto&& self, long long k) -> pair<long long, long long> {
        if (k == 0) {
            return {0, 1 % mod};
        }
        auto [a, b] = self(self, k >> 1);
        long long even = (__int128)a * ((2 * b - a + mod) % mod) % mod;
        long long odd = ((__int128)a * a + (__int128)b * b) % mod;
        if (k & 1) {
            return {odd, (even + odd) % mod};
        }
        return {even, odd};
    };
    return fibPair(fibPair, x - 1).first;
}