class Solution:
    def repeatedNTimes(self, nums: List[int]) -> int:
        dominant = None
        surplus = 1
        for i in range(len(nums)):
            prevDominant = dominant
            num = nums[i]
            if num == dominant:
                surplus += 1
            else:
                surplus -= 1
            if surplus == 0:
                dominant = num
                surplus = 1

        seenPrevDominant = False
        for num in nums:
            if num == prevDominant:
                if seenPrevDominant:
                    return prevDominant
                else:
                    seenPrevDominant = True
        return dominant
        