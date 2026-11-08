# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/matrices/LinearRecurrence.py

MOD = 10**9 + 7  # berlekampMassey / guessNthTerm need MOD prime


# Linear recurrences mod MOD, terms 0-indexed:
#   a[i] = coeffs[0] * a[i-1] + coeffs[1] * a[i-2] + ... + coeffs[d-1] * a[i-d]   for i >= d
# The same thing as vec @ M^n with a d x d companion matrix, but d^2 log n instead of d^3 log n
# nthTerm(coeffs, initial, n)     a[n], given coeffs and the first d terms
# berlekampMassey(seq)            the shortest coeffs that generate seq
# guessNthTerm(seq, n)            a[n], given enough first terms (2d of them suffice) and no recurrence
# fib: nthTerm([1, 1], [0, 1], 10) -> 55
#      berlekampMassey([0, 1, 1, 2, 3, 5]) -> [1, 1]
#      guessNthTerm([0, 1, 1, 2, 3, 5], 10) -> 55


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


# shortest coeffs (same convention as nthTerm) with seq[i] = sum coeffs[j] * seq[i-1-j] for all i >= len(coeffs)
# O(len(seq)^2)
def berlekampMassey(seq):
    seq = [x % MOD for x in seq]
    cur = [1]  # connection polynomial: sum cur[j] * seq[i-j] = 0
    prev = [1]
    length = 0
    gap = 1
    prevDisc = 1
    for i, val in enumerate(seq):
        disc = val
        for j in range(1, length + 1):
            disc += cur[j] * seq[i - j]
        disc %= MOD
        if disc == 0:
            gap += 1
            continue
        factor = disc * pow(prevDisc, MOD - 2, MOD) % MOD
        nxt = cur + [0] * max(0, len(prev) + gap - len(cur))
        for j, p in enumerate(prev):
            nxt[j + gap] = (nxt[j + gap] - factor * p) % MOD
        if 2 * length <= i:
            prev, length, prevDisc, gap = cur, i + 1 - length, disc, 1
        else:
            gap += 1
        cur = nxt
    cur += [0] * (length + 1 - len(cur))
    return [(-c) % MOD for c in cur[1 : length + 1]]


# a[n] of the shortest recurrence that fits seq, n >= 0 (for a recurrence of order d, give at least 2d terms)
# O(len(seq)^2 + d^2 log n)
def guessNthTerm(seq, n):
    if n < len(seq):
        return seq[n] % MOD
    coeffs = berlekampMassey(seq)
    if not coeffs:
        return 0
    return nthTerm(coeffs, seq[: len(coeffs)], n)


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
