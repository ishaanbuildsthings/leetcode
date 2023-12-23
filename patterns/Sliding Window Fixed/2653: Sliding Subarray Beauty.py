# https://leetcode.com/problems/sliding-subarray-beauty/
# difficulty: hard
# tags: prefix

# problem
# Given an integer array nums containing n integers, find the beauty of each subarray of size k.

# The beauty of a subarray is the xth smallest integer in the subarray if it is negative, or 0 if there are fewer than x negative integers.

# Return an integer array containing n - k + 1 integers, which denote the beauty of the subarrays in order from the first index in the array.

# A subarray is a contiguous non-empty sequence of elements within an array.

# solution
# We can, for each fixed window, maintain a counter of the number of elements that occur, since nums[i] is heavily bounded, so we get nums[i]*n time and O([nums[i]]) space. I think we could even use an AVL for the counters to get log(nums[i]) instead.

class Solution:
    def getSubarrayBeauty(self, nums: List[int], k: int, x: int) -> List[int]:
        counts = defaultdict(int) # maps negative numbers to how many times they have occured in our current window
        for i in range(k):
            if nums[i] < 0:
                counts[nums[i]] += 1

        def getXthSmallest():
            seen = 0
            for num in range(-50, 0):
                seen += counts[num]
                if seen >= x:
                    return num
            return 0

        res = [getXthSmallest()]

        r = k - 1
        while r < len(nums) - 1:
            r += 1
            gainedNum = nums[r]
            lostNum = nums[r - k]
            counts[gainedNum] += 1
            counts[lostNum] -= 1
            res.append(getXthSmallest())

        return res