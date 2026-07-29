class Solution:
    def maxNumberOfApples(self, weight: List[int]) -> int:
        weight.sort() # can use bucket sort
        curr = 0
        res = 0
        for w in weight:
            if curr + w <= 5000:
                res += 1
                curr += w
            else:
                return res
        return res