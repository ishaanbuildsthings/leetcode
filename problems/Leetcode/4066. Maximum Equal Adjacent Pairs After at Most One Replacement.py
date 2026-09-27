class Solution:
    def maxEqualAdjacentPairs(self, nums: list[int]) -> int:

        changes = Counter() # maps (from, to) -> frq
        pairs = 0

        n = len(nums)
        for i in range(n - 1):
            left = nums[i]
            right = nums[i + 1]
            if left == right:
                pairs += 1
                continue
            changes[min(left, right), max(left, right)] += 1

        
        ans = pairs
        if changes:
            ans += max(changes.values())

        return ans
            