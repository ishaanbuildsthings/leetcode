n = int(input())
weights = list(map(int, input().split()))


# meet in the middle, split into two groups of (2^(n/2)) and run two pointers to get a groupA size as close to `half` as possible
left = weights[:n//2]
right = weights[n//2:]
tot = sum(weights)
half = tot // 2

def getSums(arr):
    sums = [0]
    for v in arr:
        sums += [x + v for x in sums]
    return sorted(sums)

leftSums = getSums(left)
rightSums = getSums(right)
i = 0
j = len(rightSums) - 1
res = float('inf')

while i < len(leftSums) and j >= 0:
    groupA = leftSums[i] + rightSums[j]
    groupB = tot - groupA
    res = min(res, abs(groupB - groupA))
    if groupA <= half:
        i += 1
    else:
        j -= 1


print(res)


# slower version that is 2^n, generate all subset sums (still use an optimization to get sums in 2^n, not n * 2^n)

# sums = [0]
# for v in weights:
#     sums += [x + v for x in sums]
# tot = sum(weights)
# res = float('inf')
# for v in sums:
#     diff = abs((tot - v) - v)
#     res = min(res, diff)
# print(res)