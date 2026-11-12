# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/prime-exponents-lcm-mod/template.py
# @operations: add clear count lcmAllMod remove size
# @data-structure-type: prime-exponents
# @values: online
# @keys: numbers
# @tracks: none
# @complexities:
#   add: log(U)+U^(1/4) expected
#   clear: N
#   count: 1
#   lcmAllMod: 1
#   remove: log(U)
#   size: 1
#   build: 1
# @memory:
#   layout: none
#   node: cnt[1*N] factors[1*N*log(U)]
#   tags: none
#   other: none
#   note: N = distinct values present; each keeps its factorization (at most log2 U primes). The sieve below SIEVE_LIMIT is shared by every multiset in the run and grows only as far as the values seen need

# The exact LCM of a multiset, however huge, mod a prime MOD, with adds and removes in any order (values >= 0).
# The LCM is the product of p^(the largest exponent of p in any value), so each prime keeps how many of the values
# present have each exponent, and the product of p^top % MOD is kept current: an add multiplies in the primes whose top
# exponent grew, a remove the inverse of the ones whose top fell (that's why MOD must be prime). Only the first copy of
# a value and the removal of its last copy touch the primes: copies don't change the LCM.
# Empty multiset: lcmAllMod() is 1 (the LCM of nothing); a 0 present makes it 0; so does a value divisible by MOD.
#
# Factorizing: values below SIEVE_LIMIT come from a smallest-prime-factor table that grows (by doubling) only as far
# as the values seen so far need, shared by every multiset this run, so test case after test case never rebuilds it;
# bigger values never touch it and go to Miller-Rabin + Pollard rho instead (about U^(1/4) steps, no memory), so huge
# values are fine too. Growing the table costs O(its new size) once (at most SIEVE_LIMIT), and by doubling all of the
# growth over a run adds up to O(SIEVE_LIMIT): an add that triggers it pays that, every other add just its own cost.
# Python's rho is slow on values near 1e18 (milliseconds each): fine for thousands, not millions.
#
# s = LcmModMultiset()            # mod 10**9 + 7
# s = LcmModMultiset(998244353)   # another prime
from math import gcd, isqrt
from random import getrandbits, randrange

SIEVE_LIMIT = 1 << 20  # values below this use the sieve (at most this many entries); raise it for many mid-size values
_spf = [0, 1]  # _spf[v] = smallest prime factor of v, for every v < len(_spf)
_SMALL = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def _sieveTo(n):  # the table covering every value <= n (n < SIEVE_LIMIT), grown by doubling
    global _spf
    if n < len(_spf):
        return
    size = min(SIEVE_LIMIT, max(n + 1, 2 * len(_spf)))
    spf = list(range(size))
    r = isqrt(size - 1)
    composite = bytearray(r + 1)
    primes = []
    for i in range(2, r + 1):
        if not composite[i]:
            primes.append(i)
            composite[i * i::i] = b"\x01" * len(range(i * i, r + 1, i))
    for p in reversed(primes):  # (largest first, so each entry ends up with its smallest prime)
        spf[p * p::p] = [p] * len(range(p * p, size, p))
    _spf = spf


def _isPrime(n):  # deterministic Miller-Rabin (these bases are exact below 3.3e24)
    if n < 2:
        return False
    for p in _SMALL:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in _SMALL:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def _rho(n):  # a factor of the odd composite n other than 1 and n (Brent's Pollard rho)
    while True:
        y, c, m = randrange(1, n), randrange(1, n), 128
        g = r = q = 1
        while g == 1:
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                g = gcd(q, n)
                k += m
            r *= 2
        if g == n:
            g = 1
            while g == 1:
                ys = (ys * ys + c) % n
                g = gcd(abs(x - ys), n)
        if g != n:
            return g


# {prime: exponent} of x >= 1: the sieve below SIEVE_LIMIT, else small primes, then Miller-Rabin + Pollard rho
# O(log x) below SIEVE_LIMIT, about x^(1/4) expected above
def factorize(x):
    res = {}
    stack = [x]
    while stack:
        n = stack.pop()
        if n == 1:
            continue
        if n < SIEVE_LIMIT:
            _sieveTo(n)
            while n > 1:
                p = _spf[n]
                n //= p
                res[p] = res.get(p, 0) + 1
            continue
        for p in _SMALL:
            while n % p == 0:
                n //= p
                res[p] = res.get(p, 0) + 1
        if n == 1:
            continue
        if n < SIEVE_LIMIT:
            stack.append(n)
        elif _isPrime(n):
            res[n] = res.get(n, 0) + 1
        else:
            d = _rho(n)
            stack += [d, n // d]
    return res


class LcmModMultiset:
    __slots__ = ("mod", "salt", "cnt", "n", "fac", "exps", "top", "prod")

    # O(1) -- an empty multiset; mod must be prime (a remove divides by the primes whose top exponent fell)
    def __init__(self, mod=10**9 + 7):
        self.mod = mod
        # int keys are salted, so no fixed input can make them collide
        self.salt = getrandbits(62)
        self.cnt = {}  # value -> copies
        self.n = 0
        self.fac = {}  # value present -> its factorization
        self.exps = {}  # prime -> {exponent: how many distinct values present have exactly that exponent}
        self.top = {}  # prime -> the largest exponent it has in any value present
        self.prod = 1 % mod  # the product of prime^top over the primes other than mod, % mod

    # O(logU + U^(1/4) expected) -- add one copy of x (x >= 0); the first add needing a bigger shared sieve also pays
    # its one-time growth (all of it together O(SIEVE_LIMIT) per run)
    def add(self, x):
        if x < 0:
            raise ValueError(f"LcmModMultiset.add: {x} is negative")
        self.n += 1
        k = x ^ self.salt
        c = self.cnt.get(k, 0)
        self.cnt[k] = c + 1
        if c or x == 0:  # another copy (the LCM is unchanged), or a 0 (lcmAllMod checks for it)
            return
        f = self.fac[k] = factorize(x)
        mod, salt, exps, top = self.mod, self.salt, self.exps, self.top
        for p, e in f.items():
            pk = p ^ salt
            d = exps.setdefault(pk, {})
            d[e] = d.get(e, 0) + 1
            t = top.get(pk, 0)
            if e > t:
                top[pk] = e
                if p != mod:
                    self.prod = self.prod * pow(p, e - t, mod) % mod

    # O(logU + log(MOD)) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        k = x ^ self.salt
        c = self.cnt.get(k, 0)
        if not c:
            return 0
        self.n -= 1
        if c > 1:
            self.cnt[k] = c - 1
            return 1
        del self.cnt[k]
        if x == 0:
            return 1
        mod, salt, exps, top = self.mod, self.salt, self.exps, self.top
        for p, e in self.fac.pop(k).items():
            pk = p ^ salt
            d = exps[pk]
            d[e] -= 1
            if d[e]:
                continue
            del d[e]
            if e != top[pk]:
                continue
            new = max(d) if d else 0  # (at most log2 U exponents)
            if d:
                top[pk] = new
            else:
                del exps[pk], top[pk]
            if p != mod:
                self.prod = self.prod * pow(pow(p, e - new, mod), mod - 2, mod) % mod
        return 1

    # O(1) -- the exact LCM of all values, however huge, % mod: 1 if empty (the LCM of nothing), 0 if a 0 is present
    # or some value is divisible by mod
    def lcmAllMod(self):
        if not self.n:
            return 1 % self.mod
        if (0 ^ self.salt) in self.cnt or (self.mod ^ self.salt) in self.top:
            return 0
        return self.prod

    # O(1) -- how many copies of x (0 if none)
    def count(self, x):
        return self.cnt.get(x ^ self.salt, 0)

    # O(1) -- how many values (copies count; 0 if empty)
    def size(self):
        return self.n

    # O(N) -- remove everything (the same mod; the shared sieve stays)
    def clear(self):
        self.cnt, self.fac, self.exps, self.top = {}, {}, {}, {}
        self.n = 0
        self.prod = 1 % self.mod
