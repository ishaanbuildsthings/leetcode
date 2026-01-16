t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))
    tot = sum(A)
    k = len(A)
    if tot == k:
        print(0)
        continue
    if tot < k:
        print(1)
        continue
    print(tot - k)
