import math
tests = int(input())
for _ in range(tests):
    # print('=========')
    
    n, target = map(int, input().split())
    jumps = [] # holds (forward, magic time, back)
    for j in range(n):
        a, b, c = map(int, input().split())
        jumps.append((a, b, c))
    
    gain = 0
    for a, b, c in jumps:
        jumpsNoPenalty = b - 1
        distCovered = a * jumpsNoPenalty
        gain += distCovered
    
    if gain >= target:
        print(0)
        continue
    
    # print(f'gain is: {gain}')
    
    res = float('inf')

    # pick one to endure jumps
    for a, b, c in jumps:
        distance = target - gain # we need to cover DISTANCE more ground with up up up then fallback
        fullCycle = (a * b) - c
        # print(f'a full cycle is: {fullCycle}')
        if fullCycle <= 0:
            continue
        fullCyclesReq = (distance + fullCycle - 1) // fullCycle
        res = min(res, fullCyclesReq)
    
    if res == float('inf'):
        print(-1)
    else:
        print(res)
