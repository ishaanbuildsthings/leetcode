class Solution:
    def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:
        n = len(candidates)
        candidates.sort()
        res = []
        curr = []
        def bt(i, curr, tot):
            if tot == target: return res.append(curr[:])
            if i == n or tot > target: return
            nextI = next((j for j in range(i + 1, n) if candidates[j] != candidates[i]), n)
            ifSkip = bt(nextI, curr, tot)
            curr.append(candidates[i])
            bt(i + 1, curr, tot + candidates[i])
            curr.pop()
        bt(0, [], 0)
        return res
            