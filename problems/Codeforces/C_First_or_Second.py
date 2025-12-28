T = int(input())
for _ in range(T):
    n = int(input())
    arr = list(map(int, input().split()))

    pf = []
    curr = 0
    for v in arr:
        curr += v
        pf.append(curr)

    # to gain a child, we need to gain all before it

    pfEvict = [arr[0]]
    for i in range(1, len(arr)):
        oldScore = pfEvict[-1]
        newScore = oldScore + abs(arr[i])
        pfEvict.append(newScore)
    
    def query(l, r, arr):
        if l >= len(arr):
            return 0
        if r >= len(arr):
            r = en(arr) - 1
        if l == 0:
            return arr[r]
        ans = arr[r] - arr[l - 1]
        return ans

    res = float('-inf')

    for i in range(len(arr)): # last person standing
        subtracted = query(i + 1, n - 1, pf)
        evicted = 0
        if i:
            evicted = pfEvict[i-1]
        score = evicted - subtracted
        res = max(res, score)
    
    print(res)


    # max prefix score from 0...i is the loss i+1: plus max full eviction score 0...i-1

    # while a negative in 2nd spot, pop

    # -5 3

