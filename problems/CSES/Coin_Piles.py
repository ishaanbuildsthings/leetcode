t = int(input())
for _ in range(t):
    a, b = map(int, input().split())
    tot = a + b
    if tot % 3:
        print("NO")
        continue
    if max(a, b) > 2 * min(a, b):
        print("NO")
        continue
    print("YES")