opts = [[] for _ in range(51)] # digit sum -> list of numbers we can take

for number in range(5001):
    tot = sum(int(x) for x in str(number))
    opts[tot].append(number)
    
class Solution:
    def countArrays(self, digitSum: list[int]) -> int:
        n = len(digitSum)
        MOD = 10**9 + 7

        dp = [0] * (5001)
        dp[0] = 1

        for i in range(n):
            ndp = [0] * 5001
            bucket = opts[digitSum[i]]
            
            pf = []
            curr = 0
            for v in dp:
                curr += v
                curr %= MOD
                pf.append(curr)

            for opt in bucket:
                beforeTot = pf[opt]
                ndp[opt] += beforeTot
                ndp[opt] %= MOD

            dp = ndp

        return sum(dp) % MOD
            
                
            

        # @cache
        # def dp(i, prevNum):
        #     if i == n:
        #         return 1
        #     resHere = 0

        #     # find the leftmost start point that is >= prevNum
        #     bucket = opts[digitSum[i]]
        #     l = 0
        #     r = len(bucket) - 1
        #     resI = None

        #     while l <= r:
        #         m = (r+l)//2
        #         if bucket[m] >= prevNum:
        #             resI = m
        #             r = m - 1
        #         else:
        #             l = m + 1

        #     if resI is not None:
        #         for j in range(resI, len(bucket)):
        #             num = bucket[j]
        #             resHere += dp(i + 1, num)
        #             resHere %= MOD
        #     return resHere

        # ans = dp(0,0)
        # dp.cache_clear()
        # return ans
            

        