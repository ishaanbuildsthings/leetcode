class Solution:
    def checkSubarraySum(self, nums: List[int], k: int) -> bool:
        pf = {0:-1}
        cur = 0
        for i, val in enumerate(nums):
            cur += val
            bigger = math.ceil(cur/k) * k
            target = (cur - bigger + k) % k
            if target in pf and i-pf[target] >= 2:
                return True
            if cur%k not in pf:
                pf[cur%k]=i
        return False