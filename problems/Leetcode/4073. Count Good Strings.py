MOD = 10**9 + 7
def matMul(A, B):
    size = len(A)
    C = [[0] * size for _ in range(size)]
    for i in range(size):
        for k in range(size):
            if A[i][k] == 0:
                continue
            for j in range(size):
                C[i][j] = (C[i][j] + A[i][k] * B[k][j]) % MOD
                # C[i][j] = (C[i][j] + A[i][k] * B[k][j])
    return C

def matVecMul(M, v):
    # print(f'multiplying matrix: {M}')
    # print(f'by vector: {v}')
    size = len(v)
    result = [0] * size
    for c in range(len(v)):
        resC = 0
        for r in range(len(M)):
            resC += M[r][c] * v[r]
            resC %= MOD
            # print(f'point is: {M[r][c]}')
            # print(f'vector val is: {v[c]}')
            # print(f'----accumulated res c is: {resC}')
        result[c] = resC

    # print(f'FINAL RESULT {result}')
    return result
            
    
    # for i in range(size):
    #     for j in range(size):
    #         # result[i] = (result[i] + M[i][j] * v[j]) % MOD
    #         result[i] = (result[i] + M[i][j] * v[j])
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
    
class Solution:
    def countGoodStrings(self, n: int) -> int:
        #n=
        # 1 2 3 4
        #answers
        # 2 2 4 6


        # f(x)

        # place a divider after every odd amount

        # A A A

        #  | |

        # f(4)

        # alternate after 3, get f(0)
        # alternate after 1, get 2 * f(2)



        # alternate after 1, get f(3)
        # alternate after 3, get f(1)

        

        # def dp(remain):
        #     if remain == 1:
        #         return 2
        #     if remain == 0:
        #         return 0
        #     res = 0
        #     for sz in range(1, remain, 2):
        #         res += dp(remain - sz)
        #     if remain % 2:
        #         res += 2
        #     return res

        # for v in range(2, 18, 1):
        #     print(f'{v=} {dp(v)}')

        # for v in range(1, 18, 1):
        #     print(f'{v=} {dp(v)}')

        # 68*3 - 26 = 178


        # 26*3 - 10 = 68

        # to go from X to X+2, we multiply by 3, subtract X-2


        # f(x)   [6] [2, 1, 0] -> f(x+1)
        # f(x-1) [4] [0, 0, 1] -> f(x)
        # f(x-2) [2] [-1, 0, 0] -> f(x-1)

        # n=17

        # n = 100000000000


        v1 = [6, 4, 2] # f(4) is at the head
        mat = [ [2,1,0], [0,0,1], [-1,0,0] ]

        INIT = [2, 2, 4, 6]
        if n <= 4:
            return INIT[n - 1]

        transitions = n - 4
        # print(f'{transitions=}')
        bigMat = matPow(mat, transitions)
        # print(f'{bigMat=}')

        finalVec = matVecMul(bigMat, v1)
        # print(f'{finalVec=}')
        return finalVec[0]

            
    

# f(x) = 2*f(x-1) - f(x-3)

            

#         v=1 2
# v=3 4
# v=5 10
# v=7 26
# v=9 68
# v=11 178
# v=13 466
# v=15 1220


# IN GENERAL, TO GO UP BY 2
# multiply by 2, then subtract f(x-2)


        
                