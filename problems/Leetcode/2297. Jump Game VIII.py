class Solution:
    def minCost(self, nums: List[int], costs: List[int]) -> int:

        # go to first GTE on right

        # go to first LT on right

        # strict decreasing stack
        stack = []
        onRight = [None] * len(nums)
        for i, v in enumerate(nums):
            while stack and nums[stack[-1]] <= v:
                poppedI = stack.pop()
                onRight[poppedI] = i
            stack.append(i)
        
        stack = []
        # mono-increasing stack
        smaller = [None] * len(nums)
        for i, v in enumerate(nums):
            while stack and nums[stack[-1]] > v:
                poppedI = stack.pop()
                smaller[poppedI] = i
            stack.append(i)
        
        @cache
        def dp(i):
            if i == len(nums) - 1:
                return 0
                        
            if onRight[i] is not None:
                opt1 = costs[onRight[i]] + dp(onRight[i])
            else:
                opt1 = inf
            
            if smaller[i] is not None:
                opt2 = costs[smaller[i]] + dp(smaller[i])
            else:
                opt2 = inf
        
            return min(opt1, opt2)
        
        return dp(0)