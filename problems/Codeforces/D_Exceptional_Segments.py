MOD = 998244353
def solve():
    n, x = list(map(int, input().split()))
    # print('-------')
    # print(f'{n=} {x=}')
    # how many starts from 0, 4, 8, ... are <= X
    starts = (x // 4) + 1
    # print(f'{starts=}')
    # smallest overhang past X
    # 0 1 2 3
    # 4 5 6 7
    # 8 9 10 11

    if (x + 1) % 4 == 0:
        overhang = x
    elif (x + 1) % 4 == 3:
        overhang = x + 1
    elif (x + 1) % 4 == 2:
        overhang = x + 2
    else:
        overhang = x + 3

    # print(f'{overhang=}')

    # how many endings overhang, overhang + 4, ... can we take
    width = n - overhang + 1
    endings = ((width-1) // 4) + 1

    answer = (starts * endings) if overhang <= n else 0

    # print(f'init answer: {answer}')


    # but now we have to do it for blocks of 4 starting at a 2
    # start at 2, 6, 10, ...
    starts = ((x-2)//4) + 1
    # print(f'starts 2: {starts=}')
    if x % 4 == 1:
        # print(f'yes first')
        overhang = x
    elif x % 4 == 0:
        overhang = x + 1
    elif x % 4 == 3:
        overhang = x + 2
    else:
        overhang = x + 3
    
    # print(f'overhang 2: {overhang}')
    # how many endings overhang, overhang + 4, ... can we take
    width = n - overhang + 1
    endings = ((width-1) // 4) + 1
    ans2 = (starts * endings) if overhang <= n else 0
    ans = answer + ans2
    ans %= MOD


    print(ans)


t = int(input())
for _ in range(t):
    solve()