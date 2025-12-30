"""
E. New Year's Gifts
time limit per test2 seconds
memory limit per test512 megabytes
Monocarp has 𝑛
 friends and decided to give a New Year's gift to each of them. He has also prepared 𝑚
 boxes to place the gifts in; the beauty of the 𝑖
-th box is 𝑎𝑖
. Every box can contain at most one gift.

Monocarp wants to give a gift worth at least 𝑦𝑖
 coins to the 𝑖
-th friend. Additionally, he knows that the 𝑖
-th friend will be happy if at least one of the following conditions holds:

the gift is in a box with beauty at least 𝑥𝑖
;
the gift is worth at least 𝑧𝑖
 (𝑧𝑖>𝑦𝑖
).
Your task is to help Monocarp calculate the maximum possible number of friends he can make happy if he has 𝑘
 coins. Note that Monocarp must purchase a gift for each friend, and the gift may not necessarily come in a box.
"""

T = int(input())
for _ in range(T):
    print('===========')
    n, m, k = map(int, input().split())
    beauty = list(map(int, input().split()))
    friends = [] # holds (beautyPoint, requiredCoins, coinsPoint)
    for j in range(n):
        a, b, c = map(int, input().split())
        friends.append((a, b, c))
    
    print(f'{n=} {m=} {k=}')
    print(f'{beauty=}')
    print(f'{friends=}')

    # left half will be people we spend purely coins on, we need to know the right half coin cost
    # right half will be sorted by boxes