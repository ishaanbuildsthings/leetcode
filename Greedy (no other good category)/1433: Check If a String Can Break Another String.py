# https://leetcode.com/problems/check-if-a-string-can-break-another-string/description/
# difficulty: medium
# tags: greedy

# Problem
# Given two strings: s1 and s2 with the same size, check if some permutation of string s1 can break some permutation of string s2 or vice-versa. In other words s2 can break s1 or vice-versa.

# A string x can break string y (both of size n) if x[i] >= y[i] (in alphabetical order) for all i between 0 and n-1.

# Solution, try both ways greedily, I used sorting and reallocated but you can bucket sort for O(n) sort

class Solution:
    def checkIfCanBreak(self, s1: str, s2: str) -> bool:
        # check if s1 can break s2
        s1Arr = list(s1)
        s1Arr.sort()
        s2Arr = list(s2)
        s2Arr.sort()
        reverseFound = False
        for i in range(len(s1Arr)):
            if s1Arr[i] < s2Arr[i]:
                reverseFound = True
                break
        if not reverseFound:
            return True

        # check the other way
        s1Arr.sort(reverse=True)
        s2Arr.sort(reverse=True)
        reverseFound = False
        for i in range(len(s1Arr)):
            if s2Arr[i] < s1Arr[i]:
                reverseFound = True
                break
        if not reverseFound:
            return True
