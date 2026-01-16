
# dbca|dabc


# dbca dbca

# once we choose to duplicate, it is done and we repeat and then trim

n, k = map(int, input().split())
s = input()

res = 'z' * k

for takePf in range(1, n + 1):
    pf = s[:takePf]
    fullFits = k // len(pf)
    # print(f'full fits: {fullFits} for takepf: {takePf}')
    start = pf * fullFits
    remainLength = k - len(start)
    start += pf[:remainLength]
    res = min(res, start)

print(res)