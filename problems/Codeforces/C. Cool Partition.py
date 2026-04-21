import sys
input = sys.stdin.readline
from collections import Counter
 
t = int(input())
for _ in range(t):
    n = int(input())
    a = list(map(int, input().split()))
 
    # the last partition should have every unique element
    c = Counter(a)
    splits = 0
    # allUnique = list(c.keys())
    curr = Counter()
    for i in range(len(a) - 1, -1, -1):
        curr[a[i]] += 1
        if len(curr) < len(c):
            continue
        splits += 1
        for key in curr:
            c[key] -= curr[key]
            if not c[key]:
                del c[key]
        curr = Counter()
 
    print(splits)