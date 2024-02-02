# https://leetcode.com/problems/sequential-digits/submissions/1163442197/?envType=daily-question&envId=2024-02-02
# difficulty: medium
# tags: recursion

# Problem
# An integer has sequential digits if and only if each digit in the number is one more than the previous digit.

# Return a sorted list of all the integers in the range [low, high] inclusive that have sequential digits.

# Solution
# I just did recursion. We can use numbers instead of an array and probably find better pruning and whatnot.

class Solution:
    def sequentialDigits(self, low: int, high: int) -> List[int]:
        res = []
        def backtrack(curr):
            num = int(''.join(curr))
            if num >= low and num <= high:
                res.append(num)

            if len(curr) == len(str(high)):
                return

            if curr[-1] == '9':
                return

            curr.append(str(int(curr[-1]) + 1))

            backtrack(curr)

        for startDigit in range(1, 10):
            backtrack([str(startDigit)])

        return sorted(res)



