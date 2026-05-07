#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<int> doubled(2 * n);
    for (int i = 0; i < n; i++) {
        int num; cin >> num;
        doubled[i] = num;
        doubled[i + n] = num;
    }
    int LOG = 32;
    vector<vector<int>> next(LOG, vector<int>(2 * n, 2 * n)); // next[power][i] -> next i starting point
    // or 2*n if ends
    vector<ll> pf;
    ll curr = 0;
    for (auto x : doubled) {
        curr += x;
        pf.push_back(curr);
    }
    auto query = [&](int l, int r) -> ll {
        ll right = pf[r];
        ll left = l > 0 ? pf[l - 1] : 0;
        return right - left;
    };

    // for each starting point
    // figure out the rightmost index where l...r sums to <= k
    for (int l = 0; l < 2 * n; l++) {
        int left = l;
        int right = 2 * n - 1;
        int resI = -1;
        while (left <= right) {
            int m = (left + right) / 2;
            if (query(l, m) <= k) {
                resI = m;
                left = m + 1;
            } else {
                right = m - 1;
            }
        }
        next[0][l] = resI + 1;
    }

    for (int p = 1; p < LOG; p++) {
        for (int l = 0; l < 2 * n; l++) {
            int half = next[p - 1][l];
            if (half == 2 * n) {
                next[p][l] = 2 * n;
            } else {
                int full = next[p - 1][half];
                next[p][l] = full;
            }
        }
    }

    int res = 1000000000;
    for (int l = 0; l < n; l++) {
        int curr = l;
        int splits = 0;
        // find how many partitions we need to reach l + n
        for (int p = LOG - 1; p >= 0; p--) {
            int jumped = next[p][curr];
            if (jumped < l + n) {
                curr = jumped;
                splits += pow(2, p);
            }
        }
        splits++; // 1 more jump needed
        res = min(res, splits);
    }

    cout << res << endl;

}