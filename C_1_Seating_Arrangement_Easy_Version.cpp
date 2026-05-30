#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const int NINF = -1 * (INT_MAX / 4);

void solve() {
    int n, tables, seats; cin >> n >> tables >> seats;
    string s; cin >> s;
    cout << s << endl;

    vector<vector<int>> memo(tables + 1, vector<int>(tables + 1, NINF));

    auto dp = [&](auto&& self, int i, int open) -> int {
        if (i == -1) {
            return 0;
        }
        auto& res = memo[i][open];
        if (res != NINF) return res;

        char c = s[i];

        if (c == 'I') {
            int ifSkip = self(self, i - 1, open);
            res = ifSkip;
            if (open < tables) {
                int ifOpen = self(self, i - 1, open + 1) + 1;
                res = max(res, ifOpen);
            }
            return res;
        }

        if (c == 'E') {
            int ifSkip = self(self, i - 1, open);
            res = ifSkip;
            
        }
    };
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}