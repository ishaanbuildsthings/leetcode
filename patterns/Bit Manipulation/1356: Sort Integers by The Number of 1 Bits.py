# https://leetcode.com/problems/sort-integers-by-the-number-of-1-bits/description/?envType=daily-question&envId=2023-10-30
# difficulty: easy
# tags: sorting, bit manipulation, bucket sort

# Problem
# You are given an integer array arr. Sort the integers in the array in ascending order by the number of 1's in their binary representation and in case of two or more integers have the same number of 1's you have to sort them in ascending order.

# Return the array after sorting it.

# Solution, make a custom sorting function. We can count bits and use bucket sort too.

MAX_BITS = math.ceil(math.log2(10**4))

class Solution:
    def sortByBits(self, arr: List[int]) -> List[int]:
        def countBits(num):
            totalOnes = 0
            for offset in range(MAX_BITS):
                totalOnes += ((num >> offset) & 1)
            return totalOnes

        return sorted(arr, key=lambda x: (countBits(x), x))
