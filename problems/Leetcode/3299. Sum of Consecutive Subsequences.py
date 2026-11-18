class Solution:
    def getSum(self, nums: List[int]) -> int:
        MOD = 10**9 + 7

        MX = max(nums)

        sumUp = [0] * (MX + 2)
        cntUp = [0] * (MX + 2)
        sumDown = [0] * (MX + 2)
        cntDown = [0] * (MX + 2)
        res = 0

        def madd(a, b):
            return (a + b) % MOD

        for i, v in enumerate(nums):
            prevUp = cntUp[v - 1]
            newSequences = (prevUp + 1) % MOD

            sumUp[v] = madd(sumUp[v], v * newSequences)
            sumUp[v] = madd(sumUp[v], sumUp[v - 1])
            cntUp[v] = madd(cntUp[v], cntUp[v - 1] + 1)

            prevDown = cntDown[v + 1]
            newSequences = (prevDown + 1) % MOD

            sumDown[v] = madd(sumDown[v], v * newSequences)
            sumDown[v] = madd(sumDown[v], sumDown[v + 1])
            cntDown[v] = madd(cntDown[v], cntDown[v + 1] + 1)
        
        return (sum(sumUp) + sum(sumDown) - sum(nums)) % MOD