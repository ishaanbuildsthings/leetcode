class Solution:
    def findKthPositive(self, arr: List[int], k: int) -> int:
        # you can use binary search for logN since the numbers are distinct
        remain = k
        for i in range(len(arr)):
            prev = 0 if not i else arr[i-1]
            missed = arr[i]-prev-1
            remain -= missed
            if remain <= 0:
                remain += missed
                return prev + remain
        return arr[-1] + remain
