n = int(input())
grid = []
for i in range(n):
    grid.append(input().strip())
 
MOD = 10**9 + 7
dp = [0] * n # the above row
for c in range(n):
    if grid[0][c] == '*':
        break
    dp[c] = 1
for r in range(1, n):
    newDp = [0] * n
    for c in range(n):
        if grid[r][c] == '*':
            continue
        newDp[c] = ((newDp[c - 1] if c else 0) + dp[c]) % MOD
    dp = newDp
print(dp[-1])
