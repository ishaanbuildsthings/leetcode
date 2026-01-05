n = int(input())
A = list(map(int, input().split()))
if max(A) > sum(A) / 2:
    print(2 * max(A))
else:
    print(sum(A))