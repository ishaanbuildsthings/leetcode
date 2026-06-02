class Solution:
    def totalFruit(self, fruits: List[int]) -> int:
        l = r = res = 0
        seen = Counter()
        while r < len(fruits):
            newFruit = fruits[r]
            seen[newFruit] += 1
            while len(seen) > 2:
                lostFruit = fruits[l]
                seen[lostFruit] -= 1
                if not seen[lostFruit]:
                    del seen[lostFruit]
                l += 1
            res = max(res, r - l + 1)
            r += 1
        return res
            