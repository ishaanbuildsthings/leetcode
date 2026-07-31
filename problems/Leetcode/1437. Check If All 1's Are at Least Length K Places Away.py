class Solution:
    def kLengthApart(self, nums: List[int], k: int) -> bool:
        prev = -inf
        for i, num in enumerate(nums):
            if num == 1:
                if i - prev <= k:
                    return False
                prev = i
        return True