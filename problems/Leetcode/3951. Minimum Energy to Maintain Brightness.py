class Solution:
    def minEnergy(self, n: int, brightness: int, intervals: list[list[int]]) -> int:
        def merge(i):
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

        merged = merge(intervals)

        lights = math.ceil(brightness / 3)

        size = 0
        for a, b in merged:
            size += b - a + 1

        return size * lights