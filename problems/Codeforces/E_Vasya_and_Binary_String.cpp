#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const int MAX_I = 100;

ll cache[MAX_I][MAX_I][MAX_I];

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    string s; cin >> s;
    vector<ll> scores(n + 1);
    for (int i = 0; i < n; i++) {
        cin >> scores[i + 1];
    }

    for (int j = 0; j < n; j++) {
        for (int k = j; k < n; k++) {
            for (int surplus = 0; surplus < n; surplus++) {
                cache[j][k][surplus] = -1;
            }
        }
    }

    auto dp = [&](auto&& self, int l, int r, int surplus) -> ll {
        // base case
        if (l > r) return 0;

        auto& res = cache[l][r][surplus];
        if (res != -1) return res;

        // sacrifice to the group before it
        ll scoreLeft = scores[surplus + 1];
        ll nxtDp = self(self, l + 1, r, 0);
        res = scoreLeft + nxtDp;

        for (int i = l + 1; i <= r; i++) {
            if (s[i] != s[l]) continue;
            ll middleDp = self(self, l + 1, i - 1, 0);
            ll nextDpScore = self(self, i, r, surplus + 1);
            res = max({res, middleDp + nextDpScore});
        }
        return res;
    };

    cout << dp(dp, 0, n - 1, 0) << endl;


}