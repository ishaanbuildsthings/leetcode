# https://leetcode.com/problems/numbers-with-same-consecutive-differences/description/
# difficulty: medium
# tags: backtracking

# Problem
# Given two integers n and k, return an array of all the integers of length n where the difference between every two consecutive digits is k. You may return the answer in any order.

# Note that the integers should not have leading zeros. Integers as 02 and 043 are not allowed.

# Solution, backtracking across digits, branching factor is 2 and depth is n. When we get a result we serialize in O(1), could be faster by using hashing. O(n * 2^n) time, O(n) space

class Solution:
    def numsSameConsecDiff(self, n: int, k: int) -> List[int]:
        res = []
        def backtrack(accumulated):
            # base case
            if len(accumulated) == n:
                res.append(int(''.join(accumulated)))
                return

            prevDigit = int(accumulated[-1]) if accumulated else None

            if prevDigit != None:
                higher = prevDigit + k
                lower = prevDigit - k
                if higher <= 9:
                    accumulated.append(str(higher))
                    backtrack(accumulated)
                    accumulated.pop()
                if lower >= 0 and lower != higher:
                    accumulated.append(str(lower))
                    backtrack(accumulated)
                    accumulated.pop()
            else:
                for firstNum in range(1, 10):
                    accumulated.append(str(firstNum))
                    backtrack(accumulated)
                    accumulated.pop()

        backtrack([])
        return res

