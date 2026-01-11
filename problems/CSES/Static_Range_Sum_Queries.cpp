#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, q; cin >> n >> q;
    vector<int> A(n);
    vector<long long> pf(n);
    for (int i = 0; i < n; i++) {
        cin >> A[i];
        if (i == 0) {
            pf[i] = A[i];
        } else {
            pf[i] = A[i] + pf[i - 1];
        }
    }
    for (int i = 0; i < q; i++) {
        int l, r; cin >> l >> r;
        l--; r--;
        long long v = pf[r] - (l > 0 ? pf[l - 1] : 0);
        cout << v << endl;
    }
}