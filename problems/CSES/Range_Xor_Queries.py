n, q = map(int, input().split())
A = list(map(int, input().split()))
pf = []
curr = 0
for v in A:
    curr ^= v
    pf.append(curr)
for _ in range(q):
    l, r = map(int, input().split())
    l -= 1
    r -= 1
    if not l:
        print(pf[r])
    else:
        print(pf[r] ^ pf[l - 1])