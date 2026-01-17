t = int(input())
for _ in range(t):
    n = int(input())
    stones = list(map(int, input().split()))
    stones = set([str(x) for x in stones]) # can safely remove duplicates
    stones2 = []
    for x in stones:
        stones2.append(int(x))
    stones = stones2
    stones.sort()
    # print('============')
    # print(f'{stones=}')

    # If I am on the last pile I win
    # If I am on the second to last pile, as long as it is not 1, I win

    # If I am on the third to last pile, I am at 1 or not
    # If not at 1 I can always win
    # I can either bring this pile down to 1 and force myself to get second to last pile
    # Or force opponent to get second to last pile

    # first person to reach a diff of 2 over the last wins
    if stones[0] > 1:
        print("Alice")
        continue

    sol = False

    for i in range(1, len(stones)):
        stone = stones[i]
        if stone > stones[i - 1] + 1:
            if i % 2:
                print("Bob")
            else:
                print("Alice")
            sol = True
            break
    
    if sol:
        continue
    
    if len(stones) % 2:
        print("Alice")
    else:
        print("Bob")
        
