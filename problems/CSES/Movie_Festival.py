n = int(input())
movies = []
for _ in range(n):
    a, b = map(int, input().split())
    movies.append([a, b])
movies.sort(key=lambda x: x[1])

prevRightBorder = -1
res = 0
for l, r in movies:
    if l >= prevRightBorder:
        prevRightBorder = r
        res += 1
print(res)
