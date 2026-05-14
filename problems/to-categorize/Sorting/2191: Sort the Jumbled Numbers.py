# https://leetcode.com/problems/sort-the-jumbled-numbers/description/
# difficulty: medium
# tags: sorting

# Problem
# You are given a 0-indexed integer array mapping which represents the mapping rule of a shuffled decimal system. mapping[i] = j means digit i should be mapped to digit j in this system.

# The mapped value of an integer is the new integer obtained by replacing each occurrence of digit i in the integer with mapping[i] for all 0 <= i <= 9.

# You are also given another integer array nums. Return the array nums sorted in non-decreasing order based on the mapped values of its elements.

# Notes:

# Elements with the same mapped values should appear in the same relative order as in the input.
# The elements of nums should only be sorted based on their mapped values and not be replaced by them.

# Solution, for each number, spend log n or constant time remapping it, zip everything, and sort.

class Solution:
    def sortJumbled(self, mapping: List[int], nums: List[int]) -> List[int]:
        mappingDict = {i : mapping[i] for i in range(len(mapping))}

        def getMapped(num):
            if num == 0:
                return mappingDict[0]

            mapped = 0
            power = 0

            while num:
                lastDigit = num % 10
                mappedDigit = mappingDict[lastDigit]
                mapped += (mappedDigit * 10**power)
                power += 1
                num //= 10
            return mapped

        mappedNums = [getMapped(num) for num in nums]

        zipped = [[mappedNums[i], nums[i]] for i in range(len(nums))]

        zipped.sort(key=lambda x: x[0])

        return [tup[1] for tup in zipped]