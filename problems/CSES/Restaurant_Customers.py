import sys
import heapq
input = sys.stdin.readline

n = int(input())
stays = [tuple(map(int, input().split())) for _ in range(n)]
stays.sort()

rights = [] # min heap
push = heapq.heappush
pop = heapq.heappop

res = 0
for l, r in stays:
    while rights and rights[0] < l:
        pop(rights)
    push(rights, r)
    if len(rights) > res:
        res = len(rights)

print(res)
