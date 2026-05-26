#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<string> arr(n);
    vector<pair<ll,ll>> counts(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
        ll ones = count(arr[i].begin(), arr[i].end(), '1');
        ll zeros = arr[i].size() - ones;
        counts[i] = {ones, zeros};
    }
    sort(counts.begin(), counts.end(), [](const pair<ll,ll>& a, const pair<ll,ll>& b) {
        ll oneA = a.first, zeroA = a.second;
        ll oneB = b.first, zeroB = b.second;
        ll invA = oneA * zeroB;
        ll invB = oneB * zeroA;
        return invA < invB;
    });

    ll res = 0;
    ll currOnes = 0;
    for (auto [one, zero] : counts) {
        res += currOnes * zero;
        currOnes += one;
    }
    for (auto& s : arr) {
        ll ones = 0;
        for (char v : s) {
            if (v == '1') ones++;
            else res += ones;
        }
    }
    cout << res << endl;
}