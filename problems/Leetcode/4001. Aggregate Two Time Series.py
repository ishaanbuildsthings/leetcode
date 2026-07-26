

# Wrong Answer
# 251 / 863 testcases passed
# Input
# series1 =
# [[1,3],[4,1]]
# series2 =
# [[2,2],[5,2]]
# Use Testcase
# Output
# [[1,5],[2,3],[4,3],[[5,2]]]
# Expected
# [[1,5],[2,3],[4,3],[5,2]]
class Solution:
    def aggregateTimeSeries(self, series1: list[list[int]], series2: list[list[int]]) -> list[list[int]]:

        res = []

        i = 0
        j = 0

        while i < len(series1) and j < len(series2):
            # print(f'{i=} {j=}')
            t1, v1 = series1[i]
            t2, v2 = series2[j]

            if t1 == t2:
                res.append([t1, v1 + v2])
                i += 1
                j += 1
                continue

            # if this time is smaller, our score is v1 + the next score in series2
            if t1 < t2:
                nscore = v1 + v2
                res.append([t1, nscore])
                i += 1
                continue

            elif t1 > t2:
                # print(f't1 too big')
                nscore = v2 + v1
                res.append([t2, nscore])
                j += 1
                continue

        while i < len(series1):
            res.append(series1[i])
            i += 1
        while j < len(series2):
            res.append(series2[j])
            j += 1

        return res
                