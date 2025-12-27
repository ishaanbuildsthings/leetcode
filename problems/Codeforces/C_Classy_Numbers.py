T = int(input())
for _ in range(T):
    L, R = map(int, input().split())
    strL = str(L)
    strR = str(R)
    diff = len(strR) - len(strL)
    strL = '0' * diff + strL
    n = len(strR)

    looseCache = [
        [
            None for _ in range(4)
        ] for _ in range(n)
    ]

    def dp(i, lowTight, highTight, used):
        if used > 3:
            return 0
        if i == n:
            return 1
        if not lowTight and not highTight:
            if looseCache[i][used] is not None:
                return looseCache[i][used]

        ub = 9 if not highTight else int(strR[i])
        lb = 0 if not lowTight else int(strL[i])
        resHere = 0
        for d in range(lb, ub + 1):
            nUsed = used + (d != 0)
            nht = highTight and d == ub
            nlt = lowTight and d == lb
            resHere += dp(i + 1, nlt, nht, nUsed)
        if not lowTight and not highTight:
            looseCache[i][used] = resHere
        return resHere
    
    print(dp(0, 1, 1, 0))

