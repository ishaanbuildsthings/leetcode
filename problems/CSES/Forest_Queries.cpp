#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, q; cin >> n >> q;
    vector<string> board;
    for (int i = 0; i < n; i++) {
        string s; cin >> s;
        board.push_back(s);
    }
    vector<vector<int>> pf(n, vector<int>(n)); // pf[r][c] is the # of trees in that prefix range
    for (int r = 0; r < n; r++) {
        for (int c = 0; c < n; c++) {
            int left = c > 0 ? pf[r][c - 1] : 0;
            int up = r > 0 ? pf[r - 1][c] : 0;
            int upLeft = r > 0 && c > 0 ? pf[r - 1][c - 1] : 0;
            int total = left + up - upLeft + (board[r][c] == '*' ? 1 : 0);
            pf[r][c] = total;
        }
    }

    for (int i = 0; i < q; i++) {
        int y1, x1, y2, x2; cin >> y1 >> x1 >> y2 >> x2;
        y1--;
        x1--;
        y2--;
        x2--;
        int result = pf[y2][x2];
        int leftLost = x1 > 0 ? pf[y2][x1 - 1] : 0;
        int topLost = y1 > 0 ? pf[y1 - 1][x2] : 0;
        int tlGained = x1 > 0 && y1 > 0 ? pf[y1 - 1][x1 - 1] : 0;
        cout << result - leftLost - topLost + tlGained << endl;
    }
}