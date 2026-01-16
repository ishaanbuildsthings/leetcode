t = int(input())
for _ in range(t):
    n, ZERO = map(int, input().split())
    A = list(map(int, input().split()))
    # print(f'{A=}')

    prevMinus = 0
    prevPlus = float('-inf')
    for v in A:
        newPrevPlus = prevMinus + v
        newPrevMinus = prevPlus - v
        prevMinus = max(prevMinus, newPrevMinus)
        prevPlus = max(prevPlus, newPrevPlus)
    print(max(prevMinus, prevPlus))