T = int(input())
for _ in range(T):
    # print('=========')
    a, b = map(int, input().split())
    # a = 10
    # b = 10

    def solve(topC, bottomC):
        nxtLayer = 0
        turn = 0
        steps = 0
        # print(f'topC={topC} {bottomC=}')
        while True:
            if turn == 0:
                topC -= 2**nxtLayer
            else:
                bottomC -= 2**nxtLayer
            # print(f'after losing layer: {topC=} {bottomC=}')
            if min(topC, bottomC) < 0:
                return steps
            turn ^= 1
            steps += 1
            nxtLayer += 1
    
    print(max(solve(a,b),solve(b,a)))
