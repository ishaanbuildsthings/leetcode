#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int H, W; cin >> H >> W;
    vector<string> board(H);
    for (int i = 0; i < H; i++) cin >> board[i];


    vector<pair<int,int>> DIFFS = {{1,0},{-1,0},{0,1},{0,-1}};

    vector<vector<char>> res(H);
    for (int r = 0; r < H; r++) {
        for (int c = 0; c < W; c++) {
            vector<char> bad = {board[r][c]};
            if (r) {
                char up = res[r-1][c];
                bad.push_back(up);
            }
            if (c) {
                char left = res[r][c-1];
                bad.push_back(left);
            }
            for (char letter : "ABCD") {
                bool exists = find(bad.begin(), bad.end(), letter) != bad.end();
                if (!exists) {
                    res[r].push_back(letter);
                    break;
                }
            }
        }
    }

    for (auto row : res) {
        for (auto letter : row) {
            cout << letter;
        }
        cout << '\n';
    }
}