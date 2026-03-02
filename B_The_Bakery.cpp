#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];
    vector<int> frq(n + 1, 0); // global
    int s = 0;
    int e = -1;
    int uniq = 0;
    auto add = [&](int i) -> void {
        frq[arr[i]]++;
        if (frq[arr[i]] == 1) uniq++;
    };
    auto remove = [&](int i) -> void {
        frq[arr[i]]--;
        if (frq[arr[i]] == 0) uniq--;
    };
    auto val = [&](int l, int r) -> int {
        while (s > l) add(--s);
        while (e < r) add(++e);
        while (s < l) remove(s++);
        while (e > r) remove(e--);
        return uniq;
    };
    vector<int> dp(n + 1);
    vector<int> frqSeed(n + 1, 0);
    int uniqSeed = 0;
    for (int i = 0; i < n; i++) {
        int v = arr[i];
        frqSeed[v]++;
        if (frqSeed[v] == 1) uniqSeed++;
        dp[i] = uniqSeed;
    }

    vector<int> ndp(n + 1);
    for (int p = 2; p <= k; p++) {
        auto solve = [&](auto&& self, int fillL, int fillR, int leftJ, int rightJ) -> void {
            if (fillL > fillR) return;
            int mid = (fillR + fillL) / 2;
            int best = 0;
            int bestJ = -1;
            for (int j = leftJ; j <= min(rightJ, mid); j++) {
                int costHere = val(j, mid);
                int costBefore = j > 0 ? dp[j - 1] : 0;
                int totCost = costHere + costBefore;
                if (totCost > best) {
                    best = totCost;
                    bestJ = j;
                }
            }
            ndp[mid] = best;
            self(self, fillL, mid - 1, leftJ, bestJ);
            self(self, mid + 1, fillR, bestJ, rightJ);
        };
        solve(solve, 0, n - 1, 0, n - 1);
        swap(dp, ndp);
    }
    cout << dp[n - 1] << endl;
}