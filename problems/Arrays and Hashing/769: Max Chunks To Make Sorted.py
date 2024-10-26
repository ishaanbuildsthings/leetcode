# https://leetcode.com/problems/max-chunks-to-make-sorted/description/
# difficulty: medium

# Solution, O(n) time O(1) space, could probably simplify a bit

class Solution:
    def maxChunksToSorted(self, arr: List[int]) -> int:
        prevHigh = -1
        minSeen = float('inf')
        maxSeen = float('-inf')
        countSeen = 0
        res = 0
        for i, val in enumerate(arr):
            minSeen = min(minSeen, val)
            maxSeen = max(maxSeen, val)
            countSeen += 1
            if maxSeen - minSeen + 1 == countSeen and minSeen == prevHigh + 1:
                res += 1
                prevHigh = maxSeen
                minSeen = float('inf')
                maxSeen = float('-inf')
                countSeen = 0
        return res

