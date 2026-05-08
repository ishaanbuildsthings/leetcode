n, m = map(int, input().split())
arr = list(map(int, input().split()))
 
MOD = 10**9 +7
 
prev = [0] * (m+1) # the running answer for if the previous number is m
if arr[0] != 0:
  prev[arr[0]] = 1
else:
  prev = [0] + ([1] * m)
 
for i in range(1, len(arr)):
  curr = [0] * (m + 1)
  for number in range(1, m + 1):
    # if there was a number in the array and it isn't what we are proposing to put here, the dp becomes 0
    if arr[i] != 0 and number != arr[i]:
      continue
    left = prev[number-1]
    same = prev[number]
    right = prev[number+1] if number != m else 0
    newVal = left + right + same
    curr[number] = newVal % MOD
  prev = curr
print(sum(prev) % MOD)
