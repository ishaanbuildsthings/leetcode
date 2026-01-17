class Solution:
    def missingNumber(self, arr: List[int]) -> int:
        mn = min(arr)
        mx = max(arr)
        betweenShouldBe = len(arr) - 1
        gaps = betweenShouldBe + 1
        diffPerGap = int((mx - mn) / gaps)
        if diffPerGap == 0:
            return mn
        c = Counter(arr)
        for v in range(mn, mx + 1, diffPerGap):
            print(v)
            if not c[v]:
                return v