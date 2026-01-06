n, tot = map(int, input().split())
A = list(map(int, input().split()))
vToI = {}
for i, v in enumerate(A):
    req = tot - v
    if str(req) in vToI:
        print(*[i + 1, vToI[str(req)] + 1])
        exit()
    else:
        vToI[str(v)] = i
print('IMPOSSIBLE')