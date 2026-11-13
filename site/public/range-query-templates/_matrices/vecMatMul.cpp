// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/matrices/vecMatMul.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// vec[1, x] * M[x, y] = res[1, y], every entry mod mod: res[j] = vec times column j of M
// vec.size() must equal M's row count; 1 <= mod <= 2^31. Entries may be any long long (negative ones come back reduced
// into [0, mod))
// vecMatMul({1, 2}, {{5, 6}, {7, 8}}, 1'000'000'007) -> {19, 22}
// O(x * y)
vector<ll> vecMatMul(const vector<ll>& vec, const vector<vector<ll>>& M, ll mod) {
    int x = M.size(), y = M.empty() ? 0 : M[0].size();
    if ((int)vec.size() != x) throw invalid_argument("vecMatMul: vec's length must equal M's row count");
    vector<ll> res(y, 0);
    for (int k = 0; k < x; k++) {
        ll v = (vec[k] % mod + mod) % mod;
        if (!v) continue;
        for (int j = 0; j < y; j++) res[j] = (res[j] + v * ((M[k][j] % mod + mod) % mod)) % mod;
    }
    return res;
}
