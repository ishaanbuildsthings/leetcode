class Solution:
    def trimMean(self, arr: List[int]) -> float:
        # can do in O(n) time using two quickselects, or maybe moving the bottom 5% to the left and the top 5% to the right (move zeroes)

        arr.sort()
        size = 0.9 * len(arr)
        return sum(arr[i] for i in range(
            int(len(arr) / 20),
            int(19 * len(arr) / 20))) / size