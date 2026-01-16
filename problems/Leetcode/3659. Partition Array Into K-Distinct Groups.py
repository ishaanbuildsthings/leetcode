class Solution:
    def partitionArray(self, nums: List[int], k: int) -> bool:
        n = len(nums)
        if n % k:
            return False

        groups = n // k
        c = Counter(nums)
        for key, v in c.items():
            if v > groups:
                return False

        return True