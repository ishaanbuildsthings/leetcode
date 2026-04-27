#include <bits/stdc++.h>
using namespace std;
void solve() {
    int n; cin >> n;
    vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];
    int res = 0;
    // walk until we hit a 0, adding up those prefixes
    int i = 0;
    long long tot = 0;
    while (i < n) {
        if (!arr[i]) break;
        tot += arr[i];
        if (tot == 0) res++;
        i++;
    }
    // now we are at a 0, walk until we hit the next 0, maintaining the most common prefix count
    while (i < n) {
        int j = i + 1;
        unordered_map<long long, int> cnt; // map sum -> count
        cnt[0] = 1;
        int mxFrq = 1;
        long long total = 0;
        while (j < n) {
            if (!arr[j]) break;
            total += arr[j];
            cnt[total]++;
            mxFrq = max(mxFrq, cnt[total]);
            j++;
        }
        res += mxFrq;
        i = j;
    }

    cout << res << endl;
}
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}