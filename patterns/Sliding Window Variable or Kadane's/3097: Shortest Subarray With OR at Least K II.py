# https://leetcode.com/problems/shortest-subarray-with-or-at-least-k-ii/description/
# difficulty: medium
# tags: sliding window variable

# Solution, O(n log max(nums)) time O(log max(nums)) space

class Solution:
    def minimumSubarrayLength(self, nums: List[int], k: int) -> int:

        currCounts = {
            i : 0 for i in range(32)
        }

        def isAtLeastK():
            orResult = 0
            for i in range(32):
                if currCounts[i]:
                    orResult |= 1 << i
            return orResult >= k

        l = r = 0


        res = float('inf')

        while r < len(nums):
            num = nums[r]

            for bitOffset in range(32):
                if num >> bitOffset & 1:
                    currCounts[bitOffset] += 1

            while isAtLeastK() and l <= r:
                res = min(res, r - l + 1)
                # drop the left number
                for bitOffset in range(32):
                    if nums[l] >> bitOffset & 1:
                        currCounts[bitOffset] -= 1
                l += 1

            r += 1

        return res if res != float('inf') else -1