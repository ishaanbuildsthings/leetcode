def solve():
    n, k = map(int, input().split())
    A = list(map(int, input().split()))
    xs = list(map(int, input().split()))
    rights = [0] * (n + 1)
    for i, x in enumerate(xs):
        hlth = A[i]
        rights[abs(x)] += hlth

    extraShots = 0
    for i, v in enumerate(rights[1:]):
        extraShots += k
        if extraShots < v:
            print("NO")
            return
        extraShots -= v
    print("YES")
t = int(input())
for _ in range(t):
    solve()