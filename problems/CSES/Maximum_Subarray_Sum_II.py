from collections import deque
n, a, b = map(int, input().split())
arr = list(map(int, input().split()))

class Monodeque:
    def __init__(self, arr):
        self.arr = arr
        self.q = deque() # holds indices, mono-increasing numbers
    
    def append(self, idx):
        while self.q and self.arr[self.q[-1]] > self.arr[idx]:
            self.q.pop()
        self.q.append(idx)
    
    def popleftWhileIndexLessThan(self, idx):
        while self.q and self.q[0] < idx:
            self.q.popleft()
    
    def minVal(self):
        if not self.q:
            return 0
        return self.arr[self.q[0]]
    
res = -float('inf')

pf = []
curr = 0
for i, v in enumerate(arr):
    curr += v
    pf.append(curr)

q = Monodeque(pf)

for r in range(a - 1, len(arr)):
    latestCanCutOff = r - a
    if latestCanCutOff >= 0:
        q.append(latestCanCutOff)
    earliestCanCutOff = r - b
    q.popleftWhileIndexLessThan(earliestCanCutOff)
    currSum = pf[r]
    smallestWeCanRemove = q.minVal()
    if earliestCanCutOff < 0:
        smallestWeCanRemove = min(smallestWeCanRemove, 0)
    res = max(res, currSum - smallestWeCanRemove)

print(res)


# 0 1 2 3 4 5



