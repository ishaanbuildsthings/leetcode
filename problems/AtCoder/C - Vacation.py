n = int(input())
activities = [tuple(map(int, input().split())) for _ in range(n)]

prevA = 0
prevB = 0
prevC = 0

for a, b, c in activities:
  newPrevA = max(prevA, prevB + a, prevC + a)
  newPrevB = max(prevB, prevA + b, prevC + b)
  newPrevC = max(prevC, prevA + c, prevB + c)
  prevA = newPrevA
  prevB = newPrevB
  prevC = newPrevC

print(max(prevA, prevB, prevC))