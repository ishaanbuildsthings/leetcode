import math
def solve():
    # print('======')
    n = int(input())
    A = list(map(int, input().split()))
    frq = [0] * (n + 1)
    for i in range(len(A)):
        num = i + 1
        frq[num] = A[i]
    
    # print(f'{frq=}')

    if (sum(frq) < 3):
        # print('less than three total')
        print(0)
        return

    singles = 0
    chains = 0
    for v in frq:
        if v == 0:
            continue
        if v == 1:
            singles += 1
        else:
            chains += 1
    
    # print(f'{singles=}')
    # print(f'{chains=}')

    # if we have only one chain, use that and fill with singles
    if chains == 1:
        # print(f'only one chain...')
        # if we have one chain like AAAAAAA
        # we can insert into the first gap, third, fifth, and so on

        # we CAN insert into the last gap after the last A
        chainSize = max(frq)
        gaps = chainSize // 2
        usableGaps = min(gaps, singles)
        # print(f'{usableGaps=}')
        print(chainSize + usableGaps)
        return
    
    res = 0
    # for each chain, we put a padding of two on both sides
    usableSingles = 0
    chainSum = 0
    def mp(x):
        return (x - 2) // 2
    for v in frq:
        if v >= 2:
            chainSum += v
            if v >= 4:
                gaps = mp(v)
                usableSingles += gaps
    
    answer = chainSum + min(usableSingles, singles)

    print(answer)


t = int(input())
for _ in range(t):
    solve()