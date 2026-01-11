#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);

    int n, q; cin >> n >> q;
    vector<int> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];

    int msb = 31 - __builtin_clz(n);

    vector<vector<int>> sparse(msb + 1, vector<int>(n)); // sparse[power][i] is the minium for i:i+2^power - 1
    for (int i = 0; i < n; i++) {
        sparse[0][i] = A[i];
    }
    for (int power = 1; power <= msb; power++) {
        int halfSize = 1 << (power - 1);
        for (int i = 0; i < n; i++) {
            int newMin = sparse[power - 1][i]; // left half minimum
            int rightIndex = i + halfSize;
            if (rightIndex < n) {
                newMin = min(newMin, sparse[power - 1][rightIndex]);
            }
            sparse[power][i] = newMin;
        }
    }

    for (int i = 0; i < q; i++) {
        int l, r; cin >> l >> r;
        l--; r--;
        int width = r - l + 1;
        int power = 31 - __builtin_clz(width);
        int leftHalfMin = sparse[power][l];
        int rightStart = l + width - (1 << power);
        int rightHalfMin = sparse[power][rightStart];
        cout << min(leftHalfMin, rightHalfMin) << endl;
    }
}