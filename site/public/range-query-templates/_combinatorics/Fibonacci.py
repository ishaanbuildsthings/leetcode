from math import isqrt

# returns a list of all fibs <= n
# example: n=10 -> [0, 1, 1, 2, 3, 5, 8]
# O(log(n)) time and space
def getFibList(n):
    fibs = [0]
    nxt = 1
    while nxt <= n:
        fibs.append(nxt)
        nxt = fibs[-1] + fibs[-2] if len(fibs) >= 2 else 1
    return fibs

# O(1) time
# x is fibonacci number exactly when 5x^2 + 4 or 5x^2 - 4 is a perfect square
def isFib(x):
    if x < 0:
        return False
    for candidate in (5 * x * x + 4, 5 * x * x - 4):
        root = isqrt(candidate)
        if root * root == candidate:
            return True
    return False

# gets the xth fibonacci number
# getXthFib(1) -> 0
# getXthFib(2) -> 1
# getXthFib(3) -> 1
# getXthFib(10) -> 34
# O(log(x))
def getXthFib(x):
    def pair(k):
        if k == 0:
            return (0, 1)
        a, b = pair(k >> 1)
        even = a * (2 * b - a)
        odd = a * a + b * b
        return (odd, even + odd) if k & 1 else (even, odd)
    return pair(x - 1)[0]

# same as above with mod
def getXthFibMod(x, mod):
    def pair(k):
        if k == 0:
            return (0, 1 % mod)
        a, b = pair(k >> 1)
        even = a * (2 * b - a) % mod
        odd = (a * a + b * b) % mod
        return (odd, (even + odd) % mod) if k & 1 else (even, odd)
    return pair(x - 1)[0]