# https://leetcode.com/problems/get-maximum-in-generated-array/
# difficulty: easy

# Problem
# You are given an integer n. A 0-indexed integer array nums of length n + 1 is generated in the following way:

# nums[0] = 0
# nums[1] = 1
# nums[2 * i] = nums[i] when 2 <= 2 * i <= n
# nums[2 * i + 1] = nums[i] + nums[i + 1] when 2 <= 2 * i + 1 <= n
# Return the maximum integer in the array nums​​​.

# Solution, O(n) time and space, didn't try to think of a closed form solution

class Solution:
    def getMaximumGenerated(self, n: int) -> int:
        arrLength = n + 1
        if arrLength == 1:
            return 0
        elif arrLength == 2:
            return 1

        res = 0
        arr = [0, 1]

        for i in range(2, n + 1):
            if i % 2 == 0:
                newVal = arr[int(i / 2)]
                arr.append(newVal)
                res = max(res, newVal)
            else:
                firstIndex = int((i - 1) / 2)
                newVal = arr[firstIndex] + arr[firstIndex + 1]
                arr.append(newVal)
                res = max(res, newVal)
        return res
