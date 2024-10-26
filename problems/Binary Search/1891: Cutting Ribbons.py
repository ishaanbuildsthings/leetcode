# https://leetcode.com/problems/cutting-ribbons/description/
# difficulty: medium
# tags: binary search

# Solutionm O(n * log(max)) time, O(1) space

class Solution:
    def maxLength(self, ribbons: List[int], k: int) -> int:

        def isLengthDoable(length):
            count = 0
            for ribbon in ribbons:
                count += ribbon // length
                if count >= k:
                    return True
            return False

        l = 1
        r = max(ribbons)
        while l <= r:
            m = (r + l) // 2
            if isLengthDoable(m):
                l = m + 1
            else:
                r = m - 1
        return l - 1
