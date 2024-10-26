# https://leetcode.com/problems/maximum-product-of-the-length-of-two-palindromic-subsequences/
# difficulty: medium
# tags: dynamic programming 1d, backtracking

# Problem
# Given a string s, find two disjoint palindromic subsequences of s such that the product of their lengths is maximized. The two subsequences are disjoint if they do not both pick a character at the same index.

# Return the maximum possible product of the lengths of the two palindromic subsequences.

# A subsequence is a string that can be derived from another string by deleting some or no characters without changing the order of the remaining characters. A string is palindromic if it reads the same forward and backward.

# Solution
# This is a cursed problem. I tried the n*3^n backtracking solution which passed all test cases but got a custom error that it still took too long, despite other n*3^n solutions being accepted. That is just to try all comboes of two subsequences and run an O(n) isPal on them. Then I restored to a bitmask where we cache the palindromic-ness of a mask. The TC is worse due to writing bits but faster in clock cylces.



class Solution:
    def maxProduct(self, s: str) -> int:

        @cache
        def countBits(mask):
            # print(f'count bits called on mask {mask}')
            bits = 0
            for bit in range (len(s)):
                if mask >> bit & 1:
                    bits += 1
            # print(f'ret {bits}')
            return bits

        @cache
        def isPal(mask):
            # print(f'is pal called on mask {mask}')
            letters = []
            for bit in range(len(s)):
                if mask >> bit & 1:
                    letters.append(s[bit])
            # print(f'letters are {letters}')
            for i in range(math.floor(len(letters) / 2)):
                if letters[i] != letters[len(letters) - i - 1]:
                    # print(f'ret false')
                    return False
            # print(f'ret true')
            return True

        res = 0


        def backtrack(i, maskOne, maskTwo):
            nonlocal res
            # base case
            if i == len(s):
                if isPal(maskOne) and isPal(maskTwo):
                    res = max(res, countBits(maskOne) * countBits(maskTwo))
                return

            # if we skip
            backtrack(i + 1, maskOne, maskTwo)

            # if we take in the first sequence
            maskOneTake = maskOne | 1 << (len(s) - i - 1)
            backtrack(i + 1, maskOneTake, maskTwo)

            # if we take in the second
            maskTwoTake = maskTwo | 1 << (len(s) - i - 1)
            backtrack(i + 1, maskOne, maskTwoTake)

        backtrack(0, 0, 0)

        return res




#### The backtracking solution that TLE'd


        # def isPal(arr):
        #     # print(f'arr is {arr}')
        #     for i in range(math.floor(len(arr) / 2)):
        #         # print(f'i is {i}')
        #         # print(f'left: {i}, right: {len(arr) - i}')
        #         if arr[i] != arr[len(arr) - i - 1]:
        #             return False
        #     return True

        # res = 0
        # currOne = []
        # currTwo = []
        # def backtrack(i):
        #     nonlocal res
        #     nonlocal currOne
        #     nonlocal currTwo
        #     # base case
        #     if i == len(s):
        #         if isPal(currOne) and isPal(currTwo):
        #             res = max(res, len(currOne) * len(currTwo))
        #         return

        #     # if we skip this letter
        #     backtrack(i + 1)

        #     # if we add to currOne
        #     currOne.append(s[i])
        #     backtrack(i + 1)
        #     currOne.pop()

        #     # if we add to currTwo
        #     currTwo.append(s[i])
        #     backtrack(i + 1)
        #     currTwo.pop()

        # backtrack(0)
        # return res