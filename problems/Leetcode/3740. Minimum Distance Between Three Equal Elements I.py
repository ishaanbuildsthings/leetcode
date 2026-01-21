class Solution:
    def minimumDistance(self, nums: List[int]) -> int:
        idxs = defaultdict(list)
        res = inf
        for i, v in enumerate(nums):
            if len(idxs[v]) <= 1:
                idxs[v].append(i)
                continue
            width = 2 * (i - idxs[v][0])
            res = min(res, width)
            idxs[v].pop(0)
            idxs[v].append(i)
        return res if res != inf else -1