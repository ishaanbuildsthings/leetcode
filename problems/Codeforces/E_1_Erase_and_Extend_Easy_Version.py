n, k = map(int, input().split())
s = input()

res = 'z' * k

for takePf in range(1, n + 1):
    pf = s[:takePf]
    fullFits = k // len(pf)
    start = pf * fullFits
    remainLength = k - len(start)
    start += pf[:remainLength]
    res = min(res, start)

print(res)