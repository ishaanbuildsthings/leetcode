# https://leetcode.com/problems/find-the-prefix-common-array-of-two-arrays/
# Difficulty: Medium
# Tags: prefix

# Problem
# You are given two 0-indexed integer permutations A and B of length n.

# A prefix common array of A and B is an array C such that C[i] is equal to the count of numbers that are present at or before the index i in both A and B.

# Return the prefix common array of A and B.

# A sequence of n integers is called a permutation if it contains all integers from 1 to n exactly once.

# Solution, O(n) time and space
# Iterate, tracking numbers in both a and b before, and updating the result.

class Solution:
    def findThePrefixCommonArray(self, A: List[int], B: List[int]) -> List[int]:
        aSet = set()
        bSet = set()
        matched = 0
        res = []
        for i in range(len(A)):
            aNum = A[i]
            bNum = B[i]
            # if our aNum completes a pair
            if not aNum in aSet and aNum in bSet:
                matched += 1
            # if our bNum completes a pair
            if not bNum in bSet and bNum in aSet:
                matched += 1
            # if the two nums complete a set
            if aNum == bNum and not aNum in aSet and not bNum in bSet:
                matched +=1
            aSet.add(aNum)
            bSet.add(bNum)
            res.append(matched)
        return res
