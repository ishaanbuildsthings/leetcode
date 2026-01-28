#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, l, k; cin >> n >> l >> k;
    vector<int> d(n); for (int i = 0; i < n; i++) cin >> d[i];
    d.push_back(l);
    vector<int> a(n); for (int i = 0; i < n; i++) cin >> a[i];
    vector<vector<long long>> cache(n, vector<long long>(k + 1, -1));
    auto dp = [&](auto&& self, int i, int removesLeft) -> long long {
        if (i == n) return 0;
        long long resHere = -1;
        if (cache[i][removesLeft] != -1) return cache[i][removesLeft];
        for (int j = i + 1; j <= n; j++) {
            int removes = j - i - 1;
            if (removes > removesLeft) break;
            int nremoves = removesLeft - removes;
            long long dist = d[j] - d[i];
            long long speed = a[i];
            long long time = dist * speed;
            auto nxtDp = self(self, j, nremoves);
            if (resHere == -1) {
                resHere = time + nxtDp;
            } else {
                resHere = min(resHere, time + nxtDp);
            }
        }
        cache[i][removesLeft] = resHere;
        return resHere;
    };
    long long out = (1LL << 60);
    for (int removes = 0; removes <= k; removes++) {
        out = min(out, dp(dp, 0, removes));
    }
    cout << out << '\n';
}