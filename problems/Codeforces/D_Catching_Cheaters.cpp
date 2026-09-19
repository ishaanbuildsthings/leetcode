#include <bits/stdc++.h>
using namespace std;

int n, m;
string A, B;

// length A, length B
vector<vector<int>> memo;

int dp(int i, int j) {
    if (i == n) return 0;
    if (j == m) return 0;
    int &res = memo[i][j];
    if (res != INT_MIN) return res;
    if (A[i] == B[j]) {
        res = 2 + dp(i + 1, j + 1);
    } else {
        int resHere = 0;
        int incI = -1 + dp(i + 1, j);
        int incJ = -1 + dp(i, j + 1);
        res = max({resHere, incI, incJ});
    }
    return res;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n >> m;
    cin >> A;
    cin >> B;

    memo.assign(n, vector<int>(m, INT_MIN));
    int res = 0;
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < m; ++j) {
            res = max(res, dp(i, j));
        }
    }
    cout << res;
    return 0;
}