#include<bits/stdc++.h>
using namespace std;
const int MOD = 1e9 + 7;
int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, m, k; cin >> n >> m >> k;
    vector<vector<int>> g(n + 1);
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b;
        g[a].push_back(b);
    }
    vector<int> state(n + 1); // number of ways to reach node N
    state[1] = 1; // start at node 1

    vector<vector<int>> T(n + 1, vector<int>(n + 1, 0));

    for (int fromNode = 1; fromNode <= n; fromNode++) {
        for (auto toNode : g[fromNode]) {
            T[toNode][fromNode] += 1; // we do this because of duplicate edges
        }
    }

    auto matMult = [&](auto& A, auto& B) -> vector<vector<int>> {
        vector<vector<int>> C(n + 1, vector<int>(n + 1, 0));
        for (int i = 0; i <= n; i++) {
            for (int k2 = 0; k2 <= n; k2++) {
                if (A[i][k2] == 0) continue;
                long long a = A[i][k2];
                for (int j = 0; j <= n; j++) {
                    C[i][j] = (C[i][j] + a * B[k2][j]) % MOD;
                }
            }
        }
        return C;
    };
    
    auto matPow = [&](auto mat, int e) -> vector<vector<int>> {
        vector<vector<int>> res(n + 1, vector<int>(n + 1, 0));
        for (int i = 0; i <= n; i++) res[i][i] = 1; // identity
        while (e > 0) {
            if (e & 1) res = matMult(res, mat);
            mat = matMult(mat, mat);
            e >>= 1;
        }
        return res;
    };
    
    auto matVecMul = [&](auto& mat, auto& vec) -> vector<int> {
        vector<int> res(n + 1, 0);
        for (int i = 0; i <= n; i++) {
            for (int j = 0; j <= n; j++) {
                res[i] = (res[i] + (long long)mat[i][j] * vec[j]) % MOD;
            }
        }
        return res;
    };

    int transitions = k;
    auto powered = matPow(T, transitions);
    auto finalVec = matVecMul(powered, state);
    cout << finalVec[n];
}