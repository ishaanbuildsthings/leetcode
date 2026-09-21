import sys
import math
INF = 10**18

def solve(n, arr):
    res = INF
    buckets = []
    currBucket = []
    for i in range(len(arr)):
        if not currBucket:
            currBucket.append(arr[i])
            continue
        if arr[i] == currBucket[-1]:
          currBucket.append(arr[i])
          continue
        else:
          buckets.append(currBucket)
          currBucket = [arr[i]]
    if currBucket:
      buckets.append(currBucket)
    onLeft = 0
    for bucket in buckets:
        lengthOutsideBucket = len(arr) - len(bucket)
        onRight = len(arr) - onLeft - len(bucket)
        costToSetLeft = onLeft * bucket[0]
        costToSetRight = onRight * bucket[-1]
        costToSetBucket = costToSetLeft + costToSetRight
        res = min(res, costToSetBucket)


        onLeft += lengthOutsideBucket
    print(res)

input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n = int(input())
    a = list(map(int, input().split()))
    result = solve(n, a)
    # print(result)