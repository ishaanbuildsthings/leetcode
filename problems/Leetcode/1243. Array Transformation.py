class Solution:
    def transformArray(self, arr: List[int]) -> List[int]:
        while True:
            change = False
            narr = arr[:]
            for i, v in enumerate(arr):
                if i and i < len(arr) - 1 and ((arr[i-1]<arr[i]>arr[i+1]) or (arr[i-1]>arr[i]<arr[i+1])):
                    narr[i] += (-1 if arr[i]>arr[i-1] else 1)
                    change = True
            arr = narr
            if not change:
                break
        return arr