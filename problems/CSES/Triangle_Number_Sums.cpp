#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const ll MAX_N = 1000000000000;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    vector<ll> triNums;
    for (ll num = 1; (num * (num + 1LL)) / 2LL <= MAX_N; num++) {
        triNums.push_back((num * (num + 1LL)) / 2LL);
    }
    auto solve = [&](ll n) -> int {
        for (auto num : triNums) {
            if (num == n) return 1;
            if (num > n) break;
        }
        int l = 0;
        int r = triNums.size() - 1;
        while (l <= r) {
            ll tot = triNums[l] + triNums[r];
            if (tot == n) return 2;
            else if (tot > n) r--;
            else l++;
        }
        return 3;
    };
    
    while (t--) {
        ll n; cin >> n;
        cout << solve(n) << endl;
    }
}