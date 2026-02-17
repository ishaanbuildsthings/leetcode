class Solution:
    def merge(self, i: List[List[int]]) -> List[List[int]]:
        i.sort()
        prevStart = i[0][0]
        prevBig = i[0][1]
        res = []
        for j in range(1, len(i)):
            start, end = i[j]
            if start <= prevBig:
                prevBig = max(prevBig, end)
            else:
                res.append([prevStart, prevBig])
                prevStart, prevBig = i[j]
        res.append([prevStart, prevBig])
        return res