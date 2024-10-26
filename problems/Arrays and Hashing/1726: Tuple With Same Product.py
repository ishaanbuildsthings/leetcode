# https://leetcode.com/problems/tuple-with-same-product/description/
# difficulty: medium

# Problem
# Given an array nums of distinct positive integers, return the number of tuples (a, b, c, d) such that a * b = c * d where a, b, c, and d are elements of nums, and a != b != c != d.

# Solution
# My way was bad, I just implemented what I first thought of, which was getting products for two numbers and using those. Instead we can observe that all the numbers are distinct and just use path to solve it, as if there are two ways to make a product of a number, none of the 4 numbers are similar.

class Solution:
    def tupleSameProduct(self, nums: List[int]) -> int:
        nums = sorted(list(set(nums)))

        # maps a product to a list of tuples that produce it
        products = defaultdict(list)
        for i in range(len(nums) - 1):
            for j in range(i + 1, len(nums)):
                products[nums[i] * nums[j]].extend(
                    [
                        (nums[i], nums[j]),
                        (nums[j], nums[i])
                    ])

        res = 0
        for product in products:
            tuples = products[product]
            for i in range(len(tuples) - 1):
                tup1 = tuples[i]
                for j in range(i + 1, len(tuples)):
                    tup2 = tuples[j]
                    if not set(tup1) & set(tup2):
                        res += 2
        return res


