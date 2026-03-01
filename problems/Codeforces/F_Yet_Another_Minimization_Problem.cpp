#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];
    vector<ll> dp(n, LLONG_MAX); // dp[i] is the cost to partition ...i into that many partitions
    vector<int> frqInit(n + 1, 0);
    ll cost = 0;
    // seed the dp
    for (int i = 0; i < n; i++) {
        int v = arr[i];
        cost += frqInit[v];
        frqInit[v]++;
        dp[i] = cost;
    }

    vector<int> frq(n + 1, 0); // global sliding window representing s...e
    int s = 0;
    int e = -1;
    ll currCost = 0;
    auto add = [&](int i) -> void {currCost += frq[arr[i]]++;};
    auto rem = [&](int i) -> void {currCost -= --frq[arr[i]];};
    auto val = [&](int l, int r) -> ll {
        while (s > l) add(--s);
        while (e < r) add(++e);
        while (s < l) rem(s++);
        while (e > r) rem(e--);
        return currCost;
    };

    vector<ll> ndp(n, LLONG_MAX);
    for (int p = 2; p <= k; p++) {
        auto solve = [&](auto&& self, int fillL, int fillR, int leftJ, int rightJ) -> void {
            // cerr << "solve called: " << fillL << " " << fillR << " " << leftJ << " " << rightJ << endl;
            if (fillL > fillR) return;
            int mid = (fillR + fillL) / 2;
            // cerr << "mid: " << mid << endl;
            ll best = LLONG_MAX;
            int bestJ = -1;
            unordered_map<int,int> frqMap; // number -> occ
            ll costHere = 0;
            for (int j = leftJ; j <= min(rightJ, mid); j++) {
                ll costHere = val(j, mid);
                ll costBefore = j > 0 ? dp[j - 1] : 0;
                ll totCost = costHere + costBefore;
                if (totCost < best) {
                    best = totCost;
                    bestJ = j;
                }
            }
            // cerr << "best is: " << best << endl;
            ndp[mid] = best;
            self(self, fillL, mid - 1, leftJ, bestJ);
            self(self, mid + 1, fillR, bestJ, rightJ);
        };
        solve(solve, 0, n - 1, 0, n - 1);
        swap(dp, ndp);
    }
    cout << dp[n - 1] << '\n';
}