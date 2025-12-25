t = int(input())

def numToTernaryMaskAndCounts(num):
    cnt = [0] * 10
    for c in str(num):
        cnt[int(c)] += 1
        if cnt[int(c)] == 3: return (None, None)
    mask = 0
    for i, v in enumerate(cnt):
        mask += 3**i * v
    return (mask, cnt)

pow3 = [3**i for i in range(10)]

fmax = lambda x, y: x if x > y else y

for _ in range(t):
    n = int(input())
    weights = list(map(int, input().split()))
    fmask = (3 ** 10) - 1 # ternary full mask

    dp = [0] * (fmask + 1) # dp[mask] tells us the most weights we can achieve with that ternary mask

    for w in weights:
        ternaryMask, counts = numToTernaryMaskAndCounts(w)
        if ternaryMask is None:
            continue
        ndp = dp[:]
        for mask in range(fmask + 1):
            cantAddMask = False
            newMask = 0
            for d in range(10):
                cnt = (mask // (pow3[d])) % 3
                newTritCount = cnt + counts[d]
                if newTritCount > 2:
                    cantAddMask = True
                    break
                newMask += pow3[d] * newTritCount
            if cantAddMask:
                continue
            ndp[newMask] = fmax(ndp[newMask], dp[mask] + w)
        dp = ndp
    
    print(max(dp))




