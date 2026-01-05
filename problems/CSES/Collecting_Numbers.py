n = int(input())
A = list(map(int, input().split()))
vToI = { v : i for i, v in enumerate(A) }
score = 1 # initial pass
for num in range(1, n):
    if vToI[num + 1] < vToI[num]:
        score += 1
print(score)