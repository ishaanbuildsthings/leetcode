class Solution:
    def buttonWithLongestTime(self, events: List[List[int]]) -> int:
        biggestTime = defaultdict(int)
        for i in range(len(events)):
            index, time = events[i]
            prevTime = 0 if i == 0 else events[i - 1][1]
            timeToPush = time - prevTime
            biggestTime[index] = max(biggestTime[index], timeToPush)
        big = -inf
        res = None
        for index in biggestTime:
            time = biggestTime[index]
            if time > big:
                res = index
                big = time
                continue
            elif time == big:
                if res is None:
                    res = index
                else:
                    res = min(res, index)
        return res