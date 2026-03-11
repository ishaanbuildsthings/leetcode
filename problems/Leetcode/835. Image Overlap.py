class Solution:
    def largestOverlap(self, img1: List[List[int]], img2: List[List[int]]) -> int:
        res = 0
        n = len(img1)
        for r1 in range(-(n-1), n):
            for c1 in range(-(n-1), n):
                # img2[0][0] aligns with img1[r1][c1]
                resHere = 0
                for r2 in range(n):
                    for c2 in range(n):
                        if 0 <= r1 + r2 < n and 0 <= c1 + c2 < n:
                            if img1[r1 + r2][c1 + c2] and img2[r2][c2]:
                                resHere += 1
                res = max(res, resHere)
        return res