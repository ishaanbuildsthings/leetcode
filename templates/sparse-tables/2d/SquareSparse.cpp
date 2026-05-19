// If we have an N * M grid but we only want to make square submatrix queries
// Then we only need square side lengths of powers of 2 to be preprocessed, up to max(M, N), instead of two separate dimensions which is required for rectangle subqueries
// This allows the build time to be O(N * M * log(max(N, M)))
template<typename T, typename Combine> // T = type of grid[r][c], Combine is the type signature of our aggregator
struct SquareSparseTable {
    vector<vector<vector<T>>> dp; // dp[power][r][c], where (r, c) is the top left corner, power first is best because of cache acess, we read from dp[power] and dp[power-1] often so they get cached, as opposed to jumping around different top level r and c in the dp, if we put those dimensions first
    int LOG;
    Combine combine;
    
    SquareSparseTable(const vector<vector<T>>& grid, Combine combine) : combine(combine) {
        int h = grid.size();
        int w = grid[0].size();
        LOG = __lg(min(h, w)) + 1; // I think this is sometimes 1 extra which is fine, we do +1 for 0 and 1 indexing handling I think
        dp.resize(LOG);
        dp[0] = grid; // basically we imply the input grid already has the preprocessed single values, so we can copy directly
        for (int power = 1; power < LOG; power++) {
            // at a given power, our square is sidelength 2^power
            // so in a 10x10 grid and power=3, the square is 8x8, we only need a 3x3 table
            int halfPower = (1 << (power - 1));
            int fullPower = 1 << power;
            int verticalRows = h - fullPower + 1;
            int horizontalRows = w - fullPower + 1;
            // once we "get past" the power and resize it, for a given power we know exactly how many r and c get assigned so we can do this in one go
            dp[power].assign(verticalRows, vector<T>(horizontalRows)); // despite using T, the compiler knows what this is at compile time, so it can set a default value
            for (int r = 0; r < verticalRows; r++) {
                for (int c = 0; c < horizontalRows; c++) {
                    dp[power][r][c] = combine(
                        combine(dp[power-1][r][c], dp[power-1][r+halfPower][c]),
                        combine(dp[power-1][r+halfPower][c+halfPower], dp[power-1][r][c+halfPower])
                    );
                }
            }
        }
    }
    // query square (r1,c1) to (r2,c2) inclusive, must have r2-r1 == c2-c1
    T querySquare(int r1, int c1, int r2, int c2) {
        int n = r2 - r1 + 1;
        int bit = __lg(n); // 2^bit is the largest side that fits in our query range, except if the query range is a power of 2, like an 8x8 we will combine four 4x4s
        int offset = n - (1 << bit);
        return combine(
            combine(dp[bit][r1][c1], dp[bit][r1 + offset][c1]),
            combine(dp[bit][r1][c1 + offset], dp[bit][r1+offset][c1+offset])
        );
    }
};
// first change grid to its base values, so a grid of letters might need to be remapped to bitmasks:
// grid[i][j] = base_value_fn(raw[i][j]);

// explicitly providing types
// auto fn = [](int a, int b) { return min(a, b); };
// SquareSparseTable<int, decltype(fn)> st(grid, fn);

// inferred
// SquareSparseTable st(grid, [](int a, int b) { return min(a, b); });