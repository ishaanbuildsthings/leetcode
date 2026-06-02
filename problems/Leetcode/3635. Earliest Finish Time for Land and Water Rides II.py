
# len(arr) if no number is >= threshold
def firstIndexGTE(arr, threshold):
    index = bisect.bisect_left(arr, threshold)
    return index if index < len(arr) else len(arr)

# -1 if no number is <= threshold
def firstIndexLTE(arr, threshold):
    index = bisect.bisect_left(arr, threshold)
    return index - 1 if index > 0 and arr[index - 1] == threshold else -1

# -1 if no number <= threshold
def lastIndexLTE(arr, threshold):
    index = bisect.bisect_right(arr, threshold)
    return index - 1 if index > 0 else -1

class Solution:
    def earliestFinishTime(self, landStartTime: List[int], landDuration: List[int], waterStartTime: List[int], waterDuration: List[int]) -> int:
        # start time, duration
        lands = sorted([[landStartTime[i], landDuration[i]] for i in range(len(landStartTime))])
        # print(f'{lands=}')
        landStarts = [lands[i][0] for i in range(len(lands))]

        waters = sorted([[waterStartTime[i], waterDuration[i]] for i in range(len(waterStartTime))])
        # print(f'{waters=}')
        waterStarts = [waters[i][0] for i in range(len(waters))]
        # print(f'{waterStarts=}')

        suffW = {} # suffW[i] tells us the earliest water finihs time given we can use i...
        early = inf
        for i in range(len(waters) - 1, -1, -1):
            start, dur = waters[i]
            early = min(early, start + dur)
            suffW[i] = early

        # print(f'{suffW}')

        suffL = {}
        early = inf
        for i in range(len(lands) - 1, -1, -1):
            start, dur = lands[i]
            early = min(early, start + dur)
            suffL[i] = early

        prefW = {}
        early = inf
        for i in range(len(waters)):
            start, dur = waters[i]
            early = min(early, dur)
            prefW[i] = early

        prefL = {}
        early = inf
        for i in range(len(lands)):
            start, dur = lands[i]
            early = min(early, dur)
            prefL[i] = early


        res = inf

        # for each land, if we take this, find the lowest water count in a given range
        for i in range(len(lands)):
            start, dur = lands[i]
            end = start + dur # we can board any water who starts >= end

            lastI = lastIndexLTE(waterStarts, end) # all of these waters are already ready
            if lastI != -1:
                pfWaterDurMin = prefW[lastI]
                res = min(res, end + pfWaterDurMin)

            lastI += 1
            if lastI < len(waters):
                res = min(res, suffW[lastI])




        for i in range(len(waters)):
            start, dur = waters[i]
            end = start + dur
            # print(f'water end time: {end}')

            lastI = lastIndexLTE(landStarts, end)
            if lastI != -1:
                pfLandDurMin = prefL[lastI]
                res = min(res, end + pfLandDurMin)
            lastI += 1
            if lastI < len(lands):
                res = min(res, suffL[lastI])

        return res
            
            
            

    











        