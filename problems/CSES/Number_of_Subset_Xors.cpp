#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<int> slots(32, 0);
    for (auto x : A) {
        while (x) {
            int msb = 31 - __builtin_clz(x);
            if (!slots[msb]) {
                slots[msb] = x;
                break;
            } else {
                x = x ^ slots[msb];
            }
        }
    }
    ll res = 1;
    for (auto x : slots) {
        if (x) res *= 2;
    }
    cout << res;
}