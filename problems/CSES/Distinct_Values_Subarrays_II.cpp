#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, k; cin >> n >> k;
    vector<int> A;
    for (int i = 0; i < n; i++) {
        int v; cin >> v;
        A.push_back(v);
    }
    int r = 0;
    long long out = 0;
    unordered_map<int, int> frq;
    for (int l = 0; l < n; l++) {
        while (r < n) {
            int gained = A[r];
            auto sz = frq.size();
            auto it = frq.find(gained);
            int frqHere = 0;
            if (it != frq.end()) frqHere = it->second;
            // if taking this number would break the window, do not do it
            if (sz == k && frqHere == 0) {
                break;
            }
            frq[gained]++;
            r++;
        }
        int validSize = r - l;
        out += validSize;
        auto it = frq.find(A[l]);
        it->second--;
        if (it->second == 0) frq.erase(it);
    }
    cout << out;
}