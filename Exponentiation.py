MOD = 10**9 + 7
n = int(input())
for _ in range(n):
    b, e = list(map(int, input().split()))

    BASE = b
    res = 1
    for bit in range(32):
        if (1 << bit) & e:
            res *= BASE
            res %= MOD
        BASE *= BASE
        BASE %= MOD

    print(res % MOD)


# 5^11 = 5^1 * 5^2 * 5^8

# 11 = 1 0 1 1
