# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/matrices/LinearRecurrence.py

MOD = 10**9 + 7


# Linear recurrences mod MOD, terms 0-indexed:
#   a[i] = coeffs[0] * a[i-1] + coeffs[1] * a[i-2] + ... + coeffs[d-1] * a[i-d]   for i >= d
# The same thing as vec @ M^n with a d x d companion matrix, but d^2 log n instead of d^3 log n
# nthTerm(coeffs, initial, n)     a[n], given coeffs and the first d terms
# fib: nthTerm([1, 1], [0, 1], 10) -> 55


# a[n] of the recurrence above, n >= 0, len(initial) == len(coeffs) == d >= 1
# O(d^2 log n), Python big ints make it nearer d^1.6 log n for big d
def nthTerm(coeffs, initial, n):
    d = len(coeffs)
    if d == 0 or len(initial) != d:
        raise ValueError(f"nthTerm needs d >= 1 coeffs and exactly d initial terms, got {d} and {len(initial)}")
    if n < d:
        return initial[n] % MOD
    # a[n] = [x^n] P(x) / Q(x) with Q = 1 - coeffs[0] x - ... - coeffs[d-1] x^d and P = (initial * Q) mod x^d
    # Bostan-Mori: P/Q = P(x)Q(-x) / Q(x)Q(-x), the denominator is even, so keep the half of the numerator
    # matching n's parity and halve n
    Q = [1] + [(-c) % MOD for c in coeffs]
    P = _polyMul([x % MOD for x in initial], Q)[:d]
    while n:
        Qneg = [q if i % 2 == 0 else (MOD - q) % MOD for i, q in enumerate(Q)]
        P = _polyMul(P, Qneg)[n & 1 :: 2]
        Q = _polyMul(Q, Qneg)[::2]
        n >>= 1
    return P[0]  # Q[0] stays 1


def _polyMul(a, b):  # coefficients in [0, MOD)
    if min(len(a), len(b)) <= 8:
        res = [0] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    res[i + j] += x * y
        return [x % MOD for x in res]
    # pack each polynomial into one big int (fixed-width slots) and let Python multiply them
    width = ((min(len(a), len(b)) * (MOD - 1) ** 2).bit_length() + 7) // 8
    pa = int.from_bytes(b"".join(x.to_bytes(width, "little") for x in a), "little")
    pb = int.from_bytes(b"".join(x.to_bytes(width, "little") for x in b), "little")
    size = len(a) + len(b) - 1
    raw = (pa * pb).to_bytes(width * size, "little")
    fromBytes = int.from_bytes
    return [fromBytes(raw[j : j + width], "little") % MOD for j in range(0, width * size, width)]
