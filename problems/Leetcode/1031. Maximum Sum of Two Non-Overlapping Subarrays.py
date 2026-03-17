class Solution:
    def maxSumTwoNoOverlap(self, nums: List[int], firstLen: int, secondLen: int) -> int:

        def solve(nums):
            pf = []
            curr = 0
            for num in nums:
                curr += num
                pf.append(curr)
            
            def q(l, r):
                if not l:
                    return pf[r]
                return pf[r] - pf[l-1]
            
            @cache
            def dp(i, stage):
                if i == len(nums):
                    return -inf
                if stage == 0:
                    ifNoStart = dp(i + 1, 0)
                    rightEndpoint = i + firstLen - 1
                    if rightEndpoint >= len(nums):
                        ifTake = -inf
                    else:
                        sumIfTake = q(i, i + firstLen - 1)
                        ifTake = sumIfTake + dp(rightEndpoint + 1, 1)
                    return max(ifNoStart, ifTake)
                if stage == 1:
                    ifNoStart = dp(i + 1, 1)
                    rightEndpoint = i + secondLen - 1
                    if rightEndpoint >= len(nums):
                        ifTake = -inf
                    else:
                        sumIfTake = q(i, i + secondLen - 1)
                        ifTake = sumIfTake
                    return max(ifNoStart, ifTake)
                
            
            return dp(0, 0)
        
        return max(solve(nums), solve(nums[::-1]))