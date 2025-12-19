#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const int MOD = 1000000007;

int N;
vector<vector<int>> A;
vector<ll> memo;
int fullMask;

ll dfs(int mask) {
    if (mask == fullMask) return 1;
    ll &res = memo[mask];
    if (res != -1) return res;
    res = 0;
    int man = __builtin_popcount((unsigned)mask);
    for (int w = 0; w < N; ++w) {
        if (!(mask & (1 << w)) && A[man][w]) {
            res += dfs(mask | (1 << w));
            if (res >= MOD) res -= MOD;
        }
    }
    return res;
}

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> N;
    A.assign(N, vector<int>(N));
    for (int i = 0; i < N; ++i)
        for (int j = 0; j < N; ++j)
            cin >> A[i][j];

    fullMask = (1 << N) - 1;
    memo.assign(1 << N, -1LL);
    cout << dfs(0) << "\n";
    return 0;
}
