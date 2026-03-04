#include <bits/stdc++.h>
using namespace std;

// If we have an N * M grid we have N * M * logN * logM build time and space
template<typename T, typename Combine> // T = type of grid[r][c], Combine is the type signature of our aggregator
struct RectangleSparseTable {
    int LOG;
    Combine combine;
    vector<vector<vector<vector<T>>>> dp; // dp[powerHeight][powerWidth][r1][c1], use powers first I think it is better cache access since we access the same top layers
    RectangleSparseTable(const vector<vector<T>>& grid, Combine combine) : combine(combine) {
        int h = grid.size();
        int w = grid[0].size();
        int LOG_H = __lg(h) + 1; // if h=10 we need an 8x8 so we need LOG=4 since it is 0-indexed
        int LOG_W = __lg(w) + 1;
        dp.resize(LOG_H);
        // allocating up front makes edge cases so much easier and lets us loop on powHeight=1 and powWidth=1 otherwise I ran into so many annoying issues
        for (int powHeight = 0; powHeight < LOG_H; powHeight++) {
            dp[powHeight].resize(LOG_W);
            int height = (1 << powHeight);
            int rowsNeeded = h - height + 1;
            for (int powWidth = 0; powWidth < LOG_W; powWidth++) {
                int width = (1 << powWidth);
                int colsNeeded = w - width + 1;
                dp[powHeight][powWidth].assign(rowsNeeded, vector<T>(colsNeeded));
            }
        }
        dp[0][0] = grid;

        // we cannot start building dp[powHeight][powWidth] from powHeight=1 and powWidth=1
        // cause dp[ph][pw] depends on dp[ph-1][pw-1]
        // so if we loop like this we would do ph=1, pw=1, ph=1, pw=2 and now we error because we don't have ph=0 pw=1 set
        // so prefill all dp[0][pw] and dp[ph][0]
        for (int powWidth = 1; powWidth < LOG_W; powWidth++) {
            int width = (1 << powWidth);
            int halfWidth = width / 2;
            int colsNeeded = w - width + 1;
            for (int r = 0; r < h; r++) {
                for (int c = 0; c < colsNeeded; c++) {
                    dp[0][powWidth][r][c] = combine(
                        dp[0][powWidth-1][r][c],
                        dp[0][powWidth-1][r][c + halfWidth]
                    );
                }
            }
        }
        for (int powHeight = 1; powHeight < LOG_H; powHeight++) {
            int height = (1 << powHeight);
            int halfHeight = height / 2;
            int rowsNeeded = h - height + 1;
            for (int r = 0; r < rowsNeeded; r++) {
                for (int c = 0; c < w; c++) {
                    dp[powHeight][0][r][c] = combine(
                        dp[powHeight-1][0][r][c],
                        dp[powHeight-1][0][r+halfHeight][c]
                    );
                }
            }
        }
        for (int powHeight = 1; powHeight < LOG_H; powHeight++) {
            int height = (1 << powHeight);
            int halfHeight = height / 2;
            int rowsNeeded = h - height + 1;
            for (int powWidth = 1; powWidth < LOG_W; powWidth++) {
                int width = (1 << powWidth);
                int halfWidth = width / 2;
                int colsNeeded = w - width + 1;
                for (int r = 0; r < rowsNeeded; r++) {
                    for (int c = 0; c < colsNeeded; c++) {
                        dp[powHeight][powWidth][r][c] = combine(
                            combine(dp[powHeight-1][powWidth-1][r][c], dp[powHeight-1][powWidth-1][r+halfHeight][c]),
                            combine(dp[powHeight-1][powWidth-1][r][c+halfWidth], dp[powHeight-1][powWidth-1][r+halfHeight][c+halfWidth])
                        );
                    }
                }
            }
        }
    }
    // (r1, c1) top left, (r2, c2) bottom right
    T query(int r1, int c1, int r2, int c2) {
        int height = r2 - r1 + 1;
        int width = c2 - c1 + 1;
        int heightBit = __lg(height); // if height = 10, this is 3, we use an 8x8. but if height = some power of 2, like 8, we will aggregate 4 4x4s which is redundant but fine
        int widthBit = __lg(width);
        int midR =  r2 - (1 << heightBit) + 1;
        int midC = c2 - (1 << widthBit) + 1;
        return combine(
            combine(dp[heightBit][widthBit][r1][c1], dp[heightBit][widthBit][midR][c1]),
            combine(dp[heightBit][widthBit][r1][midC], dp[heightBit][widthBit][midR][midC])
        );
    }
};
// // first change grid to its base values, so a grid of letters might need to be remapped to bitmasks:
// // grid[i][j] = base_value_fn(raw[i][j]);

// // explicitly providing types
// // auto fn = [](int a, int b) { return min(a, b); };
// // RectangleSparseTable<int, decltype(fn)> st(grid, fn);

// // inferred
// // RectangleSparseTable st(grid, [](int a, int b) { return min(a, b); });

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<vector<int>> grid(n, vector<int>(n, 0));
    for (int r = 0; r < n; r++) {
        string s; cin >> s;
        for (int c = 0; c < n; c++) {
            int num = s[c] - 'A';
            grid[r][c] = 1 << num;
        }
    }
    // for (auto row : grid) {
    //     for (auto v : row) {
    //         cout << v << " ";
    //     }
    //     cout << endl;
    // }
    auto agg = [&](int a, int b) -> int {
        return a | b;
    };
    int fmask = (1 << k) - 1;
    RectangleSparseTable sparse(grid, agg);

    auto solve = [&](int r1, int r2) -> long long {
        int l = 0;
        int r = 0;
        long long res = 0;
        while (l < n) {
            r = max(r, l);
            // while we have not found a region with all letters, and we can expand right, do so
            while (r < n && sparse.query(r1, l, r2, r) != fmask) {
                r++;
            }
            if (r == n) break;
            // now l...r is the smallest width we can use
            int widthsGained = n - r;
            res += widthsGained;
            l++;
        }
        return res;
    };

    long long out = 0;
    for (int r1 = 0; r1 < n; r1++) {
        for (int r2 = r1; r2 < n; r2++) {
            out += solve(r1, r2);
        }
    }

    cout << out << '\n';
}