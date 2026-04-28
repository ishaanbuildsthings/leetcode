#include<bits/stdc++.h>
using namespace std;

const int MAXB = 1001;
vector<long long> cost(MAXB, 0);

void precomputeCost() {
    deque<int> q;
    q.push_back(1);
    vector<bool> seen(MAXB, false);
    seen[1] = true;
    while (q.size()) {
        int length = q.size();
        for (int i = 0; i < length; i++) {
            int num = q.front(); q.pop_front();
            int x = 1;
            while (x <= num) {
                int qVal = num / x;
                int xMax = num / qVal;
                int next = num + qVal;
                if (next < MAXB && !seen[next]) {
                    seen[next] = true;
                    cost[next] = cost[num] + 1;
                    q.push_back(next);
                }
                x = xMax + 1;
            }
        }
    }
}

void solve() {
    int n, k; cin >> n >> k;
    vector<int> B(n); for (int i = 0; i < n; i++) cin >> B[i];
    vector<int> C(n); for (int i = 0; i < n; i++) cin >> C[i];

    vector<vector<int>> cache(n, vector<int>(20 * n, -1));

    // gives us max coins we can get
    auto dp = [&](auto&& self, int i, int opsUsed) -> int {
        if (i == n) return 0;
        if (cache[i][opsUsed] != -1) {
            return cache[i][opsUsed];
        }
        int ifSkip = self(self, i + 1, opsUsed);
        int ifTake = (opsUsed + cost[B[i]] <= k ? (self(self, i + 1, opsUsed + cost[B[i]]) + C[i]) : 0);
        int ans = max(ifSkip, ifTake);
        cache[i][opsUsed] = ans;
        return ans;
    };
    int ans = dp(dp, 0, 0);
    cout << ans << '\n';

}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    precomputeCost();
    int t; cin >> t;
    while (t--) solve();
}