n = int(input())
keysNeeded = []
keys = []
for i in range(n):
    a, b = list(map(int, input().split()))
    keysNeeded.append(a)
    keys.append(b)

res = 0
currKeys = 0
for i in range(n):
    diff = keysNeeded[i] - currKeys
    diff = max(diff, 0)
    res += diff
    currKeys = max(currKeys, keysNeeded[i])
    currKeys += keys[i]

print(res)
