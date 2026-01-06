n, a, b = list(map(int, input().split()))
dp = [0] * (b + 1) # dp[sum] is the chance of making that sum as we process rolls
dp[0] = 1
for roll in range(1, n + 1):
    pf = []
    curr = 0
    for v in dp:
        curr += v
        pf.append(curr)
    ndp = [0] * (b + 1)
    for nsum in range(1, b + 1):
        left = max(0, nsum - 6)
        right = max(0, nsum - 1)
        tot = pf[right] - (pf[left - 1] if left else 0)
        newOdds = tot / 6
        ndp[nsum] += newOdds
    dp = ndp

print(f"{sum(dp[a:b+1]):.6f}")