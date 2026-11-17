class Solution:
    def totalSteps(self, nums: List[int]) -> int:
        n = len(nums)
        onLeft = [inf] * n
        
        stack = [] # mono-increasing
        dp = [0] * n
        for i in range(len(nums) -1, -1, -1):
            v = nums[i]
            while stack and v > nums[stack[-1]]:
                dp[i] = max(dp[i] + 1, dp[stack[-1]])
                stack.pop()
            stack.append(i)
        
        return max(dp)




        # # for each number, find the first on left that is bigger

        # n = len(nums)
        # onLeft = [inf] * n
        
        # stack = [] # mono-increasing
        # for i in range(len(nums) -1, -1, -1):
        #     v = nums[i]
        #     if not stack:
        #         stack.append(i)
        #         continue
        #     while stack and v > nums[stack[-1]]:
        #         poppedI = stack.pop()
        #         onLeft[poppedI] = i
        #     stack.append(i)
        
        # # how long l...r takes to die, l-1 is guaranteed bigger than l
        # @cache
        # def die(l, r):
        #     if l == r:
        #         return 1
        #     if l > r:
        #         return 0
        #     killer = onLeft[r]
        #     piece1 = die(l, killer)
        #     piece2 = die(killer + 1, r - 1) + 1
        #     return max(piece1, piece2)

        # res = 0
        
        # for i, v in enumerate(nums):
        #     if onLeft[i] == inf:
        #         continue
        #     res = max(res, die(onLeft[i] + 1, i))
        #     # how long does l+1...r-1 take to die

        # return res