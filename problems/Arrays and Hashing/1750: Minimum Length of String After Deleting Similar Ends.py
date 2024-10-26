# https://leetcode.com/problems/minimum-length-of-string-after-deleting-similar-ends/description/?envType=daily-question&envId=2024-03-05
# difficulty: medium

# Solution
class Solution:
    def minimumLength(self, s: str) -> int:
        l = 0
        r = len(s) - 1
        while True:
            if r == l:
                return 1
            if l > r:
                return 0

            charLeft = s[l]
            charRight = s[r]
            if charLeft != charRight:
                return r - l + 1

            while s[l] == charLeft and l <= r and l < len(s) - 1:
                l += 1
            while s[r] == charLeft and l <= r and r > 0:
                r -= 1

        return 0
