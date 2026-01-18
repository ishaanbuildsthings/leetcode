def solve(x, y):
    if x == y:
        return -1
    curr = 1
    while True:
        if curr - max(x, y) >= 10**18:
            return -1
        if curr >= max(x, y):
            return curr - max(x, y)
        curr *= 2
        
t = int(input())
for _ in range(t):
    x, y = map(int, input().split())
    print(solve(x, y))