class Solution:
    def maxFrequencyScore(self, nums: List[int], k: int) -> int:
        MOD = 10**9 + 7

        @cache
        def modPow(base, exponent, mod=MOD):
            if exponent == 0:
                return 1
            if exponent == 1:
                return base % mod
            half = modPow(base, exponent // 2, mod)
            if exponent % 2 == 0:
                return (half * half) % mod
            else:
                return (half * half * base) % mod

        # build initial window
        frq = Counter(nums[:k])

        curr = 0
        for num in frq:
            curr += num**frq[num]
        curr %= MOD
        
        res = curr

        l = 0
        r = k - 1
        while r < len(nums) - 1:
            r += 1
            gainedNum = nums[r]
            if gainedNum == nums[l]:
                l += 1
                continue

            # RIGHT SIDE
            # assume we are going 4^3 -> 4^4 with the new num

            # we drop a 4^3 contribution, and gain a 4^4 contribution
            oldGainedFrq = frq[gainedNum]
            frq[gainedNum] += 1

            oldLoss = modPow(gainedNum, oldGainedFrq) if oldGainedFrq else 0

            curr -= oldLoss

            newGain = modPow(gainedNum, frq[gainedNum])
            curr += newGain

            curr %= MOD

            # LEFT SIDE
            lostNum = nums[l]
            # 2^3 -> 2^2, so we need to lose 2^3 contribution

            oldLostFrq = frq[lostNum]

            oldLoss = modPow(lostNum, oldLostFrq)

            frq[lostNum] -= 1
            curr -= oldLoss

            newLostFrq = oldLostFrq - 1
            oldGain = modPow(lostNum, newLostFrq) if newLostFrq else 0

            curr += oldGain

            curr %= MOD

            res = max(res, curr)

            l += 1
        
        return res