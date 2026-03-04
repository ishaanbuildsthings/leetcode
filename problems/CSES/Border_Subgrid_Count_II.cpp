#include<bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<string> grid;
    for (int i = 0; i < n; i++) {
        string s; cin >> s; grid.push_back(s);
    }
    vector<vector<int>> downChain(n, vector<int>(n, 1));
    for (int r = n - 2; r >= 0; r--) {
        for (int c = 0; c < n; c++) {
            if (grid[r][c] == grid[r+1][c]) {
                downChain[r][c] = downChain[r+1][c] + 1;
            }
        }
    }
    vector<long long> out(k, 0);
    for (int r1 = 0; r1 < n; r1++) {
        for (int r2 = r1; r2 < n; r2++) {
            int chains = 0;
            char chainType = '#'; // sentinel
            for (int c = 0; c < n; c++) {
                int cell = grid[r1][c] - 'A';
                // complete mismatch
                if (grid[r1][c] != grid[r2][c]) {
                    chains = 0;
                    chainType = '#';
                    continue;
                }
                // has a down chain
                if (downChain[r1][c] + r1 - 1 >= r2) {
                    // same down chain
                    if (grid[r1][c] == chainType) {
                        chains += 1;
                        out[cell] += chains;
                    } 
                    // different down chain
                    else {
                        chains = 1;
                        out[cell]++;
                        chainType = grid[r1][c];
                    }
                } else {
                    // new border type
                    if (chainType != grid[r1][c]) {
                        chainType = grid[r1][c];
                        chains = 0;
                    }
                }
            }
        }
    }
    for (auto x : out) {
        cout << x << '\n';
    }
}