class Solution:
    def sortArrayByParityII(self, nums: List[int]) -> List[int]:
        evens = [v for v in nums if v % 2 == 0 ]
        odds = [v for v in nums if v % 2]
        res = []
        for i in range(len(nums)):
            if i % 2:
                res.append(odds.pop())
            else:
                res.append(evens.pop())
        return res
