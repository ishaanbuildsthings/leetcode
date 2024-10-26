# https://leetcode.com/problems/number-of-divisible-triplet-sums/description/
# difficulty: medium

# Solution, O(n^2) time O(n) space

class Solution:
    def divisibleTripletCount(self, nums: List[int], d: int) -> int:
        nums.sort()

        remainders = defaultdict(int) # maps a remainder to the # of elements that form that remainder
        for num in nums:
            remainders[num % d] += 1

        res = 0

        for i in range(len(nums) - 1):
            for j in range(i + 1, len(nums)):
                twoSum = nums[i] + nums[j]
                remainder = twoSum % d
                targetRemainder = (d - remainder) % d
                countOfTargetRemainder = remainders[targetRemainder]
                countOfTargetRemainder -= nums[i] % d == targetRemainder
                countOfTargetRemainder -= nums[j] % d == targetRemainder
                res += countOfTargetRemainder

        return int(res / 3)
