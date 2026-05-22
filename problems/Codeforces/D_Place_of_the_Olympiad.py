import sys
input = sys.stdin.readline
import math

t = int(input())
for _ in range(t):
    n, m, k = map(int, input().split())

    def numSeatsConsumedForOneRowWithMaxBenchSize(maxBenchSize):
        groupWithSpaceOnRight = maxBenchSize + 1
        groupsThatFit = m // groupWithSpaceOnRight
        totalSpace = groupsThatFit * groupWithSpaceOnRight
        spaceAfterLastBench = m - totalSpace
        totalDesksPlaced = groupsThatFit * maxBenchSize
        totalDesksPlaced += min(max(0, spaceAfterLastBench), maxBenchSize)
        return totalDesksPlaced


    def numSeatsConsumedWithMaxBenchSize(maxBenchSize):
        numSeatsConsumedInOneRow = numSeatsConsumedForOneRowWithMaxBenchSize(maxBenchSize)
        return numSeatsConsumedInOneRow * n

    l = 1
    r = m
    res = m
    while l <= r:
        mid = (r+l)//2
        totalSeatsDoable = numSeatsConsumedWithMaxBenchSize(mid)
        if totalSeatsDoable >= k:
            res = mid
            r = mid - 1
        else:
            l = mid + 1
    print(res)

 