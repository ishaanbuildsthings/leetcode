n, k = map(int, input().split())
MOD = 10**9 + 7

# b^e % MOD
def fn(b, e):
    base = b
    res = 1
    for bit in range(32):
        if (1 << bit) & e:
            res *= base
            res %= MOD
        base *= base
        base %= MOD
    return res
    # if e == 0:
    #     return 1
    # if e % 2:
    #     return (b * fn(b, e - 1)) % MOD
    # half = fn(b, e // 2)
    # return (half * half) % MOD

modFac = [1]
for fac in range(1, n + 1):
    nfac = (modFac[fac-1] * fac) % MOD
    modFac.append(nfac)

invFac = [1] * (n + 1)
invFac[n] = pow(modFac[n], MOD - 2, MOD)
for i in range(n - 1, -1, -1):
    invFac[i] = invFac[i + 1] * (i + 1) % MOD

def nckMod(N, K):
    # N! * N-1! * ...
    numerator = modFac[N]
    denominator = invFac[N-K]

    return (numerator * denominator * invFac[K]) % MOD


# number of ways to form a valid sequence is:

# num ways to form ANY sequence and we subtract invalid ones
numAnySequence = fn(k, n)

# invalid sequences is:
# a sequence where at least one number is missing, say a 1
# or a sequence where a 5 is missing, etc

# we subtract all of those for one number missing, and we need the number of ways to pick one number missing

invalidSequences = 0

for missingCount in range(1, k + 1):
    waysToPickMissing = nckMod(k, missingCount)
    presentCount = k - missingCount
    sequences = (waysToPickMissing * fn(presentCount, n)) % MOD
    shouldAdd = (missingCount % 2) == 1
    if shouldAdd:
        invalidSequences += sequences
    else:
        invalidSequences -= sequences
    invalidSequences %= MOD

print((numAnySequence - invalidSequences) % MOD)





