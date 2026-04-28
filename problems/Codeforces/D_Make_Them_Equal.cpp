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
                int qVal = num / x; // quotient, we start by floor dividing say 100/1 to see what we can add to 100, obviously 100/1 starts at 100
                int xMax = num / qVal; // what is the largest number we can floor divide by that also gives 1?
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

int MX = 13; // max number of operations needed as per the BFS

void solve() {
    int n, k; cin >> n >> k;
    vector<int> B(n); for (int i = 0; i < n; i++) cin >> B[i];
    vector<int> C(n); for (int i = 0; i < n; i++) cin >> C[i];
    int maxOps = min(k, MX * n); // at most we let k ops, or the actual number of ops required

    vector<int> dp(maxOps + 1, 0); // dp[ops used] is the max # of coins we can get
    for (int i = 0; i < n; i++) {
        int v = B[i];
        int costToMakeB = cost[v];
        int score = C[i];
        for (int newOps = maxOps; newOps >= costToMakeB; newOps--) {
            int prevOps = newOps - costToMakeB;
            dp[newOps] = max(dp[newOps], dp[prevOps] + score);
        }
    }
    int ans = *max_element(dp.begin(), dp.end());
    cout << ans << '\n';
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    precomputeCost();
    int t; cin >> t;
    while (t--) solve();
}