class Solution:
    def maximumMEX(self, nums: List[int]) -> List[int]:
        n = len(nums)
        suffMex = [None] * n
        missing = SortedList([num for num in range(n + 10)])

        for i in range(n - 1, -1, -1):
            missing.discard(nums[i])
            suffMex[i] = missing[0]

        res = []
        i = 0
        while i < n:
            res.append(suffMex[i])
            seen = set()
            for j in range(i, n):
                if nums[j] < mex:
                    seen.add(num)
                if len(seen) == mex:
                    break
            i = j + 1

        return res
                
            