t = int(input())
for _ in range(t):
    a, x, y = map(int, input().split())
    if a == x or a == y:
        print("NO")
        continue
    if a < min(x, y) or a > max(x, y):
        print("YES")
        continue
    print("NO")