# https://leetcode.com/problems/number-of-steps-to-reduce-a-number-in-binary-representation-to-one/
# difficulty: medium
# tags: simulation

# Problem
# Given the binary representation of an integer as a string s, return the number of steps to reduce it to 1 under the following rules:

# If the current number is even, you have to divide it by 2.

# If the current number is odd, you have to add 1 to it.

# It is guaranteed that you can always reach one for all test cases.

# Solution, I just simulated it. There's faster since I used a prepend which isn't needed.

class Solution:
    def numSteps(self, s: str) -> int:
        arr = list(s)

        def add():
            i = len(arr) - 1
            while i >= 0 and arr[i] == '1':
                arr[i] = '0'
                i -= 1
            if i >= 0:
                arr[i] = '1'
            else:
                arr.insert(0, '1')



        def divide():
            arr.pop()

        res = 0

        while len(arr) > 1:
            if arr[-1] == '0':
                divide()
            else:
                add()
            res += 1

        return res
