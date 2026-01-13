n = int(input())
MOD = 10**9 + 7
curr = 1
for power in range(1, n + 1):
    curr *= 2
    curr %= MOD
print(curr)