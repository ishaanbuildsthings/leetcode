# https://leetcode.com/problems/beautiful-arrangement/description/
# difficulty: medium
# tags: backtracking

# Problem
# Suppose you have n integers labeled 1 through n. A permutation of those n integers perm (1-indexed) is considered a beautiful arrangement if for every i (1 <= i <= n), either of the following is true:

# perm[i] is divisible by i.
# i is divisible by perm[i].
# Given an integer n, return the number of the beautiful arrangements that you can construct.

# Solution, O(n * n!) -> n! time, and O(n) space
# Just backtrack all possibilities


class Solution:
    def countArrangement(self, n: int) -> int:
        res = 0
        # track nums remaining also so we can instantly access which ones remain
        def backtrack(currentNums, numsRemaining):
            nonlocal res
            # base case
            if len(currentNums) == n:
                res += 1
                return

            insertionIndex = len(currentNums) + 1
            for num in list(numsRemaining): # don't mutate the set while iterating over it
                if num % insertionIndex == 0 or insertionIndex % num == 0:
                    currentNums.add(num)
                    numsRemaining.remove(num)

                    backtrack(currentNums, numsRemaining)

                    currentNums.remove(num)
                    numsRemaining.add(num)

        initNumsRemaining = set()

        for num in range(1, n + 1):
            initNumsRemaining.add(num)

        backtrack(set(), initNumsRemaining)
        return res