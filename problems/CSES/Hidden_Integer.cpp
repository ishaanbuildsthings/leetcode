#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int l = 1;
    int r = 1000000000;
    while (l < r) {
        int m = (r + l) / 2;
        cout << "? " << m << "\n" << flush;
        string response; cin >> response;
        // m is less than the target
        if (response == "YES") {
            l = m + 1;
        } else {
            r = m;
        }
    }
    cout << "! " << l << "\n" << flush;
}