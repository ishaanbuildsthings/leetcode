def solve(n, k):
    # We should make all sums from 0...k-1 doable

    # Then skip k

    ans = []

    nextPow2 = 1
    currSum = 0

    for i in range(25):
        if nextPow2 + currSum >= k:
            # placing this would get up to k, we cannot
            diff = k - currSum # even placing diff would be bad
            if diff - 1 > 0:
                ans.append(diff - 1)
            break
        else:
            ans.append(nextPow2)
            currSum += nextPow2
            nextPow2 *= 2

    # we can make all numbers up to but not include k

    # must add k+1

    # can make k+1... 2k

    ans.append(k + 1)
    currSum += k + 1

    maxMake = 2*k

    ans.append(2 * k + 1)
    maxMake += 2 * k + 1 # max make now 4K + 1, except for hole at 3k + 1
    hole = 3*k + 1
    while hole < n:
        ans.append(hole)
        hole *= 2
    
    ans.sort()
    while len(ans) > 25:
        ans.pop()

    if n != k and len(ans) < 25:
        ans.append(n)
    return ans
        # when we add some number X, we can make everything up to 2*X - 1, except for X+K
        # now we can make maxMake

    #                     K+1 addded

    # _ _ _ _ _ _ _ _ _ K _ _ _ _ _ _ _ _ _ 

    # |               |  |K+1... 2K|2K+1            3K|(3K+1)
    #.  A.  B.  C         D         E

    # Now I want to make 2K+1, I can add that, and it makes 2K+1 up to 4K+1, except for 3K+1, so I add 3K+1 as well

import random

t = int(input())
for _ in range(t):
    n, k = map(int, input().split())

    ans = solve(n, k)
    print(len(ans))
    print(*ans)