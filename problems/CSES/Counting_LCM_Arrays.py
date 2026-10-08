t = int(input())

MOD = 10**9 + 7


# A[x, y] @ B[y, z] = C[x, z]
# O(x*y*z)
def matMul(A, B):
    colsB = list(zip(*B))
    C = []
    for rowA in A:
        newRow = []
        for colB in colsB:
            newRow.append(sum(a * b for a, b in zip(rowA, colB)) % MOD)
        C.append(newRow)
    return C

# vec[1, x] @ mat[x, y] = vec[1, y]
# O(x*y)
def vecMatMul(vec, M):
    result = []
    for colM in zip(*M):
        result.append(sum(x * y for x, y in zip(vec, colM)) % MOD)
    return result

# mat[x, x] ^ power
# O(x^3) * log(power)
def matPow(M, p):
    size = len(M)
    result = [[int(i == j) for j in range(size)] for i in range(size)]
    while p > 0:
        if p & 1:
            result = matMul(result, M)
        M = matMul(M, M)
        p >>= 1
    return result

import random
from math import gcd

def isPrime(n):
    if n < 2:
        return False
    smallPrimes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in smallPrimes:
        if n % p == 0:
            return n == p

    d = n - 1
    s = 0
    while d & 1 == 0:
        d >>= 1
        s += 1

    for a in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True

def pollardRho(n):
    if n & 1 == 0:
        return 2
    if n % 3 == 0:
        return 3
    while True:
        c = random.randrange(1, n)
        f = lambda x: (x * x + c) % n
        x = random.randrange(0, n)
        y = x
        d = 1
        while d == 1:
            x = f(x)
            y = f(f(y))
            d = gcd(abs(x - y), n)
        if d != n:
            return d


# Prime factorization
# Output shape: [(p1, e1), (p2, e2), ...] where n = Π (pi ** ei)
# Time: expected ~O(n^(1/4) * log n), randomized
# Supports: integers up to 2^64 (≈ 1.8e19)
def primeFactorize(n):
    factors = {}

    def dfs(m):
        if m == 1:
            return
        if isPrime(m):
            factors[m] = factors.get(m, 0) + 1
            return
        d = pollardRho(m)
        dfs(d)
        dfs(m // d)

    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            factors[p] = factors.get(p, 0) + e

    if n > 1:
        dfs(n)

    return sorted(factors.items())


# All positive divisors of n
# Output shape: [d1, d2, ...]
# Time: expected ~O(n^(1/4) * log n + D), where D = number of divisors
def allFactors(n):
    primeFactors = primeFactorize(n)
    res = [1]
    for p, e in primeFactors:
        cur = []
        mul = 1
        for _ in range(e):
            mul *= p
            for v in res:
                cur.append(v * mul)
        res += cur
    return res


def solve():
    n, k = map(int, input().split())

    # holds [(p, e), (p, e), ...]
    primeFacs = primeFactorize(k)

    res = 1

    # number of ways to make a sequence of size N, where every pair is like p^e lcm
    def solveForPrimeFactor(exponent):
        # 2x2 transition table

        # [sequences ending with max exponent, below max exponent]
        vec = [1, exponent]
        mat = [[1, exponent], [1, 0]]
        transitions = n - 1
        bigMat = matPow(mat, transitions)
        finalVec = vecMatMul(vec, bigMat)
        return sum(finalVec) % MOD


        # bigger log x log transition table
        # vec = [1] * (exponent + 1) # 1 way to make any sequence of length 1, as we start with any number

        # side = len(vec)

        # mat = [[0 for _ in range(side)] for _ in range(side)]

        # # any previous sequence not p^e must be followed by p^e
        # # so last column of the mat can be followed by any previous one
        # for r in range(len(mat)):
        #     mat[r][-1] = 1
        
        # # otherwise, the # of ways to form a sequence with x as the exponent
        # # is exactly equal to the previous # of p^e
        # for c in range(len(mat[0]) - 1):
        #     mat[-1][c] = 1
        
        # transitions = n - 1
        # bigMat = matPow(mat, transitions)
        # finalVec = vecMatMul(vec, bigMat)

        # return sum(finalVec) % MOD
    
    for p, e in primeFacs:
        res *= solveForPrimeFactor(e)
        res %= MOD
    
    print(res)



for _ in range(t):
    solve()