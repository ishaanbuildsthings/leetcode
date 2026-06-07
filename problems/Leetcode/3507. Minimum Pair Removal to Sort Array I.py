class Solution:
    def minimumPairRemoval(self, nums: List[int]) -> int:
        res = 0
        curr = nums
        while True:
            if all(curr[i] <= curr[i + 1] for i in range(len(curr) - 1)):
                return res
            minSum = min(curr[i] + curr[i + 1] for i in range(len(curr) - 1))
            for i in range(len(curr) - 1):
                if curr[i] + curr[i + 1] == minSum:
                    resI = i
                    break
            curr[i] += curr[i + 1]
            curr.pop(i + 1)
            res += 1