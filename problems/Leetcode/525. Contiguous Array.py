class Solution:
    def findMaxLength(self, nums: List[int]) -> int:
        nums = [num if num == 1 else -1 for num in nums]
        surplusToLeftmost = {}
        currSurplus = 0
        res = 0
        for i in range(len(nums)):
            currSurplus += nums[i]
            if not currSurplus in surplusToLeftmost:
                surplusToLeftmost[currSurplus] = i
            if not currSurplus:
                res = max(res, i + 1)
            amountToCutOff = currSurplus
            if amountToCutOff in surplusToLeftmost:
                leftmost = surplusToLeftmost[amountToCutOff]
                newWidth = i - leftmost
                res = max(res, newWidth)
        return res
        