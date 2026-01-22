t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))
    print(max(A) - min(A))