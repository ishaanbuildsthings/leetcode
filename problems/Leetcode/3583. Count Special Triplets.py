class Solution:
    def specialTriplets(self, nums: List[int]) -> int:
        MOD = 10**9 + 7

        seenLeft = Counter()
        seenRight = Counter(nums)
        seenRight[nums[0]] -= 1

        res = 0
        for j in range(1, len(nums) - 1):
            seenLeft[nums[j-1]] += 1
            seenRight[nums[j]] -= 1
            res += seenLeft[nums[j] * 2] * seenRight[nums[j] * 2]
        return res % MOD
            