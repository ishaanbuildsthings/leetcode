# TEMPLATE BY ishaanbuildsthings on github

def _checkBase(n, a, d, s):
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return True
    for _ in range(1, s):
        x = x * x % n
        if x == n - 1:
            return True
    return False

# Deterministic miller rabin to check if it is prime, O(logN), it uses that weird fermat theorem remainder thing
def isPrime(n):
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
        if n == p:
            return True
        if n % p == 0:
            return False
    d = n - 1
    s = 0
    while (d & 1) == 0:
        d >>= 1
        s += 1
    # deterministic for all n (uses 64-bit witness set)
    for a in [2, 325, 9375, 28178, 450775, 9780504, 1795265022]:
        if a % n == 0:
            continue
        if not _checkBase(n, a, d, s):
            return False
    return True