n, q = list(map(int, input().split()))
arr = list(map(int, input().split()))
qs = []
for _ in range(q):
    qs.append(int(input()))

pairs = 0
for i in range(n // 2):
    pairs += arr[i] != arr[~i]

# 1 2 3 4 -> 2 pairs, so k=2, k=4, k=6 etc are doable
# 1 2 3 4 5 -> 2 pairs, so same thing

def solveQ(q):
    if q < pairs:
        print('NO')
        return
    if n % 2:
        if q == pairs:
            print('YES')
            return
        if (q - pairs) % 2 == 0:
            print('YES')
            return
        toSwapCenter = 3
        remainPairs = pairs - 1
        minDo = toSwapCenter + remainPairs
        if q < minDo:
            print('NO')
            return
        print('YES')
        return
    if (q - pairs) % 2:
        print('NO')
        return
    print('YES')
    
    # we have at least pairs swaps, but a wrong toggled bit
    # if we have an odd number 

for q in qs:
    solveQ(q)