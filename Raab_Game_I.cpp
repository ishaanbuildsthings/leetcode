#include <bits/stdc++.h>
using namespace std;
using ll = long long;

void solve() {
    int n, a, b; cin >> n >> a >> b;
    if (a + b > n) {
        cout << "NO" << '\n';
        return;
    }
    int ties = n - (a + b);
    vector<int> aRes;
    vector<int> bRes;
    int curr = n;
    for (int i = 0; i < ties; i++) {
        aRes.push_back(curr);
        bRes.push_back(curr);
        curr--;
    }
    int high = curr; // problem is from 1...high now
}


int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}

