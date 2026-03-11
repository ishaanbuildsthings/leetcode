class Solution:
    def maxWidthRamp(self, nums: List[int]) -> int:

        # O(n log n) solution 1
        # for each index consider it as the right edge, find the leftmost edge with a value that is <= the right edge
        # binary search with prefix min to do this
        # could also use seg tree type of thing on values where we store the min index per value and then query a prefix min on [0, nums[i]]
        # pfMin = []
        # curr = inf
        # for v in nums:
        #     curr = min(curr, v)
        #     pfMin.append(curr)
        # res = 0
        # for right in range(len(nums)):
        #     # binary search on the leftmost bound where [0, m] has a min <= nums[right]
        #     num = nums[right]
        #     l = 0
        #     r = right
        #     resI = None
        #     while l <= r:
        #         m = (r + l) // 2
        #         minInRange = pfMin[m]
        #         if minInRange <= num:
        #             resI = m
        #             r = m - 1
        #         else:
        #             l = m + 1
        #     res = max(res, right - resI)
        # return res


        # O(n log n) solution 2
        # we sort values in increasing order, and track min prefix index so far
        # tuples = []
        # for i, v in enumerate(nums):
        #     tuples.append((v, i))
        # tuples.sort()
        # res = 0
        # minI = tuples[0][1]
        # for v, i in tuples[1:]:
        #     dist = i - minI
        #     res = max(res, dist)
        #     minI = min(minI, i)
        # return res


        # O(n) solution 3, two pointers idea
        # at a given index L if the suffix max at R is big enough there's at least some ramp there, we update result with r-l and trry going further
        # if we cannot go furthere there we have no option at this L
        # I think the idea is say we found some L R that worked and now we find some R' that breaks L and we must advance to L'
        # We're worried about some earlier R, since we cannot backtrack now, but that earlier R would have been captured by an earlier L which is strictly longer
        # not fully convinced here yet claude says I wasn't precise
        # suffMax = [None] * len(nums)
        # curr = -inf
        # for i in range(len(nums) - 1, -1, -1):
        #     curr = max(curr, nums[i])
        #     suffMax[i] = curr
        # l = r = res = 0
        # while r < len(nums):
        #     if nums[l] <= suffMax[r]:
        #         res = max(res, r - l)
        #         r += 1
        #     else:
        #         l += 1
        # return res


        # O(n) solution 4, stack
        # only some left indices are worth considering, ones that form a strictly decreasing value sequence
        # this is NOT our normal stack of like "find next smaller element", stack cannot find the "furthest right" smaller element in that sense
        stack = []
        for i, v in enumerate(nums):
            if not stack or v < nums[stack[-1]]:
                stack.append(i)
        # now for a given right index, we greedily pop as much as we can
        res = 0
        for i in range(len(nums) - 1, -1, -1):
            while stack and nums[stack[-1]] <= nums[i]:
                poppedI = stack.pop()
                width = i - poppedI
                res = max(res, width)
        return res


