t = int(input())
for _ in range(t):
    n, s, x = map(int, input().split())
    A = list(map(int, input().split()))
    tot = sum(A)
    if tot == s:
        print("YES")
        continue
    
    if tot > s:
        print("NO")
        continue
    
    diff = s - tot

    if diff % x == 0:
        print("YES")
    else:
        print("NO")
