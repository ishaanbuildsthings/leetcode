class Solution:
    def maxSubarraySum(self, nums: List[int], k: int) -> int:
        n = len(nums)

        def fn(type):
            vops = []
            for v in nums:
                if type == 0:
                    vop = v * k
                else:
                    vop = (v // k) if v >= 0 else ceil(v / k)
                vops.append(vop)

            c = [[None] * 3 for _ in range(n)]
            def dp(i, opStage):
                if i == n:
                    return 0 if opStage == 2 else -inf
                if c[i][opStage] is not None:
                    return c[i][opStage]
                
                v = nums[i]
                vOp = vops[i]
                
                if opStage == 0:
                    ifSkipOp = v + dp(i + 1, 0)
                    ifStartOp = vOp + dp(i + 1, 1)
                    ifFinishOp = vOp + max(0, dp(i + 1, 2))
                    ans = max(ifSkipOp, ifStartOp, ifFinishOp)
                
                if opStage == 2:
                    ans = v + max(0, dp(i + 1, 2))
                
                if opStage == 1:
                    ans = vOp + max(0, dp(i + 1, 1), dp(i + 1, 2))
                
                c[i][opStage] = ans
                return ans
            
            return dp
        
        dp1 = fn(0)
        dp2 = fn(1)
        
        res = -inf
        for i in range(n):
            res = max(res, dp1(i, 0), dp2(i, 0))
            if i:
                res = max(res, dp1(i, 1), dp2(i, 1))
                res = max(res, dp1(i, 2), dp2(i, 2))
        
        return res
                    