class Solution:
    def minPatches(self, nums: List[int], n: int) -> int:
        formable = 0 # we can form from 0...formable
        res = 0
        for v in nums:
            if formable >= n:
                return res
            if v == formable + 1:
                formable += v
                continue
            while formable < v - 1:
                res += 1
                adding = formable + 1
                formable += formable + 1
                if formable >= n:
                    return res
            formable += v
        while formable < n:
            formable += formable + 1
            res += 1
        return res
            