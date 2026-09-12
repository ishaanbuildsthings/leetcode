# https://leetcode.com/problems/minimum-adjacent-swaps-to-make-a-valid-array/description/
# difficulty: medium

# Solution, O(n) time O(1) space

class Solution:
    def minimumSwaps(self, nums: List[int]) -> int:
        biggest = max(nums)
        smallest = min(nums)

        if len(nums) == 1:
            return 0


        res = 0

        for i in range(len(nums) - 1, -1, -1):
            if nums[i] == biggest:
                biggestPos = i
                biggestToRight = len(nums) - (i + 1)
                res += biggestToRight
                break


        for i in range(len(nums)):
            if nums[i] == smallest:
                res += i
                if biggestPos < i:
                    res -= 1
                return res




