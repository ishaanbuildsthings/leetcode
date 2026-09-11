# https://leetcode.com/problems/minimum-number-of-k-consecutive-bit-flips/description/
# difficulty: hard
# tags: greedy, sweep line

# Problem
# You are given a binary array nums and an integer k.

# A k-bit flip is choosing a subarray of length k from nums and simultaneously changing every 0 in the subarray to 1, and every 1 in the subarray to 0.

# Return the minimum number of k-bit flips required so that there is no 0 in the array. If it is not possible, return -1.

# A subarray is a contiguous part of an array.

# Solution
# A standard problem where we flip from the left as needed. To deal with the flips we can do a sweep line sort of thing, but instead of allocating a sweep line, we have a set of at most k elements that denote when we drop from the flip counter. The flip counter helps determine the parity for the current bit. We can do O(1) space by overriding numbers to a non 1 or 0 then changing them back. O(n-k) time and O(k) space.

class Solution:
    def minKBitFlips(self, nums: List[int], k: int) -> int:
        res = 0
        flips = 0
        dropFlips = set() # coordinates for when we should lose a flop
        for i in range(len(nums)):
            # drop the bit if we need it
            if i in dropFlips:
                flips -= 1
                dropFlips.remove(i)

            # determine if the bit is off based on its status and the flips
            parity = flips % 2
            bit = (nums[i] + parity) % 2

            if not bit:
                if i > len(nums) - k:
                    return -1
                res += 1
                flips += 1
                dropFlips.add(i + k)

        return res



