#include <bits/stdc++.h>
using namespace std;

struct Sparse {
    int n;
    int LOG;
    vector<vector<int>> sparse; // sparse[power][left] is the AND for that range
    Sparse(const vector<int>& arr) {
        n = arr.size();
        LOG = 32 - __builtin_clz(n);
        sparse.resize(LOG, vector<int>(n));
        for (int i = 0; i < n; i++) {
            sparse[0][i] = arr[i];
        }
        for (int power = 1; power < LOG; power++) {
            int width = pow(2, power);
            int halfWidth = width / 2;
            for (int left = 0; left < n; left++) {
                int andLeft = sparse[power-1][left];
                int rightEdge = left + halfWidth;
                if (rightEdge < n) {
                    andLeft &= sparse[power-1][rightEdge];
                }
                sparse[power][left] = andLeft;
            }
        }
    }
    int query(int l, int r) {
        int width = r - l + 1;
        int maxPow = 31 - __builtin_clz(width);
        int powWidth = pow(2, maxPow);
        int left = sparse[maxPow][l];
        int right = sparse[maxPow][l + width - powWidth];
        return left & right;
    }
};

struct Q {
    int l;
    int r;
    int andVal;
};

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, m; cin >> n >> m;
    vector<Q> qs(m);
    for (int i = 0; i < m; i++) {
        int l, r, andVal;
        cin >> l >> r >> andVal; l--; r--;
        qs[i] = Q{l, r, andVal};
    }
    vector<vector<int>> sweep(n + 1, vector<int>(30, 0)); // sweep[index] = [0, 2, 1, ...] to hold sweep line bit diffs
    for (auto [l, r, andVal] : qs) {
        for (int bit = 0; bit < 30; bit++) {
            if (andVal & (1 << bit)) {
                sweep[l][bit]++;
                sweep[r+1][bit]--;
            }
        }
    }
    vector<int> out(n);
    vector<int> frq(30, 0); // current bit frequencies
    for (int i = 0; i < n; i++) {
        int number = 0;
        for (int bit = 0; bit < 30; bit++) {
            frq[bit] += sweep[i][bit];
            if (frq[bit] > 0) {
                number |= (1 << bit);
            }
        }
        out[i] = number;
    }

    Sparse sparse(out);
    for (auto [l, r, andVal] : qs) {
        if (sparse.query(l, r) != andVal) {
            cout << "NO" << endl;
            return 0;
        }
    }
    cout << "YES" << endl;
    for (auto x : out) cout << x << " ";
}