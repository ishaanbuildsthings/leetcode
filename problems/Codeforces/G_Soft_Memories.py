
DEBUG = False
debug = print if DEBUG else lambda *args, **kwargs: None

t = int(input())
def solve():
    # debug('-----')
    m, k = map(int, input().split())
    A = list(map(int, input().split()))
    SHIFT = 10**9 + 1
    A = [A[i] + SHIFT for i in range(m)]
    A.sort()
    debug(A)
    res = 0
    sizes = []
    sz = 2
    while sz <= m:
        sizes.append(sz)
        sz *= 2
    
    for sz in sizes:
        half = sz // 2
        worstHalf = A[:half]
        bestHalf = A[-half:]

        # debug(f'{worstHalf=} {bestHalf=}')

        score = 0
        for v in worstHalf:
            score -= v
        
        battles = sz - 1

        currHalf = half // 2
        j = 0
        wins = 1
        while currHalf:
            for i in range(j, j + currHalf):
                scoreHere = bestHalf[i]
                score += (wins * scoreHere)
                score -= scoreHere
            j += currHalf
            currHalf //= 2
            wins += 1
        score += bestHalf[-1] * wins
        score -= battles * k

        res = max(res, score)
    
    print(res)


        
for _ in range(t):
    solve()