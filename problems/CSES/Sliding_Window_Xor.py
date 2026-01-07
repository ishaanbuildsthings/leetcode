from collections import deque
n, k = map(int, input().split())
x, a, b, c = map(int, input().split())
res = 0
q = deque()
xor = 0
currX = None
for i in range(n):
    if i == 0:
        currX = x
    else:
        currX = (a * currX + b) % c
    q.append(currX)
    xor ^= currX
    if len(q) > k:
        lost = q.popleft()
        xor ^= lost
    if len(q) == k:
        res ^= xor
print(res)


# x_1 = x
# x_i = (a * x_i-1 + b) % c
