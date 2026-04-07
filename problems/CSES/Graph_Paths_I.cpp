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

    vector<vector<int> T(n + 1, vector<int>(n + 1, 0));

    for (int fromNode = 1; fromNode <= n; fromNode++) {
        for (auto toNode : g[node]) {
            T[toNode][fromNode] = 1;
        }
    }

    auto matMult(auto& A, auto&B) -> vector<vector<int>> {
        vector<vector<int>> C(n + 1, vector<int>(n + 1, 0));
        for (int i = 0; i < n + 1; i++) {
            auto& Ai = A[i];
            auto& Ci = C[i];
            for (int k = 0; k < n + 1; k++) {
                if (Ai[k] == 0) continue;
                int a = Ai[k];
                auto& Bk = B[k];
                for (int j = 0; j < n + 1; j++) {
                    Ci[j] = (Ci[j] + a * Bk[j]) % MOD;
                }
            }
        }
        return C;
    };

    auto matPow = [&](auto& mat, int e) -> vector<vector<int>> {

    };

    auto matVecMult = [&](auto& mat, auto& vec) -> vector<vector<int>> {

    };

    int transitions = n - 1;
    auto powered = matPow(T, transitions);
    auto finalVec = matVecMul(powered, state);
    cout << finalVec[n];
}