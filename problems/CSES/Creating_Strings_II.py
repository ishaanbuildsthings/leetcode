from collections import Counter

s = input()

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

numerator = fact[len(s)]
c = Counter(s)
for k, v in c.items():
    denominator = invFact[v]
    numerator *= denominator
    numerator %= MOD

print(numerator)
