class Solution:
    def filterOccupiedIntervals(self, occupiedIntervals: List[List[int]], freeStart: int, freeEnd: int) -> List[List[int]]:
        ivals = occupiedIntervals
        ivals.sort()
        prevStart = ivals[0][0]
        prevEnd = ivals[0][-1]
        merged = []
        for i in range(1, len(ivals)):
            s, e = ivals[i]
            if s <= prevEnd + 1:
                prevEnd = max(e, prevEnd)
                continue
            merged.append([prevStart, prevEnd])
            prevStart = s
            prevEnd = e
        merged.append([prevStart, prevEnd])

        # print(merged)

        res = []

        for s, e in merged:
            if e < freeStart or s > freeEnd:
                res.append([s, e])
                continue
            # contained
            if s >= freeStart and e <= freeEnd:
                continue

            # contains
            if s <= freeStart and e >= freeEnd:
                LEFT = [s, freeStart - 1]
                RIGHT = [freeEnd + 1, e]
                if s <= freeStart - 1:
                    res.append(LEFT)
                if freeEnd + 1 <= e:
                    res.append(RIGHT)
                continue

            # on left
            if s <= freeStart:
                LEFT = [s, freeStart - 1]
                if s <= freeStart - 1:
                    res.append(LEFT)
                continue

            # on right
            if e >= freeEnd:
                RIGHT = [freeEnd + 1, e]
                if freeEnd + 1 <= e:
                    res.append(RIGHT)
                continue

        return res
            
            