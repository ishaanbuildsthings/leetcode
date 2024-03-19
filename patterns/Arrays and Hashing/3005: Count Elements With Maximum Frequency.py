# https://leetcode.com/problems/count-elements-with-maximum-frequency/description/?envType=daily-question&envId=2024-03-08
# difficulty: easy

# Solution
class Solution:
    def maxFrequencyElements(self, nums: List[int]) -> int:
        # can make faster / not call frqs.values()
        frqs = Counter(nums)
        maxFrq = max(frqs.values())
        res = sum(1 if frqs[num] == maxFrq else 0 for num in nums)
        return res