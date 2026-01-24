t = int(input())
for _ in range(t):
    n, k = map(int, input().split())
    s = input()
    # a card X is guaranteed removed if X tops were taken, N - X + 1 bottoms were taken
    # a card is guaranteed in the deck if X tops + eithers cannot reach it, or the bottoms + eithers could not reach it

    tops = sum(x == '0' for x in s)
    bottoms = sum(x == '1' for x in s)
    either = sum(x == '2' for x in s)

    res = []

    for card in range(1, n + 1):
        # guaranteed removed
        if tops >= card:
            res.append('-')
            continue
        if card >= n - bottoms + 1:
            res.append('-')
            continue
        if k == n:
            res.append('-')
            continue
        
        # guaranteed in deck
        if tops + either < card:
            if n - (bottoms + either) >= card:
                res.append('+')
                continue

        res.append('?')
    
    print(''.join(res))