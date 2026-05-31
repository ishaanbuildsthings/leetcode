import heapq
n = int(input())
A = list(map(int, input().split()))
minHeap = []
totHealth = 0
for i, v in enumerate(A):
    if v >= 0:
        totHealth += v
        heapq.heappush(minHeap, v)
        continue
    # if v is negative but we can tank it, do so
    if v < 0 and abs(v) <= totHealth:
        totHealth += v
        heapq.heappush(minHeap, v)
        continue
    # if v is negative but there was a worse negative, swap
    if minHeap:
        small = minHeap[0]
        if small < v:
            heapq.heappop(minHeap)
            heapq.heappush(minHeap, v)
            totHealth += v - small
print(len(minHeap))

