#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n; cin >> n;
    vector<string> board(n);
    for (int i = 0; i < n; i++) cin >> board[i];

    string result = "";
    vector<vector<bool>> seen(n, vector<bool>(n, false));
    vector<pair<int,int>> frontier;
    seen[0][0] = true;
    frontier.push_back({0, 0});

    while (!frontier.empty()) {
        vector<pair<int,int>> newFrontier;
        char minLetter = 'Z';

        result.push_back(board[frontier[0].first][frontier[0].second]);

        for (auto [r, c] : frontier) {
            // down
            if (r + 1 < n && !seen[r + 1][c]) {
                seen[r + 1][c] = true;
                char nxt = board[r + 1][c];

                if (nxt > minLetter) {
                } else if (nxt == minLetter) {
                    newFrontier.push_back({r + 1, c});
                } else {
                    minLetter = nxt;
                    newFrontier.clear();
                    newFrontier.push_back({r + 1, c});
                }
            }

            // right
            if (c + 1 < n && !seen[r][c + 1]) {
                seen[r][c + 1] = true;
                char nxt = board[r][c + 1];

                if (nxt > minLetter) {
                } else if (nxt == minLetter) {
                    newFrontier.push_back({r, c + 1});
                } else {
                    minLetter = nxt;
                    newFrontier.clear();
                    newFrontier.push_back({r, c + 1});
                }
            }
        }

        frontier = move(newFrontier);
    }

    cout << result;
}