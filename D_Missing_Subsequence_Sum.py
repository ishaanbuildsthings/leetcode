# def buildSubseqSumBitset(nums):
#     bits = 1
#     for x in nums:
#         if x < 0:
#             raise ValueError("bitset method requires non-negative integers")
#         bits |= bits << x
#     return bits

# def canMakeSum(bits, target):
#     if target < 0:
#         return False
#     return (bits >> target) & 1 == 1

# def listAllSums(bits, maxSum=None):
#     if maxSum is None:
#         maxSum = bits.bit_length() - 1
#     out = []
#     i = bits & ((1 << (maxSum + 1)) - 1)
#     while i:
#         lsb = i & -i
#         out.append(lsb.bit_length() - 1)
#         i -= lsb
#     return out






def solve(n, k):
    # print('========')
    # print(f'{n=} {k=}')

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

    # print(f'init ans before k: {ans}')

    # we can make all numbers up to but not include k

    # must add k+1

    # can make k+1... 2k

    ans.append(k + 1)
    currSum += k + 1
    # print(f'can make k+1... 2k: {ans}')

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
    
    # return ans


    # while maxMake < n:
    #     X = maxMake + 1
    #     ans.append(X)
    #     currSum += X
    #     maxMake = 2*X - 1
    #     hole = X + k
    #     if maxMake > n:
    #         break
        
    #     ans.append(hole)
    #     currSum += hole
    #     maxMake += hole
    ans.sort()
    while len(ans) > 25:
        ans.pop()
    # print(f'n is: {n}')
    if n != k and len(ans) < 25:
        ans.append(n)
    # if sum(ans) < n and n != k:
    #     ans.append(n)

    return ans
        # when we add some number X, we can make everything up to 2*X - 1, except for X+K
        # now we can make maxMake

    #                     K+1 addded

    # _ _ _ _ _ _ _ _ _ K _ _ _ _ _ _ _ _ _ 

    # |               |  |K+1... 2K|2K+1            3K|(3K+1)
    #.  A.  B.  C         D         E

    # Now I want to make 2K+1, I can add that, and it makes 2K+1 up to 4K+1, except for 3K+1, so I add 3K+1 as well

    # 


import random

t = int(input())
for _ in range(t):
    # print('================')
    n, k = map(int, input().split())


    # a = random.randint(2, 10**2)
    # b = random.randint(1, a)
    # n = a
    # k = b

    # cant make 2408 or 3211?

    # n = 50
    # k = 3

    # I make [1, 1] up to k-1
    # I put K+1 at the end, [1, 1, 4]
    # I can make up to 2K, except for K
    # Now I want 2K+1, I place a 7: [1, 1, 4, 7]
    # Can make up to 4K + 1 (13), except for 3K + 1 hole (10) due to K=3
    # So I place that 10 as well: [1, 1, 4, 7, 10]
    # Somehow I claim I can make up to 23 now, why?
    # We cannot make twice the hole, we need to place that 20

    # n=32
    # k=5
    # cannot make sum 32




    # n = 50 k = 3 
    # I produced: 1 1 4 7 10 24 27
    # cannot make sum 20



    ans = solve(n, k)
    print(len(ans))
    print(*ans)

    # BITS = buildSubseqSumBitset(ans)
    # for number in range(1, n + 1):
    #     if number != k:
    #         if not canMakeSum(BITS, number):
    #             print(f'error, couldnt make sum: {number} for n={n} k={k}')
    #     if number == k:
    #         if canMakeSum(BITS, number):
    #             print(f'error, could make sum: {number} for n={n} k={k}')
