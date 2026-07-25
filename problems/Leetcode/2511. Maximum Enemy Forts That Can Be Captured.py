class Solution:
    def captureForts(self, forts: List[int]) -> int:
        res = 0
        i = 1
        while i < len(forts):
            if forts[i] != 0:
                i += 1
                continue
            j = i + 1
            while j < len(forts):
                if forts[j] != 0:
                    left = forts[i-1]
                    right = forts[j]
                    s = sorted([left, right])
                    if s == [-1, 1]:
                        width = j - i
                        res = max(res, width)
                    i = j
                    break
                j += 1
            i += 1
        return res