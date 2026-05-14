# https://leetcode.com/problems/max-number-of-k-sum-pairs/
# difficulty: medium

# problem
# You are given an integer array nums and an integer k.

# In one operation, you can pick two numbers from the array whose sum equals k and remove them from the array.

# Return the maximum number of operations you can perform on the array.

# Solution, O(n) time and space
# I just counted everything, added complements (unnecessarily doubles work, we could use a seen set too but that also adds work anyway), and handled the edge case if a number plus itself is the target

class Solution:
    def maxOperations(self, nums: List[int], k: int) -> int:
        counts = collections.Counter(nums)
        res = 0
        for num in counts.keys():
            # edge case
            if num * 2 == k:
                continue
            complement = k - num
            if not complement in counts:
                continue

            res += min(counts[num], counts[complement])

        res = int(res / 2)
        if (k / 2) in counts:
            res += math.floor(counts[int(k / 2)] / 2)

        return res