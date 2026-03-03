#include <bits/stdc++.h>
using namespace std;
using ll = long long;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<string> grid(n); for (int i = 0; i < n; i++) cin >> grid[i];
    vector<vector<int>> histogram(n, vector<int>(n, 0));
    for (int r = 0; r < n; r++) {
        for (int c = 0; c < n; c++) {
            if (r == 0) {
                histogram[r][c] = 1;
                continue;
            }
            if (grid[r][c] != grid[r-1][c]) {
                histogram[r][c] = 1;
            } else {
                histogram[r][c] = 1 + histogram[r-1][c];
            }
        }
    }

    vector<ll> out(k);

    auto solveForHistRow = [&](vector<int>& histRow, int r) -> void {
        vector<int> leftSmallerOrDifferentLetter(n, -1);
        vector<int> stack; // strict-increasing
        for (int c = 0; c < n; c++) {
            // while we are <= to the left and the same letter, we can push further
            while (stack.size() && histRow[c] <= histRow[stack.back()] && grid[r][c] == grid[r][stack.back()]) {
                stack.pop_back();
            }
            if (stack.size()) {
                leftSmallerOrDifferentLetter[c] = stack.back();
            }
            stack.push_back(c);
        }

        vector<int> rightSmallerOrDifferentLetter(n, n);
        vector<int> stack2; // strict-increasing
        for (int c = n - 1; c >= 0; c--) {
            while (stack2.size() && histRow[c] < histRow[stack2.back()] && grid[r][c] == grid[r][stack2.back()]) {
                stack2.pop_back();
            }
            if (stack2.size()) {
                rightSmallerOrDifferentLetter[c] = stack2.back();
            }
            stack2.push_back(c);
        }

        for (int c = 0; c < n; c++) {
            int left = leftSmallerOrDifferentLetter[c] + 1;
            int right = rightSmallerOrDifferentLetter[c] - 1;
            int leftOpts = c - left + 1;
            int rightOpts = right - c + 1;
            ll rects = 1LL * leftOpts * rightOpts * histRow[c];
            out[grid[r][c] - 'A'] += rects;
        }
    };
    int rowNum = 0;
    for (auto& row : histogram) {
        solveForHistRow(row, rowNum++);
    }

    for (auto x : out) {
        cout << x << '\n';
    }
}