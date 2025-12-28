import functools

while True:
    L, R = map(int, input().split())
    if L == R == -1:
        exit()

    def boundSum(num):
        strNum = str(num)
        @functools.lru_cache(maxsize=None)
        def dp(i, tight):
            if i == len(strNum):
                return (0, 1) # returns (sum of all numbers in this config, how many numbers are in this config)
            ub = 9 if not tight else int(strNum[i])
            resSum = 0
            resCount = 0
            for d in range(ub + 1):
                nt = tight and d == ub
                dpSum, dpCount = dp(i + 1, nt)
                gained = dpSum + d * dpCount
                resSum += gained
                resCount += dpCount
            return resSum, resCount
        ansSum, ansCount = dp(0, True)
        return ansSum



    print(boundSum(R) - boundSum(L - 1) if L else 0)