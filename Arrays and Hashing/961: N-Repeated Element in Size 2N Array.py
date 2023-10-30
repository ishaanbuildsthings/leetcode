# https://leetcode.com/problems/n-repeated-element-in-size-2n-array/
# difficulty: easy
# tags: boyer-moore

# Problem
# You are given an integer array nums with the following properties:

# nums.length == 2 * n.
# nums contains n + 1 unique elements.
# Exactly one element of nums is repeated n times.
# Return the element that is repeated n times.

# Solution, O(n) time and O(1) space. I found a clever use of boyer-moore, the n/2 element must be one of the last two, and we can just verify which of the two it is.

class Solution:
    def repeatedNTimes(self, nums: List[int]) -> int:
        dominant = None
        surplus = 1
        for i in range(len(nums)):
            prevDominant = dominant
            num = nums[i]
            if num == dominant:
                surplus += 1
            else:
                surplus -= 1
            if surplus == 0:
                dominant = num
                surplus = 1

        seenPrevDominant = False
        for num in nums:
            if num == prevDominant:
                if seenPrevDominant:
                    return prevDominant
                else:
                    seenPrevDominant = True
        return dominant
