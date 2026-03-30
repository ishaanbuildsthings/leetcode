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


MOD = 676767677
t = int(input())

def solve():
    x, y = list(map(int, input().split())) # x 1s, y -1ss

    # print(F'{x=} {y=}')

    diff = abs(x - y)
    # print(f'{diff=}')
    facs = allFactors(diff) if diff > 0 else [1]
    print(len(facs))
    arr = [1] * x
    arr += ([-1] * y)
    print(*arr)

    # if x == 0 or y == 0:
    #     big = max(x, y)
    #     facs = allFactors(big)
    #     print(len(facs) % MOD)
    #     arr = [1 if x > 0 else -1] * big
    #     print(*arr)
    #     return


    # # print(f'{x=} {y=}')
    # res = ([1] * x) + ([-1] * y)
    # # print(f'init res: {res}')

    # ways = 1 # always 1 way which is everything
    # tot = sum(res)
    # # check any prefix
    # curr = 0
    # for i in range(len(res) - 1):
    #     curr += res[i]
    #     remain = tot - curr
    #     if curr == remain:
    #         ways += 1
    
    # print(ways)
    # print(*res)



for _ in range(t):
    # print('-------------')

    solve()
