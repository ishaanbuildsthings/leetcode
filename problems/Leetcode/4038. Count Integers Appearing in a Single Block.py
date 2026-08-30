class Solution:
    def countSpecialIntegers(self, nums: list[int]) -> int:
        lefts = {}
        rights = {}
        cnt = Counter(nums)
        for i, v in enumerate(nums):
            if v not in lefts:
                lefts[v] = i
            rights[v] = i

        res = 0
        for k, frq in cnt.items():
            width = rights[k] - lefts[k] + 1
            if width == frq:
                res += 1

        return res