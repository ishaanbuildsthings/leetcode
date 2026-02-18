class Solution:
    def createTargetArray(self, nums: List[int], index: List[int]) -> List[int]:
        res = []
        for i in range(len(nums)):
            pos = index[i]
            v = nums[i]
            res.insert(pos, v)
        return res