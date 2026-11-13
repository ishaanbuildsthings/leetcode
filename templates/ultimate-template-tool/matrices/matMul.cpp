// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/matMul.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// A[x, y] * B[y, z] = C[x, z], every entry mod mod: C[i][j] = row i of A times column j of B
// A's column count must equal B's row count; 1 <= mod <= 2^31. Entries may be any long long (negative ones come back
// reduced into [0, mod))
// matMul({{1, 2}, {3, 4}}, {{5, 6}, {7, 8}}, 1'000'000'007) -> {{19, 22}, {43, 50}}
// O(x * y * z)
vector<vector<ll>> matMul(const vector<vector<ll>>& A, const vector<vector<ll>>& B, ll mod) {
    int x = A.size(), y = B.size(), z = B.empty() ? 0 : B[0].size();
    if (x && (int)A[0].size() != y) throw invalid_argument("matMul: A's column count must equal B's row count");
    vector<vector<ll>> C(x, vector<ll>(z, 0));
    for (int i = 0; i < x; i++) {
        for (int k = 0; k < y; k++) {  // (row i of A against every column at once: B is read row by row)
            ll a = (A[i][k] % mod + mod) % mod;
            if (!a) continue;
            for (int j = 0; j < z; j++) C[i][j] = (C[i][j] + a * ((B[k][j] % mod + mod) % mod)) % mod;
        }
    }
    return C;
}
