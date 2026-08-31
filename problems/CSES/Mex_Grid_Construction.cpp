#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;

    vector<vector<int>> res(n, vector<int>(n, 0));
    for (int r = 0; r < n; r++) {
        for (int c = 0; c < n; c++) {
            unordered_set<int> seen;
            for (int pc = 0; pc < c; pc++) {
                seen.insert(res[r][pc]);
            }
            for (int pr = 0; pr < r; pr++) {
                seen.insert(res[pr][c]);
            }
            for (int num = 0; num <= 2 * n; num++) {
                if (seen.find(num) == seen.end()) {
                    res[r][c] = num;
                    break;
                }
            }
        }
    }
    for (auto row : res) {
        for (auto x : row) {
            cout << x << " ";
        }
        cout << '\n';
    }
}