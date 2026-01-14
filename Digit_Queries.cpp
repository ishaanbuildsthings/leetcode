#include <bits/stdc++.h>
using namespace std;

int solve(long long k) {
    long long curr = 0; // current number we are at, if k to go is 0, we return curr
    long long kToGo = k;
    for (int width = 1; width <= 30; width++) {
        long long numbersOfWidth = 9 * pow(10, width - 1);
        long long digitsAtWidth = numbersOfWidth * width;
        if (digitsAtWidth <= kToGo) {
            kToGo -= digitsAtWidth;
            continue;
        }
        long long fullFit = kToGo / width;
        kToGo -= fullFit * width; 
    }
}

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int q; cin >> q;
    for (int i = 0; i < q; i++) {
        long long k; cin >> k;
        cout << solve(k) << endl;
    }
}