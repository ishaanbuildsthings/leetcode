def solve():
    # print('------------')
    n, k, p, MAX_ENERGY = list(map(int, input().split()))
    p -= 1
    # print(f'{k=} {p=} {MAX_ENERGY=}')
    arr = list(map(int, input().split()))
    # print(f'{arr=}')

    def excise(i):
        pre = arr[:i]
        post = arr[i+1:]
        return pre + post + [arr[i]]

    remain = MAX_ENERGY
    res = 0
    currP = p
    while remain >= 0:
        # print(f'remain energy={remain}')
        # if winning card is in range
        if currP < k:
            # print(f'winning card is in range')
            # dont have enough energy to play winning card
            if remain < arr[currP]:
                break
            remain -= arr[currP]
            arr = excise(currP)
            currP = n - 1
            res += 1
            continue
        else:
            # print(f'winning card is not in range')
            smallest = min(arr[:k])
            # print(f'smallest is: {smallest}')
            # we can play smallest
            if remain >= smallest:
                smallestI = arr.index(smallest)
                remain -= arr[smallestI]
                arr = excise(smallestI)
                currP -= 1
            else:
                break
    
    print(res)




t = int(input())
for _ in range(t):
    solve()