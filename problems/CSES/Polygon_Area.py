n = int(input())
points = []
for _ in range(n):
    x, y = map(int, input().split())
    points.append((x, y))
res = 0
for i in range(n):
    x, y = points[i]
    x2, y2 = points[(i + 1) % n]
    res += (x*y2 - y*x2)
print(abs(res))