class Solution:
    def zigzagTraversal(self, grid: List[List[int]]) -> List[int]:
        arr = []
        for i in range(len(grid)):
            if i % 2 == 0:
                for num in grid[i]:
                    arr.append(num)
            else:
                for num in grid[i][::-1]:
                    arr.append(num)
        
        res = []
        for i in range(len(arr)):
            if not i % 2:
                res.append(arr[i])
        
        return res