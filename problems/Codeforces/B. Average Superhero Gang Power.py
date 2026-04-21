import sys
input = sys.stdin.readline
 
n, k, m = map(int, input().split())
powers = list(map(int, input().split()))
 
# n = heroes
# k = max ops per hero
# m = total ops
 
powers.sort(reverse=True)
# print(f'{powers=}')
 
pfSum = 0
width = 0
res = 0
for p in powers:
  # print('-----------')
  pfSum += p
  # print(f'{pfSum=}')
  width += 1
  # print(f'{width=}')
  # max ops we can apply is at most m, or width * k
  opsConsumedFromDeletions = n - width
  newOpsLeft = m - opsConsumedFromDeletions
  if newOpsLeft < 0:
    continue
  maxOps = min(newOpsLeft, width * k)
  # print(f'{maxOps=}')
  newPower = maxOps + pfSum
  # print(f'{newPower=}')
  avg = newPower / width
  # print(f'{avg=}')
  res = max(res, avg)
 
print(res)