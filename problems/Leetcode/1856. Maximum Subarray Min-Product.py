class Solution:
    def maxSumMinProduct(self, nums: List[int]) -> int:
        # for each number, find how far right it can go, it has to be <= all numbers
        goRight = {}
        stack = [] # holds indices
        for i, num in enumerate(nums):
            if not stack:
                stack.append(i)
                continue
            if num >= nums[stack[-1]]:
                stack.append(i)
                continue
            while stack and num < nums[stack[-1]]:
                popped = stack.pop()
                goRight[popped] = i - 1
            stack.append(i)
        for index in stack:
            goRight[index] = len(nums) - 1
        

        # for each number, find how far left it can go, it has to be <= all numbers on the left
        goLeft = {}
        stack = [len(nums) - 1] # going backwards, INCREASING stack, so will find first left number that is LTE
        for i in range(len(nums) - 2, -1, -1):
            while stack and nums[stack[-1]] > nums[i]:
                p = stack.pop()
                if not p in goLeft:
                    goLeft[p] = i + 1
            stack.append(i)
        for index in stack:
            goLeft[index] = 0
        
        res = 0

        pf = []
        curr = 0
        for i, num in enumerate(nums):
            curr += num
            pf.append(curr)
        
        def query(l, r):
            if not l:
                return pf[r]
            return pf[r] - pf[l - 1]

        for index in range(len(nums)):
            left = goLeft[index]
            right = goRight[index]
            tot = query(left, right)
            res = max(res, nums[index] * tot)
        return res % (10**9 + 7)

            
            