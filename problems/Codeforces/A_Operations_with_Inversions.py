T = int(input())
for _ in range(T):
    n = int(input())
    arr = list(map(int, input().split()))
    pfMax = []
    curr = 0
    for v in arr:
        curr = max(curr, v)
        pfMax.append(curr)
    
    res = 0
    for i, v in enumerate(arr):
        if i == 0: continue
        if pfMax[i-1] > arr[i]:
            res += 1
    print(res)
    