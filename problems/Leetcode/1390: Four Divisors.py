# https://leetcode.com/problems/four-divisors/description/
# difficulty: medium
# tags: math

# Problem
# Given an integer array nums, return the sum of divisors of the integers in that array that have exactly four divisors. If there is no such integer in the array, return 0.

# Solution
# Standard math stuff

def getIsFourDivisors(num):
    isPerfectSquare = math.sqrt(num) == math.floor(math.sqrt(num))
    count = 0
    tot = 0
    for divisor in range(1, math.ceil(math.sqrt(num))):
        if num % divisor == 0:
            count += 1
            tot += divisor
            tot += num / divisor
        if count == 3:
            return (False, None)
    if count != 2 or isPerfectSquare:
        return (False, None)
    return (True, tot) if count == 2 else (False, None)

fourDivisorToSum = defaultdict(int)
for num in range(1, 10**5 + 1):
    result = getIsFourDivisors(num)
    if result[0]:
        fourDivisorToSum[num] = result[1]


class Solution:
    def sumFourDivisors(self, nums: List[int]) -> int:
        return int(sum(fourDivisorToSum[num] for num in nums))
