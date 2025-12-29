"""
You have n
 coins with denominations
 and a natural number k
. You also have a bag, which is initially empty, where you can place coins. You need to perform exactly k
 actions. In each action, you take one coin from those you have left and put it in your bag. After that, you can no longer take that coin.

At the same time, you have a cat that loves even numbers, so every time the sum of the denominations of the coins in your bag becomes even,
your cat empties the bag, meaning it takes all the coins to a place known only to it, and the bag is empty again.
Note that the bag is emptied every time the sum becomes even during the process of adding coins, not just at the very last moment.

Let your score be the sum of the denominations of the coins in the bag. Your task is to perform k
 actions such that your final score is maximized. Find the answer for all 1≤k<=n
.
"""
T = int(input())
for _ in range(T):
    print('================')
    n = int(input())
    A = list(map(int, input().split()))
    print(f'{A=}')

    # to place on odd amount, we must place O->E->E->E->...

    # We want the biggest chain of that we can place
    E = sorted([x for x in A if x % 2 == 0], reverse=True)
    O = sorted([x for x in A if x % 2], reverse=True)
    print(f'{E=}')
    print(f'{O=}')

    if not O:
        print(f'no odds, not doable')
        print(*([0] * n))
        continue

    res = [O[0]]
    for evenTake in range(1, len(E) + 1):
        res.append(res[-1] + E[evenTake - 1])
    totE = sum(E)

    pfE = []
    curr = 0
    for v in E:
        curr += v
        pfE.append(curr)
    pfO = []
    curr = 0
    for v in O:
        curr += v
        pfO.append(curr)
    
    if not E:
        print(*[O[i] if i % 2 == 0 else 0 for i in range(len(O))])
        continue
    
    print(f'initial easy res: {res}')
    for k in range(1 + len(E) + 1, n + 1):
        print(f'trying harder take: {k}')
        extraElements = k - len(E) - 1 # we need to figure out how to take these
        print(f'{extraElements=}')
        # if it even that is good, we will cancel out some small odd values and then score our max normal score
        if extraElements % 2 == 0:
            res.append(O[0] + totE)
            continue
        
        evenWouldTakeOdds = k - len(E)
        print(f'how many odds would we take if we had to take an even amount: {evenWouldTakeOdds}')
        # if they are odd, we would be taking an even amount of odds, we cannot have that happen
        # including another odd will break the chain, we must include 2 more odds, but then drop an even
        oddAmountOfOdds = evenWouldTakeOdds + 1
        print(f'instead we will taken this many odds: {oddAmountOfOdds}')
        if oddAmountOfOdds > len(O):
            res.append(0)
            continue
        evensTaken = k - oddAmountOfOdds
        # print(f'and this many evens: {evensTaken}')
        

        oddScore = O[0]
        evenScore = pfE[evensTaken - 1] if evensTaken else 0
        print(f'even score: {evenScore}')
        print(f'{oddScore=}')
        res.append(oddScore + evenScore)
    
    print(*res)

        
