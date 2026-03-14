def solve():
    print('---')
    x, y = list(map(int, input().split()))
    res = 0
    if x == y:
        print(0)
        return
    if x < y:
        # keep doubling until exceed
        while x < y:
            res += 1
            x *= 2
        print(res)
        return
    
    if y == 1:
        # guessing we cant downgrade to 1
        print(-1)
        return
    
    # x can go to half+1, so 100->51 if we pick 51
    # if x is odd like 11, we can go to 11//2 + 1

    # absolute smallest we could drop to is x//2 + 1

    # the largest we could drop to is 2/3rds though
    while x > y:
        smallest = x//2 + 1

        if x % 3 == 0:
            largest = ((x * 2) // 3) + 1 # 9 can drop to 5
        else:
            largest = (x*2 // 3) + 1
        x = largest
        res += 1
    
    print(res)

    # 72 -> 49
    # 100 -> 67
    
    # print(f'x is bigger than y...')
t = int(input())
for _ in range(t):
    solve()
