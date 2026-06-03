class Solution:
    def longestIncreasingPath(self, matrix: List[List[int]]) -> int:
        n_rows, n_cols = len(matrix), len(matrix[0])
        
        memo = [[0 for _ in range(n_cols)] for _ in range(n_rows)]

        def dfs(r, c):
            if memo[r][c]:
                return memo[r][c]

            max_len = 1

            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                if r+dr < 0 or r+dr >= n_rows: continue
                if c+dc < 0 or c+dc >= n_cols: continue

                if matrix[r+dr][c+dc] > matrix[r][c]:
                    max_len = max(max_len, 1 + dfs(r+dr, c+dc))

            memo[r][c] = max_len
            return max_len

        longest_path = 0
        for r in range(n_rows):
            for c in range(n_cols):
                longest_path = max(longest_path, dfs(r, c))

        return longest_path