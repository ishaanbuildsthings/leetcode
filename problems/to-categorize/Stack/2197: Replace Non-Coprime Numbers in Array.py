# https://leetcode.com/problems/replace-non-coprime-numbers-in-array/
# difficulty: hard
# tags: stack, math

# Problem
# You are given an array of integers nums. Perform the following steps:

# Find any two adjacent numbers in nums that are non-coprime.
# If no such numbers are found, stop the process.
# Otherwise, delete the two numbers and replace them with their LCM (Least Common Multiple).
# Repeat this process as long as you keep finding two adjacent non-coprime numbers.
# Return the final modified array. It can be shown that replacing adjacent non-coprime numbers in any arbitrary order will lead to the same result.

# The test cases are generated such that the values in the final array are less than or equal to 108.

# Two values x and y are non-coprime if GCD(x, y) > 1 where GCD(x, y) is the Greatest Common Divisor of x and y.

# Solution, O(n log max(nums)) time, O(n) space
# We can just use a stack, since it's always adjacent. I didn't even think about how thie gcd/lcm can update and pop more off the stack, but a stack clearly works because once you move past some numbers they cannot need to be popped unless we do it from the right.

class Solution:
    def replaceNonCoprimes(self, nums: List[int]) -> List[int]:
        stack = [nums[0]]
        for i in range(1, len(nums)):
            stack.append(nums[i])
            while len(stack) >= 2 and math.gcd(stack[-1], stack[-2]) > 1:
                new = math.lcm(stack[-1], stack[-2])
                stack.pop()
                stack.pop()
                stack.append(new)
        return stack
