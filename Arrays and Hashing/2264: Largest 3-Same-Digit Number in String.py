# https://leetcode.com/problems/largest-3-same-digit-number-in-string/description/
# difficulty: Easy
# tags: rolling hash

# Problem
# You are given a string num representing a large integer. An integer is good if it meets the following conditions:

# It is a substring of num with length 3.
# It consists of only one unique digit.
# Return the maximum good integer as a string or an empty string "" if no such integer exists.

# Note:

# A substring is a contiguous sequence of characters within a string.
# There may be leading zeroes in num or a good integer.

# Solution, O(n) time and O(1) space, just having fun

class Solution:
    def largestGoodInteger(self, num: str) -> str:
        maxHash = float('-inf')
        acceptableHashes = set([0, 111, 222, 333, 444, 555, 666, 777, 888, 999])
        currHash = int(num[0:3])
        if currHash in acceptableHashes:
            maxHash = max(maxHash, currHash)

        for start in range(1, len(num) - 2):
            gainedDigit = int(num[start + 2])
            currHash = currHash % 100 # drop first digit
            currHash *= 10 # shift left
            currHash += gainedDigit
            if currHash in acceptableHashes:
                maxHash = max(maxHash, currHash)

        if maxHash == 0:
            return '000'
        if maxHash == float('-inf'):
            return ''
        return str(maxHash)
