class Solution:
    def countIntersectingIntervals(self, intervals: list[list[int]]) -> int:
        OPEN = 0
        CLOSE = 1
        events = []
        for l, r in intervals:
            events.append((l, OPEN))
            events.append((r, CLOSE))
        events.sort()
        open = 0
        res = 0
        for i, type in events:
            if type == OPEN:
                open += 1
                continue
            res += (open - 1)
            open -= 1

        return res
            