n, k = map(int, input().split())
A = list(map(int, input().split()))
l = 1
r = 10**18
res = None
def canMake(totalTime):
    v = 0
    for rate in A:
        v += totalTime // rate
        if v >= k:
            return True
    return False
while l <= r:
    m = (r+l)//2
    if canMake(m):
        res = m
        r = m - 1
    else:
        l = m + 1
print(res)
