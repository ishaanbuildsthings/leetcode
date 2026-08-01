class Solution:
    def countGoodTriplets(self, arr: List[int], a: int, b: int, c: int) -> int:
        # can do n^2 log n with checking every pair of a and b then using a range query
        return sum(
            abs(arr[i] - arr[j]) <= a and
            abs(arr[j] - arr[k]) <= b and
            abs(arr[i] - arr[k]) <= c
            for i in range(len(arr) - 2) for j in range(i + 1, len(arr) - 1) for k in range(j + 1, len(arr))
        )