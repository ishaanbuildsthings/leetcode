class Solution:
    def minOrAfterOperations(self, nums: List[int], k: int) -> int:
        promise = 0
        if max(nums) == 0:
            return 0
        LOG = int(math.log2(max(nums))) + 2
        fmask = (1 << LOG) - 1
        for b in range(LOG - 1, -1, -1):
            trial = promise | (1 << b)
            running = fmask
            mergesUsed = 0
            for v in nums:
                running &= v
                if running & trial == 0:
                    running = fmask
                else:
                    mergesUsed += 1
            if mergesUsed <= k:
                promise = trial
        
        return fmask ^ promise
