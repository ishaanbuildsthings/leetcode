t = int(input())
from collections import Counter
for _ in range(t):
    n = int(input())
    grid = []
    c = Counter()
    for _ in range(n):
        row = list(map(int, input().split()))
        grid.append(row)
        for v in row:
            c[v] += 1
    big = max(c.values())
    maxAllowed = (n*n)-n

    if n == 1:
        print("NO")
        continue
    
    if big <= maxAllowed:
        print("YES")
    else:
        print("NO")
    
    

    # X X X X X O
    # O X X X X X
    # X X X X X O
    # O X X X X X
    # X X X X X O