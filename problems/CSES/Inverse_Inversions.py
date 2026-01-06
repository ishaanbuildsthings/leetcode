n, k = map(int, input().split())

# if we place the max number (say 5) we can choose how many versions include that number
# keep placing inversions greedily as much as we can, when we hit our target, fill out the remainders with no inversions

res = [None] * n
currInversions = 0
currNum = n
while currInversions < k:
    takeInversions = min(k - currInversions, currNum - 1)
    idx = n - takeInversions - 1
    res[idx] = currNum
    currNum -= 1
    currInversions += takeInversions

# print(res)
num = 1
for i, v in enumerate(res):
    if v is None:
        res[i] = num
        num += 1

print(*res)

    