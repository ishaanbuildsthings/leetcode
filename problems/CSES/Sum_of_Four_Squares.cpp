#include <bits/stdc++.h>
using namespace std;
using ll = long long;
int MAX_N = 10000000;
vector<pair<int,int>> numToPairsSquared(MAX_N + 1, {-1, -1});

void precompute() {
    for (ll num1 = 0; num1 <= sqrt(MAX_N) + 5; num1++) {
        for (ll num2 = 0; num2 <= sqrt(MAX_N) + 5; num2++) {
            ll total = num1 * num1 + num2 * num2;
            if (total > MAX_N) break;
            if (numToPairsSquared[total].first == -1) {
                numToPairsSquared[total] = {num1, num2};
            }
        }
    }
}

void solve() {
    int n; cin >> n;
    for (int firstPart = 0; firstPart <= n; firstPart++) {
        int secondPart = n - firstPart;
        if (numToPairsSquared[firstPart].first != -1 && numToPairsSquared[secondPart].first != -1) {
            auto [a, b] = numToPairsSquared[firstPart];
            auto [c, d] = numToPairsSquared[secondPart];
            cout << a << " " << b << " " << c << " " << d << '\n';
            return;
        }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    precompute();
    int t; cin >> t;
    while (t--) solve();
}