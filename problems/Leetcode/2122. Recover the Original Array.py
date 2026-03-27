class Solution:
    def recoverArray(self, nums: List[int]) -> List[int]:
        ks = []
        nums.sort()
        for i in range(len(nums) - 2, -1, -1):
            diff = nums[-1] - nums[i]
            if diff % 2 == 0:
                k = diff // 2
                if k:
                    ks.append(k)
        
        for kopt in ks:
            c = Counter(nums)
            res = []
            for i in range(len(nums) - 1, -1, -1):
                v = nums[i]
                if not c[v]:
                    continue
                c[v] -= 1
                c[v - 2 * kopt] -= 1

                res.append(v - (kopt))
                    
            if max(c.values()) == min(c.values()) == 0:
                return res

