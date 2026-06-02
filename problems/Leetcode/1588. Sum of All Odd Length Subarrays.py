class Solution:
    def sumOddLengthSubarrays(self, arr: List[int]) -> int:
        res = 0
        for i, num in enumerate(arr):
            allRights = len(arr) - i
            oddRights = math.ceil(allRights / 2)
            evenRights = allRights - oddRights

            allLefts = i + 1
            oddLefts = math.ceil(allLefts / 2)
            evenLefts = allLefts - oddLefts

            res += (num * (oddRights * oddLefts))
            res += (num * (evenRights * evenLefts))
        
        return res