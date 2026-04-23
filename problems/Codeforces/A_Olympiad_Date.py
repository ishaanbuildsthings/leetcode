import sys
input = sys.stdin.readline
from collections import Counter

t = int(input())
for _ in range(t):
    n = int(input())
    digits = list(map(int, input().split()))

    target = [0, 1, 0, 3, 2, 0, 2, 5]
    targetC = Counter(target)

    c = Counter()
    turns = 0
    shouldstop = False
    for d in digits:
        c[d] += 1
        turns += 1
        if c >= targetC:
            shouldstop = True
            print(turns)
            break
    if shouldstop:
        continue
    print(0)

 