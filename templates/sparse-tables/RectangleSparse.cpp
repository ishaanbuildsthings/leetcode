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
        dp[0][0] = grid;
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
    T query(int r1, int r2, int c1, int c2) {
        int height = r2 - r1 + 1;
        int width = c2 - c1 + 1;
        int heightBit = __lg(height); // if height = 10, this is 3, we use an 8x8. but if height = some power of 2, like 8, we will aggregate 4 4x4s which is redundant but fine
        int widthBit = __lg(width);
        int heightOffset = (1 << heightBit);
        int widthOffset = (1 << widthBit);
        return combine(
            combine(dp[heightBit][widthBit][r1][c1], dp[heightBit][widthBit][r1+heightOffset][c1]),
            combine(dp[heightBit][widthBit][r1][c1+widthOffset], dp[heightBit][widthBit][r1+heightOffset][c1+widthOffset])
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