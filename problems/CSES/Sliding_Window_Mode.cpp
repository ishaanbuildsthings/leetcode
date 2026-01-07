#include<bits/stdc++.h>
using namespace std;
using ll = long long;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k;
    cin >> n >> k;
    vector<ll> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];
    unordered_map<ll, int> freq; // num -> freq
    set<pair<int, ll>> tups; // holds sorted (-frequency, numberWithThatFrequency)

    auto add = [&](ll x) {
        int oldFrq = freq[x];
        tups.erase({-oldFrq, x});
        int newFrq = oldFrq + 1;
        tups.insert({-newFrq, x});
        freq[x]++;
    };

    auto remove = [&](ll x) {
        int oldFrq = freq[x];
        tups.erase({-oldFrq, x});
        int newFrq = oldFrq - 1;
        if (newFrq > 0) {
            tups.insert({-newFrq, x});
        }
        freq[x]--;
    };

    for (int r = 0; r < n; r++) {
        add(A[r]);
        if (r >= k) {
            int l = r - k;
            remove(A[l]);
        }
        if (r + 1 >= k) {
            auto it = tups.begin(); // points to best (-freq, value)
            ll mode = it->second; // the value
            // int freqMode = -it->first; // its frequency
            cout << mode << " ";
        }
    }
    cout << "\n";
}