# https://leetcode.com/problems/construct-smallest-number-from-di-string/
# difficulty: medium
# tags: backtracking

# problem
# You are given a 0-indexed string pattern of length n consisting of the characters 'I' meaning increasing and 'D' meaning decreasing.

# A 0-indexed string num of length n + 1 is created using the following conditions:

# num consists of the digits '1' to '9', where each digit is used at most once.
# If pattern[i] == 'I', then num[i] < num[i + 1].
# If pattern[i] == 'D', then num[i] > num[i + 1].
# Return the lexicographically smallest possible string num that meets the conditions.

# Solution
# We can track which numbers we have used and the current direction and enumerate all paths. The stack depth is O(n) and each depth contains O(n) chars, so n^2 space, not sure about time since upper bound is a bit tricky.

class Solution:
    def smallestNumber(self, pattern: str) -> str:
        used = set()
        res = '999999999'
        def backtrack(i, accLetters):
            # base case
            if i == len(pattern):
                res = min(res, accLetters)
                return

            if accLetters == '':
                low = 1
                high = 9
            else:
                lastMove
                lastNum = int(accLetters[-1])
                if lastNum

            lastNum = int(accLetters[-1])

