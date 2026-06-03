# O(n^2) no tle
n, target = map(int, input().split())
A = list(map(int, input().split()))
frontPairSums = {} # maps a sum -> (i, j) for the front pair of 2 elements

# our 4 elements are (i, j, k, l)
for k in range(n):
    v_k = A[k]
    for l in range(k + 1, n):
        backPairSum = v_k + A[l]
        req = target - backPairSum
        if req in frontPairSums:
            pair = frontPairSums[req]
            ans = [pair[0] + 1, pair[1] + 1, k + 1, l + 1]
            print(*ans)
            exit()
    # now form a front pair
    for i in range(k):
        pairSum = v_k + A[i]
        frontPairSums[pairSum] = (i, k)

print('IMPOSSIBLE')


# O(n^2) but tle
# from collections import defaultdict
# n, target = map(int, input().split())
# A = list(map(int, input().split()))
 
# pfSumToPairs = defaultdict(set)
# suffSumToPairs = defaultdict(set)
# for i in range(n):
#     for j in range(i + 1, n):
#         tot = A[i] + A[j]
#         suffSumToPairs[tot].add((i, j))
 
# for i in range(n):
#     for j in range(i + 1, n):
#         tot = A[i] + A[j]
#         suffSumToPairs[tot].remove((i, j))
#     for j in range(i):
#         tot = A[i] + A[j]
#         pfSumToPairs[tot].add((i, j))
#     for j in range(i):
#         pairSum = A[i] + A[j]
#         req = target - pairSum
#         if req in suffSumToPairs and suffSumToPairs[req]:
#             pfPairs = list(pfSumToPairs[pairSum])
#             suffPairs = list(suffSumToPairs[req])
#             ans = [pfPairs[0][0] + 1, pfPairs[0][1] + 1, suffPairs[0][0] + 1, suffPairs[0][1] + 1]
#             print(*ans)
#             exit()
 
# print('IMPOSSIBLE')
