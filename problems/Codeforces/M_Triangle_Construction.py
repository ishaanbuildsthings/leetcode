n = int(input())
A = list(map(int, input().split()))

tot = sum(A)
mx = max(A)
other = tot - mx
if mx > other * 2:
    print(other)
    exit()
print(tot // 3)