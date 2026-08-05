class Solution:
    def permute(self, nums: List[int]) -> List[List[int]]:
        path = [] # current visited numbers in order
        seen = set() # tracks which nodes are in our path, set for O(1) lookup
        ans = []

        def backtrack():
            # base case
            if len(path) == len(nums):
                ans.append(path[:])
                return
            for num in nums:
                # skip nodes already in our path
                if num in seen:
                    continue
                path.append(num)
                seen.add(num)
                backtrack()
                path.pop()
                seen.remove(num)
        
        backtrack()

        return ans
            
