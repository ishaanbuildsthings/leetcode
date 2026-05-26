#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int H, W; cin >> H >> W;
    vector<string> grid(H);
    for (int i = 0; i < H; i++) cin >> grid[i];

    vector<vector<int>> up(H, vector<int>(W, 0));
    for (int r = 0; r < H; r++)
        for (int c = 0; c < W; c++)
            if (grid[r][c] == '.') up[r][c] = 1;
    
    for (int r = 1; r < H; r++) {
        for (int c = 0; c < W; c++) {
            if (grid[r][c] == '*') continue;
            up[r][c] = 1 + up[r-1][c];
        }
    }

    int res = 0;

    auto process = [&](vector<int> row) -> int {
        vector<int> stack; // mono-increasing, tells us how far right we can go
        vector<int> right(W, 0);
        for (int c = 0; c < W; c++) {
            int v = row[c];
            while (stack.size() && v < row[stack.back()]) {
                int poppedI = stack.back(); stack.pop_back();
                right[poppedI] = c - 1;
            }
            stack.push_back(c);
        }
        for (auto x : stack) {
            right[x] = W - 1;
        }

        vector<int> left(W, 0);
        stack.clear();
        for (int c = W - 1; c >= 0; c--) {
            int v = row[c];
            while (stack.size() && v < row[stack.back()]) {
                int poppedI = stack.back(); stack.pop_back();
                left[poppedI] = c + 1;
            }
            stack.push_back(c);
        }

        int resHere = 0;
        for (int c = 0; c < W; c++) {
            int height = row[c];
            int width = right[c] - left[c] + 1;
            resHere = max(resHere, height * width);
        }
        return resHere;
    };

    for (int r = 0; r < H; r++) {
        res = max(res, process(up[r]));
    }

    cout << res;

}