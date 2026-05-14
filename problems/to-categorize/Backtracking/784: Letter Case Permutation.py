# https://leetcode.com/problems/letter-case-permutation/
# difficulty: medium
# tags: backtracking

# Problem
# Given a string s, you can transform every letter individually to be lowercase or uppercase to create another string.

# Return a list of all possible strings we could create. Return the output in any order.

# Solution, O(n*2^n) time, O(n^2) space for stack depth + stored string
# For each character, we try the options. Worst case is 2^n possibile states and each state takes n time to string copy.

class Solution:
    def letterCasePermutation(self, s: str) -> List[str]:
        res = []
        def backtrack(i, accLetters):
            # base case
            if i == len(s):
                res.append(accLetters)
                return
            if s[i].isdigit():
                backtrack(i + 1, accLetters + s[i])
            else:
                backtrack(i + 1, accLetters + s[i].upper())
                backtrack(i + 1, accLetters + s[i].lower())
        backtrack(0, '')
        return res