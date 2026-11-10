#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];

    vector<int> slots(32, 0);
    for (int i = 0; i < n; i++) {
        int v = A[i];
        int curr = v;
        while (curr) {
            int msb = 31 - __builtin_clz(curr);
            if (slots[msb] == 0) {
                slots[msb] = curr;
                break;
            }
            curr = curr ^ slots[msb];
        }
    }

    // convert to full-basis
    for (int row = 0; row < 32; row++) {
        if (slots[row] == 0) continue;
        for (int b = row - 1; b >= 0; b--) {
            int smaller = slots[b];
            if (slots[row] & smaller) {
                
            }
        }
    }

    vector<int> res;

    for (int kth = 1; kth <= k; kth++) {
        // need kth smallest
    }
}