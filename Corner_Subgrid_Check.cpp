#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<string> grid(n);
    for (int i = 0; i < n; i++) cin >> grid[i];
    string abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    vector<vector<vector<int>>> letterPositions(k, vector<vector<int>>(n)); // letterPositions[letterI][r] = vector of the columns
    for (int r = 0; r < n; r++) {
        for (int c = 0; c < n; c++) {
            char letter = grid[r][c];
            int idx = letter - 'A';
            letterPositions[idx][r].push_back(c);
        }
    }
    for (int letterI = 0; letterI < k; letterI++) {
        vector<vector<bool>> seenPairs(n, vector<bool>(n, false));
        bool win = false;
        for (int r = 0; r < n; r++) {
            auto& colPoses = letterPositions[letterI][r];
            for (int idx1 = 0; idx1 < colPoses.size(); idx1++) {
                int c1 = colPoses[idx1];
                for (int idx2 = idx1 + 1; idx2 < colPoses.size(); idx2++) {
                    int c2 = colPoses[idx2];
                    if (seenPairs[c1][c2]) {
                        win = true;
                        break;
                    } else {
                        seenPairs[c1][c2] = true;
                    }
                }
                if (win) {
                    break;
                }
            }
            if (win) break;
        }
        cout << (win ? "YES" : "NO") << '\n';
    }
}