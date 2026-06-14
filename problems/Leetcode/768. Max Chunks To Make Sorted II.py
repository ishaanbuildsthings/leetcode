class Solution:
    def maxChunksToSorted(self, arr: List[int]) -> int:
        smallest = [None] * len(arr)
        run = float('inf')
        for i in range(len(arr) - 1, -1, -1):
            run = min(run, arr[i]) 
            smallest[i] = run
        
        splits = 0
        biggest = -1
        for i in range(len(arr)-1):
            biggest = max(biggest, arr[i])
            if smallest[i+1] >= biggest:
                splits += 1
        return splits + 1
            