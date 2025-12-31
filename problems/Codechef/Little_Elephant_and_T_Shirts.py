import functools
MOD = 10**9 + 7
T = int(input())

for _ in range(T):
    n = int(input())
    peopleToShirts = [None] * n
    for i in range(n):
        peopleToShirts[i] = set(list(map(int, input().split())))
    fmask = (1 << n) - 1
    @functools.lru_cache(maxsize=None)
    def dp(shirtI, mask):
        if shirtI == 101:
            return 1 if mask == fmask else 0
        resHere = dp(shirtI + 1, mask) # no one takes this shirt
        for person in range(n):
            if shirtI in peopleToShirts[person] and not (mask & (1 << person)):
                nmask = mask | (1 << person)
                resHere += dp(shirtI + 1, nmask)
                resHere %= MOD
        return resHere
    print(dp(1, 0))
        
        
