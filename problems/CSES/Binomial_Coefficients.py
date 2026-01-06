MOD = 10**9 + 7
MAX_N = 10**6
fact = [1] # 0! % MOD
for num in range(1, MAX_N + 1):
    nfac = (fact[-1] * num) % MOD
    fact.append(nfac)

invFact = [1] * (MAX_N + 1)
invFact[MAX_N] = pow(fact[MAX_N], MOD - 2, MOD)
for i in range(MAX_N, 0, -1):
    invFact[i - 1] = invFact[i] * i % MOD

def nCkMod(n, k):
    if k < 0 or k > n:
        return 0
    return fact[n] * invFact[k] % MOD * invFact[n - k] % MOD

n = int(input())
for _ in range(n):
    a, b = map(int, input().split())
    print(nCkMod(a, b))