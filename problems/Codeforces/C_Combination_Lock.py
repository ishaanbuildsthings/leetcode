# 1 -> 1
# 2 -> None work! (1, 2) has 2, (2, 1) has 0
# 3 -> 1 3 2 | 2 1 3 | 3 2 1 work
# 4 -> None work!
# 5 -> 1 3 5 2 4

import sys
input = sys.stdin.readline

t = int(input())
for _ in range(t):
    n = int(input())
    if n % 2 == 0:
        print(-1)
        continue
    arr = [0] * n
    curr = 1
    for i in range(n):
        arr[i] = curr
        curr += 2
        if curr > n:
            break
    # print(*arr)
    i += 1
    curr = 2
    for j in range(i, n):
        arr[j] = curr
        curr += 2
        if curr > n:
            break
    print(*arr)