class Solution:
    def findLucky(self, arr: List[int]) -> int:
        # can bucket sort or normal sprt
        counts = Counter(arr)
        res = max(
            (num for num in arr if counts[num] == num), default=0
        )
        return res if res else -1