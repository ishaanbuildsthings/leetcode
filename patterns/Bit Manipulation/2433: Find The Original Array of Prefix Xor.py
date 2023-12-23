# https://leetcode.com/problems/find-the-original-array-of-prefix-xor/description/
# difficulty: medium
# tags: bit manipulation

# Problem
# You are given an integer array pref of size n. Find and return the array arr of size n that satisfies:

# pref[i] = arr[0] ^ arr[1] ^ ... ^ arr[i].
# Note that ^ denotes the bitwise-xor operation.

# It can be proven that the answer is unique.

# Solution, O(n) time and O(1) space, we use prefic properties like a ^ b = c means a = b ^ c to solve this.

class Solution:
    def findArray(self, pref: List[int]) -> List[int]:
        runningXor = 0
        res = []
        for i in range(len(pref)):
            newNum = runningXor ^ pref[i]
            res.append(newNum)
            runningXor = runningXor ^ res[-1]

        return res