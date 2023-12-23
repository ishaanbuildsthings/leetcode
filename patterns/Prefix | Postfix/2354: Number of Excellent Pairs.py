# https://leetcode.com/problems/number-of-excellent-pairs/
# Difficulty: Hard
# Tags: Prefix / postfix, bit manipulation

# Problem
# You are given a 0-indexed positive integer array nums and a positive integer k.

# A pair of numbers (num1, num2) is called excellent if the following conditions are satisfied:

# Both the numbers num1 and num2 exist in the array nums.
# The sum of the number of set bits in num1 OR num2 and num1 AND num2 is greater than or equal to k, where OR is the bitwise OR operation and AND is the bitwise AND operation.
# Return the number of distinct excellent pairs.

# Two pairs (a, b) and (c, d) are considered distinct if either a != c or b != d. For example, (1, 2) and (2, 1) are distinct.

# Note that a pair (num1, num2) such that num1 == num2 can also be excellent if you have at least one occurrence of num1 in the array.

# Solution, O(n) time and space
# First, observe duplicate values do nothing for us, so remove them. Then, notice bits in n1 OR n2  and   n1 AND n2 is just bits in n1 + bits in n2. So make a prefix or a postfix array that tells us how many numbers to the right have 1 bit, have 2, etc. So 30*n size. Now, for each number, count its bits, then we need some minimum extra amount of bits to put us over the threshold. Check the postfix and add up all numbers to the right with that many bits. For instance if we have 15 bits in our number and we need 20, check the amount of numbers to the right with 5 bits, with 6, ... to 30. Multiply the result by 2 since pairs can be inverted. Then account for any numbers that can pair with themselves.

class Solution:
    def countExcellentPairs(self, nums: List[int], k: int) -> int:
        # since we want unique pairs by value, we can remove duplicates
        nums = list(set(nums))

        @cache
        def countBits(n):
            total = 0
            for bit in range(30):
                if n & (1 << bit):
                    total += 1
            return total

        # create the postfix
        runningBits = {}
        for bit in range(30):
            runningBits[bit] = 0
        postfix = [None for _ in range(len(nums))]
        for i in range(len(nums) - 1, -1, -1):
            num = nums[i]
            postfix[i] = runningBits.copy()
            bitsInNum = countBits(num)
            runningBits[bitsInNum] += 1

        # for each number, use the postfix to add to the result
        result = 0
        for i, num in enumerate(nums):
            bitsInNum = countBits(num)
            bitsNeeded = k - bitsInNum
            if bitsNeeded < 0:
                bitsNeeded = 0 # prevent key errors
            totalViableToTheRight = 0 # how many numbers we can use from the right that have adequate bits
            # if we go out of range, we have the biggest number, there is nothing on the right to use
            if i + 1 == len(nums):
                break
            for bitCount in range(bitsNeeded, 30):
                totalViableToTheRight += postfix[i][bitCount]
            result += totalViableToTheRight

        result *= 2 # pairs can be inverted
        # we can use the same number twice
        for num in nums:
            if countBits(num) * 2 >= k:
                result += 1
        return result


