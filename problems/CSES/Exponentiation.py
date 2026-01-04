T = int(input())
for _ in range(T):
    a, b = map(int, input().split())
    MOD = 10**9 + 7

    # a^b

    res = 1
    base = a
    while b:
        if b & 1:
            res *= base
            res %= MOD
        base *= base
        b >>= 1
        base %= MOD
    print(res)

