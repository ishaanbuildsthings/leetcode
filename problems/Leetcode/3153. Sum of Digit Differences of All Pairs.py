class Solution:
    def sumDigitDifferences(self, nums: List[int]) -> int:
        c = defaultdict(lambda:defaultdict(int)) # maps [i][digit] to a count

        res = 0
        for j, num in enumerate(nums):
            for i, d in enumerate(str(num)):
                cnt = c[i][d]
                otherCnt = j - cnt
                res += otherCnt
            for i, d in enumerate(str(num)):
                c[i][d] += 1
        return res


