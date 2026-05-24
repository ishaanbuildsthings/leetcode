class Solution:
    def limitOccurrences(self, nums: list[int], k: int) -> list[int]:
        c = Counter()
        res = []
        for v in nums:
            if c[v] >= k:
                continue
            c[v] += 1
            res.append(v)

        return res