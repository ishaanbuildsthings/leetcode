class Solution:
    def zigZagArrays(self, n: int, l: int, r: int) -> int:
        MOD = 10**9 + 7

        width = r - l + 1
        vec = [1] * (width * 2) # number of ways to make a sequence ending in vec[that number], first half means we have to move up after

        T = [[0] * (width*2) for _ in range(width*2)]

        # first solving for the new states where "we must go up" which means we fadded up numbers bigger than me
        for number in range(width):
            for prevBigger in range(number + 1, width):
                T[number][prevBigger + width] = 1
        
        # now new states where we must go down so we just came from a smaller number
        for number in range(width):
            for prevSmaller in range(number):
                T[number + width][prevSmaller] = 1
        
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
        
        powed = matPow(T, n-1)
        finalVec = matVecMul(powed, vec)
        return sum(finalVec) % MOD


