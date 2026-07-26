class Solution:
    def validMountainArray(self, arr: List[int]) -> bool:
        if len(arr) < 3:
            return False

        i = 1
        for i in range(1, len(arr)):
            if arr[i] > arr[i - 1]:
                continue
            else:
                break
        i -= 1

        j = len(arr) - 2

        for j in range(len(arr) - 2, -1, -1):
            if arr[j] > arr[j + 1]:
                continue
            else:
                break
        j += 1

        return i >= j
            