#include <bits/stdc++.h>
using namespace std;
using ll = long long;

void solve() {
    int n, a, b; cin >> n >> a >> b;
    if (a + b > n || (a == 0 && b != 0) || (b == 0 && a != 0)) {
        cout << "NO" << '\n';
        return;
    }
    int ties = n - (a + b);
    vector<int> resA;
    vector<int> resB;
    int curr = n;
    for (int i = 0; i < ties; i++) {
        resA.push_back(curr);
        resB.push_back(curr);
        curr--;
    }

    // a wins
    for (int i = 0; i < a; i++) {
        int aWin = curr - a + i + 1;
        int bLose = i + 1;
        resA.push_back(aWin);
        resB.push_back(bLose);
    }
    // b wins
    for (int i = 0; i < b; i++) {
        int bWin = curr - b + i + 1;
        int aLose = i + 1;
        resB.push_back(bWin);
        resA.push_back(aLose);
    }
    cout << "YES" << endl;
    for (auto x : resA) cout << x << " ";
    cout << endl;
    for (auto x : resB) cout << x << " ";
    cout << endl;
}


int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}

