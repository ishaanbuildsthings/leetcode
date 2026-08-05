class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        res = []
        def backtrack(bucket, currSum, i):
            if currSum == target:
                res.append(bucket[:])
                return
            if currSum > target:
                return
            if i == len(candidates):
                return
            # if we take this
            bucket.append(candidates[i])
            backtrack(bucket, currSum + candidates[i], i)
            bucket.pop()

            # if we skip
            backtrack(bucket, currSum, i + 1)
        
        backtrack([], 0, 0)
        return res