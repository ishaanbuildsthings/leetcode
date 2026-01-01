MOD = 10**9 + 7
n = int(input())
A = list(map(int, input().split()))
mx = max(A)

counts = [0] * (n + 1)
for v in A:
    counts[v] += 1

# for each factor, see how many numbers are divisible by it
factorToDivis = [0] * (n + 1)
for factor in range(1, n + 1):
    score = 0
    curr = factor
    while curr <= mx:
        score += counts[curr]
        curr += factor
    factorToDivis[factor] = score

modPow2 = [1] # 2^e = modPow2[e]
for i in range(n + 1):
    modPow2.append((2 * modPow2[-1]) % MOD)

res = [0] * (n + 1)
for factor in range(n, 0, -1):
    numsWithFactor = factorToDivis[factor]
    numberOfSubsetsThatHaveThisAsAFactor = modPow2[numsWithFactor] - 1 # don't allow empty subset
    # but we need to exclude things that have a larger factor
    lost = 0
    curr = factor + factor
    while curr <= n:
        lost += res[curr]
        curr += factor
    res[factor] = (numberOfSubsetsThatHaveThisAsAFactor - lost) % MOD


print(*res[1:])
