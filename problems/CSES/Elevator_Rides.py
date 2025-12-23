import functools
n, maxElevator = map(int, input().split())
weights = list(map(int, input().split()))

print(f'{weights=}')

fmask = (1 << n) - 1
@functools.lru_cache(maxsize=None)
def dp(mask):
    if mask == fmask:
        return (0, 0) # completed rides, smallest weight in current ride

    resHere = (float('inf'), float('inf'))
    
    for i in range(n):
        if mask & (1 << i): continue # skip taken passengers
        newMask = mask | (1 << i)
        minRides, smallestWeight = dp(newMask)
        