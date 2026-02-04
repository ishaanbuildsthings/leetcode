def solve():
    n, q = map(int, input().split())
    C = list(map(int, input().split()))
    qs = []
    for _ in range(q):
        l, r = map(int, input().split())
        l -= 1
        r -= 1
        qs.append((l, r))
    # print('=======')
    # print(f'{C=}')
    # print(f'{qs=}')

    pf = []
    curr = 0
    pfOnes = []
    currOnes = 0
    for v in C:
        curr += v
        currOnes += v == 1
        pf.append(curr)
        pfOnes.append(currOnes)
    
    def sumQuery(l, r):
        if not l:
            return pf[r]
        return pf[r] - pf[l - 1]
    
    def ones(l, r):
        if not l:
            return pfOnes[r]
        return pfOnes[r] - pfOnes[l - 1]
    
    for l, r in qs:
        if r - l == 0:
            print("NO")
            continue
        tot = sumQuery(l, r)
        numOnes = ones(l, r)
        usedForOnes = 2 * numOnes
        remain = tot - usedForOnes
        remainNumbers = (r - l + 1) - numOnes
        if remain >= remainNumbers:
            print("YES")
        else:
            print("NO")
t = int(input())
for _ in range(t):
    solve()