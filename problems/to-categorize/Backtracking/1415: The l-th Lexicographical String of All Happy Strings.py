# https://leetcode.com/problems/the-k-th-lexicographical-string-of-all-happy-strings-of-length-n/
# difficulty: medium
# tags: backtracking

# Problem
# A happy string is a string that:

# consists only of letters of the set ['a', 'b', 'c'].
# s[i] != s[i + 1] for all values of i from 1 to s.length - 1 (string is 1-indexed).
# For example, strings "abc", "ac", "b" and "abcbabcbcb" are all happy strings and strings "aa", "baa" and "ababbc" are not happy strings.

# Given two integers n and k, consider a list of all happy strings of length n sorted in lexicographical order.

# Return the kth string of this list or return an empty string if there are less than k happy strings of length n.

# Solution, 3^n log (3^n) + n^2 time, sort(3^n log 3^n) + n^2 space + 3^n
# We track accumulated letters, store all possibilities, sort, then check. Our stack depth is at most n, each one takes n time and space for string handling. We get at most 3^n states which are sorted.

class Solution:
    def getHappyString(self, n: int, k: int) -> str:
        strings = []
        def backtrack(i, accLetters):
            # base case
            if i == n:
                strings.append(accLetters)
                return

            for char in 'abc':
                if accLetters != '' and accLetters[-1] == char:
                    continue
                backtrack(i + 1, accLetters + char)
        backtrack(0, '')
        if len(strings) < k:
            return ''
        strings.sort()
        return strings[k-1]