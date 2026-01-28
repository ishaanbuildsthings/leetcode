def nc3(n):
    return n * (n - 1) * (n - 2) // 6
import collections
BIG = 31623

import math
import random

def _modMul(a, b, mod):
    return (a * b) % mod

def _modPow(a, e, mod):
    return pow(a, e, mod)

def _isPrime(n):
    if n < 2:
        return False
    smallPrimes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for p in smallPrimes:
        if n % p == 0:
            return n == p

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    # deterministic for 64-bit
    bases = [2, 325, 9375, 28178, 450775, 9780504, 1795265022]
    for a in bases:
        if a % n == 0:
            continue
        x = _modPow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        ok = False
        for _ in range(s - 1):
            x = _modMul(x, x, n)
            if x == n - 1:
                ok = True
                break
        if not ok:
            return False
    return True

def _pollardRho(n):
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3

    while True:
        c = random.randrange(1, n)
        x = random.randrange(0, n)
        y = x
        d = 1

        def f(v):
            return (_modMul(v, v, n) + c) % n

        while d == 1:
            x = f(x)
            y = f(f(y))
            d = math.gcd(abs(x - y), n)

        if d != n:
            return d

def _factorRec(n, out):
    if n == 1:
        return
    if _isPrime(n):
        out[n] = out.get(n, 0) + 1
        return
    d = _pollardRho(n)
    _factorRec(d, out)
    _factorRec(n // d, out)

def fastFactorize(number):
    curr = number
    primePowers = [] # list of lists: [1, p, p^2, ...] for each prime factor

    factors = {}
    _factorRec(curr, factors)

    for p in sorted(factors.keys()):
        cnt = factors[p]
        powers = [1]
        powVal = 1
        for _ in range(cnt):
            powVal *= p
            powers.append(powVal)
        primePowers.append(powers)

    divs = [1]
    for powers in primePowers:
        base = divs[:]
        for mul in powers[1:]:
            for v in base:
                divs.append(v * mul)

    divs.sort()
    return divs


def solve():
    n = int(input())
    A = list(map(int, input().split()))
    # print('=========')
    
    mx = max(A)
    frq = collections.Counter([str(x) for x in A])

    res = 0
    for k, v in frq.items():
        triples = nc3(int(v))
        orders = 6 * triples
        res += orders
    
    prevAdded = 0
    A.sort()
    # print(f'{A=}')
    frqLeft = collections.Counter()
    for i, v in enumerate(A):
        if i and A[i] == A[i - 1]:
            res += prevAdded
            frqLeft[str(v)] += 1
            continue
        prevAdded = 0
        for div in fastFactorize(v):
            if div == 1:
                continue
            # print(f'v is: {v} div is: {div}')
        # print(f'{v=}')
        # for div in divs[v]:
            # print(f'{div=}')
            leftOpts = frqLeft[str(v // div)]
            # print(f'left opts: {leftOpts}')
            reqRight = div * v
            # print(f'req right: {reqRight}')
            if reqRight > mx:
                break
            frqRight = frq[str(reqRight)] - frqLeft[str(reqRight)]
            # print(f'frq right: {frqRight}')
            res += leftOpts * frqRight
            prevAdded += leftOpts * frqRight
        # print(f'prev added now: {prevAdded}')
        frqLeft[str(v)] += 1
    
    print(res)



t = int(input())
for _ in range(t):
    solve()