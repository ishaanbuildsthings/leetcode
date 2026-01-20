#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n; cin >> n;
    vector<int> out(n + 5, 1); // 1 means prime, 2 means not prime
    for (int div = 2; div < n + 3; div++) {
        if (out[div] != 1) continue;
        for (int mult = div * 2; mult < n + 3; mult += div) {
            out[mult] = 2;
        }
    }
    if (n <= 2) {
        cout << 1 << endl;
    } else {
        cout << 2 << endl;
    }
    for (int i = 2; i <= n + 1; i++) {
        cout << out[i] << " ";
    }

}