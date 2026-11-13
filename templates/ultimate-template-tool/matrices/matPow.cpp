// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/matPow.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// M[x, x] ^ p, every entry mod mod (p = 0 gives the identity). M must be square; p >= 0; 1 <= mod <= 2^31
// matPow({{1, 1}, {1, 0}}, 10, 1'000'000'007) -> {{89, 55}, {55, 34}}   // Fibonacci numbers
// O(x^3 * log(p))
vector<vector<ll>> matPow(vector<vector<ll>> M, ll p, ll mod) {
    int n = M.size();
    for (auto& row : M) {
        if ((int)row.size() != n) throw invalid_argument("matPow: M must be square");
        for (ll& v : row) v = (v % mod + mod) % mod;
    }
    if (p < 0) throw invalid_argument("matPow: p is negative");
    auto mul = [&](const vector<vector<ll>>& A, const vector<vector<ll>>& B) {  // A * B mod mod, entries in [0, mod)
        vector<vector<ll>> C(n, vector<ll>(n, 0));
        for (int i = 0; i < n; i++)
            for (int k = 0; k < n; k++) {
                if (!A[i][k]) continue;
                for (int j = 0; j < n; j++) C[i][j] = (C[i][j] + A[i][k] * B[k][j]) % mod;
            }
        return C;
    };
    vector<vector<ll>> result(n, vector<ll>(n, 0));
    for (int i = 0; i < n; i++) result[i][i] = 1 % mod;
    for (; p; p >>= 1) {
        if (p & 1) result = mul(result, M);
        M = mul(M, M);
    }
    return result;
}
