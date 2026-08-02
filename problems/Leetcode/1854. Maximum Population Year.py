class Solution:
    def maximumPopulation(self, logs: List[List[int]]) -> int:
        events = []
        diffs = defaultdict(int)
        for b, d in logs:
            diffs[b] += 1
            diffs[d] -= 1
        for key in diffs:
            events.append((key, diffs[key]))
        
        # could use a linesweep instead of sorting events, and could use coordinate compression, but that requires sorting the logs anyway
        events.sort()
        currSize = biggestSize = 0
        res = None
        for year, diff in events:
            currSize += diff
            if currSize > biggestSize:
                res = year
                biggestSize = currSize
        return res
