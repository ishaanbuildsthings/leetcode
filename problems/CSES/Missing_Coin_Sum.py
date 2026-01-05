n = int(input())
A = list(map(int, input().split()))
A.sort()
makeable = 0
for i, v in enumerate(A):
    if v > makeable + 1:
        print(makeable + 1)
        exit()
    makeable += v
print(makeable + 1)