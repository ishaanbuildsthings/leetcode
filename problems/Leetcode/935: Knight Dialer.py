# SOLUTION 1, DP, O(12 * n * 8)
# COORDS = { 1 : [0, 0], 2 : [0, 1], 3 : [0, 2], 4 : [1, 0], 5 : [1, 1], 6 : [1, 2], 7 : [2, 0], 8: [2, 1], 9 : [2, 2], 0 : [3, 1] }
# GRID = [ [1, 2, 3], [4, 5, 6], [7, 8, 9], [None, 0, None] ]

# DIFFS = [ [1, 2], [-1, 2], [1, -2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1] ]

# MOD = 10**9 + 7

# class Solution:
#     def knightDialer(self, n: int) -> int:
#         HEIGHT = 4
#         WIDTH = 3

#         @cache
#         def dp(movesLeft, number):
#             # base case
#             if movesLeft == 0:
#                 return 1
            
#             resForThis = 0

#             row, col = COORDS[number]
#             for rowDiff, colDiff in DIFFS:
#                 newRow = row + rowDiff
#                 newCol = col + colDiff
#                 if newRow == 3 and (newCol == 0 or newCol == 2):
#                     continue
#                 if newRow >= 0 and newRow < HEIGHT and newCol >= 0 and newCol < WIDTH:
#                     resForThis += dp(movesLeft - 1, GRID[newRow][newCol])
            
#             return resForThis % MOD
        
#         res = 0
#         for r in range(HEIGHT):
#             for c in range(WIDTH):
#                 if r == 3 and c == 0:
#                     continue
#                 if r == 3 and c == 2:
#                     continue
#                 res += dp(n - 1, GRID[r][c])
#                 res %= MOD
#         return res
        

# SOLUTION 2, MATRIX EXPONENTIATION
# O(12 * 12 * 12 * logN)
class Solution:
    def knightDialer(self, n: int) -> int:
        MOD = 10**9 + 7
        vec = [1] * 10 # number of ways to to end at that number

        adj = {
            1 : [6, 8],
            2 : [7, 9],
            3 : [4, 8],
            4 : [0, 3, 9],
            5 : [],
            6 : [0, 1, 7],
            7 : [2, 6],
            8 : [1, 3],
            9 : [4, 2],
            0 : [4, 6]
        }

        # if number a can reach number b
        def feed(a, b):
            return b in adj[a]

        T = [[0] * 10 for _ in range(10)]
        for r in range(10):
            for c in range(10):
                if feed(c, r):
                    T[r][c] = 1
        
        def matMul(A, B):
            size = len(A)
            C = [[0] * size for _ in range(size)]
            for i in range(size):
                for k in range(size):
                    if A[i][k] == 0:
                        continue
                    for j in range(size):
                        C[i][j] = (C[i][j] + A[i][k] * B[k][j]) % MOD
            return C

        def matVecMul(M, v):
            size = len(v)
            result = [0] * size
            for i in range(size):
                for j in range(size):
                    result[i] = (result[i] + M[i][j] * v[j]) % MOD
            return result

        def matPow(M, p):
            size = len(M)
            result = [[0] * size for _ in range(size)]
            for i in range(size):
                result[i][i] = 1  # identity matrix
            while p > 0:
                if p & 1:
                    result = matMul(result, M)
                M = matMul(M, M)
                p >>= 1
            return result
        
        transitions = n - 1
        tpow = matPow(T, transitions)

        return sum(
            matVecMul(tpow, vec)
        ) % MOD

        