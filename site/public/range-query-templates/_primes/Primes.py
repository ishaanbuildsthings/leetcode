# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/primes/Primes.py

# @if isPrime
# isPrime(97) -> True        isPrime(10**18 + 9) -> True        isPrime(561) -> False
# @endif
# @if primeFactorize
# primeFactorize(360) -> [(2, 3), (3, 2), (5, 1)]        primeFactorize(1) -> []
# @endif
# @if allFactors
# allFactors(12) -> [1, 2, 3, 4, 6, 12]
# @endif
# @if sieveIsPrime sieveSmallestPrimeFactor sieveFactorize sieveFactorizeUpToNSquared sievePrimes
# sieve = PrimeSieve(10**6)                  # sieves 0..10**6, both ends included: O(N) once, then the calls below
# @endif
# @if sieveIsPrime
# sieve.isPrime(97) -> True                  # needs x <= N
# @endif
# @if sieveSmallestPrimeFactor
# sieve.smallestPrimeFactor(91) -> 7         # needs 2 <= x <= N
# @endif
# @if sieveFactorize
# sieve.factorize(360) -> [(2, 3), (3, 2), (5, 1)]                  # needs 1 <= x <= N
# @endif
# @if sieveFactorizeUpToNSquared
# sieve.factorizeUpToNSquared(999962000357) -> [(999979, 1), (999983, 1)]    # needs 1 <= x <= N^2
# @endif
# @if sievePrimes
# sieve.primes -> [2, 3, 5, 7, ...]          # every prime <= N
# @endif
# @if primesUpTo
# primesUpTo(20) -> [2, 3, 5, 7, 11, 13, 17, 19]
# @endif
# @if forEachPrimeUpTo
# forEachPrimeUpTo(20, print)                # calls print(2), print(3), ..., print(19) without storing the list
# @endif
# @if primesInRange
# primesInRange(10**12, 10**12 + 100) -> [1000000000039, 1000000000061, 1000000000063, 1000000000091]
# @endif
# @if countPrimes
# countPrimes(100) -> 25                     countPrimes(10**9) -> 50847534
# @endif

from itertools import compress
from math import isqrt
# @if primeFactorize allFactors
import random
from math import gcd
# @endif
# @if sieveIsPrime sieveSmallestPrimeFactor sieveFactorize sieveFactorizeUpToNSquared sievePrimes
from array import array
# @endif

# @if isPrime primeFactorize allFactors
# ============================================================== ONE BIG NUMBER (no setup, any x < 2^64)
# @endif
# @if isPrime primeFactorize allFactors
_SMALL = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


# O(log x) -- True if x is prime; deterministic Miller-Rabin, exact for every x < 2^64
def isPrime(x):
    if x < 2:
        return False
    for p in _SMALL:
        if x % p == 0:
            return x == p
    d, s = x - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if a % x == 0:
            continue
        y = pow(a, d, x)
        if y == 1 or y == x - 1:
            continue
        for _ in range(s - 1):
            y = y * y % x
            if y == x - 1:
                break
        else:
            return False
    return True


# @endif
# @if primeFactorize allFactors
def _pollardRho(n):
    # a non-trivial factor of the composite n (randomized)
    if n % 2 == 0:
        return 2
    while True:
        c = random.randrange(1, n)
        x = y = random.randrange(0, n)
        d = 1
        while d == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = gcd(abs(x - y), n)
        if d != n:
            return d


# about x^(1/4) expected (randomized) -- [(prime, exponent), ...] sorted by prime, for any 1 <= x < 2^64
def primeFactorize(x):
    if x < 1:
        raise ValueError(f"primeFactorize: needs x >= 1, got {x}")
    counts = {}
    for p in _SMALL:
        while x % p == 0:
            x //= p
            counts[p] = counts.get(p, 0) + 1
    stack = [x] if x > 1 else []
    while stack:
        m = stack.pop()
        if isPrime(m):
            counts[m] = counts.get(m, 0) + 1
        else:
            d = _pollardRho(m)
            stack += [d, m // d]
    return sorted(counts.items())


# @endif
# @if allFactors
# primeFactorize cost + D log D (D = number of divisors) -- every positive divisor of x, increasing
def allFactors(x):
    res = [1]
    for p, e in primeFactorize(x):
        res = [d * p ** k for d in res for k in range(e + 1)]
    return sorted(res)


# @endif
# @if sieveIsPrime sieveSmallestPrimeFactor sieveFactorize sieveFactorizeUpToNSquared sievePrimes
# ============================================================== MANY SMALL NUMBERS (sieve once up to N)
# @endif
# @if sieveIsPrime sieveSmallestPrimeFactor sieveFactorize sieveFactorizeUpToNSquared sievePrimes
class PrimeSieve:
    # O(N log log N), memory about 5N bytes -- sieves every number 0..N, N included (Python: N = 10^7 takes ~0.4s)
    def __init__(self, n):
        self.n = n
        flags = bytearray([1]) * (n + 1)
        flags[:2] = b"\x00\x00"[: min(2, n + 1)]
        for p in range(2, isqrt(n) + 1):
            if flags[p]:
                flags[p * p :: p] = bytes(len(range(p * p, n + 1, p)))
        self._flags = flags
        self.primes = list(compress(range(n + 1), flags))  # every prime <= N, increasing
        # spf[x] = smallest prime factor of x: going from big primes to small, the smallest one writes last
        spf = array("i", range(n + 1))
        for p in reversed(self.primes[: self._countUpTo(isqrt(n))]):
            spf[p * p :: p] = array("i", [p]) * len(range(p * p, n + 1, p))
        self._spf = spf

    def _countUpTo(self, x):
        lo, hi = 0, len(self.primes)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.primes[mid] <= x:
                lo = mid + 1
            else:
                hi = mid
        return lo

    # @if sieveIsPrime
    # O(1) -- True if x is prime; needs 0 <= x <= N
    def isPrime(self, x):
        return self._flags[x] == 1

    # @endif
    # @if sieveSmallestPrimeFactor
    # O(1) -- the smallest prime dividing x; needs 2 <= x <= N
    def smallestPrimeFactor(self, x):
        if x < 2:
            raise ValueError(f"smallestPrimeFactor: needs x >= 2, got {x}")
        return self._spf[x]

    # @endif
    # @if sieveFactorize sieveFactorizeUpToNSquared
    # O(log x) -- [(prime, exponent), ...] sorted by prime; needs 1 <= x <= N
    def factorize(self, x):
        res = []
        while x > 1:
            p = self._spf[x]
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            res.append((p, e))
        return res

    # @endif
    # @if sieveFactorizeUpToNSquared
    # O(number of primes <= sqrt(x)) -- like factorize, but x can go up to N^2: trial division by the sieved primes;
    # whatever is left after the primes up to sqrt(x) is 1 or a single prime above sqrt(x)
    def factorizeUpToNSquared(self, x):
        if x <= self.n:
            return self.factorize(x)
        if x > self.n * self.n:
            raise ValueError(f"factorizeUpToNSquared: needs x <= N^2 = {self.n * self.n}, got {x}")
        res = []
        for p in self.primes:
            if p * p > x:
                break
            if x % p == 0:
                e = 0
                while x % p == 0:
                    x //= p
                    e += 1
                res.append((p, e))
        if x > 1:
            res.append((x, 1))
        return res
    # @endif


# @endif
# @if primesUpTo forEachPrimeUpTo primesInRange countPrimes
# ============================================================== LISTING AND COUNTING PRIMES
# @endif
# @if primesUpTo
# O(N log log N), memory about N bytes plus the list -- every prime <= N, increasing (Python: N = 10^8 takes ~2.5s)
def primesUpTo(n):
    if n < 2:
        return []
    flags = bytearray([1]) * (n + 1)
    flags[0] = flags[1] = 0
    for p in range(2, isqrt(n) + 1):
        if flags[p]:
            flags[p * p :: p] = bytes(len(range(p * p, n + 1, p)))
    return list(compress(range(n + 1), flags))


# @endif
# @if forEachPrimeUpTo
# O(N log log N) time, O(sqrt(N)) memory (segmented) -- calls f(p) for every prime p <= N in increasing order, without
# ever storing them (Python: N = 10^8 takes ~1s; the C++ version does 10^9 in ~0.7s)
def forEachPrimeUpTo(n, f):
    if n < 2:
        return
    r = isqrt(n)
    small = bytearray([1]) * (r + 1)
    base = []
    for p in range(2, r + 1):
        if small[p]:
            base.append(p)
            small[p * p :: p] = bytes(len(range(p * p, r + 1, p)))
    size = 1 << 18
    for lo in range(2, n + 1, size):
        hi = min(n, lo + size - 1)
        block = bytearray([1]) * (hi - lo + 1)
        for p in base:
            if p * p > hi:
                break
            start = max(p * p, (lo + p - 1) // p * p)
            block[start - lo :: p] = bytes(len(range(start, hi + 1, p)))
        for p in compress(range(lo, hi + 1), block):
            f(p)


# @endif
# @if primesInRange
# O((hi - lo) log log hi + sqrt(hi)) -- every prime in [lo, hi], increasing; hi can be ~10^12 as long as hi - lo is
# about 10^7 or less
def primesInRange(lo, hi):
    lo = max(lo, 2)
    if lo > hi:
        return []
    r = isqrt(hi)
    small = bytearray([1]) * (r + 1)
    block = bytearray([1]) * (hi - lo + 1)
    for p in range(2, r + 1):
        if small[p]:
            small[p * p :: p] = bytes(len(range(p * p, r + 1, p)))
            start = max(p * p, (lo + p - 1) // p * p)
            block[start - lo :: p] = bytes(len(range(start, hi + 1, p)))
    return list(compress(range(lo, hi + 1), block))


# @endif
# @if countPrimes
# O(n^(3/4)) time, O(sqrt(n)) memory (Lucy_Hedgehog) -- how many primes are <= n, without listing them (Python: n =
# 10^10 takes ~1s, 10^11 ~5s; the C++ version does 10^13 in ~1s)
def countPrimes(n):
    if n < 2:
        return 0
    r = isqrt(n)
    # count[v] for every distinct value v = n // k: "numbers in 2..v not yet crossed off"; small v at lowCount[v],
    # big v = n // k at highCount[k]
    lowCount = [0] + [v - 1 for v in range(1, r + 1)]
    highCount = [0] + [n // k - 1 for k in range(1, r + 1)]
    for p in range(2, r + 1):
        if lowCount[p] == lowCount[p - 1]:
            continue  # p was crossed off: not a prime
        before = lowCount[p - 1]  # primes below p
        p2 = p * p
        kEnd = min(r, n // p2)
        for k in range(1, kEnd + 1):
            kp = k * p
            highCount[k] -= (highCount[kp] if kp <= r else lowCount[n // kp]) - before
        for v in range(r, p2 - 1, -1):
            lowCount[v] -= lowCount[v // p] - before
    return highCount[1]
# @endif
